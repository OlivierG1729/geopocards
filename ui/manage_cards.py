import streamlit as st
import html
from services.flashcards_service import get_flashcards, update_flashcard, delete_flashcard
from services.tags_service import get_tags_for_flashcard, get_all_tags, set_flashcard_tags


def manage_cards_screen(user_id: str):
    # =========================
    # STYLE CSS
    # =========================
    st.html(
        """
        <style>
        .card-item {
            background-color: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin: 15px 0;
            border-left: 4px solid #667eea;
        }
        .card-label {
            font-weight: 600;
            font-size: 1.2em;
            color: #2c3e50;
            margin-bottom: 8px;
            margin-top: 15px;
        }
        .card-content {
            color: #555;
            font-size: 1.1em;
            background-color: white;
            padding: 12px;
            border-radius: 6px;
        }
        /* Augmenter la taille des champs d'édition */
        .stTextInput input, .stTextArea textarea {
            font-size: 1.1em !important;
        }
        .tag-badge {
            display: inline-block;
            padding: 6px 12px;
            margin: 4px 4px 4px 0;
            border-radius: 16px;
            font-size: 0.85em;
            font-weight: 500;
            color: white;
        }
        </style>
        """
    )
    
    st.header("📝 Gérer mes flashcards")

    cards = get_flashcards(user_id)

    if not cards:
        st.info("Aucune flashcard à gérer")
        return

    # Filtre de recherche
    search = st.text_input("🔍 Rechercher une flashcard", "")
    
    if search:
        cards = [c for c in cards if 
                 search.lower() in c['question'].lower() or 
                 search.lower() in c['answer'].lower()]

    st.write(f"**{len(cards)} flashcard(s) trouvée(s)**")

    # Liste des cartes
    for card in cards:
        # Récupérer les tags de cette carte
        tags = get_tags_for_flashcard(card['id'])
        tags_html = ""
        if tags:
            for tag in tags:
                tags_html += f'<span class="tag-badge" style="background-color: {tag["color"]}">{html.escape(tag["name"])}</span>'
        
        with st.expander(f"❓ {card['question'][:70]}..."):
            st.html(
                f"""
                <div class="card-item">
                    <div class="card-label">📌 Question</div>
                    <div class="card-content">{html.escape(card['question'])}</div>
                    
                    <div class="card-label">💡 Réponse</div>
                    <div class="card-content">{html.escape(card['answer'])}</div>
                    
                    <div class="card-label">🏷️ Tags</div>
                    <div class="card-content">
                        {tags_html if tags_html else "<em>Aucun tag</em>"}
                    </div>
                    
                    <div class="card-label" style="margin-top: 20px;">📊 Statistiques</div>
                    <div class="card-content">
                        Maîtrise : {int(card['mastery'] * 100)} % 
                        (✔️ {card['times_correct']} / 👁️ {card['times_seen']})
                    </div>
                </div>
                """
            )
            
            # Mode édition
            if st.checkbox("✏️ Modifier cette flashcard", key=f"edit_{card['id']}"):
                new_question = st.text_input(
                    "Nouvelle question", 
                    value=card['question'],
                    key=f"q_{card['id']}"
                )
                new_answer = st.text_area(
                    "Nouvelle réponse", 
                    value=card['answer'],
                    key=f"a_{card['id']}",
                    height=150
                )
                
                # Sélection des tags
                all_tags = get_all_tags(user_id)
                tag_options = {tag["name"]: tag["id"] for tag in all_tags}
                current_tag_names = [tag["name"] for tag in tags]
                
                selected_tag_names = st.multiselect(
                    "Tags",
                    options=list(tag_options.keys()),
                    default=current_tag_names,
                    key=f"tags_{card['id']}"
                )
                
                selected_tag_ids = [tag_options[name] for name in selected_tag_names]
                
                col1, col2 = st.columns(2)
                
                if col1.button("💾 Enregistrer les modifications", key=f"save_{card['id']}"):
                    if new_question.strip() and new_answer.strip():
                        update_flashcard(user_id, card['id'], new_question, new_answer)
                        set_flashcard_tags(card['id'], selected_tag_ids)
                        st.success("✅ Flashcard mise à jour !")
                        st.rerun()
                    else:
                        st.warning("⚠️ Question et réponse obligatoires")
                
                if col2.button("🗑️ Supprimer définitivement", key=f"del_{card['id']}", type="secondary"):
                    if st.session_state.get(f"confirm_del_{card['id']}", False):
                        delete_flashcard(user_id, card['id'])
                        st.success("✅ Flashcard supprimée !")
                        st.rerun()
                    else:
                        st.session_state[f"confirm_del_{card['id']}"] = True
                        st.warning("⚠️ Cliquez à nouveau pour confirmer la suppression")