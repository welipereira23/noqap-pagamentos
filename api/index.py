from flask import Flask, request, jsonify
import logging
import sys
import os
from dotenv import load_dotenv
import stripe
from supabase import create_client, Client

# Configuração de logs
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.info('Iniciando aplicação...')

# Carrega variáveis de ambiente
load_dotenv()
logger.info('Variáveis de ambiente carregadas')

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# Configuração do Stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

# Configuração do Supabase
try:
    supabase: Client = create_client(
        os.getenv('SUPABASE_URL', ''),
        os.getenv('SUPABASE_KEY', '')
    )
    logger.info('Cliente Supabase criado com sucesso')
except Exception as e:
    logger.error(f'Erro ao criar cliente Supabase: {str(e)}')
    supabase = None

@app.route('/', methods=['GET'])
def home():
    logger.info('Acessando rota /')
    return jsonify({
        'status': 'ok',
        'message': 'API funcionando!',
        'env': {
            'supabase_url': bool(os.getenv('SUPABASE_URL')),
            'supabase_key': bool(os.getenv('SUPABASE_KEY')),
            'stripe_key': bool(os.getenv('STRIPE_SECRET_KEY')),
            'secret_key': bool(os.getenv('SECRET_KEY'))
        }
    })

@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    logger.info('Criando sessão de checkout')
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
        logger.info('Sessão de checkout criada com sucesso')
        return jsonify({'id': session.id})
    except Exception as e:
        logger.error(f'Erro ao criar sessão: {str(e)}')
        return jsonify({'error': str(e)}), 400

def handler(request):
    """Handle a request to the Flask app."""
    logger.info(f'Recebendo requisição: {request.method} {request.path}')
    
    with app.request_context(request):
        try:
            response = app.full_dispatch_request()
            logger.info('Requisição processada com sucesso')
            return response
        except Exception as e:
            logger.error(f'Erro ao processar requisição: {str(e)}')
            return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run()
