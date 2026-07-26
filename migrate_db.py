"""
migrate_db.py — Agrega columnas nuevas a tablas que ya existen, sin borrar
datos. Complementa a init_db.py (que sólo crea tablas si no existen, y por
lo tanto nunca agrega columnas a una tabla que un deploy anterior ya creó).

Soporta SQLite (local) y PostgreSQL (producción) y se ejecuta en cada
deploy desde start.sh, después de init_db.py.
"""
import os

DATABASE_URL = os.environ.get("DATABASE_URL", "")
USE_POSTGRES = bool(DATABASE_URL)

# (tabla, columna, definición de tipo/default — sin "ADD COLUMN")
COLUMNAS = [
    ("restaurantes", "abierto",              "INTEGER NOT NULL DEFAULT 1"),
    ("restaurantes", "ciudad",               "TEXT NOT NULL DEFAULT 'Rosario'"),
    ("promociones",  "producto_id",          "INTEGER REFERENCES productos(id)"),
    ("promociones",  "tipo_descuento",       "TEXT DEFAULT 'porcentaje'"),
    ("promociones",  "descuento_monto",      "REAL DEFAULT 0"),
    ("promociones",  "precio_con_descuento", "REAL"),
    ("cadetes",      "ciudad",               "TEXT NOT NULL DEFAULT 'Rosario'"),
    ("valoraciones", "vista",                "INTEGER NOT NULL DEFAULT 0"),
    ("productos",    "sabores_por_kilo",     "INTEGER"),
    ("items_pedido", "peso_kg",              "REAL"),
]


def migrar_postgres():
    import psycopg2
    conn = psycopg2.connect(DATABASE_URL)
    cur  = conn.cursor()
    for tabla, columna, tipo in COLUMNAS:
        try:
            cur.execute(f"ALTER TABLE {tabla} ADD COLUMN IF NOT EXISTS {columna} {tipo}")
            conn.commit()
            print(f"✅ {tabla}.{columna} verificada/agregada")
        except Exception as e:
            conn.rollback()
            print(f"⚠️  {tabla}.{columna}: {e}")
    conn.close()


def migrar_sqlite():
    import sqlite3
    DB_PATH = os.environ.get("DB_PATH", "pediaca.db")
    if not os.path.exists(DB_PATH):
        print("DB no existe todavía, se creará con init_db.py")
        return
    conn = sqlite3.connect(DB_PATH)
    for tabla, columna, tipo in COLUMNAS:
        try:
            existentes = {row[1] for row in conn.execute(f"PRAGMA table_info({tabla})")}
            if columna in existentes:
                continue
            conn.execute(f"ALTER TABLE {tabla} ADD COLUMN {columna} {tipo}")
            conn.commit()
            print(f"✅ {tabla}.{columna} agregada")
        except Exception as e:
            print(f"⚠️  {tabla}.{columna}: {e}")
    conn.close()


def migrar():
    if USE_POSTGRES:
        migrar_postgres()
    else:
        migrar_sqlite()


if __name__ == "__main__":
    migrar()
