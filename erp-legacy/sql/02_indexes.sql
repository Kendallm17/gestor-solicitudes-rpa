-- Índices de apoyo para las consultas de reportes.
-- Orden de columnas: primero la de igualdad (categoria), luego la de rango (fecha_registro).
CREATE INDEX IF NOT EXISTS idx_registros_categoria_fecha
    ON registros (categoria, fecha_registro);

-- Búsquedas por solicitante (pantalla "Registros" y reportes por persona).
CREATE INDEX IF NOT EXISTS idx_registros_solicitante
    ON registros (solicitante_email);
