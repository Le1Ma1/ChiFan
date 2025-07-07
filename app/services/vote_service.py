from datetime import datetime, timedelta, timezone
from linebot.models import TextSendMessage

from app.services.db import (
    add_restaurant, get_restaurant_by_name, add_vote, get_votes_by_session,
    has_voted, get_active_vote, finish_vote, get_session_initiator, get_vote_expire_at, get_all_restaurants
)

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
                # LINE API 包含 bot 本人，通常需扣掉 1
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

    # ===== 新增餐廳投票 ====
    @classmethod
    def start_add_vote(cls, event, group_id, user_id, text, line_bot_api):
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
        add_vote(session_id, "add", group_id, None, user_id, 1, name=name, expire_at=expire_at, status="ongoing")
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(
                text=f"{name} 餐廳已發起新增投票，大家快來投票吧！（發起人自動同意）\n請用 `/vote 1` 同意，`/vote 0` 不同意。"
            )
        )

    # ====== 選餐廳票選 =====
    @classmethod
    def start_choose_vote(cls, event, group_id, user_id, line_bot_api, duration_min=1):
        restaurants = get_all_restaurants(group_id)
        if not restaurants:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="目前餐廳清單為空，請先新增餐廳！"))
            return

        now = datetime.now(timezone.utc)
        expire_at = (now + timedelta(minutes=duration_min)).isoformat()
        session_id = f"{group_id}-choose-{now.strftime('%Y%m%d%H%M%S')}"
        restaurant_list = "\n".join([f"{i+1}. {r['name']}" for i, r in enumerate(restaurants)])

        add_vote(session_id, "choose", group_id, None, user_id, None, expire_at=expire_at, status="ongoing")
        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(
                text=f"【今天吃什麼】請回覆 /vote 餐廳編號\n{restaurant_list}\n投票限時 {duration_min} 分鐘！"
            )
        )

    # ====== 投票指令整合分流 =====
    @classmethod
    def cast_vote(cls, event, group_id, user_id, text, line_bot_api):
        # 先判斷進行中投票型別（優先選餐廳，然後新增餐廳）
        active_choose = get_active_vote(group_id, "choose")
        if active_choose:
            cls.cast_choose_vote(event, group_id, user_id, text, line_bot_api)
            return
        active_add = get_active_vote(group_id, "add")
        if active_add:
            cls.cast_add_vote(event, group_id, user_id, text, line_bot_api)
            return
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="目前沒有進行中的投票。"))

    # ====== 投選餐廳票 =====
    @classmethod
    def cast_choose_vote(cls, event, group_id, user_id, text, line_bot_api):
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
            index = int(text.split()[1]) - 1
        except Exception:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請用 /vote 餐廳編號（例如 /vote 2）"))
            return

        restaurants = get_all_restaurants(group_id)
        if index < 0 or index >= len(restaurants):
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="編號無效，請重新輸入。"))
            return

        restaurant_id = restaurants[index]["id"]
        # 覆蓋式投票：如果已投過，先刪再加，或直接插入讓後來的票有效
        add_vote(session_id, "choose", group_id, restaurant_id, user_id, 1)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"你投給 {restaurants[index]['name']}！"))

    # ====== 投新增餐廳票 =====
    @classmethod
    def cast_add_vote(cls, event, group_id, user_id, text, line_bot_api):
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
            value = int(text.split()[1])
        except Exception:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請用 `/vote 1` 同意，`/vote 0` 不同意。"))
            return

        if has_voted(session_id, user_id):
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="你已經投過票囉！"))
            return

        add_vote(session_id, "add", group_id, active[0]["restaurant_id"], user_id, value)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="已記錄你的投票！"))

    # ====== 選餐廳投票結算 =====
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
        counter = Counter(v["restaurant_id"] for v in votes)
        max_vote = max(counter.values())
        winners = [rid for rid, cnt in counter.items() if cnt == max_vote]

        restaurants = get_all_restaurants(group_id)
        id2name = {r["id"]: r["name"] for r in restaurants}
        win_names = [id2name.get(rid, "未知") for rid in winners]

        msg = "最高票餐廳：" + "、".join(win_names) + f"\n({max_vote} 票)"
        line_bot_api.push_message(group_id, TextSendMessage(text=msg))

    # ====== 新增餐廳投票提前結束原有功能 =====
    @classmethod
    def end_vote(cls, event, group_id, user_id, line_bot_api):
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
        total = cls.get_group_member_count(line_bot_api, group_id)
        print(f'[DEBUG] 群組總人數: {total} 人')
        if agree <= total // 2:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(
                text=f"同意票僅 {agree}，尚未超過群組一半({total // 2 + 1})，無法提前結束。"))
            return

        finish_vote(session_id)
        vote_name = votes[0]["name"] if votes and "name" in votes[0] else "(未知餐廳)"
        add_restaurant(group_id, vote_name)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(
            text=f"提前結束投票，{agree}/{total} 人同意 , 『 {vote_name} 」 已加入清單！"))
