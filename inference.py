import os
import requests
import json

SPACE_URL = os.getenv(
    "SPACE_URL",
    "https://angiesaray-pqrs-cul-api.hf.space"
)

def generar_respuesta(pregunta):
    try:
        # iniciar evento
        r = requests.post(
            f"{SPACE_URL}/gradio_api/call//predict",
            json={"data": [pregunta]},
            timeout=60
        )

        if r.status_code != 200:
            return "Error iniciando consulta al modelo."

        event_id = r.json()["event_id"]

        # obtener resultado
        r2 = requests.get(
            f"{SPACE_URL}/gradio_api/call//predict/{event_id}",
            timeout=60
        )

        for line in r2.text.split("\n"):
            if line.startswith("data:"):
                data = json.loads(line[5:])
                return data[0]

        return "No se recibió respuesta del modelo."

    except Exception as e:
        print(f"Error Space: {e}")
        return "El modelo no está disponible en este momento."