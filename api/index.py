from flask import Flask
from app import app

# Vercel precisa desta variável
app.debug = False

# Vercel handler
def handler(request, context):
    return app(request)

if __name__ == "__main__":
    app.run()
