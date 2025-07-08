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
    elif text.startswith("/del"):
        VoteService.start_del_vote(event, group_id, user_id, text, line_bot_api)
    elif text.startswith("/choose"):
        # 設定測試時長為 1 分鐘（正式用 30）
        VoteService.start_choose_vote(event, group_id, user_id, line_bot_api, duration_min=1)
    elif text.startswith("/vote"):
        parts = text.split()
        if len(parts) == 3:
            vote_type = parts[1].lower()  # add / del / choose
            vote_value = parts[2]
            VoteService.cast_vote(event, group_id, user_id, vote_type, vote_value, line_bot_api)
        else:
            # 引導用戶新格式，並保留原先自動分流（短期過渡）
            reply = "請用 `/vote 類型 參數`，例如 `/vote add 1`、`/vote choose 2`、`/vote del 1`"
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
    elif text.startswith("/endvote"):
        parts = text.split()
        if len(parts) == 2:
            vote_type = parts[1].lower()
            VoteService.end_vote(event, group_id, user_id, line_bot_api, vote_type)
        else:
            reply = "請用 `/endvote 類型`，例如 `/endvote add` `/endvote del` `/endvote choose`"
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
    
