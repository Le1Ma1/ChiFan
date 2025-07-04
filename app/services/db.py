from supabase import create_client
import os

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def add_restaurant(group_id, name, address):
    return supabase.table("restaurants").insert({"group_id": group_id, "name": name, "address": address}).execute()

def get_restaurants(group_id):
    res = supabase.table("restaurants").select("*").eq("group_id", group_id).execute()
    return res.data if hasattr(res, "data") else res
