import os
import json
from flask import Flask, render_template, request, redirect, url_for, session
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)
app.secret_key = 'sahilxglory_super_secret_key'

# Firebase Setup
firebase_json = os.environ.get('FIREBASE_JSON')
db = None
if firebase_json:
    try:
        cert_dict = json.loads(firebase_json)
        if not firebase_admin._apps:
            cred = credentials.Certificate(cert_dict)
            firebase_admin.initialize_app(cred)
        db = firestore.client()
    except Exception as e:
        print("Firebase Error:", e)

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
            
        # NORMAL USER
        if db:
            user_ref = db.collection('users').document(email)
            if not user_ref.get().exists:
                user_ref.set({'email': email, 'password': password, 'wallet_balance': 0})
        
        session['user'] = 'user'
        session['email'] = email
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user' not in session or session.get('user') == 'admin':
        return redirect(url_for('index'))
        
    email = session.get('email')
    wallet_balance = 0
    my_orders = []
    
    if db:
        if request.method == 'POST':
            # Deposit form submit hua
            if request.form.get('utr'):
                db.collection('deposits').add({
                    'email': email, 'amount': request.form.get('amount'), 
                    'utr': request.form.get('utr'), 'status': 'Pending'
                })
            # Order form submit hua
            elif request.form.get('guild_uid'):
                db.collection('orders').add({
                    'email': email, 'package': request.form.get('package_name'), 
                    'price': request.form.get('package_price'),
                    'guild_uid': request.form.get('guild_uid'), 
                    'status': 'Processing'
                })
            return redirect(url_for('dashboard'))

        # Asli Data Fetch Karo
        try:
            user_doc = db.collection('users').document(email).get()
            if user_doc.exists:
                wallet_balance = user_doc.to_dict().get('wallet_balance', 0)
            
            orders_query = db.collection('orders').where('email', '==', email).get()
            for order in orders_query:
                my_orders.append(order.to_dict())
        except Exception as e:
            pass

    # Data HTML ko bhej do
    return render_template('dashboard.html', balance=wallet_balance, orders=my_orders)

@app.route('/admin')
def admin():
    if session.get('user') != 'admin':
        return redirect(url_for('index')) 
    return render_template('admin.html')

@app.route('/logout')
def logout():
    session.clear() 
    return redirect(url_for('index'))

app = app
