import os
import json
from flask import Flask, render_template, request, redirect, url_for, session
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)
app.secret_key = 'sahilxglory_super_secret_key'

# 🚀 FIREBASE CONNECTION LOGIC (Secure via Vercel Environment Variables)
firebase_json = os.environ.get('FIREBASE_JSON')
db = None
if firebase_json:
    try:
        cert_dict = json.loads(firebase_json)
        cred = credentials.Certificate(cert_dict)
        firebase_admin.initialize_app(cred)
        db = firestore.client()
    except Exception as e:
        print("Firebase setup error:", e)

# 1. Login & Register Route
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # 🔐 ADMIN SECURE LOGIN
        if email == 'sahiladmin@gmail.com' and password == 'sahil@12':
            session['user'] = 'admin'
            session['email'] = email
            return redirect(url_for('admin'))
            
        # 👤 NORMAL USER LOGIN & REGISTER
        if db:
            user_ref = db.collection('users').document(email)
            if not user_ref.get().exists:
                # Naya user aaya toh database me save karo
                user_ref.set({'email': email, 'password': password, 'wallet_balance': 0})
        
        session['user'] = 'user'
        session['email'] = email
        return redirect(url_for('dashboard'))
            
    return render_template('index.html')

# 2. User Dashboard Route (Handle Orders & Deposits)
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user' not in session or session.get('user') == 'admin':
        return redirect(url_for('index'))
        
    email = session.get('email')
    
    if request.method == 'POST':
        if db:
            # Check if it's a Deposit Request (UTR form)
            if 'utr' in request.form:
                amount = request.form.get('amount')
                utr = request.form.get('utr')
                db.collection('deposits').add({
                    'email': email,
                    'amount': amount,
                    'utr': utr,
                    'status': 'Pending'
                })
            
            # Check if it's a Glory Order (Guild UID form)
            elif 'guild_uid' in request.form:
                pkg_name = request.form.get('package_name')
                pkg_price = request.form.get('package_price')
                guild_uid = request.form.get('guild_uid')
                guild_name = request.form.get('guild_name')
                tg_user = request.form.get('tg_username')
                phone = request.form.get('phone_number')
                
                db.collection('orders').add({
                    'email': email,
                    'package': pkg_name,
                    'price': pkg_price,
                    'guild_uid': guild_uid,
                    'guild_name': guild_name,
                    'contact_tg': tg_user,
                    'contact_phone': phone,
                    'status': 'Processing'
                })
        return redirect(url_for('dashboard'))

    return render_template('dashboard.html')

# 3. Master Admin Panel Route
@app.route('/admin')
def admin():
    if session.get('user') != 'admin':
        return redirect(url_for('index')) 
    return render_template('admin.html')

# 4. Logout Route
@app.route('/logout')
def logout():
    session.clear() 
    return redirect(url_for('index'))

# Vercel handler
app = app
