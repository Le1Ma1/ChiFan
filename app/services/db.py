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

def add_vote(session_id, vote_type, group_id, restaurant_id, user_id, value):
    data = {
        "session_id": session_id,
        "vote_type": vote_type,
        "group_id": group_id,
        "restaurant_id": restaurant_id,
        "user_id": user_id,
        "value": value
    }
    return supabase.table("votes").insert(data).execute()

def count_votes(session_id):
    res = supabase.table("votes").select("*").eq("session_id", session_id).execute()
    return res.data if hasattr(res, "data") else []

def has_voted(session_id, user_id):
    res = supabase.table("votes").select("id").eq("session_id", session_id).eq("user_id", user_id).execute()
    return len(res.data) > 0 if hasattr(res, "data") else False
