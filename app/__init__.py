# /tu_proyecto/app/__init__.py
from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": "*"}})

    with app.app_context():
        from .hermanos import hermanos_bp
        from .reuniones import reuniones_bp

        app.register_blueprint(hermanos_bp)
        app.register_blueprint(reuniones_bp)

    return app
