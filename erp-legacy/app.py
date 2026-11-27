"""ERP contable "legacy" simulado.

Sistema deliberadamente SIN API: solo tiene interfaz web (login + formularios).
Existe para justificar un bot RPA (Automation Anywhere) que registre las
solicitudes aprobadas desde Power Platform.
"""
import os
import re
import sqlite3
from functools import wraps

from flask import (Flask, flash, g, redirect, render_template, request,
                   session, url_for)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CATEGORIAS = ["Alimentación", "Transporte", "Hospedaje", "Capacitación"]
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def create_app(db_path=None):
    app = Flask(__name__)
    app.secret_key = os.environ.get("ERP_SECRET", "solo-para-desarrollo")
    app.config["DB_PATH"] = db_path or os.path.join(BASE_DIR, "erp.db")
    app.config["ERP_USER"] = os.environ.get("ERP_USER", "erp_user")
    app.config["ERP_PASSWORD"] = os.environ.get("ERP_PASSWORD", "erp1234")

    # ---------- base de datos ----------
    def get_db():
        if "db" not in g:
            g.db = sqlite3.connect(app.config["DB_PATH"])
            g.db.row_factory = sqlite3.Row
        return g.db

    @app.teardown_appcontext
    def close_db(_exc):
        db = g.pop("db", None)
        if db is not None:
            db.close()

    def init_db():
        schema = os.path.join(BASE_DIR, "sql", "01_schema.sql")
        with sqlite3.connect(app.config["DB_PATH"]) as con, open(schema, encoding="utf-8") as f:
            con.executescript(f.read())

    init_db()

    # ---------- autenticación ----------
    def login_required(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if not session.get("user"):
                return redirect(url_for("login"))
            return view(*args, **kwargs)
        return wrapped

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            ok = (request.form.get("username") == app.config["ERP_USER"]
                  and request.form.get("password") == app.config["ERP_PASSWORD"])
            if ok:
                session["user"] = request.form["username"]
                return redirect(url_for("nuevo"))
            flash("Usuario o contraseña incorrectos.", "error")
        return render_template("login.html")

    @app.route("/logout")
    def logout():
        session.clear()
        return redirect(url_for("login"))

    # ---------- páginas ----------
    @app.route("/")
    @login_required
    def index():
        return redirect(url_for("nuevo"))

    @app.route("/nuevo", methods=["GET", "POST"])
    @login_required
    def nuevo():
        datos = {k: (request.form.get(k) or "").strip() for k in
                 ("id_solicitud", "solicitante_email", "categoria", "monto", "descripcion")}
        if request.method == "POST":
            errores = validar(datos)
            if errores:
                for e in errores:
                    flash(e, "error")
                return render_template("nuevo.html", categorias=CATEGORIAS, datos=datos), 400
            db = get_db()
            try:
                cur = db.execute(
                    "INSERT INTO registros (id_solicitud, solicitante_email, categoria, monto, descripcion) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (datos["id_solicitud"], datos["solicitante_email"], datos["categoria"],
                     float(datos["monto"].replace(",", ".")), datos["descripcion"]))
            except sqlite3.IntegrityError:
                flash("Ya existe un registro para esta solicitud (id duplicado).", "error")
                return render_template("nuevo.html", categorias=CATEGORIAS, datos=datos), 409
            codigo = "ERP-%06d" % cur.lastrowid
            db.execute("UPDATE registros SET codigo = ? WHERE id = ?", (codigo, cur.lastrowid))
            db.commit()
            return redirect(url_for("confirmacion", codigo=codigo))
        return render_template("nuevo.html", categorias=CATEGORIAS, datos=datos)

    @app.route("/registro/<codigo>")
    @login_required
    def confirmacion(codigo):
        fila = get_db().execute("SELECT * FROM registros WHERE codigo = ?", (codigo,)).fetchone()
        if fila is None:
            return "Registro no encontrado", 404
        return render_template("confirmacion.html", r=fila)

    @app.route("/registros")
    @login_required
    def registros():
        q = (request.args.get("q") or "").strip()
        sql = "SELECT * FROM registros"
        params = ()
        if q:
            sql += " WHERE solicitante_email LIKE ? OR codigo LIKE ? OR id_solicitud LIKE ?"
            params = (f"%{q}%",) * 3
        sql += " ORDER BY id DESC LIMIT 100"
        filas = get_db().execute(sql, params).fetchall()
        return render_template("registros.html", filas=filas, q=q)

    return app


def validar(d):
    errores = []
    if not d["id_solicitud"]:
        errores.append("El id de solicitud es obligatorio.")
    if not EMAIL_RE.match(d["solicitante_email"]):
        errores.append("El correo del solicitante no es válido.")
    if d["categoria"] not in CATEGORIAS:
        errores.append("Seleccione una categoría válida.")
    try:
        if float(d["monto"].replace(",", ".")) <= 0:
            raise ValueError
    except ValueError:
        errores.append("El monto debe ser un número mayor que cero.")
    if not d["descripcion"]:
        errores.append("La descripción es obligatoria.")
    return errores


if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=5000, debug=False)
