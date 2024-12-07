from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime, timedelta
import os
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import stripe

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'sua-chave-secreta')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///users.db')
if app.config['SQLALCHEMY_DATABASE_URI'].startswith('postgres://'):
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace('postgres://', 'postgresql://', 1)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

NOQAP_URL = 'https://noqap.vercel.app'

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    trial_start = db.Column(db.DateTime, nullable=True)
    subscription_status = db.Column(db.String(20), default='trial')  # trial, active, expired
    subscription_end = db.Column(db.DateTime, nullable=True)
    stripe_customer_id = db.Column(db.String(120), unique=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def generate_access_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=1)
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(email=email).first():
            flash('Email já registrado')
            return redirect(url_for('register'))
        
        hashed_password = generate_password_hash(password)
        new_user = User(
            email=email,
            password=hashed_password,
            trial_start=datetime.utcnow(),
            subscription_end=datetime.utcnow() + timedelta(days=7)
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        login_user(new_user)
        return redirect(url_for('dashboard'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        
        flash('Email ou senha inválidos')
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    now = datetime.utcnow()
    if current_user.subscription_end and current_user.subscription_end > now:
        access_token = generate_access_token(current_user.id)
        redirect_url = f"{NOQAP_URL}?token={access_token}"
        return redirect(redirect_url)
    return render_template('dashboard.html', user=current_user)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/verify-token', methods=['POST'])
def verify_token():
    token = request.json.get('token')
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = payload.get('user_id')
        user = User.query.get(user_id)
        
        if user and user.subscription_end > datetime.utcnow():
            return jsonify({'valid': True, 'email': user.email}), 200
        return jsonify({'valid': False, 'message': 'Assinatura expirada'}), 403
    except:
        return jsonify({'valid': False, 'message': 'Token inválido'}), 401

@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    try:
        data = request.get_json()
        price_id = data.get('priceId')
        plan = data.get('plan')

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            mode='subscription',
            success_url=url_for('success', _external=True),
            cancel_url=url_for('cancel', _external=True),
            metadata={
                'plan': plan
            }
        )
        
        return jsonify({'id': checkout_session.id})
    except Exception as e:
        return jsonify({'error': str(e)}), 403

@app.route('/success')
def success():
    session_id = request.args.get('session_id')
    if session_id:
        session = stripe.checkout.Session.retrieve(session_id)
        customer = stripe.Customer.retrieve(session.customer)
        
        # Save or update user in database
        user = User.query.filter_by(stripe_customer_id=customer.id).first()
        if not user:
            user = User(
                email=customer.email,
                stripe_customer_id=customer.id,
                subscription_status='active'
            )
            db.session.add(user)
        else:
            user.subscription_status = 'active'
        
        db.session.commit()
        
        flash('Subscription successful!', 'success')
    return render_template('success.html')

@app.route('/cancel')
def cancel():
    return render_template('cancel.html')

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
