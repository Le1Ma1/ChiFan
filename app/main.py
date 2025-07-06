from flask import Blueprint, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from linebot.exceptions import InvalidSignatureError
import os
from datetime import datetime, timedelta, timezone

from app.services.db import (
    add_restaurant, get_restaurant_by_name, add_vote, get_votes_by_session,
    has_voted, get_active_vote, finish_vote, get_session_initiator, get_vote_expire_at
)

bp = Blueprint('webhook', __name__)
line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))

# LINE API 取得真實人數
def get_group_member_count(group_id):
    try:
        summary = line_bot_api.get_group_summary(group_id)
        count = line_bot_api.get_group_member_count(group_id)
        # 這是官方方法，會排除 bot 自己
        return count
    except Exception as e:
        print(f"[Error] 取得群組人數失敗: {e}")
        return 1

def session_is_expired(expire_at):
    if not expire_at:
        return False
    expire_time = datetime.fromisoformat(expire_at)
    now = datetime.now(timezone.utc)
    return now > expire_time

@bp.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text.strip()
    user_id = event.source.user_id
    group_id = event.source.group_id if event.source.type == "group" else None

    # 檢查有無已過期的進行中投票
    active = get_active_vote(group_id, "add")
    if active:
        session_id = active[0]["session_id"]
        expire_at = get_vote_expire_at(session_id)
        if session_is_expired(expire_at):
            # 自動結束投票
            finish_vote(session_id)
            votes = get_votes_by_session(session_id)
            agree = sum(1 for v in votes if v["value"] == 1)
            total = get_group_member_count(group_id)
            if agree > total // 2:
                line_bot_api.push_message(group_id, TextSendMessage(
                    text=f"投票已自動結束，{agree}/{total} 人同意，餐廳成功加入清單！"))
            else:
                line_bot_api.push_message(group_id, TextSendMessage(
                    text=f"投票已自動結束，僅 {agree}/{total} 人同意，餐廳未通過。"))
            return  # 此訊息不會回 event.reply_token

    # 發起新增餐廳投票
    if text.startswith("/add "):
        name = text[5:].strip()
        if get_restaurant_by_name(group_id, name):
            line_bot_api.reply_message(
                event.reply_token, TextSendMessage(text="該餐廳已經在清單中，不用再新增囉～"))
            return
        active = get_active_vote(group_id, "add")
        if active:
            line_bot_api.reply_message(
                event.reply_token, TextSendMessage(text="已有新增餐廳的投票進行中，請稍後再試！"))
            return

        now = datetime.now(timezone.utc)
        expire_at = (now + timedelta(hours=24)).isoformat()
        session_id = f"{group_id}-add-{now.strftime('%Y%m%d%H%M%S')}"
        rest = add_restaurant(group_id, name)
        add_vote(session_id, "add", group_id, rest["id"], user_id, 1, name=name, expire_at=expire_at, status="ongoing")
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"{name} 餐廳已發起新增投票，大家快來投票吧！（發起人自動同意）\n請用 `/vote 1` 同意，`/vote 0` 不同意。")
        )
        return

    # 投票
    if text.startswith("/vote"):
        active = get_active_vote(group_id, "add")
        if not active:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="目前沒有進行中的新增餐廳投票。"))
            return
        session_id = active[0]["session_id"]
        expire_at = get_vote_expire_at(session_id)
        if session_is_expired(expire_at):
            finish_vote(session_id)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="投票已結束！"))
            return
        try:
            value = int(text.split()[1])
        except Exception:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請用 `/vote 1` 同意，`/vote 0` 不同意。"))
            return
        if has_voted(session_id, user_id):
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="你已經投過票囉！"))
            return
        add_vote(session_id, "add", group_id, active[0]["restaurant_id"], user_id, value)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="已記錄你的投票！"))
        return

    # 發起人提前結束投票（/endvote）
    if text == "/endvote":
        active = get_active_vote(group_id, "add")
        if not active:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="目前沒有進行中的新增餐廳投票。"))
            return
        session_id = active[0]["session_id"]
        initiator_id = get_session_initiator(session_id)
        if user_id != initiator_id:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="只有發起人能提前結束投票！"))
            return
        votes = get_votes_by_session(session_id)
        agree = sum(1 for v in votes if int(v["value"]) == 1)
        total = get_group_member_count(group_id)
        print(f'[Debug] 群組總人數: {total} 人')
        if agree <= total // 2:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(
                text=f"同意票僅 {agree}，尚未超過群組一半({total // 2 + 1})，無法提前結束。"))
            return
        finish_vote(session_id)
        vote_name = votes[0]["name"] if votes and "name" in votes[0] else "(未知餐廳)"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(
            text=f"提前結束投票，{agree}/{total} 人同意，餐廳已加入清單！"))
        return

    # 其他訊息
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請輸入正確指令！"))
