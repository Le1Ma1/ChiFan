from flask import Blueprint, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from linebot.exceptions import InvalidSignatureError
import os

from app.services.vote_service import VoteService

bp = Blueprint('webhook', __name__)
line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))

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

    if not group_id:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請在群組內使用本 Bot"))
        return

    if text.startswith("/add "):
        VoteService.start_add_vote(event, group_id, user_id, text, line_bot_api)
    elif text.startswith("/choose"):
        # 設定測試時長為 1 分鐘（正式用 30）
        VoteService.start_choose_vote(event, group_id, user_id, line_bot_api, duration_min=1)
    elif text.startswith("/vote"):
        # 自動分辨選餐還是新增餐廳投票
        VoteService.cast_vote(event, group_id, user_id, text, line_bot_api)
    elif text == "/endvote":
        VoteService.end_vote(event, group_id, user_id, line_bot_api)
    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請輸入正確指令！"))
