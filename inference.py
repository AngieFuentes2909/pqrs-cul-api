import os
import requests
import json

SPACE_URL = os.getenv(
    "SPACE_URL",
    "https://angiesaray-pqrs-cul-api.hf.space"
)

def generar_respuesta(pregunta):
    try:
        # 1️⃣ iniciar llamada
        r = requests.post(
            f"{SPACE_URL}/gradio_api/call//predict",
            json={"data": [pregunta]},
            timeout=60
        )

        event_id = r.json()["event_id"]

        # 2️⃣ obtener resultado
        r2 = requests.get(
            f"{SPACE_URL}/gradio_api/call//predict/{event_id}",
            timeout=60
        )

        for line in r2.text.split("\n"):
            if line.startswith("data:"):
                data = json.loads(line[5:])
                return data[0]

        return "No se pudo obtener respuesta."

    except Exception as e:
        print(f"Error Space: {e}")
        return "El modelo no está disponible en este momento."