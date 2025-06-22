from .api_routes import init_api

from flask import send_from_directory

def init_routes(app):
    @app.route('/')
    def index():
        return send_from_directory('templates', 'index.html')
    
    init_api(app)