            
            
import streamlit as st
from services.flashcards_service import create_flashcard
from services.tags_service import get_all_tags, create_tag, set_flashcard_tags


def create_card_screen(user_id: str):
    # =========================
    # STYLE CSS (formulaire)
    # =========================
    st.html(
        """
        <style>
        /* Augmenter la taille des labels */
        .stTextInput label, .stTextArea label {
            font-size: 1.3em;
            font-weight: 500;
        }
        
        /* Augmenter la taille du texte dans les champs */
        .stTextInput input, .stTextArea textarea {
            font-size: 1.2em !important;
        }
        
        /* Augmenter la taille du bouton */
        .stButton button {
            font-size: 1.2em;
            padding: 0.6em 1.5em;
        }
        
        /* Style pour les tags */
        .tag-badge {
            display: inline-block;
            padding: 6px 12px;
            margin: 4px;
            border-radius: 16px;
            font-size: 0.9em;
            font-weight: 500;
            color: white;
        }
        </style>
        """
    )
    
    st.header("➕ Créer une flashcard")

    question = st.text_input("Question")
    answer = st.text_area("Réponse", height=150)
    
    # =========================
    # SÉLECTION DES TAGS
    # =========================
    st.subheader("🏷️ Tags")
    
    all_tags = get_all_tags(user_id)
    
    # Multiselect pour les tags existants
    tag_options = {tag["name"]: tag["id"] for tag in all_tags}
    selected_tag_names = st.multiselect(
        "Sélectionnez des tags",
        options=list(tag_options.keys()),
        help="Vous pouvez sélectionner plusieurs tags"
    )
    
    selected_tag_ids = [tag_options[name] for name in selected_tag_names]
    
    # Option pour créer un nouveau tag
    with st.expander("➕ Créer un nouveau tag"):
        col1, col2 = st.columns([3, 1])
        new_tag_name = col1.text_input("Nom du tag")
        new_tag_color = col2.color_picker("Couleur", "#667eea")
        
        if st.button("Ajouter ce tag"):
            if new_tag_name.strip():
                new_tag = create_tag(user_id, new_tag_name.strip(), new_tag_color)
                if new_tag:
                    st.success(f"✅ Tag '{new_tag_name}' créé !")
                    st.rerun()
                else:
                    st.error("Ce tag existe déjà")
            else:
                st.warning("Le nom du tag ne peut pas être vide")
    
    # Aperçu des tags sélectionnés
    if selected_tag_names:
        st.write("**Tags sélectionnés :**")
        tags_html = ""
        for name in selected_tag_names:
            tag = next(t for t in all_tags if t["name"] == name)
            tags_html += f'<span class="tag-badge" style="background-color: {tag["color"]}">{name}</span>'
        st.html(tags_html)
    
    # =========================
    # ENREGISTREMENT
    # =========================
    if st.button("💾 Enregistrer la flashcard"):
        if question and answer:
            # Créer la flashcard
            supabase = st.session_state.get("supabase")
            from services.supabase_client import get_supabase_client
            supabase = get_supabase_client()
            
            result = supabase.table("flashcards").insert({
                "user_id": user_id,
                "question": question,
                "answer": answer
            }).execute()
            
            flashcard_id = result.data[0]["id"]
            
            # Ajouter les tags
            if selected_tag_ids:
                set_flashcard_tags(flashcard_id, selected_tag_ids)
            
            st.success("✅ Flashcard enregistrée avec succès !")
            
            # Réinitialiser le formulaire
            st.rerun()
        else:
            st.warning("⚠️ Question et réponse obligatoires")