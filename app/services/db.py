import os
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ---------- restaurants ----------
def add_restaurant(group_id: str, name: str, address: str = ""):
    """新增一筆餐廳記錄"""
    data = {
        "group_id": group_id,
        "name": name,
        "address": address
    }
    return supabase.table("restaurants").insert(data).execute()

def get_restaurants(group_id: str):
    """取得該群組所有餐廳"""
    res = (
        supabase
        .table("restaurants")
        .select("*")
        .eq("group_id", group_id)
        .order("created_at", desc=False)
        .execute()
    )
    return res.data if hasattr(res, "data") else []

def delete_restaurant(group_id: str, restaurant_id: int):
    """刪除某群組下指定 id 的餐廳"""
    return (
        supabase
        .table("restaurants")
        .delete()
        .eq("group_id", group_id)
        .eq("id", restaurant_id)
        .execute()
    )

# ---------- votes ----------
def add_vote(group_id: str, restaurant_id: int, user_id: str, session_id: str, vote_type: str, value: int = 1):
    """新增一筆投票記錄（支援各種投票模式）"""
    data = {
        "group_id": group_id,
        "restaurant_id": restaurant_id,
        "user_id": user_id,
        "session_id": session_id,
        "vote_type": vote_type,    # 'add_restaurant'/'choose_restaurant'/'delete_restaurant'
        "value": value
    }
    return supabase.table("votes").insert(data).execute()

def get_votes(group_id: str, session_id: str, vote_type: str):
    """取得某群組在某投票階段的所有投票"""
    res = (
        supabase
        .table("votes")
        .select("*")
        .eq("group_id", group_id)
        .eq("session_id", session_id)
        .eq("vote_type", vote_type)
        .execute()
    )
    return res.data if hasattr(res, "data") else []

def user_has_voted(group_id: str, session_id: str, vote_type: str, user_id: str):
    """檢查用戶是否已投過票"""
    res = (
        supabase
        .table("votes")
        .select("id")
        .eq("group_id", group_id)
        .eq("session_id", session_id)
        .eq("vote_type", vote_type)
        .eq("user_id", user_id)
        .execute()
    )
    return bool(res.data)

def count_votes(group_id: str, session_id: str, vote_type: str):
    """統計該 session 的投票數，依餐廳 group by，回傳票數"""
    res = (
        supabase
        .table("votes")
        .select("restaurant_id, count:restaurant_id")
        .eq("group_id", group_id)
        .eq("session_id", session_id)
        .eq("vote_type", vote_type)
        .group("restaurant_id")
        .execute()
    )
    return res.data if hasattr(res, "data") else []

def get_delete_votes_for_restaurant(group_id: str, session_id: str, restaurant_id: int):
    """取得某餐廳的所有刪除投票"""
    res = (
        supabase
        .table("votes")
        .select("*")
        .eq("group_id", group_id)
        .eq("session_id", session_id)
        .eq("vote_type", "delete_restaurant")
        .eq("restaurant_id", restaurant_id)
        .execute()
    )
    return res.data if hasattr(res, "data") else []

