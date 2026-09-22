import os
from dotenv import load_dotenv
import requests

load_dotenv()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

headers = {
    "apikey": key,
    "Authorization": f"Bearer {key}",
    "Range": "0-9"
}

# Get columns of public.clients
res = requests.get(f"{url}/rest/v1/clients?limit=1", headers=headers)
print("Clients keys:", res.json()[0].keys() if res.json() else "Empty")

# Get columns of public.suppliers
res = requests.get(f"{url}/rest/v1/suppliers?limit=1", headers=headers)
print("Suppliers keys:", res.json()[0].keys() if res.json() else "Empty")

