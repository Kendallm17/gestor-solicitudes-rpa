-- Esquema del ERP legacy (compatible con SQLite; casi todo es ANSI y portable a PostgreSQL/MySQL)
CREATE TABLE IF NOT EXISTS registros (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo            TEXT UNIQUE,                 -- ERP-000123, se asigna tras el INSERT
    id_solicitud      TEXT NOT NULL UNIQUE,        -- GUID de la fila en Dataverse (evita registrar dos veces)
    solicitante_email TEXT NOT NULL,
    categoria         TEXT NOT NULL,
    monto             REAL NOT NULL CHECK (monto > 0),
    descripcion       TEXT NOT NULL,
    fecha_registro    TEXT NOT NULL DEFAULT (datetime('now')),
    estado            TEXT NOT NULL DEFAULT 'Registrado'
);
