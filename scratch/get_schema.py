import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()
url = os.environ.get("SUPABASE_URL").replace("https://", "postgres://postgres:").replace(".supabase.co", ".supabase.co:5432/postgres")
# Note: I can't easily get the postgres DB password since SUPABASE_URL is usually https:// API url.
# But I can query pg_proc via postgrest if we have a table or via an existing RPC, but we don't.
# Wait, let's just dump the API schema from Supabase!

import requests
resp = requests.get(f"{os.environ.get('SUPABASE_URL')}/rest/v1/?apikey={os.environ.get('SUPABASE_KEY')}")
import json
print(json.dumps(resp.json(), indent=2))

