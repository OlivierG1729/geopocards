import os
import streamlit as st
from dotenv import load_dotenv

# Charger .env en local
load_dotenv()

# Essayer d'abord st.secrets (Streamlit Cloud), sinon .env (local)
try:
    SUPABASE_URL = st.secrets["supabase"]["url"]
    SUPABASE_KEY = st.secrets["supabase"]["key"]
except (KeyError, FileNotFoundError, AttributeError):
    # Fallback sur .env
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Vérification
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError(
        "Supabase credentials not found. "
        "Configure them in .streamlit/secrets.toml (Cloud) or .env (local)"
    )