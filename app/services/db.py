from supabase import create_client
import os

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def add_restaurant(group_id, name):
    data = {"group_id": group_id, "name": name}
    res = supabase.table("restaurants").insert(data).execute()
    if hasattr(res, "data") and res.data:
        return res.data[0]
    return None

def get_restaurant_by_name(group_id, name):
    res = supabase.table("restaurants").select("*").eq("group_id", group_id).eq("name", name).execute()
    if hasattr(res, "data") and res.data:
        return res.data[0]
    return None

def get_all_restaurants(group_id):
    res = supabase.table("restaurants").select("*").eq("group_id", group_id).execute()
    return res.data if hasattr(res, "data") else []

def delete_restaurant(group_id, name):
    res = supabase.table("restaurants").delete().eq("group_id", group_id).eq("name", name).execute()
    return res

def add_vote(session_id, vote_type, group_id, restaurant_id, user_id, value, name=None, expire_at=None, status="ongoing"):
    data = {
        "session_id": session_id,
        "vote_type": vote_type,
        "group_id": group_id,
        "restaurant_id": restaurant_id,
        "user_id": user_id,
        "value": value,
        "status": status,
    }
    if name:
        data["name"] = name
    if expire_at:
        data["expire_at"] = expire_at
    return supabase.table("votes").insert(data).execute()

def get_votes_by_session(session_id):
    res = supabase.table("votes").select("*")\
        .eq("session_id", session_id)\
        .execute()
    if hasattr(res, "data") and res.data:
        # 只回傳有投票的
        return [r for r in res.data if r.get("value") is not None]
    return []

def has_voted(session_id, user_id):
    res = supabase.table("votes").select("id,value")\
        .eq("session_id", session_id)\
        .eq("user_id", user_id)\
        .execute()
    if hasattr(res, "data") and res.data:
        # 只要有一筆 value 不是 None 就算已投過
        for r in res.data:
            if r.get("value") is not None:
                return True
    return False

def get_active_vote(group_id, vote_type):
    res = supabase.table("votes").select("*") \
        .eq("group_id", group_id) \
        .eq("vote_type", vote_type) \
        .eq("status", "ongoing") \
        .execute()
    return res.data if hasattr(res, "data") else []

def finish_vote(session_id):
    return supabase.table("votes").update({"status": "finished"}).eq("session_id", session_id).execute()

def get_session_initiator(session_id):
    res = supabase.table("votes").select("*").eq("session_id", session_id).order("id", desc=False).limit(1).execute()
    if hasattr(res, "data") and res.data:
        return res.data[0].get("user_id")
    return None

def get_vote_expire_at(session_id):
    res = supabase.table("votes").select("expire_at").eq("session_id", session_id).limit(1).execute()
    if hasattr(res, "data") and res.data:
        return res.data[0].get("expire_at")
    return None

def get_all_active_vote_groups(vote_type="choose"):
    res = supabase.table("votes").select("group_id").eq("vote_type", vote_type).eq("status", "ongoing").execute()
    if hasattr(res, "data") and res.data:
        # 用 set 去除重複 group_id
        return list(set(v["group_id"] for v in res.data))
    return []

def update_or_insert_vote(session_id, vote_type, group_id, restaurant_id, user_id, value, name=None, expire_at=None, status="ongoing"):
    """
    先查有沒有這個 session_id + user_id , 有就 update , 沒有就 insert
    """
    from datetime import datetime
    res = supabase.table("votes").select("id").eq("session_id", session_id).eq("user_id", user_id).execute()
    data = {
        "session_id": session_id,
        "vote_type": vote_type,
        "group_id": group_id,
        "restaurant_id": restaurant_id,
        "user_id": user_id,
        "value": value,
        "status": status,
    }
    if name:
        data["name"] = name
    if expire_at:
        data["expire_at"] = expire_at

    if hasattr(res, "data") and res.data:
        vote_id = res.data[0]["id"]
        return supabase.table("votes").update(data).eq("id", vote_id).execute()
    else:
        return supabase.table("votes").insert(data).execute()