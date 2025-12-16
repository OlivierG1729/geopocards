import streamlit as st


def sidebar():
    st.sidebar.title("Navigation")
    choice = st.sidebar.radio(
        "Menu",
        ["📚 Réviser", "➕ Créer une flashcard", "📝 Gérer mes flashcards"]
    )
    return choice