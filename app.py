from flask import Flask, request, jsonify
from pymongo import MongoClient
import datetime
import urllib.parse

app = Flask(__name__)

# Aapke credentials
username = urllib.parse.quote_plus('avinash0788')
password = urllib.parse.quote_plus('@Avinash8')

# Yeh link ab 100% safe hai
MONGO_URI = f"mongodb+srv://{username}:{password}@vanx-tracker.qkdovs.mongodb.net/?retryWrites=true&w=majority&appName=VanX-Tracker"

try:
    client = MongoClient(MONGO_URI)
    db = client['vanx_db']
    collection = db['location_logs']
    print("✅ Connected to MongoDB successfully!")
except Exception as e:
    print(f"❌ Connection Error: {e}")

@app.route('/')
def home():
    return "VanX Server is Running and Secure!"

@app.route('/update', methods=['POST'])
def update():
    try:
        data = request.json
        data['server_time'] = datetime.datetime.now()
        collection.insert_one(data)
        return jsonify({"status": "success", "msg": "Data Saved to Cloud"}), 200
    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)}), 500

if __name__ == "__main__":
    app.run()
