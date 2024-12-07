from flask import Flask, render_template, request, jsonify, redirect
from supabase import create_client
import stripe
import os
from datetime import datetime, timedelta
import jwt
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# Configuração do Stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

# Configuração do Supabase
supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

def generate_token(user_id):
    return jwt.encode(
        {'user_id': user_id, 'exp': datetime.utcnow() + timedelta(days=1)},
        app.config['SECRET_KEY'],
        algorithm='HS256'
    )

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': os.getenv('STRIPE_PRICE_ID'),
                'quantity': 1,
            }],
            mode='subscription',
            success_url=request.host_url + 'success',
            cancel_url=request.host_url + 'cancel',
        )
        return jsonify({'id': session.id})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/cancel')
def cancel():
    return render_template('cancel.html')

if __name__ == '__main__':
    app.run()
