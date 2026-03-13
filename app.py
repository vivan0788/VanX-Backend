from flask import Flask, request, jsonify
from pymongo import MongoClient
import datetime
import urllib.parse

app = Flask(__name__)

# Aapke Credentials (Safe mode mein)
user = urllib.parse.quote_plus('avinash0788')
pw = urllib.parse.quote_plus('@Avinash8')

# Yahan user aur pw variables ka istemal ho raha hai
MONGO_URI = f"mongodb+srv://{user}:{pw}@vanx-tracker.qkdovs.mongodb.net/?retryWrites=true&w=majority&appName=VanX-Tracker"

# Global variable banate hain taaki error na aaye
collection = None

try:
    client = MongoClient(MONGO_URI)
    db = client['vanx_db']
    collection = db['location_logs']
    print("✅ Connected to MongoDB")
except Exception as e:
    print(f"❌ Connection Error: {e}")

@app.route('/')
def home():
    return "VanX Bridge is Active!"

@app.route('/update', methods=['POST'])
def update():
    if collection is None:
        return jsonify({"status": "error", "msg": "Database not connected"}), 500
    
    try:
        data = request.json
        data['server_time'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        collection.insert_one(data)
        return jsonify({"status": "success", "msg": "Data Saved!"}), 200
    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)}), 500

if __name__ == "__main__":
    app.run()
