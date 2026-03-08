-- ═══════════════════════════════════════════════════════════
-- SISTEMA PQRS - CUL
-- Ejecutar sobre la base de datos pqrs_cul
-- ═══════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS usuarios (
    id         SERIAL PRIMARY KEY,
    nombre     VARCHAR(100) NOT NULL,
    email      VARCHAR(150) UNIQUE NOT NULL,
    password   VARCHAR(255) NOT NULL,
    rol        VARCHAR(20) DEFAULT 'estudiante'
               CHECK (rol IN ('estudiante','docente','admin')),
    activo     BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS conversaciones (
    id             SERIAL PRIMARY KEY,
    session_id     VARCHAR(30) UNIQUE NOT NULL,
    usuario_id     INTEGER REFERENCES usuarios(id) ON DELETE SET NULL,
    fecha_inicio   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_fin      TIMESTAMP,
    estado         VARCHAR(20) DEFAULT 'activa'
                   CHECK (estado IN ('activa','cerrada')),
    total_mensajes INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS mensajes (
    id              SERIAL PRIMARY KEY,
    conversacion_id INTEGER NOT NULL REFERENCES conversaciones(id) ON DELETE CASCADE,
    rol             VARCHAR(20) NOT NULL CHECK (rol IN ('user','assistant')),
    contenido       TEXT NOT NULL,
    timestamp       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tipo_pqrs (
    id          SERIAL PRIMARY KEY,
    nombre      VARCHAR(20) UNIQUE NOT NULL,
    descripcion TEXT,
    plazo_dias  INTEGER DEFAULT 15
);

INSERT INTO tipo_pqrs (nombre, descripcion, plazo_dias) VALUES
    ('PETICION',   'Solicitud de informacion, documentos o servicios', 15),
    ('QUEJA',      'Inconformidad con la prestacion de un servicio',   15),
    ('RECLAMO',    'Exigencia del cumplimiento de un derecho',         15),
    ('SUGERENCIA', 'Propuesta de mejora para la institucion',          30)
ON CONFLICT (nombre) DO NOTHING;

CREATE TABLE IF NOT EXISTS solicitudes (
    id          SERIAL PRIMARY KEY,
    radicado    VARCHAR(30) UNIQUE NOT NULL,
    usuario_id  INTEGER REFERENCES usuarios(id) ON DELETE SET NULL,
    tipo_id     INTEGER NOT NULL REFERENCES tipo_pqrs(id),
    descripcion TEXT NOT NULL,
    estado      VARCHAR(20) DEFAULT 'PENDIENTE'
                CHECK (estado IN ('PENDIENTE','EN_PROCESO','RESUELTO','CERRADO')),
    prioridad   VARCHAR(10) DEFAULT 'NORMAL'
                CHECK (prioridad IN ('BAJA','NORMAL','ALTA','URGENTE')),
    dependencia VARCHAR(100),
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS respuestas (
    id           SERIAL PRIMARY KEY,
    solicitud_id INTEGER NOT NULL REFERENCES solicitudes(id) ON DELETE CASCADE,
    agente_id    INTEGER REFERENCES usuarios(id) ON DELETE SET NULL,
    contenido    TEXT NOT NULL,
    fecha        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS trazabilidad (
    id              SERIAL PRIMARY KEY,
    solicitud_id    INTEGER NOT NULL REFERENCES solicitudes(id) ON DELETE CASCADE,
    estado_anterior VARCHAR(20),
    estado_nuevo    VARCHAR(20) NOT NULL,
    observacion     TEXT,
    usuario_id      INTEGER REFERENCES usuarios(id) ON DELETE SET NULL,
    fecha           TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_solicitudes_estado  ON solicitudes(estado);
CREATE INDEX IF NOT EXISTS idx_solicitudes_tipo    ON solicitudes(tipo_id);
CREATE INDEX IF NOT EXISTS idx_mensajes_conv       ON mensajes(conversacion_id);
CREATE INDEX IF NOT EXISTS idx_conversaciones_ses  ON conversaciones(session_id);

CREATE OR REPLACE VIEW vista_solicitudes AS
SELECT
    s.id,
    s.radicado,
    u.nombre    AS usuario,
    u.email     AS email_usuario,
    t.nombre    AS tipo,
    s.descripcion,
    s.estado,
    s.prioridad,
    s.dependencia,
    s.created_at,
    s.updated_at,
    COUNT(r.id) AS total_respuestas
FROM solicitudes s
LEFT JOIN usuarios   u ON s.usuario_id = u.id
LEFT JOIN tipo_pqrs  t ON s.tipo_id    = t.id
LEFT JOIN respuestas r ON s.id         = r.solicitud_id
GROUP BY s.id, u.nombre, u.email, t.nombre;

SELECT 'Tablas creadas exitosamente' AS mensaje;
