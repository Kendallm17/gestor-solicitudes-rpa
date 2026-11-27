"""Genera datos de prueba (5.000 registros) para practicar consultas e índices.

Uso:  python seed.py [ruta_db]
Es idempotente: borra y recrea la tabla `registros` antes de cargar.
"""
import os
import random
import sqlite3
import sys
import uuid
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB = sys.argv[1] if len(sys.argv) > 1 else os.path.join(BASE_DIR, "erp.db")

CATEGORIAS = {  # (monto mínimo, monto máximo)
    "Alimentación": (3000, 40000),
    "Transporte": (2000, 60000),
    "Hospedaje": (30000, 220000),
    "Capacitación": (15000, 350000),
}
NOMBRES = ["ana", "luis", "maria", "carlos", "sofia", "diego", "valeria", "jose", "laura", "andres",
           "paola", "mateo", "daniela", "ricardo", "camila", "esteban", "karla", "pablo", "natalia", "mario"]
DOMINIOS = ["banco-demo.com", "ejemplo.cr"]
DESCRIPCIONES = ["Reunión con cliente", "Viaje a sucursal", "Curso en línea", "Capacitación técnica",
                 "Almuerzo de equipo", "Taxi aeropuerto", "Hotel por visita", "Congreso anual"]


def main(n=5000):
    random.seed(42)  # resultados reproducibles
    con = sqlite3.connect(DB)
    con.executescript("DROP TABLE IF EXISTS registros;")
    with open(os.path.join(BASE_DIR, "sql", "01_schema.sql"), encoding="utf-8") as f:
        con.executescript(f.read())

    inicio = datetime(2025, 1, 1)
    filas = []
    for i in range(1, n + 1):
        cat = random.choice(list(CATEGORIAS))
        lo, hi = CATEGORIAS[cat]
        fecha = inicio + timedelta(days=random.randint(0, 700), minutes=random.randint(0, 1439))
        email = f"{random.choice(NOMBRES)}{random.randint(1, 9)}@{random.choice(DOMINIOS)}"
        filas.append((
            "ERP-%06d" % i, str(uuid.UUID(int=random.getrandbits(128), version=4)), email, cat,
            round(random.uniform(lo, hi), 2), random.choice(DESCRIPCIONES),
            fecha.strftime("%Y-%m-%d %H:%M:%S"),
        ))
    con.executemany(
        "INSERT INTO registros (codigo, id_solicitud, solicitante_email, categoria, monto, descripcion, fecha_registro) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)", filas)
    con.commit()
    print(f"{n} registros cargados en {DB}")
    con.close()


if __name__ == "__main__":
    main()
