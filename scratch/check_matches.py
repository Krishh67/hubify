import os
import requests
from dotenv import load_dotenv

load_dotenv()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

res = requests.get(f"{url}/rest/v1/?apikey={key}")
schema = res.json()

print("Available definitions:", list(schema.get("definitions", {}).keys()))

