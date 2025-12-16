import streamlit as st
import html
from services.flashcards_service import get_flashcards
from services.stats_service import upsert_stats
from services.tags_service import get_tags_for_flashcard, get_all_tags, get_flashcards_by_tags
from utils.sampling import weighted_choice


def review_cards_screen(user_id: str):
    # =========================
    # STYLE CSS (flashcards)
    # =========================
    st.html(
        """
        <style>
        .flashcard {
            background-color: #ffffff;
            border-radius: 14px;
            padding: 26px;
            margin: 20px 0;
            box-shadow: 0 6px 16px rgba(0,0,0,0.08);
            font-size: 1.1em;
        }
        .flashcard-question {
            font-weight: 600;
            font-size: 1.6em;
            margin-bottom: 14px;
            padding-left: 0;
        }
        .flashcard-answer {
            border-top: 1px solid #eee;
            margin-top: 28px;
            padding-top: 24px;
            padding-left: 0;
            color: #333;
            white-space: pre-wrap;
            font-size: 1.6em;
            font-weight: 600;
        }
        .flashcard-meta {
            margin-top: 32px;
            padding-top: 16px;
            border-top: 1px solid #f0f0f0;
            font-size: 0.9em;
            color: #666;
        }
        .flashcard-tags {
            margin-top: 16px;
            padding-top: 12px;
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
        .tag-filter {
            background-color: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
        }
        .tag-filter-title {
            font-size: 1.2em;
            font-weight: 600;
            margin-bottom: 12px;
            color: #2c3e50;
        }
        </style>
        """
    )

    st.header("📚 Révision")

    # =========================
    # FILTRE PAR TAGS
    # =========================
    all_tags = get_all_tags(user_id)
    
    if all_tags:
        st.html('<div class="tag-filter"><div class="tag-filter-title">🏷️ Filtrer par tags</div></div>')
        
        # Initialisation de l'état pour "Tous les tags"
        if "select_all_tags" not in st.session_state:
            st.session_state.select_all_tags = True
            st.session_state.selected_tag_ids = []
        
        # Checkbox "Sélectionner tous les tags"
        select_all = st.checkbox(
            "✅ Sélectionner tous les tags",
            value=st.session_state.select_all_tags,
            key="all_tags_checkbox"
        )
        
        # Mise à jour de l'état
        if select_all != st.session_state.select_all_tags:
            st.session_state.select_all_tags = select_all
            if select_all:
                st.session_state.selected_tag_ids = []
            # Réinitialiser la carte courante quand on change de filtre
            if "current_card" in st.session_state:
                del st.session_state.current_card
            st.rerun()
        
        # Si "Tous les tags" n'est pas coché, afficher la sélection individuelle
        if not st.session_state.select_all_tags:
            st.write("**Sélectionnez les tags à réviser :**")
            
            # Créer des colonnes pour afficher les tags de façon compacte
            cols = st.columns(4)
            
            # Initialiser selected_tag_ids si nécessaire
            if "selected_tag_ids" not in st.session_state:
                st.session_state.selected_tag_ids = []
            
            temp_selected = []
            
            for idx, tag in enumerate(all_tags):
                col = cols[idx % 4]
                with col:
                    is_selected = tag["id"] in st.session_state.selected_tag_ids
                    if st.checkbox(
                        tag["name"],
                        value=is_selected,
                        key=f"tag_{tag['id']}"
                    ):
                        temp_selected.append(tag["id"])
            
            # Détecter les changements
            if set(temp_selected) != set(st.session_state.selected_tag_ids):
                st.session_state.selected_tag_ids = temp_selected
                # Réinitialiser la carte courante
                if "current_card" in st.session_state:
                    del st.session_state.current_card
                st.rerun()
            
            # Afficher les tags sélectionnés
            if st.session_state.selected_tag_ids:
                selected_tags = [t for t in all_tags if t["id"] in st.session_state.selected_tag_ids]
                tags_html = '<div style="margin-top: 10px;">📌 Tags actifs : '
                for tag in selected_tags:
                    tags_html += f'<span class="tag-badge" style="background-color: {tag["color"]}">{html.escape(tag["name"])}</span>'
                tags_html += '</div>'
                st.html(tags_html)
            else:
                st.warning("⚠️ Veuillez sélectionner au moins un tag pour commencer la révision")
                return

    # =========================
    # RÉCUPÉRATION DES CARTES
    # =========================
    if st.session_state.select_all_tags or not all_tags:
        # Toutes les cartes
        cards = get_flashcards(user_id)
    else:
        # Cartes filtrées par tags
        if not st.session_state.selected_tag_ids:
            st.info("Sélectionnez au moins un tag pour commencer")
            return
        cards = get_flashcards_by_tags(user_id, st.session_state.selected_tag_ids)

    if not cards:
        st.info("Aucune flashcard disponible avec les tags sélectionnés")
        return

    st.write(f"**{len(cards)} flashcard(s) disponible(s)**")

    # -----------------------
    # INITIALISATION DE L'ÉTAT (UNE SEULE FOIS)
    # -----------------------
    if "current_card" not in st.session_state:
        st.session_state.current_card = weighted_choice(cards)
        st.session_state.show_answer = False

    card = st.session_state.current_card
    
    # Vérifier que la carte actuelle est toujours dans la liste filtrée
    if card['id'] not in [c['id'] for c in cards]:
        st.session_state.current_card = weighted_choice(cards)
        st.session_state.show_answer = False
        card = st.session_state.current_card
    
    # Récupérer les tags de la carte actuelle
    tags = get_tags_for_flashcard(card['id'])
    tags_html = ""
    if tags:
        tags_html = '<div class="flashcard-tags">🏷️ '
        for tag in tags:
            tags_html += f'<span class="tag-badge" style="background-color: {tag["color"]}">{html.escape(tag["name"])}</span>'
        tags_html += '</div>'

    # -----------------------
    # ÉTAT 1 — QUESTION SEULE
    # -----------------------
    if not st.session_state.show_answer:
        safe_question = html.escape(str(card['question']))
        
        st.html(
            f"""
            <div class="flashcard">
                <div class="flashcard-question">
                    ❓ {safe_question}
                </div>
                {tags_html}
            </div>
            """
        )

        if st.button("👀 Voir la réponse"):
            st.session_state.show_answer = True
            st.rerun()

        return  # ⬅️ verrouille l'état (fondamental)

    # -----------------------
    # ÉTAT 2 — QUESTION + RÉPONSE
    # -----------------------
    safe_question = html.escape(str(card['question']))
    safe_answer = html.escape(str(card['answer']))

    st.html(
        f"""
        <div class="flashcard">
            <div class="flashcard-question">
                ❓ {safe_question}
            </div>

            <div class="flashcard-answer">
                💡 {safe_answer}
            </div>

            <div class="flashcard-meta">
                📊 Maîtrise : {int(card['mastery'] * 100)} %
                (✔️ {card['times_correct']} / 👁️ {card['times_seen']})
            </div>
            
            {tags_html}
        </div>
        """
    )

    col1, col2 = st.columns(2)

    def next_card(correct: bool):
        upsert_stats(user_id, card['id'], correct)

        remaining_cards = [c for c in cards if c['id'] != card['id']]
        st.session_state.current_card = (
            weighted_choice(remaining_cards)
            if remaining_cards
            else card
        )

        st.session_state.show_answer = False
        st.rerun()

    if col1.button("✅ J'ai bien répondu"):
        next_card(correct=True)

    if col2.button("❌ Je n'ai pas bien répondu"):
        next_card(correct=False)