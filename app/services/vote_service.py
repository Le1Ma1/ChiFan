from app.flex.tiebreak_flex import make_tiebreak_flex
from linebot.models import FlexSendMessage, TextSendMessage
from app.flex.vote_card import make_vote_card
from app.flex.choose_flex import make_choose_carousel, make_choose_result_flex
from datetime import datetime, timedelta, timezone
from app.services.db import (
    add_restaurant, get_restaurant_by_name, add_vote, get_votes_by_session,
    has_voted, get_active_vote, finish_vote, get_session_initiator, get_vote_expire_at,
    get_all_restaurants, delete_restaurant, update_or_insert_vote
)

def get_line_user_name(line_bot_api, user_id):
    try:
        profile = line_bot_api.get_profile(user_id)
        return profile.display_name
    except Exception:
        return "這位用戶"

class VoteService:

    @staticmethod
    def get_group_member_count(line_bot_api, group_id):
        import requests, os
        try:
            token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
            url = f"https://api.line.me/v2/bot/group/{group_id}/members/count"
            headers = {"Authorization": f"Bearer {token}"}
            resp = requests.get(url, headers=headers)
            if resp.status_code == 200:
                correct_count = int(resp.json()["count"])
                print(f"[DEBUG] from vote_service.get_group_member_count >> 群組人數: {correct_count}")
                return max(1, correct_count - 1)
            else:
                print(f"[Error] 查詢群組人數失敗: {resp.status_code}, {resp.text}")
                return 1
        except Exception as e:
            print(f"[Error] 取得群組人數失敗: {e}")
            return 1

    @staticmethod
    def session_is_expired(expire_at):
        if not expire_at:
            return False
        expire_time = datetime.fromisoformat(expire_at)
        now = datetime.now(timezone.utc)
        return now > expire_time

    @staticmethod
    def _auto_finish_if_all_voted(session_id, group_id, vote_type, finish_func, line_bot_api):
        total = VoteService.get_group_member_count(line_bot_api, group_id)
        votes = get_votes_by_session(session_id)
        voted_user_ids = set(v["user_id"] for v in votes)
        if len(voted_user_ids) >= total:
            finish_func(group_id, line_bot_api)
            type_map = {"add": "新增餐廳", "del": "刪除餐廳", "choose": "選餐廳"}
            msg_type = type_map.get(vote_type, "投票")
            line_bot_api.push_message(
                group_id,
                TextSendMessage(
                    text=f"所有成員均已完成「{msg_type}」投票，系統已自動提前結束並立即統計結果。\n（感謝大家踴躍參與，最終票數已公告！）"
                )
            )

    # ===== 投票分流（支援型別明確指定） =====
    @classmethod
    def cast_vote(cls, event, group_id, user_id, vote_type, vote_value, line_bot_api):
        vt = vote_type.lower()
        if vt == "add":
            cls.cast_add_vote(event, group_id, user_id, vote_value, line_bot_api)
        elif vt == "del":
            cls.cast_del_vote(event, group_id, user_id, vote_value, line_bot_api)
        elif vt == "choose":
            cls.cast_choose_vote(event, group_id, user_id, vote_value, line_bot_api)
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="未知的投票類型 , 請用 add/del/choose"))

    # ===== 新增餐廳投票 =====
    @classmethod
    def start_add_vote(cls, event, group_id, user_id, text, line_bot_api):
        name = text[5:].strip()
        restaurants = get_all_restaurants(group_id)
        if len(restaurants) >= 13:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="餐廳清單已達上限（13家） , 無法再新增囉! 請先刪除一些餐廳吧")
            )
            return
        if get_restaurant_by_name(group_id, name):
            line_bot_api.reply_message(
                event.reply_token, TextSendMessage(text="該餐廳已經在清單中 , 不用再新增囉~"))
            return
        # 幽默提示
        if len(restaurants) >= 2:
            msg = f"{name} 想為今天吃什麼增添一點選擇障礙 😏"
            line_bot_api.push_message(group_id, TextSendMessage(text=msg))
    
        active = get_active_vote(group_id, "add")
        if active:
            line_bot_api.reply_message(
                event.reply_token, TextSendMessage(text="已有新增餐廳的投票進行中 , 請稍後再試!"))
            return
    
        now = datetime.now(timezone.utc)
        expire_at = (now + timedelta(minutes=30)).isoformat()
        session_id = f"{group_id}-add-{now.strftime('%Y%m%d%H%M%S')}"
        add_vote(session_id, "add", group_id, None, user_id, 1, name=name, expire_at=expire_at, status="ongoing")
    
        desc = "餐廳已發起新增投票（發起人自動同意），請於下方點選按鈕投票"
        flex = make_vote_card(name, desc, "add", session_id)
        line_bot_api.push_message(
            group_id,
            FlexSendMessage(alt_text=f"{name} 餐廳新增投票", contents=flex)
        )

    @classmethod
    def cast_add_vote(cls, event, group_id, user_id, value, line_bot_api):
        active = get_active_vote(group_id, "add")
        if not active:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="目前沒有進行中的新增餐廳投票。"))
            return

        session_id = active[0]["session_id"]
        expire_at = get_vote_expire_at(session_id)
        if cls.session_is_expired(expire_at):
            finish_vote(session_id)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="投票已結束！"))
            return

        try:
            value = int(value)
        except Exception:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請用 `/vote add 1` 同意，`/vote add 0` 不同意。"))
            return

        if has_voted(session_id, user_id):
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="你已經投過票囉！"))
            return

        add_vote(session_id, "add", group_id, active[0]["restaurant_id"], user_id, value)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="已記錄你的投票！"))
        cls._auto_finish_if_all_voted(session_id, group_id, "add", cls.finish_add_vote, line_bot_api)

    @classmethod
    def finish_add_vote(cls, group_id, line_bot_api):
        active = get_active_vote(group_id, "add")
        if not active:
            return
        session_id = active[0]["session_id"]
        finish_vote(session_id)
        votes = get_votes_by_session(session_id)
        agree = sum(1 for v in votes if int(v["value"]) == 1)
        total = cls.get_group_member_count(line_bot_api, group_id)
        name = votes[0]["name"] if votes and "name" in votes[0] else "(未知餐廳)"

        if agree > total // 2:
            add_restaurant(group_id, name)
            line_bot_api.push_message(group_id, TextSendMessage(
                text=f"投票已結束，{agree}/{total} 人同意，餐廳成功加入清單！"))
        else:
            line_bot_api.push_message(group_id, TextSendMessage(
                text=f"投票已結束，僅 {agree}/{total} 人同意，餐廳未通過。"))

    # ===== 刪除餐廳投票 =====
    @classmethod
    def start_del_vote(cls, event, group_id, user_id, text, line_bot_api):
        name = text[5:].strip()
        rest = get_restaurant_by_name(group_id, name)
        if not rest:
            line_bot_api.reply_message(
                event.reply_token, TextSendMessage(text="該餐廳不存在！"))
            return

        active = get_active_vote(group_id, "del")
        if active:
            line_bot_api.reply_message(
                event.reply_token, TextSendMessage(text="已有刪除餐廳的投票進行中，請稍後再試！"))
            return

        now = datetime.now(timezone.utc)
        expire_at = (now + timedelta(hours=30)).isoformat()
        session_id = f"{group_id}-del-{now.strftime('%Y%m%d%H%M%S')}"
        add_vote(session_id, "del", group_id, rest["id"], user_id, 1, name=name, expire_at=expire_at, status="ongoing")

        desc = "餐廳已發起刪除投票（發起人自動同意），請於下方點選按鈕投票"
        flex = make_vote_card(name, desc, "del", session_id)
        line_bot_api.push_message(
            group_id,
            FlexSendMessage(alt_text=f"{name} 餐廳刪除投票", contents=flex)
        )

    @classmethod
    def cast_del_vote(cls, event, group_id, user_id, value, line_bot_api):
        active = get_active_vote(group_id, "del")
        if not active:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="目前沒有進行中的刪除餐廳投票。"))
            return

        session_id = active[0]["session_id"]
        expire_at = get_vote_expire_at(session_id)
        if cls.session_is_expired(expire_at):
            cls.finish_del_vote(group_id, line_bot_api)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="刪除投票已結束！"))
            return

        try:
            value = int(value)
        except Exception:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請用 `/vote del 1` 同意刪除，`/vote del 0` 不同意。"))
            return

        if has_voted(session_id, user_id):
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="你已經投過票囉！"))
            return

        add_vote(session_id, "del", group_id, active[0]["restaurant_id"], user_id, value)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="已記錄你的投票！"))
        cls._auto_finish_if_all_voted(session_id, group_id, "del", cls.finish_del_vote, line_bot_api)

    @classmethod
    def finish_del_vote(cls, group_id, line_bot_api):
        active = get_active_vote(group_id, "del")
        if not active:
            return
        session_id = active[0]["session_id"]
        finish_vote(session_id)
        votes = get_votes_by_session(session_id)
        agree = sum(1 for v in votes if int(v["value"]) == 1)
        total = cls.get_group_member_count(line_bot_api, group_id)
        name = votes[0]["name"] if votes and "name" in votes[0] else "(未知餐廳)"

        if agree > total // 2:
            delete_restaurant(group_id, name)
            line_bot_api.push_message(group_id, TextSendMessage(
                text=f"投票已結束，{agree}/{total} 人同意，『{name}』已從清單中移除。"))
        else:
            line_bot_api.push_message(group_id, TextSendMessage(
                text=f"投票已結束，僅 {agree}/{total} 人同意，餐廳未通過刪除。"))

    # ===== 選餐廳票選 =====
    @classmethod
    def start_choose_vote(cls, event, group_id, user_id, line_bot_api, duration_min=30):
        restaurants = get_all_restaurants(group_id)
        if not restaurants:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="目前餐廳清單為空，請先新增餐廳！"))
            return

        active = get_active_vote(group_id, "choose")
        if active:
            line_bot_api.reply_message(
                event.reply_token, TextSendMessage(text="已有選餐廳投票進行中，請先完成再發起！"))
            return

        now = datetime.now(timezone.utc)
        expire_at = (now + timedelta(minutes=duration_min)).isoformat()
        session_id = f"{group_id}-choose-{now.strftime('%Y%m%d%H%M%S')}"
        add_vote(session_id, "choose", group_id, None, user_id, None, expire_at=expire_at, status="ongoing")
        carousel = make_choose_carousel(restaurants, session_id, duration_min=duration_min)
        line_bot_api.push_message(
            group_id,
            FlexSendMessage(alt_text=f"【今天吃什麼】餐廳票選（限時 {duration_min} 分鐘）", contents=carousel)
        )

    @classmethod
    def cast_choose_vote(cls, event, group_id, user_id, value, line_bot_api):
        active = get_active_vote(group_id, "choose")
        if not active:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="目前沒有進行中的選餐票選。"))
            return

        session_id = active[0]["session_id"]
        expire_at = get_vote_expire_at(session_id)
        if cls.session_is_expired(expire_at):
            cls.finish_choose_vote(group_id, line_bot_api)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="選餐投票已結束！"))
            return
        if has_voted(session_id, user_id):  
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="你已經投過票囉！"))
            return
        try:
            index = int(value) - 1
        except Exception:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請用 /vote choose 餐廳編號（例如 /vote choose 2）"))
            return

        restaurants = get_all_restaurants(group_id)
        if index < 0 or index >= len(restaurants):
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="編號無效，請重新輸入。"))
            return

        restaurant_id = restaurants[index]["id"]
        add_vote(session_id, "choose", group_id, restaurant_id, user_id, 1)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"你投給 {restaurants[index]['name']}！"))
        cls._auto_finish_if_all_voted(session_id, group_id, "choose", cls.finish_choose_vote, line_bot_api)

    @classmethod
    def finish_choose_vote(cls, group_id, line_bot_api):
        active = get_active_vote(group_id, "choose")
        if not active:
            return
        session_id = active[0]["session_id"]
        finish_vote(session_id)
        votes = get_votes_by_session(session_id)
        if not votes:
            line_bot_api.push_message(group_id, TextSendMessage(text="沒有人投票 QQ"))
            return

        from collections import Counter
        restaurants = get_all_restaurants(group_id)
        id2name = {r["id"]: r["name"] for r in restaurants}
        id2id = {r["id"]: r["id"] for r in restaurants}
        counter = Counter(v["restaurant_id"] for v in votes)
        all_vote_result = sorted(
            [(id2name.get(rid, "未知"), cnt) for rid, cnt in counter.items()],
            key=lambda x: -x[1]
        )
        max_vote = max(counter.values())
        winners_id = [rid for rid, cnt in counter.items() if cnt == max_vote]
        winners_name = [id2name.get(rid, "未知") for rid in winners_id]

        if len(winners_id) > 1:
            # 平票處理
            initiator_id = get_session_initiator(session_id)
            flex = make_tiebreak_flex(winners_name, session_id)
            try:
                line_bot_api.push_message(
                    initiator_id,
                    FlexSendMessage(alt_text="票選平手，請決定結果", contents=flex)
                )
                line_bot_api.push_message(
                    group_id,
                    TextSendMessage(text="本次投票出現平手，請發起人決定最終餐廳！")
                )
            except Exception as e:
                line_bot_api.push_message(group_id, TextSendMessage(text=f"平手決選通知失敗: {e}"))
            # 可於 polling.py 定時檢查是否有 tiebreak 結果，逾時自動隨機
            return

        # 正常有唯一贏家
        winners = [id2name.get(rid, "未知") for rid in winners_id]
        flex = make_choose_result_flex(winners, max_vote, all_vote_result)
        line_bot_api.push_message(group_id, FlexSendMessage(alt_text="票選結果", contents=flex))

    @classmethod
    def end_vote(cls, event, group_id, user_id, line_bot_api, vote_type=None):
        vt = vote_type.lower() if vote_type else "add"
        active = get_active_vote(group_id, vt)
        if not active:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"目前沒有進行中的 {vt} 投票。"))
            return

        session_id = active[0]["session_id"]
        initiator_id = get_session_initiator(session_id)
        if user_id != initiator_id:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="只有發起人能提前結束投票！"))
            return

        votes = get_votes_by_session(session_id)
        agree = sum(1 for v in votes if int(v["value"]) == 1)
        total = cls.get_group_member_count(line_bot_api, group_id)
        print(f'[DEBUG] from vote_service.end_vote >> 群組總人數: {total} 人')
        if agree <= total // 2:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(
                text=f"同意票僅 {agree}，尚未超過群組一半({total // 2 + 1})，無法提前結束。"))
            return

        finish_vote(session_id)
        vote_name = votes[0]["name"] if votes and "name" in votes[0] else "(未知餐廳)"

        if vt == "add":
            add_restaurant(group_id, vote_name)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(
                text=f"提前結束投票，{agree}/{total} 人同意 , 【 {vote_name} 】 已加入清單！"))
        elif vt == "del":
            delete_restaurant(group_id, vote_name)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(
                text=f"提前結束投票，{agree}/{total} 人同意 , 【 {vote_name} 】 已從清單中移除！"))
        elif vt == "choose":
            # 選餐廳無需這種同意票邏輯，直接結算即可
            cls.finish_choose_vote(group_id, line_bot_api)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(
                text=f"選餐廳投票已提前結束，最終結果已公佈！"))
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="未知的投票類型！"))

    @classmethod
    def cast_vote_postback(cls, event, group_id, user_id, vote_type, value, session_id, line_bot_api):
        # 用 session_id 精準投票
        active = get_active_vote(group_id, vote_type)
        if not active or active[0]["session_id"] != session_id:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="投票已結束或已無效。"))
            return
        if has_voted(session_id, user_id):
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="你已經投過票囉！"))
            return
        add_vote(session_id, vote_type, group_id, active[0]["restaurant_id"], user_id, int(value))
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="已記錄你的投票！"))
        # 結束判斷流程照原本 _auto_finish_if_all_voted
        cls._auto_finish_if_all_voted(session_id, group_id, vote_type, getattr(cls, f'finish_{vote_type}_vote'), line_bot_api)

    @classmethod
    def cast_choose_postback(cls, event, group_id, user_id, session_id, index, line_bot_api):
        active = get_active_vote(group_id, "choose")
        if not active or active[0]["session_id"] != session_id:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="票選已結束或已無效。"))
            return
        restaurants = get_all_restaurants(group_id)
        already_voted = has_voted(session_id, user_id)
        if index == "random":
            import random
            idx = random.randint(0, len(restaurants) - 1)
            restaurant_id = restaurants[idx]["id"]
            update_or_insert_vote(session_id, "choose", group_id, restaurant_id, user_id, 1)
            user_name = get_line_user_name(line_bot_api, user_id)
            if already_voted:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"{user_name}已修改了投票，請靜待最終結果公布。"))
            else:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"已記錄{user_name}的投票，若想更改，請於投票截止前再次投票。"))
        else:
            try:
                idx = int(index) - 1
            except Exception:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="餐廳編號錯誤"))
                return
            if idx < 0 or idx >= len(restaurants):
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="編號無效，請重新輸入。"))
                return
            restaurant_id = restaurants[idx]["id"]
            name = restaurants[idx]["name"]
            update_or_insert_vote(session_id, "choose", group_id, restaurant_id, user_id, 1)
            user_name = get_line_user_name(line_bot_api, user_id)
            if already_voted:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"{user_name}已修改了投票，請靜待最終結果公布。"))
            else:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"已記錄{user_name}的投票，若想更改，請於投票截止前再次投票。"))
        # 檢查是否可自動結算
        votes = get_votes_by_session(session_id)
        total = cls.get_group_member_count(line_bot_api, group_id)
        voted_user_ids = set(v["user_id"] for v in votes)
        if len(voted_user_ids) >= total:
            cls.finish_choose_vote(group_id, line_bot_api)

    @classmethod
    def finalize_tiebreak(cls, session_id, winner_name, line_bot_api):
        # 找出 session, group_id
        active_vote = get_votes_by_session(session_id)
        if not active_vote:
            return
        group_id = active_vote[0]["group_id"]
        # 找餐廳 id
        restaurants = get_all_restaurants(group_id)
        name2id = {r["name"]: r["id"] for r in restaurants}
        if winner_name == "random":
            import random
            # 找這次平票的餐廳 id
            from collections import Counter
            counter = Counter(v["restaurant_id"] for v in active_vote)
            max_vote = max(counter.values())
            tied_rids = [rid for rid, cnt in counter.items() if cnt == max_vote]
            winner_id = random.choice(tied_rids)
            winner_name = next((r["name"] for r in restaurants if r["id"] == winner_id), "未知")
        else:
            winner_id = name2id.get(winner_name)
        # 公布結果
        msg = f"經發起人決定，今日用餐餐廳為：「{winner_name}」"
        line_bot_api.push_message(group_id, TextSendMessage(text=msg))
