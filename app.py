from flask import Flask, request, jsonify
from pymongo import MongoClient
import datetime
import urllib.parse

app = Flask(__name__)

# Credentials handle karein
username = urllib.parse.quote_plus('avinash0788')
password = urllib.parse.quote_plus('@Avinash8')

# Sahi Connection String
MONGO_URI = f"mongodb+srv://{username}:{password}@vanx-tracker.qkdovs.mongodb.net/?retryWrites=true&w=majority&appName=VanX-Tracker"

# Database variables ko yahan set karein (Isse error theek hoga)
try:
    client = MongoClient(MONGO_URI)
    db = client['vanx_db']
    collection = db['location_logs'] # Ye line honi zaroori hai
    print("✅ MongoDB Connected")
except Exception as e:
    print(f"❌ Connection Error: {e}")

@app.route('/')
def home():
    return "VanX Bridge is Active!"

@app.route('/update', methods=['POST'])
def update():
    try:
        data = request.json
        data['server_time'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Data insert karein
        collection.insert_one(data) 
        
        return jsonify({"status": "success", "msg": "Data Received & Saved!"}), 200
    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)}), 500

if __name__ == "__main__":
    app.run()
