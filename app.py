import streamlit as st
from ui.sidebar import sidebar
from ui.create_card import create_card_screen
from ui.review_cards import review_cards_screen
from ui.manage_cards import manage_cards_screen

# TEMPORAIRE : utilisateur fictif
USER_ID = "demo-user"

st.set_page_config(page_title="GeopoFlashCards", page_icon="🌍")

# =========================
# TITRE PRINCIPAL + SOUS-TITRE
# =========================
st.html(
    """
    <style>
    .main-title {
        font-size: 2.5em;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin: 10px 0 5px 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .subtitle {
        font-size: 1.1em;
        color: #666;
        text-align: center;
        margin: 0 0 30px 0;
        font-style: italic;
    }
    </style>
    """
)

st.html('<h1 class="main-title">🌍 GeopoFlashCards</h1>')
st.html('<p class="subtitle">Application de flashcards dédiées à la géopolitique</p>')

# =========================
# NAVIGATION
# =========================
choice = sidebar()

if choice == "➕ Créer une flashcard":
    create_card_screen(USER_ID)
elif choice == "📝 Gérer mes flashcards":
    manage_cards_screen(USER_ID)
else:  # Par défaut : "📚 Réviser"
    review_cards_screen(USER_ID)