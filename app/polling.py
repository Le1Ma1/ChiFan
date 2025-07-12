from apscheduler.schedulers.background import BackgroundScheduler
from app.services.db import get_all_active_vote_groups, get_active_vote, get_vote_expire_at, get_votes_with_tiebreak_timeout
from app.services.vote_service import VoteService
import os
from datetime import datetime, timezone
from linebot import LineBotApi

def check_expired_votes():
    line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
    now = datetime.now(timezone.utc)
    print(f"[Polling] {now} 進行輪詢檢查")
    # 1. 處理選餐廳投票
    group_ids_choose = get_all_active_vote_groups("choose")
    for group_id in group_ids_choose:
        active_votes = get_active_vote(group_id, "choose")
        for vote in active_votes:
            session_id = vote["session_id"]
            expire_at = get_vote_expire_at(session_id)
            if VoteService.session_is_expired(expire_at):
                print(f"[Polling] 結算過期選餐投票 {session_id}")
                VoteService.finish_choose_vote(group_id, line_bot_api)

    # 2. 處理刪除餐廳投票
    group_ids_del = get_all_active_vote_groups("del")
    for group_id in group_ids_del:
        active_votes = get_active_vote(group_id, "del")
        for vote in active_votes:
            session_id = vote["session_id"]
            expire_at = get_vote_expire_at(session_id)
            if VoteService.session_is_expired(expire_at):
                print(f"[Polling] 結算過期刪除餐廳投票 {session_id}")
                VoteService.finish_del_vote(group_id, line_bot_api)

    # 3. 處理新增餐廳投票
    group_ids_add = get_all_active_vote_groups("add")
    for group_id in group_ids_add:
        active_votes = get_active_vote(group_id, "add")
        for vote in active_votes:
            session_id = vote["session_id"]
            expire_at = get_vote_expire_at(session_id)
            if VoteService.session_is_expired(expire_at):
                print(f"[Polling] 結算過期新增餐廳投票 {session_id}")
                VoteService.finish_add_vote(group_id, line_bot_api)

def check_tiebreak_timeout(line_bot_api):
    # 查所有 tiebreak_expire_at 已過期且未決定的 session
    sessions = get_votes_with_tiebreak_timeout()
    for session in sessions:
        session_id = session["session_id"]
        VoteService.finalize_tiebreak(session_id, "random", line_bot_api)

def start_polling_job():
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_expired_votes, 'interval', seconds=1)
    scheduler.start()
    print("[Polling] APScheduler 啟動成功")