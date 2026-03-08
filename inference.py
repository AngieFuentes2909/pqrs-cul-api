import os
import requests

SPACE_URL = os.getenv('SPACE_URL', 'https://angiesaray-pqrs-cul-api.hf.space')

def generar_respuesta(pregunta):
    try:
        r = requests.post(
            f'{SPACE_URL}/call/predict',
            json={"data": [pregunta]},
            timeout=60
        )
        if r.status_code == 200:
            event_id = r.json().get('event_id')
            r2 = requests.get(
                f'{SPACE_URL}/call/predict/{event_id}',
                timeout=60
            )
            for line in r2.text.split('\n'):
                if line.startswith('data:'):
                    import json
                    data = json.loads(line[5:])
                    return data[0]
        raise Exception(f'Error {r.status_code}')
    except Exception as e:
        print(f'Space no disponible: {e}')
        return 'El modelo no está disponible en este momento.'