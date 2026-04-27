"""
MongoDB connection and collection helpers
"""
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017/atm_security"))
db = client["atm_security"]

# Collections
users_col = db["users"]
transactions_col = db["transactions"]
logs_col = db["audit_logs"]
vulnerabilities_col = db["vulnerabilities"]
scan_results_col = db["scan_results"]
