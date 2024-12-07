from http.server import BaseHTTPRequestHandler
import json
import os
import stripe
from urllib.parse import parse_qs

# Configuração do Stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = {
            'message': 'API funcionando!',
            'stripe_configured': bool(stripe.api_key)
        }
        
        self.wfile.write(json.dumps(response).encode())
    
    def do_POST(self):
        if self.path == '/create-checkout-session':
            try:
                # Criar sessão do Stripe
                session = stripe.checkout.Session.create(
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
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {'error': 'Rota não encontrada'}
            self.wfile.write(json.dumps(response).encode())
