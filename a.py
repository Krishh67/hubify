import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load .env
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

print("Checking environment variables...")

if not SUPABASE_URL:
    print("❌ SUPABASE_URL is missing")
    exit()

if not SUPABASE_KEY:
    print("❌ SUPABASE_KEY is missing")
    exit()

print("✅ SUPABASE_URL found")
print("✅ SUPABASE_KEY found")

try:
    # Connect to Supabase
    supabase: Client = create_client(
        SUPABASE_URL,
        SUPABASE_KEY
    )

    print("\n✅ Supabase client created successfully!")

    # --------------------------------------------------
    # TEST CLIENTS TABLE
    # --------------------------------------------------

    print("\n--- Testing CLIENTS table ---")

    client_response = (
        supabase
        .table("clients")
        .select("id, client_name, email, product_requirement")
        .limit(5)
        .execute()
    )

    print("✅ clients table is accessible")
    print(f"Rows returned: {len(client_response.data)}")

    for client in client_response.data:
        print(client)

    # --------------------------------------------------
    # TEST SUPPLIERS TABLE
    # --------------------------------------------------

    print("\n--- Testing SUPPLIERS table ---")

    supplier_response = (
        supabase
        .table("suppliers")
        .select("id, supplier_name, email, product_offered")
        .limit(5)
        .execute()
    )

    print("✅ suppliers table is accessible")
    print(f"Rows returned: {len(supplier_response.data)}")

    for supplier in supplier_response.data:
        print(supplier)

    print("\n===================================")
    print("✅ SUPABASE CONNECTION TEST PASSED")
    print("===================================")

except Exception as e:
    print("\n❌ SUPABASE TEST FAILED")
    print("Error:")
    print(e)