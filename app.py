from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'secreto123'
DATABASE = 'baraja.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def crear_tabla_si_no_existe():
    conn = get_db_connection()

    # Tabla de cartas
    conn.execute('''
        CREATE TABLE IF NOT EXISTS cartas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT UNIQUE,
            nombre TEXT,
            telefono TEXT,
            asignada INTEGER DEFAULT 0
        )
    ''')

    # Tabla de usuarios
    conn.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            rol TEXT
        )
    ''')

    # Insertar cartas si no existen
    palos = ["oros", "copas", "espadas", "bastos"]
    numeros = [1, 2, 3, 4, 5, 6, 7, 10, 11, 12]
    for palo in palos:
        for numero in numeros:
            codigo = f"{numero}-{palo}"
            conn.execute("INSERT OR IGNORE INTO cartas (codigo) VALUES (?)", (codigo,))

    # Insertar usuarios básicos
    usuarios = [
        ("admin", "admin123", "admin"),
        ("juan", "juan123", "usuario")
    ]
    for username, password, rol in usuarios:
        conn.execute("INSERT OR IGNORE INTO usuarios (username, password, rol) VALUES (?, ?, ?)", (username, password, rol))

    conn.commit()
    conn.close()

@app.route("/")
def index():
    conn = get_db_connection()
    cartas = conn.execute("SELECT * FROM cartas").fetchall()
    conn.close()
    return render_template("index.html", cartas=cartas, usuario=session.get("usuario"), rol=session.get("rol"))

@app.route("/editar", methods=["POST"])
def editar():
    if "usuario" not in session:
        return redirect(url_for("login"))

    codigo = request.form.get("codigo")
    nombre = request.form.get("nombre")
    telefono = request.form.get("telefono")

    if not all([codigo, nombre, telefono]):
        return "Faltan datos", 400

    conn = get_db_connection()
    carta = conn.execute("SELECT * FROM cartas WHERE codigo = ?", (codigo,)).fetchone()

    if carta is None:
        conn.close()
        return "Carta no encontrada", 404

    if carta["asignada"]:
        # Si ya está asignada, solo el admin puede modificar
        if session.get("rol") != "admin":
            conn.close()
            return "No autorizado", 403

        conn.execute(
            "UPDATE cartas SET nombre = ?, telefono = ? WHERE codigo = ?",
            (nombre, telefono, codigo)
        )
    else:
        # Alta de ganador (rol usuario o admin)
        conn.execute(
            "UPDATE cartas SET nombre = ?, telefono = ?, asignada = 1 WHERE codigo = ?",
            (nombre, telefono, codigo)
        )

    conn.commit()
    conn.close()
    return redirect(url_for("index"))

@app.route("/eliminar", methods=["POST"])
def eliminar():
    if session.get("rol") != "admin":
        return "No autorizado", 403

    codigo = request.form.get("codigo")
    if not codigo:
        return "Código faltante", 400

    conn = get_db_connection()
    conn.execute("UPDATE cartas SET nombre = NULL, telefono = NULL, asignada = 0 WHERE codigo = ?", (codigo,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))

@app.route("/api/carta/<codigo>")
def api_carta(codigo):
    conn = get_db_connection()
    carta = conn.execute("SELECT * FROM cartas WHERE codigo = ?", (codigo,)).fetchone()
    conn.close()
    if carta:
        return {
            "codigo": carta["codigo"],
            "nombre": carta["nombre"],
            "telefono": carta["telefono"]
        }
    return {}, 404

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        conn = get_db_connection()
        user = conn.execute("SELECT * FROM usuarios WHERE username = ? AND password = ?", (username, password)).fetchone()
        conn.close()

        if user:
            session["usuario"] = user["username"]
            session["rol"] = user["rol"]
            return redirect(url_for("index"))
        else:
            return render_template("login.html", error="Usuario o contraseña incorrectos")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    import os
    crear_tabla_si_no_existe()
    port = int(os.environ.get("PORT", 5000))  # usa 5000 por defecto si no hay PORT
    app.run(host="0.0.0.0", port=port)

