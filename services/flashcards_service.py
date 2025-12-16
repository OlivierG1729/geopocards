from services.supabase_client import get_supabase_client
from services.stats_service import get_stats_for_user


def create_flashcard(user_id: str, question: str, answer: str):
    supabase = get_supabase_client()
    supabase.table("flashcards").insert({
        "user_id": user_id,
        "question": question,
        "answer": answer
    }).execute()


def get_flashcards(user_id: str):
    supabase = get_supabase_client()

    cards = supabase.table("flashcards") \
        .select("*") \
        .eq("user_id", user_id) \
        .execute().data

    stats = get_stats_for_user(user_id).data
    stats_by_card = {s["flashcard_id"]: s for s in stats}

    for c in cards:
        s = stats_by_card.get(c["id"], {})
        times_seen = s.get("times_seen", 0)
        times_correct = s.get("times_correct", 0)

        c["times_seen"] = times_seen
        c["times_correct"] = times_correct
        c["mastery"] = times_correct / max(1, times_seen)

    return cards


def update_flashcard(user_id: str, card_id: int, question: str, answer: str):
    """Met à jour une flashcard existante"""
    supabase = get_supabase_client()
    
    supabase.table("flashcards") \
        .update({"question": question, "answer": answer}) \
        .eq("id", card_id) \
        .eq("user_id", user_id) \
        .execute()


def delete_flashcard(user_id: str, card_id: int):
    """Supprime une flashcard et ses stats associées"""
    supabase = get_supabase_client()
    
    # Supprimer les stats associées (table s'appelle flashcard_stats)
    supabase.table("flashcard_stats") \
        .delete() \
        .eq("flashcard_id", card_id) \
        .execute()
    
    # Supprimer les tags associés
    supabase.table("flashcard_tags") \
        .delete() \
        .eq("flashcard_id", card_id) \
        .execute()
    
    # Supprimer la flashcard
    supabase.table("flashcards") \
        .delete() \
        .eq("id", card_id) \
        .eq("user_id", user_id) \
        .execute()


def get_flashcards_with_tags(user_id: str):
    """Récupère toutes les flashcards avec leurs tags"""
    from services.tags_service import get_tags_for_flashcard
    
    cards = get_flashcards(user_id)
    
    for card in cards:
        card["tags"] = get_tags_for_flashcard(card["id"])
    
    return cards