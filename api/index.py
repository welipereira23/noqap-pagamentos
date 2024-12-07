from flask import Flask
import sys
import os

# Adiciona o diretório pai ao PATH para poder importar o app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

# Configuração para Vercel
app.debug = False

def handler(request):
    """Handle a request to the Flask app."""
    return app.wsgi_app(request.environ, request.start_response)

if __name__ == "__main__":
    app.run()
