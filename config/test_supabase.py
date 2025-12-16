
from services.supabase_client import get_supabase_client

supabase = get_supabase_client()

# Test très simple : lister les tables du schéma public
response = supabase.rpc("pg_tables").execute()

print("Connexion OK")
print(response)
