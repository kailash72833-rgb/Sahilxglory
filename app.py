from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
# Security key session ke liye
app.secret_key = 'sahilxglory_super_secret_key'

# 1. Login & Register Route
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password') 
        
        # 🔐 ADMIN SECURE LOGIN
        if email == 'sahiladmin@gmail.com' and password == 'sahil@12':
            session['user'] = 'admin'
            return redirect(url_for('admin'))
            
        # 👤 NORMAL USER LOGIN
        else:
            session['user'] = 'user'
            return redirect(url_for('dashboard'))
            
    return render_template('index.html')

# 2. User Dashboard Route
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user' not in session:
        return redirect(url_for('index'))
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
    session.pop('user', None) 
    return redirect(url_for('index'))

# Vercel ke liye application handler
app = app
