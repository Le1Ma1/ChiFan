from app.services.db import get_all_restaurants
from app.flex.main_menu import make_main_menu_flex 
from app.flex.list_carousel import make_del_carousel     
from app.services.vote_service import VoteService
from flask import Blueprint, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage, PostbackEvent, FlexSendMessage
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

    if text == "/menu":
        flex = make_main_menu_flex()
        line_bot_api.reply_message(
            event.reply_token,
            FlexSendMessage(alt_text="主選單", contents=flex)
        )
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

@handler.add(PostbackEvent)
def handle_postback(event):
    data = event.postback.data
    params = dict(item.split('=') for item in data.split('&'))
    menu_action = params.get("menu")
    vote_type = params.get("vote")
    session_id = params.get("session")
    user_id = event.source.user_id
    group_id = event.source.group_id if event.source.type == "group" else None
    index = params.get("index")
    value = params.get("value")

    # === 主選單操作 ===
    if menu_action == "choose":
        # 直接進入 /choose 流程
        VoteService.start_choose_vote(event, group_id, user_id, line_bot_api, duration_min=1)  # 或自訂分鐘
        return
    elif menu_action == "del":
        # 推出所有餐廳列表供用戶點擊刪除
        restaurants = get_all_restaurants(group_id)
        if not restaurants:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="目前清單沒有餐廳可刪除"))
            return
        flex = make_del_carousel(restaurants, group_id)
        line_bot_api.reply_message(
            event.reply_token,
            FlexSendMessage(alt_text="刪除餐廳", contents=flex)
        )
        return
    
    if params.get("tiebreak") and params.get("winner"):
        session_id = params["tiebreak"]
        winner = params["winner"]
        VoteService.finalize_tiebreak(session_id, winner, line_bot_api)
        return

    if vote_type == "choose":
        VoteService.cast_choose_postback(event, group_id, user_id   , session_id, index, line_bot_api)
    else:
        VoteService.cast_vote_postback(event, group_id, user_id, vote_type, value, session_id, line_bot_api)
    
    del_name = params.get("name")
    if vote_type == "del" and del_name and session_id == "menu":
        # 直接啟動刪除餐廳投票流程
        VoteService.start_del_vote(event, group_id, user_id, f"/del {del_name}", line_bot_api)
        return