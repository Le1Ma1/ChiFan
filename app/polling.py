from apscheduler.schedulers.background import BackgroundScheduler
from app.services.db import get_all_active_vote_groups, get_active_vote, get_vote_expire_at
from app.services.vote_service import VoteService
import os
from linebot import LineBotApi

def check_expired_votes():
    group_ids = get_all_active_vote_groups("choose")
    line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
    for group_id in group_ids:
        active_votes = get_active_vote(group_id, "choose")
        for vote in active_votes:
            session_id = vote["session_id"]
            expire_at = get_vote_expire_at(session_id)
            if VoteService.session_is_expired(expire_at):
                print(f"[Polling] 結算過期選餐投票 {session_id}")
                VoteService.finish_choose_vote(group_id, line_bot_api)

def start_polling_job():
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_expired_votes, 'interval', seconds=1)
    scheduler.start()
    print("[Polling] APScheduler 啟動成功")
