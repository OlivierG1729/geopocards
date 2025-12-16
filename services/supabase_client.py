
from supabase import create_client
from config.settings import SUPABASE_URL, SUPABASE_KEY

_supabase = None

def get_supabase_client():
    global _supabase
    if _supabase is None:
        _supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _supabase
