from flask import Flask, render_template, request, jsonify, redirect
from supabase import create_client
import stripe
import os
from datetime import datetime, timedelta
import jwt
from dotenv import load_dotenv
import logging
import sys

# Configuração de logs
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.info('Iniciando aplicação...')

try:
    # Carrega variáveis de ambiente
    load_dotenv()
    logger.info('Variáveis de ambiente carregadas')

    app = Flask(__name__)
    logger.info('Flask app criado')

    # Configuração do Flask
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    if not app.config['SECRET_KEY']:
        logger.error('SECRET_KEY não encontrada')
    else:
        logger.info('SECRET_KEY configurada')

    # Configuração do Stripe
    stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
    if not stripe.api_key:
        logger.error('STRIPE_SECRET_KEY não encontrada')
    else:
        logger.info('Stripe configurado')

    # Configuração do Supabase
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    if not supabase_url or not supabase_key:
        logger.error('Credenciais do Supabase não encontradas')
    else:
        logger.info('Credenciais do Supabase encontradas')
        supabase = create_client(supabase_url, supabase_key)
        logger.info('Cliente Supabase criado')

except Exception as e:
    logger.error(f'Erro na inicialização: {str(e)}')
    raise e

def generate_token(user_id):
    try:
        token = jwt.encode(
            {'user_id': user_id, 'exp': datetime.utcnow() + timedelta(days=1)},
            app.config['SECRET_KEY'],
            algorithm='HS256'
        )
        logger.info(f'Token gerado para usuário {user_id}')
        return token
    except Exception as e:
        logger.error(f'Erro ao gerar token: {str(e)}')
        raise e

@app.route('/')
def index():
    logger.info('Acessando rota /')
    try:
        return 'API funcionando!'
    except Exception as e:
        logger.error(f'Erro na rota /: {str(e)}')
        return jsonify({'error': str(e)}), 500

@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    logger.info('Iniciando criação de sessão de checkout')
    try:
        price_id = os.getenv('STRIPE_PRICE_ID')
        logger.info(f'STRIPE_PRICE_ID: {price_id}')

        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            mode='subscription',
            success_url=request.host_url + 'success',
            cancel_url=request.host_url + 'cancel',
        )
        logger.info('Sessão de checkout criada com sucesso')
        return jsonify({'id': session.id})
    except Exception as e:
        logger.error(f'Erro ao criar sessão de checkout: {str(e)}')
        return jsonify({'error': str(e)}), 400

@app.route('/success')
def success():
    logger.info('Acessando rota /success')
    try:
        return 'Sucesso!'
    except Exception as e:
        logger.error(f'Erro na rota /success: {str(e)}')
        return jsonify({'error': str(e)}), 500

@app.route('/cancel')
def cancel():
    logger.info('Acessando rota /cancel')
    try:
        return 'Cancelado!'
    except Exception as e:
        logger.error(f'Erro na rota /cancel: {str(e)}')
        return jsonify({'error': str(e)}), 500

# Log de todas as variáveis de ambiente (exceto valores sensíveis)
logger.info('Variáveis de ambiente configuradas:')
logger.info(f'SECRET_KEY presente: {bool(os.getenv("SECRET_KEY"))}')
logger.info(f'STRIPE_SECRET_KEY presente: {bool(os.getenv("STRIPE_SECRET_KEY"))}')
logger.info(f'SUPABASE_URL presente: {bool(os.getenv("SUPABASE_URL"))}')
logger.info(f'SUPABASE_KEY presente: {bool(os.getenv("SUPABASE_KEY"))}')
logger.info(f'STRIPE_PRICE_ID presente: {bool(os.getenv("STRIPE_PRICE_ID"))}')

if __name__ == '__main__':
    app.run()
