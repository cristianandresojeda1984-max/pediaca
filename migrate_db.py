"""
migrate_db.py — Aplica migraciones a la DB existente sin borrar datos.
Se ejecuta en cada deploy desde start.sh.
"""
import sqlite3, os

DB_PATH = os.environ.get("DB_PATH", "pediaca.db")

MIGRACIONES = [
    ("abierto_restaurantes", """
        ALTER TABLE restaurantes ADD COLUMN abierto INTEGER NOT NULL DEFAULT 1
    """),
    ("password_reset_tokens", """
        CREATE TABLE IF NOT EXISTS password_reset_tokens (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL REFERENCES usuarios(id),
            token      TEXT NOT NULL UNIQUE,
            expira     TEXT NOT NULL,
            usado      INTEGER NOT NULL DEFAULT 0
        )
    """),
    ("valoraciones", """
        CREATE TABLE IF NOT EXISTS valoraciones (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            pedido_id      INTEGER NOT NULL UNIQUE REFERENCES pedidos(id),
            restaurante_id INTEGER NOT NULL REFERENCES restaurantes(id),
            cliente_id     INTEGER REFERENCES usuarios(id),
            estrellas      INTEGER NOT NULL CHECK(estrellas BETWEEN 1 AND 5),
            comentario     TEXT,
            fecha          TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """),
    # (nombre, sql)
    ("sabores_producto", """
        CREATE TABLE IF NOT EXISTS sabores_producto (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            producto_id INTEGER NOT NULL REFERENCES productos(id) ON DELETE CASCADE,
            nombre      TEXT NOT NULL,
            disponible  INTEGER NOT NULL DEFAULT 1,
            orden       INTEGER NOT NULL DEFAULT 0
        )
    """),
    ("promociones", """
        CREATE TABLE IF NOT EXISTS promociones (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            restaurante_id  INTEGER NOT NULL REFERENCES restaurantes(id),
            titulo          TEXT NOT NULL,
            descripcion     TEXT,
            imagen_url      TEXT,
            descuento_pct   INTEGER DEFAULT 0,
            activa          INTEGER NOT NULL DEFAULT 1,
            fecha_inicio    TEXT,
            fecha_fin       TEXT,
            fecha_creacion  TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """),
]

def migrar():
    if not os.path.exists(DB_PATH):
        print("DB no existe, se creará con init_db.py")
        return
    conn = sqlite3.connect(DB_PATH)
    for nombre, sql in MIGRACIONES:
        try:
            conn.execute(sql)
            print(f"✅ Migración '{nombre}' aplicada")
        except Exception as e:
            print(f"⚠️  '{nombre}': {e}")
    conn.commit()
    conn.close()

if __name__ == "__main__":
    migrar()
