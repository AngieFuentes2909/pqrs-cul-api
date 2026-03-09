from config.database import Database

class ConversacionModel:
    def __init__(self):
        self.db = Database.get_instance()

    def _to_dict(self, cursor, row):
        if row is None:
            return None
        return {cursor.description[i][0]: row[i] for i in range(len(row))}

    def iniciar(self, session_id, usuario_id=None):
        try:
            cursor = self.db.get_cursor()
            cursor.execute("""
                INSERT INTO conversaciones (session_id, usuario_id, estado)
                VALUES (%s, %s, 'activa')
                ON CONFLICT (session_id) DO NOTHING
                RETURNING id, session_id, fecha_inicio, estado
            """, (session_id, usuario_id))
            row = cursor.fetchone()
            if not row:
                return {'ok': True, 'conversacion': {'session_id': session_id}}
            c = self._to_dict(cursor, row)
            c['fecha_inicio'] = str(c['fecha_inicio'])
            return {'ok': True, 'conversacion': c}
        except Exception as e:
            return {'ok': False, 'error': str(e)}

    def finalizar(self, session_id, total_mensajes=0):
        try:
            cursor = self.db.get_cursor()
            cursor.execute("""
                UPDATE conversaciones
                SET estado = 'cerrada', fecha_fin = CURRENT_TIMESTAMP,
                    total_mensajes = %s
                WHERE session_id = %s
                RETURNING id, session_id, fecha_inicio, fecha_fin, estado, total_mensajes
            """, (total_mensajes, session_id))
            row = cursor.fetchone()
            if not row:
                return {'ok': False, 'error': 'Sesion no encontrada'}
            c = self._to_dict(cursor, row)
            c['fecha_inicio'] = str(c['fecha_inicio'])
            c['fecha_fin']    = str(c['fecha_fin'])
            return {'ok': True, 'conversacion': c}
        except Exception as e:
            return {'ok': False, 'error': str(e)}

    def guardar_mensaje(self, session_id, rol, contenido):
        try:
            cursor = self.db.get_cursor()
            cursor.execute(
                "SELECT id FROM conversaciones WHERE session_id = %s", (session_id,)
            )
            row = cursor.fetchone()
            if not row:
                return {'ok': False, 'error': 'Sesion no encontrada'}
            conv_id = row[0]
            cursor.execute("""
                INSERT INTO mensajes (conversacion_id, rol, contenido)
                VALUES (%s, %s, %s)
                RETURNING id, rol, contenido, timestamp
            """, (conv_id, rol, contenido))
            msg = self._to_dict(cursor, cursor.fetchone())
            msg['timestamp'] = str(msg['timestamp'])
            return {'ok': True, 'mensaje': msg}
        except Exception as e:
            return {'ok': False, 'error': str(e)}
        
        

    def obtener_historial(self, session_id):
        try:
            cursor = self.db.get_cursor()
            cursor.execute("""
                SELECT m.id, m.rol, m.contenido, m.timestamp
                FROM mensajes m
                JOIN conversaciones c ON m.conversacion_id = c.id
                WHERE c.session_id = %s
                ORDER BY m.timestamp ASC
            """, (session_id,))
            rows = cursor.fetchall()
            mensajes = []
            for row in rows:
                m = self._to_dict(cursor, row)
                m['timestamp'] = str(m['timestamp'])
                mensajes.append(m)
            return {'ok': True, 'historial': mensajes, 'total': len(mensajes)}
        except Exception as e:
            return {'ok': False, 'error': str(e)}
        
    def listar_por_usuario(self, usuario_id):
        try:
            cursor = self.db.get_cursor()
            cursor.execute("""
                SELECT id, session_id, fecha_inicio, fecha_fin, estado, total_mensajes
                FROM conversaciones WHERE usuario_id = %s
                ORDER BY fecha_inicio DESC
            """, (usuario_id,))
            rows = cursor.fetchall()
            convs = []
            for row in rows:
                c = self._to_dict(cursor, row)
                c['fecha_inicio'] = str(c['fecha_inicio'])
                if c['fecha_fin']:
                    c['fecha_fin'] = str(c['fecha_fin'])
                convs.append(c)
            return {'ok': True, 'conversaciones': convs}
        except Exception as e:
            return {'ok': False, 'error': str(e)}