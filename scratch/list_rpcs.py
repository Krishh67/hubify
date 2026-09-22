import os
from dotenv import load_dotenv
import requests

load_dotenv()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

res = requests.get(f"{url}/rest/v1/?apikey={key}")
schema = res.json()
paths = schema.get("paths", {})
rpc_paths = [p for p in paths.keys() if p.startswith("/rpc/")]
print("Available RPCs:")
for rp in rpc_paths:
    print(rp)

