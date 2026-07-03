# ---------------------------------------------------------------
# backend/db/connection.py
# WHY THIS FILE EXISTS:
#   Creates ONE connection to MongoDB Atlas that the whole backend
#   shares. Opening a new connection for every request is slow and
#   wasteful, so we open it once here and everyone imports it.
#
# WHAT IT DOES:
#   - Loads MONGO_URI and DB_NAME from backend/.env
#   - Connects to the Atlas cluster
#   - Exposes two collections: candidates and jobs
#
# HOW IT CONNECTS TO THE REST OF THE PROJECT:
#   - db/candidates.py and db/jobs.py will import `candidates` and
#     `jobs` from this file to read and write data.
#   - The WhatsApp bot (via candidates.py) stores job seekers here.
#   - The employer portal (via jobs.py) stores jobs here.
# ---------------------------------------------------------------

import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load the secrets from backend/.env into the environment.
# load_dotenv() looks for a .env file and reads KEY=value pairs.
load_dotenv()

# Read the two values we need. If they are missing, we fail loudly
# now with a clear message instead of a confusing error later.
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

if not MONGO_URI:
    raise ValueError("MONGO_URI is missing. Check backend/.env")
if not DB_NAME:
    raise ValueError("DB_NAME is missing. Check backend/.env")

# Create the single shared client.
# serverSelectionTimeoutMS=5000 means: if Atlas can't be reached in
# 5 seconds, give up and show an error instead of hanging forever.
client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)

# Select our database (created automatically on first insert).
db = client[DB_NAME]

# The two collections the whole project uses.
# Other files import these two names directly.
candidates = db["candidates"]
jobs = db["jobs"]


# A tiny helper so we can test the connection on demand.
# This runs ONLY when you execute this file directly
# (python backend/db/connection.py), not when other files import it.
if __name__ == "__main__":
    try:
        # The ping command is the standard way to check the server
        # is actually reachable. It forces a real network round-trip.
        client.admin.command("ping")
        print("SUCCESS: Connected to MongoDB Atlas.")
        print("Database:", DB_NAME)
        print("Collections ready: candidates, jobs")
    except Exception as e:
        print("FAILED to connect to MongoDB Atlas.")
        print("Reason:", e)