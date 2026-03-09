from flask import Blueprint, request, jsonify
from models.usuario_model import UsuarioModel
from models.conversacion_model import ConversacionModel
from models.solicitud_model import SolicitudModel
from gradio_client import Client


# conexión con el Space en Hugging Face
try:
    cliente_modelo = Client("Angiesaray/pqrs-cul-api")
    print("Modelo conectado correctamente")
except Exception as e:
    print("Error conectando con el modelo:", e)
    cliente_modelo = None


usuario_bp = Blueprint('usuarios', __name__)
conversacion_bp = Blueprint('conversaciones', __name__)
pqrs_bp = Blueprint('pqrs', __name__)
chat_bp = Blueprint('chat', __name__)


usuario_model = UsuarioModel()
conversacion_model = ConversacionModel()
solicitud_model = SolicitudModel()


# ═══════════════════════════════════════════════════════════
# USUARIOS
# ═══════════════════════════════════════════════════════════

@usuario_bp.route('/registro', methods=['POST'])
def registrar():

    data = request.get_json()

    if not data:
        return jsonify({'error': 'Datos requeridos'}), 400

    nombre = data.get('nombre', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()
    rol = data.get('rol', 'estudiante')

    if not nombre or not email or not password:
        return jsonify({'error': 'nombre, email y password son obligatorios'}), 400

    resultado = usuario_model.crear(nombre, email, password, rol)

    if not resultado['ok']:
        return jsonify({'error': resultado['error']}), 409

    return jsonify({
        'mensaje': 'Usuario registrado',
        'usuario': resultado['usuario']
    }), 201


@usuario_bp.route('/login', methods=['POST'])
def login():

    data = request.get_json()

    if not data:
        return jsonify({'error': 'Datos requeridos'}), 400

    email = data.get('email', '').strip()
    password = data.get('password', '').strip()

    if not email or not password:
        return jsonify({'error': 'email y password son obligatorios'}), 400

    resultado = usuario_model.login(email, password)

    if not resultado['ok']:
        return jsonify({'error': resultado['error']}), 401

    return jsonify({
        'mensaje': 'Login exitoso',
        'usuario': resultado['usuario']
    }), 200


@usuario_bp.route('/<int:usuario_id>', methods=['GET'])
def obtener_usuario(usuario_id):

    resultado = usuario_model.obtener_por_id(usuario_id)

    if not resultado['ok']:
        return jsonify({'error': resultado['error']}), 404

    return jsonify(resultado['usuario']), 200


# ═══════════════════════════════════════════════════════════
# CONVERSACIONES
# ═══════════════════════════════════════════════════════════

@conversacion_bp.route('/iniciar', methods=['POST'])
def iniciar():

    data = request.get_json(silent=True) or {}
    session_id = data.get('session_id', '').strip()
    usuario_id = data.get('usuario_id')

    if not session_id:
        return jsonify({'error': 'session_id es obligatorio'}), 400

    resultado = conversacion_model.iniciar(session_id, usuario_id)

    if not resultado['ok']:
        return jsonify({
            'mensaje': 'Sesión ya activa',
            'session_id': session_id
        }), 200

    return jsonify({
        'mensaje': 'Sesión iniciada',
        'conversacion': resultado['conversacion']
    }), 201


@conversacion_bp.route('/<session_id>/finalizar', methods=['PUT'])
def finalizar(session_id):

    data = request.get_json(silent=True) or {}
    total_mensajes = data.get('total_mensajes', 0)

    resultado = conversacion_model.finalizar(session_id, total_mensajes)

    if not resultado['ok']:
        return jsonify({
            'mensaje': 'Sesión ya finalizada',
            'session_id': session_id
        }), 200

    return jsonify({
        'mensaje': 'Sesión finalizada',
        'conversacion': resultado['conversacion']
    }), 200


@conversacion_bp.route('/<session_id>/historial', methods=['GET'])
def historial(session_id):

    resultado = conversacion_model.obtener_historial(session_id)

    if not resultado['ok']:
        return jsonify({'error': resultado['error']}), 404

    return jsonify(resultado), 200

@conversacion_bp.route('/usuario/<int:usuario_id>', methods=['GET'])
def por_usuario(usuario_id):
    resultado = conversacion_model.listar_por_usuario(usuario_id)
    if not resultado['ok']:
        return jsonify({'error': resultado['error']}), 400
    return jsonify(resultado), 200
# ═══════════════════════════════════════════════════════════
# PQRS
# ═══════════════════════════════════════════════════════════

@pqrs_bp.route('/crear', methods=['POST'])
def crear():

    data = request.get_json()

    if not data:
        return jsonify({'error': 'Datos requeridos'}), 400

    usuario_id = data.get('usuario_id')
    tipo = data.get('tipo', '').strip()
    descripcion = data.get('descripcion', '').strip()
    prioridad = data.get('prioridad', 'NORMAL')
    dependencia = data.get('dependencia')

    if not tipo or not descripcion:
        return jsonify({'error': 'tipo y descripcion son obligatorios'}), 400

    resultado = solicitud_model.crear(
        usuario_id,
        tipo,
        descripcion,
        prioridad,
        dependencia
    )

    if not resultado['ok']:
        return jsonify({'error': resultado['error']}), 400

    return jsonify({
        'mensaje': 'Solicitud PQRS creada',
        'solicitud': resultado['solicitud']
    }), 201


# ═══════════════════════════════════════════════════════════
# CHAT
# ═══════════════════════════════════════════════════════════

RESPUESTAS_OFFLINE = {
    'queja': 'Para presentar una queja en la CUL debes registrar una PQRS indicando el área y la descripción.',
    'peticion': 'Una petición es una solicitud formal de información. El plazo de respuesta es de 15 días.',
    'reclamo': 'Un reclamo exige el cumplimiento de un derecho o servicio.',
    'sugerencia': 'Las sugerencias permiten mejorar los procesos institucionales.',
    'default': 'Puedo ayudarte con información sobre el sistema PQRS de la CUL.'
}


def respuesta_offline(texto):

    t = texto.lower()

    for clave, resp in RESPUESTAS_OFFLINE.items():
        if clave in t:
            return resp

    return RESPUESTAS_OFFLINE['default']


@chat_bp.route('/mensaje', methods=['POST'])
def mensaje():

    data = request.get_json() or {}
    session_id = data.get('session_id', '').strip()
    msg = data.get('mensaje', '').strip()

    if not msg:
        return jsonify({'error': 'El mensaje no puede estar vacío'}), 400

    if not session_id:
        return jsonify({'error': 'session_id es obligatorio'}), 400

    despedidas = ['adios', 'salir', 'terminar', 'bye', 'chao']

    if any(d in msg.lower() for d in despedidas):

        respuesta = "Hasta luego. Si necesitas más ayuda con el sistema PQRS de la CUL puedes iniciar otra conversación."

        conversacion_model.guardar_mensaje(session_id, 'user', msg)
        conversacion_model.guardar_mensaje(session_id, 'assistant', respuesta)

        conversacion_model.finalizar(session_id)

        return jsonify({
            'respuesta': respuesta,
            'session_id': session_id,
            'fin_sesion': True
        }), 200


    conversacion_model.guardar_mensaje(session_id, 'user', msg)


    respuesta = None


    # intentar usar el modelo
    if cliente_modelo:
        try:

            resultado = cliente_modelo.submit(
                msg,
                api_name="/responder"
            )

            respuesta = resultado.result(timeout=120)

            if isinstance(respuesta, list):
                respuesta = respuesta[0]

        except Exception as e:

            print("Modelo tardó demasiado o falló:", e)
            respuesta = None


    # fallback si el modelo no respondió
    if not respuesta:
        respuesta = respuesta_offline(msg)


    conversacion_model.guardar_mensaje(session_id, 'assistant', respuesta)

    return jsonify({
        'respuesta': respuesta,
        'session_id': session_id,
        'fin_sesion': False
    }), 200