"""Ejecuta sql/03_analysis.sql e imprime cada resultado (sin necesidad de tener el CLI de sqlite3).

Uso:  python run_analysis.py [ruta_db]
"""
import os
import sqlite3
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB = sys.argv[1] if len(sys.argv) > 1 else os.path.join(BASE_DIR, "erp.db")


def consultas(texto):
    """Separa el archivo en sentencias, ignorando líneas de comentario."""
    limpio = "\n".join(l for l in texto.splitlines() if not l.strip().startswith("--"))
    return [s.strip() for s in limpio.split(";") if s.strip()]


def main():
    con = sqlite3.connect(DB)
    with open(os.path.join(BASE_DIR, "sql", "03_analysis.sql"), encoding="utf-8") as f:
        sentencias = consultas(f.read())
    for i, sql in enumerate(sentencias, 1):
        cur = con.execute(sql)
        cols = [d[0] for d in cur.description]
        filas = cur.fetchall()
        print(f"\n=== Consulta {i} ({len(filas)} filas) ===")
        print(" | ".join(cols))
        for fila in filas:
            print(" | ".join(str(v) for v in fila))
    con.close()


if __name__ == "__main__":
    main()
