import os
import requests

SPACE_URL = os.getenv(
    "SPACE_URL",
    "https://angiesaray-pqrs-cul-api.hf.space/gradio_api/predict"
)

def generar_respuesta(pregunta):
    try:
        response = requests.post(
            SPACE_URL,
            json={"data": [pregunta]},
            timeout=60
        )

        if response.status_code == 200:
            data = response.json()
            return data["data"][0]

        return "Error al consultar el modelo."

    except Exception as e:
        print(f"Space no disponible: {e}")
        return "El modelo no está disponible en este momento."