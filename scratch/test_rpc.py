import os
import json
from dotenv import load_dotenv
from app.services.matching import match_client

load_dotenv()
res = match_client(7)
print("Finished match pipeline for client 7:", res)
