import bcrypt
from config.database import Database

class UsuarioModel:
    def __init__(self):
        self.db = Database.get_instance()

    def _row_to_dict(self, cursor, row):
        if row is None:
            return None
        cols = [d[0] for d in cursor.description]
        return dict(zip(cols, row))

    def crear(self, nombre, email, password, rol='estudiante'):
        try:
            hash_pw = bcrypt.hashpw(
                password.encode('utf-8'), bcrypt.gensalt()
            ).decode('utf-8')
            cursor = self.db.get_cursor()
            cursor.execute("""
                INSERT INTO usuarios (nombre, email, password, rol)
                VALUES (%s, %s, %s, %s)
                RETURNING id, nombre, email, rol, created_at
            """, (nombre, email, hash_pw, rol))
            u = self._row_to_dict(cursor, cursor.fetchone())
            u['created_at'] = str(u['created_at'])
            return {'ok': True, 'usuario': u}
        except Exception as e:
            if 'unique' in str(e).lower():
                return {'ok': False, 'error': 'El email ya esta registrado'}
            return {'ok': False, 'error': str(e)}

    def login(self, email, password):
        try:
            cursor = self.db.get_cursor()
            cursor.execute("""
                SELECT id, nombre, email, password, rol
                FROM usuarios WHERE email = %s AND activo = TRUE
            """, (email,))
            row = cursor.fetchone()
            if not row:
                return {'ok': False, 'error': 'Usuario no encontrado'}
            usuario = self._row_to_dict(cursor, row)
            if not bcrypt.checkpw(password.encode('utf-8'), usuario['password'].encode('utf-8')):
                return {'ok': False, 'error': 'Contrasena incorrecta'}
            return {'ok': True, 'usuario': {
                'id': usuario['id'], 'nombre': usuario['nombre'],
                'email': usuario['email'], 'rol': usuario['rol']
            }}
        except Exception as e:
            return {'ok': False, 'error': str(e)}

    def obtener_por_id(self, usuario_id):
        try:
            cursor = self.db.get_cursor()
            cursor.execute("""
                SELECT id, nombre, email, rol, created_at
                FROM usuarios WHERE id = %s AND activo = TRUE
            """, (usuario_id,))
            row = cursor.fetchone()
            if not row:
                return {'ok': False, 'error': 'Usuario no encontrado'}
            u = self._row_to_dict(cursor, row)
            u['created_at'] = str(u['created_at'])
            return {'ok': True, 'usuario': u}
        except Exception as e:
            return {'ok': False, 'error': str(e)}