
from services.supabase_client import get_supabase_client


def get_or_create_predefined_tags(user_id: str):
    """
    Copie les tags prédéfinis (system) pour l'utilisateur s'ils n'existent pas encore
    """
    supabase = get_supabase_client()
    
    # Vérifier si l'utilisateur a déjà des tags prédéfinis
    existing = supabase.table("tags") \
        .select("id") \
        .eq("user_id", user_id) \
        .eq("is_predefined", True) \
        .execute()
    
    if len(existing.data) > 0:
        return  # L'utilisateur a déjà ses tags
    
    # Récupérer les tags système
    system_tags = supabase.table("tags") \
        .select("*") \
        .eq("user_id", "system") \
        .execute()
    
    # Copier pour l'utilisateur
    user_tags = [
        {
            "user_id": user_id,
            "name": tag["name"],
            "color": tag["color"],
            "is_predefined": True
        }
        for tag in system_tags.data
    ]
    
    if user_tags:
        supabase.table("tags").insert(user_tags).execute()


def get_all_tags(user_id: str):
    """Récupère tous les tags de l'utilisateur"""
    get_or_create_predefined_tags(user_id)
    
    supabase = get_supabase_client()
    tags = supabase.table("tags") \
        .select("*") \
        .eq("user_id", user_id) \
        .order("name") \
        .execute()
    
    return tags.data


def create_tag(user_id: str, name: str, color: str = "#667eea"):
    """Crée un nouveau tag personnalisé"""
    supabase = get_supabase_client()
    
    result = supabase.table("tags").insert({
        "user_id": user_id,
        "name": name,
        "color": color,
        "is_predefined": False
    }).execute()
    
    return result.data[0] if result.data else None


def update_tag(user_id: str, tag_id: int, name: str, color: str):
    """Met à jour un tag"""
    supabase = get_supabase_client()
    
    supabase.table("tags") \
        .update({"name": name, "color": color}) \
        .eq("id", tag_id) \
        .eq("user_id", user_id) \
        .execute()


def delete_tag(user_id: str, tag_id: int):
    """Supprime un tag"""
    supabase = get_supabase_client()
    
    # Supprimer les liaisons
    supabase.table("flashcard_tags") \
        .delete() \
        .eq("tag_id", tag_id) \
        .execute()
    
    # Supprimer le tag
    supabase.table("tags") \
        .delete() \
        .eq("id", tag_id) \
        .eq("user_id", user_id) \
        .execute()


def get_tags_for_flashcard(flashcard_id: int):
    """Récupère les tags d'une flashcard"""
    supabase = get_supabase_client()
    
    result = supabase.table("flashcard_tags") \
        .select("tag_id, tags(*)") \
        .eq("flashcard_id", flashcard_id) \
        .execute()
    
    return [item["tags"] for item in result.data]


def add_tag_to_flashcard(flashcard_id: int, tag_id: int):
    """Ajoute un tag à une flashcard"""
    supabase = get_supabase_client()
    
    try:
        supabase.table("flashcard_tags").insert({
            "flashcard_id": flashcard_id,
            "tag_id": tag_id
        }).execute()
    except:
        pass  # Le tag existe déjà


def remove_tag_from_flashcard(flashcard_id: int, tag_id: int):
    """Retire un tag d'une flashcard"""
    supabase = get_supabase_client()
    
    supabase.table("flashcard_tags") \
        .delete() \
        .eq("flashcard_id", flashcard_id) \
        .eq("tag_id", tag_id) \
        .execute()


def set_flashcard_tags(flashcard_id: int, tag_ids: list):
    """Définit les tags d'une flashcard (remplace tous les tags existants)"""
    supabase = get_supabase_client()
    
    # Supprimer tous les tags actuels
    supabase.table("flashcard_tags") \
        .delete() \
        .eq("flashcard_id", flashcard_id) \
        .execute()
    
    # Ajouter les nouveaux tags
    if tag_ids:
        flashcard_tags = [
            {"flashcard_id": flashcard_id, "tag_id": tag_id}
            for tag_id in tag_ids
        ]
        supabase.table("flashcard_tags").insert(flashcard_tags).execute()


def get_flashcards_by_tags(user_id: str, tag_ids: list):
    """Récupère les flashcards ayant au moins un des tags spécifiés"""
    supabase = get_supabase_client()
    
    # Récupérer les IDs des flashcards ayant ces tags
    result = supabase.table("flashcard_tags") \
        .select("flashcard_id") \
        .in_("tag_id", tag_ids) \
        .execute()
    
    flashcard_ids = list(set([item["flashcard_id"] for item in result.data]))
    
    if not flashcard_ids:
        return []
    
    # Récupérer les flashcards complètes
    from services.flashcards_service import get_flashcards
    all_cards = get_flashcards(user_id)
    
    return [card for card in all_cards if card["id"] in flashcard_ids]


def get_tag_statistics(user_id: str):
    """Récupère les statistiques d'utilisation des tags"""
    supabase = get_supabase_client()
    
    # Compter le nombre de flashcards par tag
    tags = get_all_tags(user_id)
    
    for tag in tags:
        count = supabase.table("flashcard_tags") \
            .select("id", count="exact") \
            .eq("tag_id", tag["id"]) \
            .execute()
        
        tag["card_count"] = count.count or 0
    
    return tags