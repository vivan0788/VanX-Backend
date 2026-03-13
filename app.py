import os
from flask import Flask, render_template, request, jsonify
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

app = Flask(__name__)

# 1. Environment variable se URI uthana (Jo humne Render settings me save kiya)
uri = os.environ.get('MONGO_URI')

# 2. MongoDB Client Setup
# Agar Render me variable nahi mila toh error handle karne ke liye
if not uri:
    print("Error: MONGO_URI environment variable nahi mila!")
else:
    client = MongoClient(uri, server_api=ServerApi('1'))
    db = client['vanx_database']  # Apne database ka naam yahan likhein

# 3. Connection Check (Logs me dikhega)
try:
    if uri:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(f"MongoDB Connection Error: {e}")

@app.route('/')
def index():
    return "VanX Backend is Running!"

# Aapke baaki routes (jaise /update, /get_location) yahan niche aayenge...

if __name__ == '__main__':
    # Render ke liye port setup
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
