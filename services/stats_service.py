from services.supabase_client import get_supabase_client


def get_stats_for_user(user_id: str):
    """Récupère les stats pour toutes les flashcards d'un utilisateur"""
    supabase = get_supabase_client()
    
    stats = supabase.table("flashcard_stats") \
        .select("*") \
        .eq("user_id", user_id) \
        .execute()
    
    return stats


def upsert_stats(user_id: str, card_id: str, correct: bool):
    """Met à jour ou crée les stats pour une flashcard"""
    supabase = get_supabase_client()
    
    # Récupérer les stats existantes
    result = supabase.table("flashcard_stats") \
        .select("*") \
        .eq("flashcard_id", card_id) \
        .eq("user_id", user_id) \
        .execute()
    
    if result.data:
        # Mettre à jour
        stat = result.data[0]
        new_times_seen = stat["times_seen"] + 1
        new_times_correct = stat["times_correct"] + (1 if correct else 0)
        
        supabase.table("flashcard_stats") \
            .update({
                "times_seen": new_times_seen,
                "times_correct": new_times_correct
            }) \
            .eq("id", stat["id"]) \
            .execute()
    else:
        # Créer
        supabase.table("flashcard_stats").insert({
            "user_id": user_id,
            "flashcard_id": card_id,
            "times_seen": 1,
            "times_correct": 1 if correct else 0
        }).execute()