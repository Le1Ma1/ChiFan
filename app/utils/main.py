from flask import Blueprint, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os

webhook_blueprint = Blueprint('webhook', __name__)

# 建議正式專案從 os.environ 或 config 模組讀取
line_bot_api = LineBotApi(os.getenv("CHANNEL_ACCESS_TOKEN", "測試用token"))
handler = WebhookHandler(os.getenv("CHANNEL_SECRET", "測試用secret"))

@webhook_blueprint.route("/", methods=['POST'])
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
    text = event.message.text
    if text == "ping":
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="pong"))
    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"你說：{text}"))
