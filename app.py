import os
os.environ["MODEL_LOCAL"] = "false"

from flask import Flask, jsonify
from flask_cors import CORS
from controllers.chat_controller import chat_bp


def create_app():
    app = Flask(__name__)
    CORS(app, origins="*", supports_credentials=True)

    app.register_blueprint(chat_bp, url_prefix='/api/chat')

    @app.route('/')
    def index():
        return jsonify({
            "api": "Sistema PQRS - CUL",
            "version": "1.0.0",
            "estado": "API funcionando",
            "endpoint_chat": "POST /api/chat/mensaje"
        })

    return app


if __name__ == '__main__':
    app = create_app()
    port = int(os.getenv("PORT", 8080))

    print("="*50)
    print("API PQRS - CUL")
    print(f"Puerto: {port}")
    print("="*50)

    app.run(host="0.0.0.0", port=port)