import os
import json
from flask import Flask, render_template, request, redirect, url_for, session
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)
app.secret_key = 'sahilxglory_super_secret_key'

# --- FIREBASE SETUP ---
firebase_json = os.environ.get('FIREBASE_JSON')
db = None

if firebase_json:
    try:
        cert_dict = json.loads(firebase_json)
        if not firebase_admin._apps:
            cred = credentials.Certificate(cert_dict)
            firebase_admin.initialize_app(cred)
        db = firestore.client()
        print("Firebase connected successfully!")
    except Exception as e:
        print("Firebase Error:", e)

# --- 1. LOGIN & REGISTER ROUTE ---
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # ADMIN LOGIN
        if email == 'sahiladmin@gmail.com' and password == 'sahil@12':
            session['user'] = 'admin'
            session['email'] = email
            return redirect(url_for('admin'))
            
        # NORMAL USER LOGIN/REGISTER
        if db:
            user_ref = db.collection('users').document(email)
            user_doc = user_ref.get()
            if not user_doc.exists:
                # Naya user aaya toh database me 0 balance ke sath save karo
                user_ref.set({
                    'email': email, 
                    'password': password, 
                    'wallet_balance': 0
                })
        
        session['user'] = 'user'
        session['email'] = email
        return redirect(url_for('dashboard'))
        
    return render_template('index.html')

# --- 2. USER DASHBOARD ROUTE ---
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user' not in session or session.get('user') == 'admin':
        return redirect(url_for('index'))
        
    email = session.get('email')
    wallet_balance = 0
    my_orders = []
    
    if db:
        if request.method == 'POST':
            # DEPOSIT REQUEST AAYI (Add Funds)
            if request.form.get('utr'):
                amount = request.form.get('amount')
                utr = request.form.get('utr')
                db.collection('deposits').add({
                    'email': email,
                    'amount': int(amount), 
                    'utr': utr,
                    'status': 'Pending'
                })
                return redirect(url_for('dashboard'))
                
            # NEW ORDER REQUEST AAYI (Buy Glory)
            elif request.form.get('guild_uid'):
                pkg_name = request.form.get('package_name')
                pkg_price = int(request.form.get('package_price'))
                
                # Check balance and deduct
                user_ref = db.collection('users').document(email)
                user_doc = user_ref.get()
                if user_doc.exists:
                    current_bal = user_doc.to_dict().get('wallet_balance', 0)
                    if current_bal >= pkg_price:
                        # Balance kaat lo
                        user_ref.update({'wallet_balance': current_bal - pkg_price})
                        # Order history me daal do
                        db.collection('orders').add({
                            'email': email,
                            'package': pkg_name, 
                            'price': pkg_price,
                            'guild_uid': request.form.get('guild_uid'), 
                            'guild_name': request.form.get('guild_name'),
                            'contact_tg': request.form.get('tg_username'),
                            'contact_phone': request.form.get('phone_number'),
                            'status': 'Processing'
                        })
                return redirect(url_for('dashboard'))

        # ASLI DATA FETCH KARO DIKHANE KE LIYE
        try:
            user_doc = db.collection('users').document(email).get()
            if user_doc.exists:
                wallet_balance = user_doc.to_dict().get('wallet_balance', 0)
            
            # User ke orders nikalo
            orders_query = db.collection('orders').where('email', '==', email).get()
            for order in orders_query:
                order_dict = order.to_dict()
                order_dict['id'] = order.id
                my_orders.append(order_dict)
        except Exception as e:
            print("Error fetching data:", e)

    return render_template('dashboard.html', balance=wallet_balance, orders=my_orders)

# --- 3. ADMIN PANEL ROUTE ---
@app.route('/admin')
def admin():
    if session.get('user') != 'admin':
        return redirect(url_for('index')) 
    return render_template('admin.html')

# --- 4. LOGOUT ROUTE ---
@app.route('/logout')
def logout():
    session.clear() 
    return redirect(url_for('index'))

# Vercel handler
app = app
