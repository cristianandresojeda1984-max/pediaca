"""
PediAcá — Aplicación Principal
Stack: Python + Flask + SQLite
"""

import sqlite3
import os
import re
import io
from functools import wraps
from flask import (Flask, render_template, request, redirect,
                   url_for, session, flash, jsonify, g)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

# ── CONFIGURACIÓN ─────────────────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-key-cambiar-en-produccion")

DB_PATH       = os.environ.get("DB_PATH", "pediaca.db")
UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXT   = {"png", "jpg", "jpeg", "webp"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ── BASE DE DATOS ─────────────────────────────────────────────────────────────
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db

@app.teardown_appcontext
def close_db(exc):
    db = g.pop("db", None)
    if db:
        db.close()

def query(sql, args=(), one=False):
    cur = get_db().execute(sql, args)
    rv  = cur.fetchall()
    return (rv[0] if rv else None) if one else rv

def execute(sql, args=()):
    db  = get_db()
    cur = db.execute(sql, args)
    db.commit()
    return cur.lastrowid


# ── HELPERS ───────────────────────────────────────────────────────────────────
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Necesitás iniciar sesión.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

def rol_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if session.get("rol") not in roles:
                flash("No tenés permiso para acceder a esa página.", "danger")
                return redirect(url_for("home"))
            return f(*args, **kwargs)
        return decorated
    return decorator

def formato_pesos(valor):
    return f"${valor:,.0f}".replace(",", ".")

app.jinja_env.filters["pesos"] = formato_pesos


# ── RUTAS PÚBLICAS ────────────────────────────────────────────────────────────

@app.route("/")
def home():
    restaurantes = query("""
        SELECT r.*, u.telefono
        FROM restaurantes r
        JOIN usuarios u ON u.id = r.usuario_id
        WHERE r.estado = 'aprobado'
        ORDER BY r.nombre_local
    """)
    auspiciantes = query("""
        SELECT * FROM auspiciantes
        WHERE activo = 1
          AND (fecha_inicio IS NULL OR fecha_inicio <= date('now'))
          AND (fecha_fin   IS NULL OR fecha_fin   >= date('now'))
    """)
    return render_template("home.html",
                           restaurantes=restaurantes,
                           auspiciantes=auspiciantes)


@app.route("/local/<int:restaurante_id>")
def ver_local(restaurante_id):
    restaurante = query("""
        SELECT r.*, u.nombre AS dueno_nombre
        FROM restaurantes r
        JOIN usuarios u ON u.id = r.usuario_id
        WHERE r.id = ? AND r.estado = 'aprobado'
    """, (restaurante_id,), one=True)

    if not restaurante:
        flash("Local no encontrado.", "danger")
        return redirect(url_for("home"))

    categorias = query("""
        SELECT c.*, GROUP_CONCAT(p.id) AS producto_ids
        FROM categorias_menu c
        LEFT JOIN productos p ON p.categoria_id = c.id AND p.disponible = 1
        WHERE c.restaurante_id = ?
        GROUP BY c.id
        ORDER BY c.orden
    """, (restaurante_id,))

    productos = query("""
        SELECT * FROM productos
        WHERE restaurante_id = ? AND disponible = 1
        ORDER BY categoria_id, orden
    """, (restaurante_id,))

    return render_template("ver_local.html",
                           restaurante=restaurante,
                           categorias=categorias,
                           productos=productos)


# ── REGISTRO ──────────────────────────────────────────────────────────────────

@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        nombre    = request.form.get("nombre", "").strip()
        apellido  = request.form.get("apellido", "").strip()
        email     = request.form.get("email", "").strip().lower()
        telefono  = request.form.get("telefono", "").strip()
        password  = request.form.get("password", "")
        password2 = request.form.get("password2", "")
        rol       = request.form.get("rol", "cliente")

        # Validaciones
        if not all([nombre, apellido, email, password]):
            flash("Completá todos los campos obligatorios.", "danger")
            return redirect(url_for("registro"))

        if password != password2:
            flash("Las contraseñas no coinciden.", "danger")
            return redirect(url_for("registro"))

        if len(password) < 6:
            flash("La contraseña debe tener al menos 6 caracteres.", "danger")
            return redirect(url_for("registro"))

        if rol not in ("cliente", "restaurante", "cadete"):
            flash("Rol inválido.", "danger")
            return redirect(url_for("registro"))

        existe = query("SELECT id FROM usuarios WHERE email = ?", (email,), one=True)
        if existe:
            flash("Ya existe una cuenta con ese email.", "warning")
            return redirect(url_for("registro"))

        # Crear usuario
        password_hash = generate_password_hash(password)
        user_id = execute("""
            INSERT INTO usuarios (nombre, apellido, email, telefono, password_hash, rol)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (nombre, apellido, email, telefono, password_hash, rol))

        # Crear perfil según rol
        if rol == "cliente":
            execute("INSERT INTO clientes (usuario_id) VALUES (?)", (user_id,))
            flash("¡Cuenta creada! Ya podés iniciar sesión.", "success")

        elif rol == "restaurante":
            nombre_local = request.form.get("nombre_local", "").strip()
            whatsapp     = request.form.get("whatsapp", "").strip()
            categoria    = request.form.get("categoria", "").strip()
            direccion    = request.form.get("direccion", "").strip()

            if not nombre_local or not whatsapp:
                flash("El nombre del local y el WhatsApp son obligatorios.", "danger")
                execute("DELETE FROM usuarios WHERE id = ?", (user_id,))
                return redirect(url_for("registro"))

            execute("""
                INSERT INTO restaurantes (usuario_id, nombre_local, whatsapp, categoria, direccion)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, nombre_local, whatsapp, categoria, direccion))
            flash("Registro enviado. Te avisamos cuando tu local esté aprobado.", "info")

        elif rol == "cadete":
            vehiculo = request.form.get("vehiculo", "moto")
            zona     = request.form.get("zona", "").strip()
            execute("""
                INSERT INTO cadetes (usuario_id, vehiculo, zona)
                VALUES (?, ?, ?)
            """, (user_id, vehiculo, zona))
            flash("Registro enviado. Te avisamos cuando seas aprobado.", "info")

        return redirect(url_for("login"))

    return render_template("registro.html")


# ── LOGIN / LOGOUT ────────────────────────────────────────────────────────────

@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        email    = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = query("SELECT * FROM usuarios WHERE email = ?", (email,), one=True)

        if not user or not check_password_hash(user["password_hash"], password):
            flash("Email o contraseña incorrectos.", "danger")
            return redirect(url_for("login"))

        if not user["activo"]:
            flash("Tu cuenta está desactivada.", "warning")
            return redirect(url_for("login"))

        session["user_id"] = user["id"]
        session["nombre"]  = user["nombre"]
        session["rol"]     = user["rol"]

        flash(f"¡Bienvenido, {user['nombre']}!", "success")
        return redirect(url_for("dashboard"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


# ── DASHBOARD (despacha según rol) ────────────────────────────────────────────

@app.route("/dashboard")
@login_required
def dashboard():
    rol = session.get("rol")
    if rol == "admin":
        return redirect(url_for("admin_panel"))
    if rol == "restaurante":
        return redirect(url_for("restaurante_panel"))
    if rol == "cadete":
        return redirect(url_for("cadete_panel"))
    return redirect(url_for("cliente_panel"))


# ── PANEL RESTAURANTE ─────────────────────────────────────────────────────────

def get_restaurante_aprobado():
    """Devuelve el restaurante si está aprobado, o None."""
    return query("""
        SELECT * FROM restaurantes
        WHERE usuario_id = ? AND estado = 'aprobado'
    """, (session["user_id"],), one=True)

def get_restaurante_any():
    """Devuelve el restaurante sin importar su estado."""
    return query(
        "SELECT * FROM restaurantes WHERE usuario_id = ?",
        (session["user_id"],), one=True
    )

def guardar_imagen(archivo, subcarpeta=""):
    """Guarda un archivo subido y devuelve la ruta relativa."""
    if not archivo or archivo.filename == "":
        return None
    if not allowed_file(archivo.filename):
        return None
    filename = secure_filename(archivo.filename)
    import uuid, time
    ext      = filename.rsplit(".", 1)[1].lower()
    filename = f"{int(time.time())}_{uuid.uuid4().hex[:6]}.{ext}"
    destino  = os.path.join(app.config["UPLOAD_FOLDER"], subcarpeta)
    os.makedirs(destino, exist_ok=True)
    ruta_completa = os.path.join(destino, filename)
    archivo.save(ruta_completa)
    return os.path.join("uploads", subcarpeta, filename).replace("\\", "/")


@app.route("/mi-local")
@login_required
@rol_required("restaurante")
def restaurante_panel():
    # Primero chequear si el local existe (puede estar pendiente)
    restaurante_raw = get_restaurante_any()
    if not restaurante_raw:
        flash("No encontramos tu local.", "danger")
        return redirect(url_for("home"))

    # Si está pendiente o suspendido, mostrar pantalla de espera
    if restaurante_raw["estado"] != "aprobado":
        return render_template("restaurante_espera.html",
                               restaurante=restaurante_raw)

    restaurante = restaurante_raw

    categorias = query("""
        SELECT c.*, COUNT(p.id) AS total_productos
        FROM categorias_menu c
        LEFT JOIN productos p ON p.categoria_id = c.id
        WHERE c.restaurante_id = ?
        GROUP BY c.id
        ORDER BY c.orden
    """, (restaurante["id"],))

    productos = query("""
        SELECT p.*, c.nombre AS categoria_nombre
        FROM productos p
        LEFT JOIN categorias_menu c ON c.id = p.categoria_id
        WHERE p.restaurante_id = ?
        ORDER BY p.categoria_id, p.orden
    """, (restaurante["id"],))

    # Cargar sabores por producto
    sabores_map = {}
    if productos:
        ids = ",".join(str(p["id"]) for p in productos)
        sabores = query(f"SELECT * FROM sabores_producto WHERE producto_id IN ({ids}) AND disponible=1 ORDER BY producto_id, orden")
        for s in sabores:
            sabores_map.setdefault(s["producto_id"], []).append(s)

    return render_template("restaurante_panel.html",
                           restaurante=restaurante,
                           categorias=categorias,
                           productos=productos,
                           sabores_map=sabores_map)


@app.route("/mi-local/editar", methods=["POST"])
@login_required
@rol_required("restaurante")
def restaurante_editar():
    restaurante = query(
        "SELECT * FROM restaurantes WHERE usuario_id = ?",
        (session["user_id"],), one=True
    )
    if not restaurante:
        return redirect(url_for("home"))

    nombre_local    = request.form.get("nombre_local", "").strip()
    descripcion     = request.form.get("descripcion", "").strip()
    categoria       = request.form.get("categoria", "").strip()
    direccion       = request.form.get("direccion", "").strip()
    whatsapp        = request.form.get("whatsapp", "").strip()
    horario         = request.form.get("horario", "").strip()
    hace_envio      = 1 if request.form.get("hace_envio") else 0
    costo_envio     = float(request.form.get("costo_envio", 0) or 0)
    tiempo_estimado = request.form.get("tiempo_estimado", "").strip() or None

    execute("""
        UPDATE restaurantes SET
            nombre_local=?, descripcion=?, categoria=?, direccion=?,
            whatsapp=?, horario=?, hace_envio=?, costo_envio=?, tiempo_estimado=?
        WHERE id=?
    """, (nombre_local, descripcion, categoria, direccion,
          whatsapp, horario, hace_envio, costo_envio,
          tiempo_estimado, restaurante["id"]))

    flash("Datos del local actualizados.", "success")
    return redirect(url_for("restaurante_panel"))


@app.route("/mi-local/categoria/nueva", methods=["POST"])
@login_required
@rol_required("restaurante")
def categoria_nueva():
    restaurante = query(
        "SELECT id FROM restaurantes WHERE usuario_id = ?",
        (session["user_id"],), one=True
    )
    nombre = request.form.get("nombre", "").strip()
    if nombre and restaurante:
        execute("""
            INSERT INTO categorias_menu (restaurante_id, nombre, orden)
            VALUES (?, ?, (SELECT COALESCE(MAX(orden),0)+1 FROM categorias_menu WHERE restaurante_id=?))
        """, (restaurante["id"], nombre, restaurante["id"]))
        flash(f"Categoría '{nombre}' creada.", "success")
    return redirect(url_for("restaurante_panel"))


@app.route("/mi-local/producto/nuevo", methods=["POST"])
@login_required
@rol_required("restaurante")
def producto_nuevo():
    restaurante = query(
        "SELECT id FROM restaurantes WHERE usuario_id = ?",
        (session["user_id"],), one=True
    )
    if not restaurante:
        return redirect(url_for("home"))

    nombre       = request.form.get("nombre", "").strip()
    descripcion  = request.form.get("descripcion", "").strip()
    precio       = float(request.form.get("precio", 0) or 0)
    categoria_id = request.form.get("categoria_id") or None
    disponible   = 1 if request.form.get("disponible") else 0

    # Foto inline
    foto_url = None
    archivo  = request.files.get("foto")
    if archivo and archivo.filename:
        foto_url = guardar_imagen(archivo, "productos")

    prod_id = execute("""
        INSERT INTO productos (restaurante_id, categoria_id, nombre, descripcion, precio, disponible, foto_url)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (restaurante["id"], categoria_id, nombre, descripcion, precio, disponible, foto_url))

    flash(f"Producto '{nombre}' agregado.", "success")
    return redirect(url_for("restaurante_panel"))


# ── CARGA MASIVA ───────────────────────────────────────────────────────────────

@app.route("/mi-local/carga-masiva", methods=["POST"])
@login_required
@rol_required("restaurante")
def carga_masiva():
    """Acepta JSON (renglones manuales), CSV o Excel."""
    restaurante = get_restaurante_aprobado()
    if not restaurante:
        return jsonify({"error": "No autorizado"}), 403

    productos_data = []

    # ── Renglones manuales (JSON) ──────────────────────────────
    if request.is_json:
        rows = request.get_json().get("productos", [])
        for r in rows:
            nombre = str(r.get("nombre", "")).strip()
            if not nombre:
                continue
            productos_data.append({
                "nombre":      nombre,
                "descripcion": str(r.get("descripcion", "")).strip(),
                "precio":      float(r.get("precio", 0) or 0),
                "categoria":   str(r.get("categoria", "")).strip(),
            })

    # ── Archivo CSV o Excel ────────────────────────────────────
    else:
        archivo = request.files.get("archivo")
        if not archivo:
            return jsonify({"error": "No se recibió archivo"}), 400

        ext = archivo.filename.rsplit(".", 1)[-1].lower()

        if ext == "csv":
            import csv, io as _io
            texto = archivo.read().decode("utf-8-sig", errors="replace")
            reader = csv.DictReader(_io.StringIO(texto))
            for row in reader:
                nombre = str(row.get("nombre", row.get("Nombre", ""))).strip()
                if not nombre:
                    continue
                productos_data.append({
                    "nombre":      nombre,
                    "descripcion": str(row.get("descripcion", row.get("Descripcion", ""))).strip(),
                    "precio":      float(row.get("precio", row.get("Precio", 0)) or 0),
                    "categoria":   str(row.get("categoria", row.get("Categoria", ""))).strip(),
                })

        elif ext in ("xlsx", "xls"):
            import openpyxl
            wb   = openpyxl.load_workbook(archivo, read_only=True, data_only=True)
            ws   = wb.active
            rows = list(ws.iter_rows(values_only=True))
            if not rows:
                return jsonify({"error": "Archivo vacío"}), 400
            # Primera fila = encabezados
            headers = [str(h or "").lower().strip() for h in rows[0]]
            def _col(row, *names):
                for n in names:
                    if n in headers:
                        v = row[headers.index(n)]
                        return v if v is not None else ""
                return ""
            for row in rows[1:]:
                nombre = str(_col(row, "nombre")).strip()
                if not nombre:
                    continue
                productos_data.append({
                    "nombre":      nombre,
                    "descripcion": str(_col(row, "descripcion")).strip(),
                    "precio":      float(_col(row, "precio") or 0),
                    "categoria":   str(_col(row, "categoria")).strip(),
                })
        else:
            return jsonify({"error": "Formato no soportado. Usá .csv o .xlsx"}), 400

    if not productos_data:
        return jsonify({"error": "No se encontraron productos válidos"}), 400

    # Mapear categorías por nombre
    cats = query("SELECT id, nombre FROM categorias_menu WHERE restaurante_id=?",
                 (restaurante["id"],))
    cat_map = {c["nombre"].lower().strip(): c["id"] for c in cats}

    insertados = 0
    for p in productos_data:
        cat_id = cat_map.get(p["categoria"].lower()) if p["categoria"] else None
        execute("""
            INSERT INTO productos (restaurante_id, categoria_id, nombre, descripcion, precio, disponible)
            VALUES (?, ?, ?, ?, ?, 1)
        """, (restaurante["id"], cat_id, p["nombre"], p["descripcion"], p["precio"]))
        insertados += 1

    return jsonify({"ok": True, "insertados": insertados})


@app.route("/mi-local/plantilla-excel")
@login_required
@rol_required("restaurante")
def descargar_plantilla():
    """Genera un Excel de ejemplo para carga masiva."""
    import openpyxl
    from flask import send_file
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Menú"
    ws.append(["nombre", "descripcion", "precio", "categoria"])
    ejemplos = [
        ("Pizza Muzzarella", "Salsa, muzzarella y orégano", 4500, "Pizzas"),
        ("Pizza Napolitana", "Salsa, muzzarella y tomate", 5000, "Pizzas"),
        ("Empanada de Carne", "Carne cortada a cuchillo", 800, "Empanadas"),
        ("Coca-Cola 500ml", "", 1200, "Bebidas"),
    ]
    for e in ejemplos:
        ws.append(e)
    # Ancho de columnas
    for col, ancho in [("A", 30), ("B", 40), ("C", 12), ("D", 20)]:
        ws.column_dimensions[col].width = ancho

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return send_file(buf, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                     as_attachment=True, download_name="plantilla_menu_pediaca.xlsx")


# ── SABORES ────────────────────────────────────────────────────────────────────

@app.route("/mi-local/producto/<int:prod_id>/sabores", methods=["POST"])
@login_required
@rol_required("restaurante")
def sabor_nuevo(prod_id):
    restaurante = get_restaurante_aprobado()
    if not restaurante:
        return redirect(url_for("restaurante_panel"))
    # Verificar que el producto es del restaurante
    prod = query("SELECT id FROM productos WHERE id=? AND restaurante_id=?",
                 (prod_id, restaurante["id"]), one=True)
    if not prod:
        return redirect(url_for("restaurante_panel"))

    nombre = request.form.get("nombre", "").strip()
    if nombre:
        execute("""
            INSERT INTO sabores_producto (producto_id, nombre, orden)
            VALUES (?, ?, (SELECT COALESCE(MAX(orden),0)+1 FROM sabores_producto WHERE producto_id=?))
        """, (prod_id, nombre, prod_id))
        flash(f"Gusto '{nombre}' agregado.", "success")
    return redirect(url_for("restaurante_panel") + "#prod-" + str(prod_id))


@app.route("/mi-local/sabor/<int:sabor_id>/eliminar", methods=["POST"])
@login_required
@rol_required("restaurante")
def sabor_eliminar(sabor_id):
    restaurante = get_restaurante_aprobado()
    if not restaurante:
        return redirect(url_for("restaurante_panel"))
    execute("""
        DELETE FROM sabores_producto
        WHERE id=? AND producto_id IN (
            SELECT id FROM productos WHERE restaurante_id=?
        )
    """, (sabor_id, restaurante["id"]))
    return redirect(url_for("restaurante_panel"))


@app.route("/api/producto/<int:prod_id>/sabores")
def get_sabores(prod_id):
    sabores = query("""
        SELECT id, nombre FROM sabores_producto
        WHERE producto_id=? AND disponible=1
        ORDER BY orden
    """, (prod_id,))
    return jsonify({"sabores": [dict(s) for s in sabores]})


@app.route("/mi-local/producto/<int:prod_id>/toggle")
@login_required
@rol_required("restaurante")
def producto_toggle(prod_id):
    restaurante = query(
        "SELECT id FROM restaurantes WHERE usuario_id = ?",
        (session["user_id"],), one=True
    )
    execute("""
        UPDATE productos SET disponible = 1 - disponible
        WHERE id = ? AND restaurante_id = ?
    """, (prod_id, restaurante["id"]))
    return redirect(url_for("restaurante_panel"))


@app.route("/mi-local/producto/<int:prod_id>/eliminar", methods=["POST"])
@login_required
@rol_required("restaurante")
def producto_eliminar(prod_id):
    restaurante = query(
        "SELECT id FROM restaurantes WHERE usuario_id = ?",
        (session["user_id"],), one=True
    )
    execute("DELETE FROM productos WHERE id = ? AND restaurante_id = ?",
            (prod_id, restaurante["id"]))
    flash("Producto eliminado.", "success")
    return redirect(url_for("restaurante_panel"))


# ── PANEL CADETE ──────────────────────────────────────────────────────────────

@app.route("/mi-panel-cadete")
@login_required
@rol_required("cadete")
def cadete_panel():
    cadete = query(
        "SELECT * FROM cadetes WHERE usuario_id = ?",
        (session["user_id"],), one=True
    )
    pedidos_disponibles = []
    if cadete and cadete["estado"] == "aprobado":
        pedidos_disponibles = query("""
            SELECT p.*, r.nombre_local, r.whatsapp
            FROM pedidos p
            JOIN restaurantes r ON r.id = p.restaurante_id
            WHERE p.tipo_entrega = 'delivery'
              AND p.estado = 'confirmado'
              AND p.cadete_id IS NULL
            ORDER BY p.fecha_pedido DESC
        """)
    return render_template("cadete_panel.html",
                           cadete=cadete,
                           pedidos=pedidos_disponibles)


@app.route("/mi-panel-cadete/disponibilidad", methods=["POST"])
@login_required
@rol_required("cadete")
def cadete_toggle_disponibilidad():
    cadete = query("SELECT * FROM cadetes WHERE usuario_id = ?",
                   (session["user_id"],), one=True)
    if cadete:
        execute("UPDATE cadetes SET disponible = 1 - disponible WHERE usuario_id = ?",
                (session["user_id"],))
    return redirect(url_for("cadete_panel"))


@app.route("/mi-panel-cadete/editar", methods=["POST"])
@login_required
@rol_required("cadete")
def cadete_editar_perfil():
    vehiculo = request.form.get("vehiculo", "moto")
    zona     = request.form.get("zona", "").strip()
    execute("UPDATE cadetes SET vehiculo=?, zona=? WHERE usuario_id=?",
            (vehiculo, zona, session["user_id"]))
    flash("Perfil actualizado.", "success")
    return redirect(url_for("cadete_panel"))


# ── PANEL CLIENTE ─────────────────────────────────────────────────────────────

@app.route("/mi-cuenta")
@login_required
@rol_required("cliente")
def cliente_panel():
    pedidos = query("""
        SELECT p.*, r.nombre_local, r.restaurante_id
        FROM pedidos p
        JOIN restaurantes r ON r.id = p.restaurante_id
        WHERE p.cliente_id = ?
        ORDER BY p.fecha_pedido DESC LIMIT 30
    """, (session["user_id"],))

    # Locales más pedidos (frecuentes)
    locales_frecuentes = query("""
        SELECT r.*, COUNT(p.id) as veces
        FROM pedidos p
        JOIN restaurantes r ON r.id = p.restaurante_id
        WHERE p.cliente_id = ? AND r.estado = 'aprobado'
        GROUP BY r.id
        ORDER BY veces DESC LIMIT 6
    """, (session["user_id"],))

    usuario = query("SELECT * FROM usuarios WHERE id = ?",
                    (session["user_id"],), one=True)
    cliente = query("SELECT * FROM clientes WHERE usuario_id = ?",
                    (session["user_id"],), one=True)

    return render_template("cliente_panel.html",
                           pedidos=pedidos,
                           locales_frecuentes=locales_frecuentes,
                           usuario=usuario,
                           cliente=cliente)


@app.route("/mi-cuenta/editar", methods=["POST"])
@login_required
@rol_required("cliente")
def cliente_editar_perfil():
    nombre    = request.form.get("nombre", "").strip()
    apellido  = request.form.get("apellido", "").strip()
    email     = request.form.get("email", "").strip().lower()
    telefono  = request.form.get("telefono", "").strip()
    dir_def   = request.form.get("direccion_default", "").strip()
    notas_def = request.form.get("notas_default", "").strip()

    execute("UPDATE usuarios SET nombre=?, apellido=?, email=?, telefono=? WHERE id=?",
            (nombre, apellido, email, telefono, session["user_id"]))
    execute("""
        UPDATE clientes SET direccion_default=?, notas_default=?
        WHERE usuario_id=?
    """, (dir_def, notas_def, session["user_id"]))

    session["nombre"] = nombre
    flash("Datos actualizados.", "success")
    return redirect(url_for("cliente_panel"))


@app.route("/mi-cuenta/password", methods=["POST"])
@login_required
@rol_required("cliente")
def cliente_cambiar_password():
    from werkzeug.security import check_password_hash, generate_password_hash
    actual = request.form.get("password_actual", "")
    nueva  = request.form.get("password_nueva", "")

    usuario = query("SELECT * FROM usuarios WHERE id = ?",
                    (session["user_id"],), one=True)

    if not check_password_hash(usuario["password_hash"], actual):
        flash("La contraseña actual es incorrecta.", "danger")
        return redirect(url_for("cliente_panel"))

    if len(nueva) < 6:
        flash("La nueva contraseña debe tener al menos 6 caracteres.", "danger")
        return redirect(url_for("cliente_panel"))

    execute("UPDATE usuarios SET password_hash=? WHERE id=?",
            (generate_password_hash(nueva), session["user_id"]))
    flash("Contraseña actualizada correctamente.", "success")
    return redirect(url_for("cliente_panel"))


# ── PANEL ADMIN ───────────────────────────────────────────────────────────────

@app.route("/admin")
@login_required
@rol_required("admin")
def admin_panel():
    pendientes_restaurantes = query("""
        SELECT r.*, u.nombre, u.apellido, u.email, u.telefono
        FROM restaurantes r JOIN usuarios u ON u.id = r.usuario_id
        WHERE r.estado = 'pendiente' ORDER BY r.fecha_alta
    """)
    pendientes_cadetes = query("""
        SELECT c.*, u.nombre, u.apellido, u.email, u.telefono
        FROM cadetes c JOIN usuarios u ON u.id = c.usuario_id
        WHERE c.estado = 'pendiente' ORDER BY u.fecha_registro
    """)
    todos_restaurantes = query("""
        SELECT r.*, u.nombre, u.apellido, u.email
        FROM restaurantes r JOIN usuarios u ON u.id = r.usuario_id
        ORDER BY r.estado, r.nombre_local
    """)
    todos_cadetes = query("""
        SELECT c.*, u.nombre, u.apellido, u.email, u.telefono
        FROM cadetes c JOIN usuarios u ON u.id = c.usuario_id
        ORDER BY c.estado, u.nombre
    """)
    ultimos_pedidos = query("""
        SELECT p.*, r.nombre_local,
               u.nombre AS nombre_cliente
        FROM pedidos p
        JOIN restaurantes r ON r.id = p.restaurante_id
        LEFT JOIN usuarios u ON u.id = p.cliente_id
        ORDER BY p.fecha_pedido DESC LIMIT 50
    """)
    stats = {
        "restaurantes_activos": query(
            "SELECT COUNT(*) as n FROM restaurantes WHERE estado='aprobado'", one=True)["n"],
        "cadetes_activos": query(
            "SELECT COUNT(*) as n FROM cadetes WHERE estado='aprobado'", one=True)["n"],
        "clientes": query(
            "SELECT COUNT(*) as n FROM usuarios WHERE rol='cliente'", one=True)["n"],
        "pedidos_hoy": query(
            "SELECT COUNT(*) as n FROM pedidos WHERE date(fecha_pedido)=date('now','localtime')",
            one=True)["n"],
    }
    return render_template("admin_panel.html",
                           pendientes_restaurantes=pendientes_restaurantes,
                           pendientes_cadetes=pendientes_cadetes,
                           todos_restaurantes=todos_restaurantes,
                           todos_cadetes=todos_cadetes,
                           ultimos_pedidos=ultimos_pedidos,
                           stats=stats)


@app.route("/admin/restaurante/<int:restaurante_id>/estado/<accion>")
@login_required
@rol_required("admin")
def admin_restaurante_estado(restaurante_id, accion):
    estados = {"aprobar": "aprobado", "suspender": "suspendido", "pendiente": "pendiente"}
    if accion not in estados:
        flash("Acción inválida.", "danger")
        return redirect(url_for("admin_panel"))
    execute("UPDATE restaurantes SET estado=? WHERE id=?",
            (estados[accion], restaurante_id))
    flash(f"Local {estados[accion]}.", "success")
    return redirect(url_for("admin_panel"))


@app.route("/admin/cadete/<int:cadete_id>/estado/<accion>")
@login_required
@rol_required("admin")
def admin_cadete_estado(cadete_id, accion):
    estados = {"aprobar": "aprobado", "suspender": "suspendido"}
    if accion not in estados:
        flash("Acción inválida.", "danger")
        return redirect(url_for("admin_panel"))
    execute("UPDATE cadetes SET estado=? WHERE id=?",
            (estados[accion], cadete_id))
    flash(f"Cadete {estados[accion]}.", "success")
    return redirect(url_for("admin_panel"))


# ── API: GENERAR LINK DE WHATSAPP ─────────────────────────────────────────────

import urllib.parse

def _limpiar_numero(tel):
    n = tel.replace("+","").replace("-","").replace(" ","")
    if not n.startswith("549"):
        n = "549" + n
    return n

def _wa_link(numero, mensaje):
    return f"https://wa.me/{numero}?text={urllib.parse.quote(mensaje)}"


@app.route("/api/whatsapp-link", methods=["POST"])
def whatsapp_link():
    data           = request.get_json()
    restaurante_id = data.get("restaurante_id")
    items          = data.get("items", [])
    tipo_entrega   = data.get("tipo_entrega", "retiro")
    direccion      = data.get("direccion", "").strip()
    notas          = data.get("notas", "").strip()
    nombre_cliente = data.get("nombre_cliente", "").strip()
    tel_cliente    = data.get("tel_cliente", "").strip()

    # Validaciones obligatorias
    if not nombre_cliente:
        return jsonify({"error": "El nombre es obligatorio"}), 400
    if tipo_entrega == "delivery" and not direccion:
        return jsonify({"error": "La dirección es obligatoria para delivery"}), 400

    restaurante = query(
        "SELECT * FROM restaurantes WHERE id = ? AND estado = 'aprobado'",
        (restaurante_id,), one=True
    )
    if not restaurante or not items:
        return jsonify({"error": "Datos inválidos"}), 400

    # Armar mensaje para el local
    total = sum(i["cantidad"] * i["precio"] for i in items)
    lineas = [f"🛵 *Nuevo pedido — {restaurante['nombre_local']}*\n"]
    lineas.append(f"👤 *Cliente:* {nombre_cliente}")
    if tel_cliente:
        lineas.append(f"📱 *Tel:* {tel_cliente}")
    lineas.append("")
    for item in items:
        sub = item["cantidad"] * item["precio"]
        lineas.append(f"• {item['cantidad']}x {item['nombre']} — ${sub:,.0f}".replace(",","."))
    lineas.append(f"\n*Total: ${total:,.0f}*".replace(",","."))
    lineas.append(f"*Entrega:* {'🛵 Delivery' if tipo_entrega == 'delivery' else '🏪 Retiro en local'}")
    if tipo_entrega == "delivery":
        lineas.append(f"*Dirección:* {direccion}")
    if notas:
        lineas.append(f"*Notas:* {notas}")
    lineas.append("\n_Pedido generado desde pediaca.ar_")

    mensaje    = "\n".join(lineas)
    numero     = _limpiar_numero(restaurante["whatsapp"])
    link       = _wa_link(numero, mensaje)

    # Guardar pedido
    cliente_id = session.get("user_id")
    nom_anon   = nombre_cliente if not cliente_id else None
    tel_anon   = tel_cliente    if not cliente_id else None

    pedido_id = execute("""
        INSERT INTO pedidos
            (restaurante_id, cliente_id, nombre_cliente_anonimo, telefono_cliente_anonimo,
             tipo_entrega, direccion_entrega, total, notas, enviado_whatsapp)
        VALUES (?,?,?,?,?,?,?,?,1)
    """, (restaurante_id, cliente_id, nom_anon, tel_anon,
          tipo_entrega, direccion, total, notas))

    for item in items:
        execute("""
            INSERT INTO items_pedido
                (pedido_id, producto_id, nombre_producto, cantidad, precio_unitario, subtotal)
            VALUES (?,?,?,?,?,?)
        """, (pedido_id, item.get("producto_id"), item["nombre"],
              item["cantidad"], item["precio"], item["cantidad"] * item["precio"]))

    return jsonify({"link": link, "pedido_id": pedido_id})


# ── API: STATUS DEL PEDIDO (polling cliente) ──────────────────────────────────

@app.route("/api/pedido/<int:pedido_id>/status")
def pedido_status(pedido_id):
    pedido = query("""
        SELECT p.estado, p.cadete_id,
               u.nombre AS cadete_nombre, u.telefono AS cadete_tel,
               c.vehiculo
        FROM pedidos p
        LEFT JOIN cadetes c ON c.id = p.cadete_id
        LEFT JOIN usuarios u ON u.id = c.usuario_id
        WHERE p.id = ?
    """, (pedido_id,), one=True)
    if not pedido:
        return jsonify({"error": "No encontrado"}), 404
    return jsonify({
        "estado":         pedido["estado"],
        "cadete_nombre":  pedido["cadete_nombre"],
        "cadete_tel":     pedido["cadete_tel"],
        "cadete_vehiculo":pedido["vehiculo"],
    })


# ── RESTAURANTE: HISTORIAL DE PEDIDOS ─────────────────────────────────────────

@app.route("/mi-local/pedidos")
@login_required
@rol_required("restaurante")
def restaurante_pedidos():
    restaurante = get_restaurante_aprobado()
    if not restaurante:
        return redirect(url_for("restaurante_panel"))

    pedidos = query("""
        SELECT p.*,
               u.nombre  AS cliente_nombre,
               u.telefono AS cliente_tel,
               uc.nombre  AS cadete_nombre,
               uc.telefono AS cadete_tel,
               c.vehiculo  AS cadete_vehiculo
        FROM pedidos p
        LEFT JOIN usuarios u  ON u.id  = p.cliente_id
        LEFT JOIN cadetes  c  ON c.id  = p.cadete_id
        LEFT JOIN usuarios uc ON uc.id = c.usuario_id
        WHERE p.restaurante_id = ?
        ORDER BY p.fecha_pedido DESC
        LIMIT 100
    """, (restaurante["id"],))

    # Items por pedido
    items_por_pedido = {}
    if pedidos:
        ids = ",".join(str(p["id"]) for p in pedidos)
        items = query(f"""
            SELECT * FROM items_pedido WHERE pedido_id IN ({ids})
            ORDER BY pedido_id, id
        """)
        for it in items:
            items_por_pedido.setdefault(it["pedido_id"], []).append(it)

    return render_template("restaurante_pedidos.html",
                           restaurante=restaurante,
                           pedidos=pedidos,
                           items_por_pedido=items_por_pedido)


@app.route("/mi-local/pedido/<int:pedido_id>/estado/<nuevo_estado>")
@login_required
@rol_required("restaurante")
def restaurante_cambiar_estado(pedido_id, nuevo_estado):
    restaurante = get_restaurante_aprobado()
    if not restaurante:
        return redirect(url_for("restaurante_panel"))

    estados_validos = ["confirmado", "cancelado"]
    if nuevo_estado not in estados_validos:
        flash("Estado inválido.", "danger")
        return redirect(url_for("restaurante_pedidos"))

    execute("""
        UPDATE pedidos SET estado=?, fecha_actualizado=datetime('now','localtime')
        WHERE id=? AND restaurante_id=?
    """, (nuevo_estado, pedido_id, restaurante["id"]))

    flash(f"Pedido #{pedido_id} marcado como {nuevo_estado}.", "success")
    return redirect(url_for("restaurante_pedidos"))


@app.route("/api/notificar-cadetes/<int:pedido_id>")
@login_required
@rol_required("restaurante")
def notificar_cadetes(pedido_id):
    """Devuelve links WA para notificar a cada cadete disponible."""
    restaurante = get_restaurante_aprobado()
    if not restaurante:
        return jsonify({"error": "No autorizado"}), 403

    pedido = query(
        "SELECT * FROM pedidos WHERE id=? AND restaurante_id=?",
        (pedido_id, restaurante["id"]), one=True
    )
    if not pedido:
        return jsonify({"error": "Pedido no encontrado"}), 404

    cadetes = query("""
        SELECT u.nombre, u.telefono, c.vehiculo, c.zona
        FROM cadetes c
        JOIN usuarios u ON u.id = c.usuario_id
        WHERE c.estado='aprobado' AND c.disponible=1 AND u.telefono IS NOT NULL
    """)

    mensaje = (
        f"🛵 *PediAcá — Pedido disponible!*\n\n"
        f"🏪 Local: {restaurante['nombre_local']}\n"
        f"📍 Retiro: {restaurante['direccion'] or 'A confirmar con el local'}\n"
        f"🗺️ Entrega: {pedido['direccion_entrega'] or 'Retiro en local'}\n"
        f"💰 Total del pedido: ${int(pedido['total'])}\n\n"
        f"Entrá a pediaca.ar para aceptarlo antes que otro cadete."
    )

    links = []
    for c in cadetes:
        if c["telefono"]:
            num  = _limpiar_numero(c["telefono"])
            links.append({
                "nombre":  c["nombre"],
                "vehiculo":c["vehiculo"],
                "link":    _wa_link(num, mensaje)
            })

    return jsonify({"cadetes": links, "pedido_id": pedido_id})


# ── CADETE: ACEPTAR PEDIDO ────────────────────────────────────────────────────

@app.route("/cadete/aceptar/<int:pedido_id>", methods=["POST"])
@login_required
@rol_required("cadete")
def cadete_aceptar_pedido(pedido_id):
    cadete = query(
        "SELECT * FROM cadetes WHERE usuario_id=? AND estado='aprobado'",
        (session["user_id"],), one=True
    )
    if not cadete:
        return jsonify({"error": "No autorizado"}), 403

    # Verificar que no está tomado
    pedido = query(
        "SELECT * FROM pedidos WHERE id=? AND cadete_id IS NULL AND estado='confirmado'",
        (pedido_id,), one=True
    )
    if not pedido:
        return jsonify({"ok": False, "msg": "El pedido ya fue tomado por otro cadete"}), 409

    execute("""
        UPDATE pedidos SET cadete_id=?, estado='en_camino',
               fecha_actualizado=datetime('now','localtime')
        WHERE id=? AND cadete_id IS NULL
    """, (cadete["id"], pedido_id))

    # Verificar que lo grabamos nosotros (race condition)
    check = query("SELECT cadete_id FROM pedidos WHERE id=?", (pedido_id,), one=True)
    if check["cadete_id"] != cadete["id"]:
        return jsonify({"ok": False, "msg": "El pedido ya fue tomado por otro cadete"}), 409

    return jsonify({"ok": True, "msg": "¡Pedido aceptado! Coordiná con el local."})


@app.route("/api/pedidos-nuevos")
@login_required
@rol_required("cadete")
def pedidos_nuevos_cadete():
    """Polling: devuelve pedidos de delivery sin cadete asignado."""
    pedidos = query("""
        SELECT p.id, p.total, p.direccion_entrega, p.fecha_pedido,
               r.nombre_local, r.direccion AS local_direccion, r.whatsapp
        FROM pedidos p
        JOIN restaurantes r ON r.id = p.restaurante_id
        WHERE p.tipo_entrega='delivery'
          AND p.estado='confirmado'
          AND p.cadete_id IS NULL
        ORDER BY p.fecha_pedido DESC
    """)
    return jsonify({"pedidos": [dict(p) for p in pedidos]})


# ── FLYER ─────────────────────────────────────────────────────────────────────

@app.route("/mi-local/flyer")
@login_required
@rol_required("restaurante")
def descargar_flyer():
    from flyer import generar_flyer
    from flask import send_file
    restaurante = get_restaurante_aprobado()
    if not restaurante:
        flash("Tu local debe estar aprobado para descargar el flyer.", "warning")
        return redirect(url_for("restaurante_panel"))

    logo_path = None
    if restaurante["logo_url"]:
        logo_path = os.path.join("static", restaurante["logo_url"])

    png_bytes = generar_flyer(
        nombre_local   = restaurante["nombre_local"],
        restaurante_id = restaurante["id"],
        logo_path      = logo_path,
        categoria      = restaurante["categoria"] or "",
    )

    nombre_archivo = f"flyer_pediaca_{restaurante['nombre_local'].replace(' ','_').lower()}.png"
    return send_file(
        io.BytesIO(png_bytes),
        mimetype="image/png",
        as_attachment=True,
        download_name=nombre_archivo
    )


# ── UPLOAD FOTOS RESTAURANTE ──────────────────────────────────────────────────

@app.route("/mi-local/foto/logo", methods=["POST"])
@login_required
@rol_required("restaurante")
def subir_logo():
    restaurante = get_restaurante_aprobado()
    if not restaurante:
        return redirect(url_for("restaurante_panel"))
    archivo = request.files.get("logo")
    ruta    = guardar_imagen(archivo, "logos")
    if ruta:
        execute("UPDATE restaurantes SET logo_url=? WHERE id=?",
                (ruta, restaurante["id"]))
        flash("Logo actualizado.", "success")
    else:
        flash("Archivo inválido. Usá PNG, JPG o WEBP.", "danger")
    return redirect(url_for("restaurante_panel"))


@app.route("/mi-local/foto/banner", methods=["POST"])
@login_required
@rol_required("restaurante")
def subir_banner():
    restaurante = get_restaurante_aprobado()
    if not restaurante:
        return redirect(url_for("restaurante_panel"))
    archivo = request.files.get("banner")
    ruta    = guardar_imagen(archivo, "banners")
    if ruta:
        execute("UPDATE restaurantes SET banner_url=? WHERE id=?",
                (ruta, restaurante["id"]))
        flash("Banner actualizado.", "success")
    else:
        flash("Archivo inválido. Usá PNG, JPG o WEBP.", "danger")
    return redirect(url_for("restaurante_panel"))


@app.route("/mi-local/producto/<int:prod_id>/foto", methods=["POST"])
@login_required
@rol_required("restaurante")
def subir_foto_producto(prod_id):
    restaurante = get_restaurante_aprobado()
    if not restaurante:
        return redirect(url_for("restaurante_panel"))
    archivo = request.files.get("foto")
    ruta    = guardar_imagen(archivo, "productos")
    if ruta:
        execute("UPDATE productos SET foto_url=? WHERE id=? AND restaurante_id=?",
                (ruta, prod_id, restaurante["id"]))
        flash("Foto del producto actualizada.", "success")
    else:
        flash("Archivo inválido.", "danger")
    return redirect(url_for("restaurante_panel"))


# ── PROMOCIONES ───────────────────────────────────────────────────────────────

@app.route("/mi-local/promociones")
@login_required
@rol_required("restaurante")
def promociones_panel():
    restaurante = get_restaurante_aprobado()
    if not restaurante:
        return redirect(url_for("restaurante_panel"))
    promociones = query("""
        SELECT * FROM promociones
        WHERE restaurante_id = ?
        ORDER BY fecha_creacion DESC
    """, (restaurante["id"],))
    return render_template("promociones.html",
                           restaurante=restaurante,
                           promociones=promociones)


@app.route("/mi-local/promocion/nueva", methods=["POST"])
@login_required
@rol_required("restaurante")
def promocion_nueva():
    restaurante = get_restaurante_aprobado()
    if not restaurante:
        return redirect(url_for("restaurante_panel"))

    titulo        = request.form.get("titulo", "").strip()
    descripcion   = request.form.get("descripcion", "").strip()
    descuento_pct = int(request.form.get("descuento_pct", 0) or 0)
    fecha_inicio  = request.form.get("fecha_inicio") or None
    fecha_fin     = request.form.get("fecha_fin") or None
    archivo       = request.files.get("imagen")
    imagen_url    = guardar_imagen(archivo, "promociones") if archivo else None

    if not titulo:
        flash("El título es obligatorio.", "danger")
        return redirect(url_for("promociones_panel"))

    execute("""
        INSERT INTO promociones
            (restaurante_id, titulo, descripcion, imagen_url, descuento_pct, fecha_inicio, fecha_fin)
        VALUES (?,?,?,?,?,?,?)
    """, (restaurante["id"], titulo, descripcion, imagen_url,
          descuento_pct, fecha_inicio, fecha_fin))
    flash(f"Promoción '{titulo}' creada.", "success")
    return redirect(url_for("promociones_panel"))


@app.route("/mi-local/promocion/<int:promo_id>/toggle")
@login_required
@rol_required("restaurante")
def promocion_toggle(promo_id):
    restaurante = get_restaurante_aprobado()
    if not restaurante:
        return redirect(url_for("restaurante_panel"))
    execute("""
        UPDATE promociones SET activa = 1 - activa
        WHERE id = ? AND restaurante_id = ?
    """, (promo_id, restaurante["id"]))
    return redirect(url_for("promociones_panel"))


@app.route("/mi-local/promocion/<int:promo_id>/eliminar", methods=["POST"])
@login_required
@rol_required("restaurante")
def promocion_eliminar(promo_id):
    restaurante = get_restaurante_aprobado()
    if not restaurante:
        return redirect(url_for("restaurante_panel"))
    execute("DELETE FROM promociones WHERE id=? AND restaurante_id=?",
            (promo_id, restaurante["id"]))
    flash("Promoción eliminada.", "success")
    return redirect(url_for("promociones_panel"))


@app.route("/mi-local/promocion/<int:promo_id>/editar", methods=["POST"])
@login_required
@rol_required("restaurante")
def promocion_editar(promo_id):
    restaurante = get_restaurante_aprobado()
    if not restaurante:
        return redirect(url_for("restaurante_panel"))

    titulo        = request.form.get("titulo", "").strip()
    descripcion   = request.form.get("descripcion", "").strip()
    descuento_pct = int(request.form.get("descuento_pct", 0) or 0)
    fecha_inicio  = request.form.get("fecha_inicio") or None
    fecha_fin     = request.form.get("fecha_fin") or None
    archivo       = request.files.get("imagen")

    promo = query("SELECT * FROM promociones WHERE id=? AND restaurante_id=?",
                  (promo_id, restaurante["id"]), one=True)
    if not promo:
        return redirect(url_for("promociones_panel"))

    nueva_imagen = guardar_imagen(archivo, "promociones") if archivo and archivo.filename else promo["imagen_url"]

    execute("""
        UPDATE promociones SET
            titulo=?, descripcion=?, imagen_url=?,
            descuento_pct=?, fecha_inicio=?, fecha_fin=?
        WHERE id=? AND restaurante_id=?
    """, (titulo, descripcion, nueva_imagen, descuento_pct,
          fecha_inicio, fecha_fin, promo_id, restaurante["id"]))
    flash("Promoción actualizada.", "success")
    return redirect(url_for("promociones_panel"))


# ── PRODUCTO EDITAR ───────────────────────────────────────────────────────────

@app.route("/mi-local/producto/<int:prod_id>/editar", methods=["POST"])
@login_required
@rol_required("restaurante")
def producto_editar(prod_id):
    restaurante = get_restaurante_aprobado()
    if not restaurante:
        return redirect(url_for("restaurante_panel"))

    nombre       = request.form.get("nombre", "").strip()
    descripcion  = request.form.get("descripcion", "").strip()
    precio       = float(request.form.get("precio", 0) or 0)
    categoria_id = request.form.get("categoria_id") or None
    disponible   = 1 if request.form.get("disponible") else 0

    execute("""
        UPDATE productos SET
            nombre=?, descripcion=?, precio=?, categoria_id=?, disponible=?
        WHERE id=? AND restaurante_id=?
    """, (nombre, descripcion, precio, categoria_id, disponible,
          prod_id, restaurante["id"]))
    flash("Producto actualizado.", "success")
    return redirect(url_for("restaurante_panel"))


# ── MAIN ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        print(f"⚠️  No existe '{DB_PATH}'. Ejecutá primero: python init_db.py")
    else:
        app.run(debug=True, port=5000)


# ── PÁGINAS LEGALES ───────────────────────────────────────────────────────────

@app.route("/terminos")
def terminos():
    return render_template("terminos.html")

@app.route("/privacidad")
def privacidad():
    return render_template("privacidad.html")


# ── SETUP INICIAL (uso único para crear admin en producción) ──────────────────

@app.route("/setup/<clave_secreta>")
def setup_admin(clave_secreta):
    CLAVE = os.environ.get("SETUP_KEY", "pediaca2026")
    if clave_secreta != CLAVE:
        return "No autorizado", 403

    admin_existe = query("SELECT id FROM usuarios WHERE rol='admin'", one=True)
    if admin_existe:
        return "Ya existe un administrador. Ruta desactivada.", 200

    from werkzeug.security import generate_password_hash
    password = os.environ.get("ADMIN_PASSWORD", "pediaca2026admin")

    execute("""
        INSERT INTO usuarios (nombre, apellido, email, telefono, password_hash, rol)
        VALUES (?, ?, ?, ?, ?, ?)
    """, ("Cristian", "Ojeda", "admin@pediaca.ar", "3417523674",
          generate_password_hash(password), "admin"))

    return f"""
    <html><head><meta charset="UTF-8"></head>
    <body style="font-family:sans-serif;padding:40px;text-align:center;max-width:500px;margin:0 auto;">
        <h2>✅ Admin creado</h2>
        <p><strong>Email:</strong> admin@pediaca.ar</p>
        <p><strong>Password:</strong> {password}</p>
        <p style="color:#e74c3c;font-weight:bold;margin-top:20px;">
            ⚠️ Anotá la password y cambiala desde tu perfil.
        </p>
        <a href="/login" style="display:inline-block;margin-top:20px;background:#F39C12;color:#fff;padding:14px 32px;border-radius:99px;text-decoration:none;font-weight:800;font-size:1rem;">
            Ir al login →
        </a>
    </body></html>
    """, 200
