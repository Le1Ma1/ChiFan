from flask import Blueprint, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from linebot.exceptions import InvalidSignatureError
import os
from app.services.db import add_restaurant

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

    # **只處理群組訊息**
    if event.source.type == "group":
        group_id = event.source.group_id
        try:
            profile = line_bot_api.get_group_member_profile(group_id, user_id)
            display_name = profile.display_name
        except:
            display_name = "用戶"

        if text.startswith("/add "):
            name = text[5:].strip()
            if not name:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="請輸入餐廳名稱：/add 餐廳名稱")
                )
                return
            add_restaurant(group_id, name)
            reply_text = f"{display_name} 想添加 『 {name} 』\n至清單增加選擇難度\n大家快來參與表決吧～"
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=reply_text)
            )
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="請輸入正確指令！")
            )
    else:
        # 其他來源，例如個人聊天室
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="請在群組中使用本機器人功能。")
        )
