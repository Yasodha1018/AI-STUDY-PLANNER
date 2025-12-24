from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
import json
import hashlib
from datetime import datetime, timedelta
import random
import ml_model

app = Flask(__name__)
app.secret_key = 'ai_study_planner_secret_2024'  # Keep this as any random string
CORS(app)

# Supabase configuration - USE THE JWT KEY YOU REVEALED
SUPABASE_URL = "https://rvtwotjtbnqhfxzssusm.supabase.co"
# ↓↓↓ COPY THE "service_role" JWT KEY HERE (starts with eyJhb...) ↓↓↓
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ2dHdvdGp0Ym5xaGZ4enNzdXNtIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTcwMDAwMDAwMCwiZXhwIjoxODAwMDAwMDAwfQ.your_actual_jwt_token_here"

try:
    from supabase import create_client, Client
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ Connected to Supabase successfully!")
    
    # Test connection
    try:
        # Create tables if they don't exist
        print("Checking database setup...")
    except Exception as e:
        print(f"Note: {e}")
        
except Exception as e:
    print(f"⚠️ Supabase connection failed: {e}")
    print("⚠️ Using in-memory storage (fallback mode)")
    supabase = None

# In-memory storage (fallback)
users_db = {}
plans_db = {}