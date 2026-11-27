-- ============================================================
-- Consultas de análisis sobre `registros`
-- Requieren SQLite >= 3.25 (funciones de ventana). Los mismos conceptos
-- funcionan en PostgreSQL/MySQL 8 cambiando strftime() por to_char()/DATE_FORMAT().
-- ============================================================

-- 1) Gasto mensual por categoría (GROUP BY + agregados)
SELECT strftime('%Y-%m', fecha_registro) AS mes,
       categoria,
       COUNT(*)                          AS solicitudes,
       ROUND(SUM(monto), 2)              AS total,
       ROUND(AVG(monto), 2)              AS promedio
FROM registros
GROUP BY mes, categoria
ORDER BY mes, categoria
LIMIT 12;

-- 2) Top 3 solicitantes por categoría (CTE + RANK() sobre partición)
WITH gasto AS (
    SELECT categoria, solicitante_email, SUM(monto) AS total
    FROM registros
    GROUP BY categoria, solicitante_email
), ranking AS (
    SELECT categoria, solicitante_email, ROUND(total, 2) AS total,
           RANK() OVER (PARTITION BY categoria ORDER BY total DESC) AS posicion
    FROM gasto
)
SELECT * FROM ranking WHERE posicion <= 3 ORDER BY categoria, posicion;

-- 3) Gasto acumulado mes a mes (SUM() OVER con ventana ordenada)
WITH mensual AS (
    SELECT strftime('%Y-%m', fecha_registro) AS mes, SUM(monto) AS total
    FROM registros
    GROUP BY mes
)
SELECT mes,
       ROUND(total, 2) AS total_mes,
       ROUND(SUM(total) OVER (ORDER BY mes), 2) AS acumulado
FROM mensual
ORDER BY mes
LIMIT 12;

-- 4) Variación porcentual contra el mes anterior (LAG)
WITH mensual AS (
    SELECT strftime('%Y-%m', fecha_registro) AS mes, SUM(monto) AS total
    FROM registros
    GROUP BY mes
)
SELECT mes,
       ROUND(total, 2) AS total_mes,
       ROUND(100.0 * (total - LAG(total) OVER (ORDER BY mes)) / LAG(total) OVER (ORDER BY mes), 1) AS variacion_pct
FROM mensual
ORDER BY mes
LIMIT 12;

-- 5) Registros por encima del promedio de su categoría (JOIN con CTE)
WITH promedio AS (
    SELECT categoria, AVG(monto) AS prom
    FROM registros
    GROUP BY categoria
)
SELECT r.codigo, r.categoria, r.monto, ROUND(p.prom, 2) AS promedio_categoria
FROM registros r
JOIN promedio p ON p.categoria = r.categoria
WHERE r.monto > 1.5 * p.prom
ORDER BY r.monto DESC
LIMIT 10;
