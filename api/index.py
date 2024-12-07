from http.server import BaseHTTPRequestHandler
import json
import os
import stripe
from supabase import create_client, Client
from urllib.parse import parse_qs, urlparse

# Configuração do Stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

# Configuração do Supabase
supabase: Client = create_client(
    os.getenv('SUPABASE_URL', ''),
    os.getenv('SUPABASE_KEY', '')
)

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/api/check-subscription':
            self.handle_check_subscription()
        else:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {
                'message': 'API funcionando!',
                'stripe_configured': bool(stripe.api_key),
                'supabase_configured': bool(os.getenv('SUPABASE_URL'))
            }
            
            self.wfile.write(json.dumps(response).encode())
    
    def do_POST(self):
        if self.path == '/api/create-checkout-session':
            self.handle_create_checkout_session()
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {'error': 'Rota não encontrada'}
            self.wfile.write(json.dumps(response).encode())
    
    def handle_check_subscription(self):
        try:
            # Pegar o token de autenticação
            auth_header = self.headers.get('Authorization', '')
            if not auth_header.startswith('Bearer '):
                raise ValueError('Token de autenticação não fornecido')
            
            token = auth_header[7:]  # Remove 'Bearer '
            
            # Verificar o usuário no Supabase
            user = supabase.auth.get_user(token)
            if not user:
                raise ValueError('Usuário não encontrado')
            
            # Verificar assinatura no Stripe
            subscriptions = stripe.Subscription.list(
                customer=user.stripe_customer_id,
                status='active'
            )
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {
                'subscribed': len(subscriptions.data) > 0
            }
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {'error': str(e)}
            self.wfile.write(json.dumps(response).encode())
    
    def handle_create_checkout_session(self):
        try:
            # Pegar o token de autenticação
            auth_header = self.headers.get('Authorization', '')
            if not auth_header.startswith('Bearer '):
                raise ValueError('Token de autenticação não fornecido')
            
            token = auth_header[7:]  # Remove 'Bearer '
            
            # Verificar o usuário no Supabase
            user = supabase.auth.get_user(token)
            if not user:
                raise ValueError('Usuário não encontrado')
            
            # Criar sessão do Stripe
            session = stripe.checkout.Session.create(
                customer=user.stripe_customer_id,
                payment_method_types=['card'],
                line_items=[{
                    'price': os.getenv('STRIPE_PRICE_ID'),
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=os.getenv('DOMAIN', 'http://localhost:3000') + '/success',
                cancel_url=os.getenv('DOMAIN', 'http://localhost:3000') + '/cancel',
            )
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {'id': session.id}
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {'error': str(e)}
            self.wfile.write(json.dumps(response).encode())
