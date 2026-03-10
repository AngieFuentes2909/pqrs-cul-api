import os
import requests

API_URL = os.getenv(
    "SPACE_URL",
    "https://angiesaray-pqrs-cul-api.hf.space/gradio_api/predict"
)

def generar_respuesta(pregunta):
    try:
        response = requests.post(
            API_URL,
            json={"data": [pregunta]},
            timeout=60
        )

        if response.status_code == 200:
            data = response.json()
            return data["data"][0]

        return "Error consultando el modelo."

    except Exception as e:
        print(f"Modelo falló: {e}")
        return "El modelo no está disponible en este momento."