from app.flex.rank_card import make_top3_flex, make_topuser_flex
from app.services.db import get_all_restaurants
from app.flex.main_menu import make_main_menu_flex
from app.flex.list_carousel import make_del_carousel
from app.services.vote_service import VoteService
from flask import Blueprint, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.models import ImageSendMessage, MessageEvent, TextMessage, TextSendMessage, PostbackEvent, FlexSendMessage
from linebot.exceptions import InvalidSignatureError
import os

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

from app.flex.intro_card import make_intro_card
from app.flex.help_card import make_help_card
from app.flex.contact_card import make_contact_card

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text.strip()
    source = event.source
    group_id = getattr(source, "group_id", None)
    user_id = getattr(source, "user_id", None)

    # 一對一（private chat）
    if not group_id:
        if text == "主選單":
            line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text="主選單", contents=make_intro_card()))
            return
        elif text == "你能為我做甚麼 ?":
            line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text="功能說明", contents=make_help_card()))
            return
        elif text == "聯繫方式":
            line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text="聯絡作者", contents=make_contact_card()))
            return
        elif text == "發起投票":
            line_bot_api.reply_message(event.reply_token, TextSendMessage("請將我邀請進群組發起投票功能！"))
            return
        elif text == "助原創一臂之力":
            messages = [
                ImageSendMessage(
                    original_content_url="https://i.postimg.cc/GhNYPv3W/USDT-QR.png",
                    preview_image_url="https://i.postimg.cc/GhNYPv3W/USDT-QR.png"
                ),
                TextSendMessage(
                    "USDT (TRC-20) 地址：\nTUmegztKiXNjhmifi7wJ8SdMkowY2s7Avw"
                )
            ]
            line_bot_api.reply_message(event.reply_token, messages)
            return
        else:
            line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text="主選單", contents=make_intro_card()))
        return

    # ======= 群組功能 =======
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
        VoteService.start_choose_vote(event, group_id, user_id, line_bot_api, duration_min=1)
    elif text.startswith("/vote"):
        parts = text.split()
        if len(parts) == 3:
            vote_type = parts[1].lower()
            vote_value = parts[2]
            VoteService.cast_vote(event, group_id, user_id, vote_type, vote_value, line_bot_api)
        else:
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
    params = dict(item.split('=') for item in data.split('&') if '=' in item)
    action = params.get("action")
    menu_action = params.get("menu")
    vote_type = params.get("vote")
    session_id = params.get("session")
    user_id = getattr(event.source, "user_id", None)
    group_id = getattr(event.source, "group_id", None)
    index = params.get("index")
    value = params.get("value")

    if action == "top3":
        top3 = [
            {"name": "八方雲集", "votes": 12},
            {"name": "麥當勞", "votes": 8},
            {"name": "燒肉丼飯", "votes": 6}
        ]
        flex = make_top3_flex(top3)
        line_bot_api.reply_message(
            event.reply_token,
            FlexSendMessage(alt_text="人氣排行", contents=flex)
        )
        return

    if action == "topuser":
        topuser = {
            "name": "W.FTX",
            "count": 10,
            "desc": "本月投票王"
        }
        flex = make_topuser_flex(topuser)
        line_bot_api.reply_message(
            event.reply_token,
            FlexSendMessage(alt_text="貢獻榜", contents=flex)
        )
        return

    # === 主選單操作 ===
    if menu_action == "choose":
        VoteService.start_choose_vote(event, group_id, user_id, line_bot_api, duration_min=30)
        return
    elif menu_action == "del":
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
        VoteService.cast_choose_postback(event, group_id, user_id, session_id, index, line_bot_api)
    else:
        VoteService.cast_vote_postback(event, group_id, user_id, vote_type, value, session_id, line_bot_api)

    del_name = params.get("name")
    if vote_type == "del" and del_name and session_id == "menu":
        VoteService.start_del_vote(event, group_id, user_id, f"/del {del_name}", line_bot_api)
        return
