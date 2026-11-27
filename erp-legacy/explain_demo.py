"""Demostración de optimización: plan de ejecución y tiempo ANTES y DESPUÉS de crear un índice.

Uso:  python explain_demo.py [ruta_db]
Requiere haber corrido antes `python seed.py`.
"""
import os
import sqlite3
import sys
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB = sys.argv[1] if len(sys.argv) > 1 else os.path.join(BASE_DIR, "erp.db")

CONSULTA = (
    "SELECT SUM(monto), COUNT(*) FROM registros "
    "WHERE categoria = 'Hospedaje' "
    "AND fecha_registro >= '2026-01-01' AND fecha_registro < '2026-07-01'"
)
REPETICIONES = 300


def plan(con):
    return [fila[3] for fila in con.execute("EXPLAIN QUERY PLAN " + CONSULTA)]


def tiempo_ms(con):
    t0 = time.perf_counter()
    for _ in range(REPETICIONES):
        con.execute(CONSULTA).fetchall()
    return (time.perf_counter() - t0) * 1000 / REPETICIONES


def main():
    con = sqlite3.connect(DB)
    con.execute("DROP INDEX IF EXISTS idx_registros_categoria_fecha")
    con.execute("DROP INDEX IF EXISTS idx_registros_solicitante")
    con.commit()
    total = con.execute("SELECT COUNT(*) FROM registros").fetchone()[0]
    print(f"Filas en la tabla: {total}")
    print("\nConsulta:\n  " + CONSULTA)

    antes_plan, antes_ms = plan(con), tiempo_ms(con)
    print("\n--- SIN índice ---")
    print("Plan:", *antes_plan, sep="\n  ")
    print(f"Tiempo promedio: {antes_ms:.3f} ms")

    con.execute("CREATE INDEX idx_registros_categoria_fecha ON registros (categoria, fecha_registro)")
    con.commit()
    despues_plan, despues_ms = plan(con), tiempo_ms(con)
    print("\n--- CON índice (categoria, fecha_registro) ---")
    print("Plan:", *despues_plan, sep="\n  ")
    print(f"Tiempo promedio: {despues_ms:.3f} ms")

    print(f"\nMejora aproximada: {antes_ms / despues_ms:.1f}x más rápido")
    con.close()


if __name__ == "__main__":
    main()
