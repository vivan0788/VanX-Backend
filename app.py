import os
import requests
from flask import Flask, request, jsonify
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime

app = Flask(__name__)

# 1. Configuration (Render Environment Variables se)
uri = os.environ.get('MONGO_URI')
BOT_TOKEN = "8517364051:AAFUprGh5hLgl0lvl1PUWiPxGXsu6D8gQY0" # Yahan apna Token dalein
CHAT_ID = "8450988216"     # Yahan apni Chat ID dalein

# 2. MongoDB Setup
client = MongoClient(uri, server_api=ServerApi('1'))
db = client['vanx_database']
locations_col = db['locations']

# Connection Check for Logs
try:
    client.admin.command('ping')
    print("MongoDB connected successfully!")
except Exception as e:
    print(f"MongoDB Error: {e}")

@app.route('/')
def index():
    return "VanX Backend is Live and Connected!"

# 3. Main Route: Jahan se Telegram aur MongoDB dono handle honge
@app.route('/update')
def update_location():
    lat = request.args.get('lat')
    lon = request.args.get('lon')

    if lat and lon:
        # A. MongoDB mein save karne ke liye data
        data_to_save = {
            "latitude": lat,
            "longitude": lon,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        try:
            # MongoDB mein insert karna
            locations_col.insert_one(data_to_save)
            
            # B. Telegram par message bhejna
            maps_link = f"https://www.google.com/maps?q={lat},{lon}"
            message = f"📍 *New Location Received!*\n\nLat: `{lat}`\nLon: `{lon}`\n\n[Open in Google Maps]({maps_link})"
            
            tele_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            requests.post(tele_url, data={"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"})
            
            return jsonify({"status": "success", "message": "Data saved and sent to Telegram"}), 200
        
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    return jsonify({"status": "failed", "message": "Missing coordinates"}), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
