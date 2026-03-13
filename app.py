from flask import Flask, request, jsonify
from pymongo import MongoClient
import datetime

app = Flask(__name__)

# Aapka MongoDB link jo humne pehle nikala tha
MONGO_URI = "mongodb+srv://avinash0788:Avinash8@vanx-tracker.qkdovs.mongodb.net/?appName=VanX-Tracker"
client = MongoClient(MONGO_URI)
db = client['vanx_db']
collection = db['location_logs']

@app.route('/')
def home():
    return "VanX Server is Running!"

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
