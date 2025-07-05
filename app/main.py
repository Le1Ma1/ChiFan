from flask import Blueprint, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from linebot.models.mention import Mention
from linebot.models.mentionee import Mentionee
from linebot.exceptions import InvalidSignatureError
import os
from app.services.db import add_restaurant

bp = Blueprint('webhook', __name__)

line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "測試用token"))
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET", "測試用secret"))

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
    group_id = None
    if event.source.type == "group":
        group_id = event.source.group_id
    else:
        group_id = "personal"

    # 取得使用者名稱
    profile = line_bot_api.get_profile(user_id)
    display_name = profile.display_name if hasattr(profile, "display_name") else "用戶"

    if text.startswith("/add "):
        name = text[5:].strip()
        add_restaurant(group_id, name)

        # 嘗試標記所有人，LINE 只支援標註特定成員，無 @everyone
        # 通常做法是製作一個 @ 名稱、或叫大家「記得看群公告」。
        # 這裡範例：只標註發起人
        mention = Mention(
            mentionees=[
                Mentionee(user_id=user_id, type="user")
            ]
        )
        reply_text = f"@{display_name} 想添加『{name}』餐廳進入吃飯表單增加選擇難度！\n大家快來參與表決吧～"

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_text, mention=mention)
        )

    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請輸入正確指令！"))

