import os
os.environ["MODEL_LOCAL"] = "false"

from flask import Flask, jsonify
from flask_cors import CORS
from controllers.controllers import chat_bp, usuario_bp, conversacion_bp, pqrs_bp


def create_app():
    app = Flask(__name__)
    CORS(app, origins="*", supports_credentials=True)

    app.register_blueprint(usuario_bp,      url_prefix='/api/usuarios')
    app.register_blueprint(conversacion_bp, url_prefix='/api/conversaciones')
    app.register_blueprint(pqrs_bp,         url_prefix='/api/pqrs')
    app.register_blueprint(chat_bp,         url_prefix='/api/chat')

    @app.route('/')
    def index():
        return jsonify({
            "api": "Sistema PQRS - CUL",
            "version": "1.0.0",
            "estado": "API funcionando"
        })

    return app


if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)