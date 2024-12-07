from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime, timedelta
import os
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import stripe
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'sua-chave-secreta')

# Configuração do Supabase
supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

# Configuração do Stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

# Configuração do Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

NOQAP_URL = 'https://noqap.vercel.app'

class User(UserMixin):
    def __init__(self, user_data):
        self.id = user_data['id']
        self.email = user_data['email']
        self.name = user_data['name']

@login_manager.user_loader
def load_user(user_id):
    try:
        response = supabase.table('users').select("*").eq('id', user_id).execute()
        if response.data:
            return User(response.data[0])
    except Exception as e:
        print(f"Erro ao carregar usuário: {e}")
    return None

def generate_access_token(user_id):
    try:
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(days=1)
        }
        return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
    except Exception as e:
        print(f"Erro ao gerar token: {e}")
        return None

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        try:
            # Verificar se usuário já existe
            response = supabase.table('users').select("*").eq('email', email).execute()
            if response.data:
                flash('Email já cadastrado')
                return redirect(url_for('register'))
            
            # Criar usuário
            user_data = {
                'email': email,
                'name': None,
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            response = supabase.table('users').insert(user_data).execute()
            user = response.data[0]
            
            # Criar assinatura trial
            subscription_data = {
                'user_id': user['id'],
                'status': 'trialing',
                'price_id': 'price_basic',
                'trial_start': datetime.utcnow().isoformat(),
                'trial_end': (datetime.utcnow() + timedelta(days=14)).isoformat(),
                'current_period_start': datetime.utcnow().isoformat(),
                'current_period_end': (datetime.utcnow() + timedelta(days=30)).isoformat(),
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            supabase.table('subscriptions').insert(subscription_data).execute()
            
            # Login do usuário
            login_user(User(user))
            return redirect(url_for('dashboard'))
            
        except Exception as e:
            print(f"Erro no registro: {e}")
            flash('Erro ao criar conta')
            return redirect(url_for('register'))
            
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        
        try:
            response = supabase.table('users').select("*").eq('email', email).execute()
            if response.data:
                user = response.data[0]
                login_user(User(user))
                return redirect(url_for('dashboard'))
            else:
                flash('Email não encontrado')
                
        except Exception as e:
            print(f"Erro no login: {e}")
            flash('Erro ao fazer login')
            
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    try:
        # Buscar assinatura do usuário
        response = supabase.table('subscriptions').select("*").eq('user_id', current_user.id).execute()
        if response.data:
            subscription = response.data[0]
            return render_template('dashboard.html', subscription=subscription)
    except Exception as e:
        print(f"Erro no dashboard: {e}")
        
    return render_template('dashboard.html', subscription=None)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/verify-token', methods=['POST'])
def verify_token():
    token = request.json.get('token')
    if not token:
        return jsonify({'valid': False}), 400
        
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = payload.get('user_id')
        
        # Verificar se usuário existe e tem assinatura ativa
        response = supabase.table('subscriptions')\
            .select("*")\
            .eq('user_id', user_id)\
            .execute()
            
        if response.data:
            subscription = response.data[0]
            is_active = subscription['status'] in ['trialing', 'active']
            return jsonify({
                'valid': is_active,
                'subscription': subscription
            })
            
        return jsonify({'valid': False}), 404
        
    except Exception as e:
        print(f"Erro na verificação do token: {e}")
        return jsonify({'valid': False}), 401

@app.route('/create-checkout-session', methods=['POST'])
@login_required
def create_checkout_session():
    price_id = request.form.get('price_id')
    if not price_id:
        return jsonify({'error': 'Price ID is required'}), 400
        
    try:
        checkout_session = stripe.checkout.Session.create(
            customer_email=current_user.email,
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            mode='subscription',
            success_url=url_for('success', _external=True),
            cancel_url=url_for('cancel', _external=True),
        )
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        print(f"Erro ao criar sessão de checkout: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/success')
@login_required
def success():
    try:
        # Atualizar status da assinatura
        subscription_data = {
            'status': 'active',
            'updated_at': datetime.utcnow().isoformat()
        }
        supabase.table('subscriptions')\
            .update(subscription_data)\
            .eq('user_id', current_user.id)\
            .execute()
            
        # Gerar token e redirecionar para o site principal
        token = generate_access_token(current_user.id)
        return redirect(f"{NOQAP_URL}?token={token}")
        
    except Exception as e:
        print(f"Erro na página de sucesso: {e}")
        return redirect(url_for('dashboard'))

@app.route('/cancel')
def cancel():
    return render_template('cancel.html')

if __name__ == '__main__':
    app.run(debug=True)
