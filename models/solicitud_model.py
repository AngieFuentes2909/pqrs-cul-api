import random, string
from config.database import Database

class SolicitudModel:
    def __init__(self):
        self.db = Database.get_instance()

    def _generar_radicado(self):
        chars = string.ascii_uppercase + string.digits
        return 'CUL-' + ''.join(random.choices(chars, k=8))

    def crear(self, usuario_id, tipo_nombre, descripcion, prioridad='NORMAL', dependencia=None):
        try:
            cursor = self.db.get_cursor()
            cursor.execute("SELECT id FROM tipo_pqrs WHERE nombre = %s", (tipo_nombre.upper(),))
            tipo = cursor.fetchone()
            if not tipo:
                return {'ok': False, 'error': f'Tipo invalido: {tipo_nombre}'}
            radicado = self._generar_radicado()
            cursor.execute("""
                INSERT INTO solicitudes (radicado, usuario_id, tipo_id, descripcion, prioridad, dependencia)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id, radicado, estado, created_at
            """, (radicado, usuario_id, tipo['id'], descripcion, prioridad.upper(), dependencia))
            sol = dict(cursor.fetchone())
            sol['created_at'] = str(sol['created_at'])
            cursor.execute("""
                INSERT INTO trazabilidad (solicitud_id, estado_anterior, estado_nuevo, observacion, usuario_id)
                VALUES (%s, NULL, 'PENDIENTE', 'Solicitud creada', %s)
            """, (sol['id'], usuario_id))
            return {'ok': True, 'solicitud': sol}
        except Exception as e:
            return {'ok': False, 'error': str(e)}

    def obtener_todas(self, limite=50, offset=0):
        try:
            cursor = self.db.get_cursor()
            cursor.execute("SELECT * FROM vista_solicitudes ORDER BY created_at DESC LIMIT %s OFFSET %s",
                           (limite, offset))
            solicitudes = []
            for row in cursor.fetchall():
                s = dict(row)
                s['created_at'] = str(s['created_at'])
                s['updated_at'] = str(s['updated_at'])
                solicitudes.append(s)
            return {'ok': True, 'solicitudes': solicitudes, 'total': len(solicitudes)}
        except Exception as e:
            return {'ok': False, 'error': str(e)}

    def buscar(self, tipo=None, estado=None, fecha_inicio=None):
        try:
            cursor = self.db.get_cursor()
            condiciones, valores = [], []
            if tipo:
                condiciones.append("tipo = %s")
                valores.append(tipo.upper())
            if estado:
                condiciones.append("estado = %s")
                valores.append(estado.upper())
            if fecha_inicio:
                condiciones.append("DATE(created_at) >= %s")
                valores.append(fecha_inicio)
            where = f"WHERE {' AND '.join(condiciones)}" if condiciones else ""
            cursor.execute(f"SELECT * FROM vista_solicitudes {where} ORDER BY created_at DESC", valores)
            solicitudes = []
            for row in cursor.fetchall():
                s = dict(row)
                s['created_at'] = str(s['created_at'])
                s['updated_at'] = str(s['updated_at'])
                solicitudes.append(s)
            return {'ok': True, 'solicitudes': solicitudes, 'total': len(solicitudes)}
        except Exception as e:
            return {'ok': False, 'error': str(e)}

    def obtener_por_id(self, solicitud_id):
        try:
            cursor = self.db.get_cursor()
            cursor.execute("SELECT * FROM vista_solicitudes WHERE id = %s", (solicitud_id,))
            sol = cursor.fetchone()
            if not sol:
                return {'ok': False, 'error': 'Solicitud no encontrada'}
            s = dict(sol)
            s['created_at'] = str(s['created_at'])
            s['updated_at'] = str(s['updated_at'])
            return {'ok': True, 'solicitud': s}
        except Exception as e:
            return {'ok': False, 'error': str(e)}

    def responder(self, solicitud_id, agente_id, contenido):
        try:
            cursor = self.db.get_cursor()
            cursor.execute("SELECT estado FROM solicitudes WHERE id = %s", (solicitud_id,))
            sol = cursor.fetchone()
            if not sol:
                return {'ok': False, 'error': 'Solicitud no encontrada'}
            estado_anterior = sol['estado']
            cursor.execute("""
                INSERT INTO respuestas (solicitud_id, agente_id, contenido)
                VALUES (%s, %s, %s) RETURNING id, contenido, fecha
            """, (solicitud_id, agente_id, contenido))
            resp = dict(cursor.fetchone())
            resp['fecha'] = str(resp['fecha'])
            cursor.execute("""
                UPDATE solicitudes SET estado = 'RESUELTO', updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (solicitud_id,))
            cursor.execute("""
                INSERT INTO trazabilidad (solicitud_id, estado_anterior, estado_nuevo, observacion, usuario_id)
                VALUES (%s, %s, 'RESUELTO', 'Respuesta emitida', %s)
            """, (solicitud_id, estado_anterior, agente_id))
            return {'ok': True, 'respuesta': resp, 'estado': 'RESUELTO'}
        except Exception as e:
            return {'ok': False, 'error': str(e)}

    def obtener_trazabilidad(self, solicitud_id):
        try:
            cursor = self.db.get_cursor()
            cursor.execute("""
                SELECT t.id, t.estado_anterior, t.estado_nuevo, t.observacion, t.fecha, u.nombre AS usuario
                FROM trazabilidad t
                LEFT JOIN usuarios u ON t.usuario_id = u.id
                WHERE t.solicitud_id = %s ORDER BY t.fecha ASC
            """, (solicitud_id,))
            traza = []
            for row in cursor.fetchall():
                t = dict(row)
                t['fecha'] = str(t['fecha'])
                traza.append(t)
            return {'ok': True, 'trazabilidad': traza}
        except Exception as e:
            return {'ok': False, 'error': str(e)}
