"""
PediAcá — Inicialización de Base de Datos
Soporta SQLite (local) y PostgreSQL (producción).
"""
import os

DATABASE_URL = os.environ.get("DATABASE_URL", "")
USE_POSTGRES = bool(DATABASE_URL)

def init_postgres():
    import psycopg2
    conn = psycopg2.connect(DATABASE_URL)
    cur  = conn.cursor()

    tablas = [
        """CREATE TABLE IF NOT EXISTS usuarios (
            id              SERIAL PRIMARY KEY,
            nombre          TEXT NOT NULL,
            apellido        TEXT NOT NULL,
            email           TEXT NOT NULL UNIQUE,
            telefono        TEXT,
            password_hash   TEXT NOT NULL,
            rol             TEXT NOT NULL CHECK(rol IN ('cliente','restaurante','cadete','admin')),
            activo          INTEGER NOT NULL DEFAULT 1,
            fecha_registro  TIMESTAMP NOT NULL DEFAULT NOW()
        )""",
        """CREATE TABLE IF NOT EXISTS clientes (
            id                  SERIAL PRIMARY KEY,
            usuario_id          INTEGER NOT NULL UNIQUE REFERENCES usuarios(id),
            direccion_default   TEXT,
            notas_default       TEXT
        )""",
        """CREATE TABLE IF NOT EXISTS restaurantes (
            id              SERIAL PRIMARY KEY,
            usuario_id      INTEGER NOT NULL UNIQUE REFERENCES usuarios(id),
            nombre_local    TEXT NOT NULL,
            descripcion     TEXT,
            categoria       TEXT,
            direccion       TEXT,
            whatsapp        TEXT NOT NULL,
            logo_url        TEXT,
            banner_url      TEXT,
            horario         TEXT,
            hace_envio      INTEGER NOT NULL DEFAULT 0,
            costo_envio     REAL NOT NULL DEFAULT 0,
            tiempo_estimado INTEGER,
            abierto         INTEGER NOT NULL DEFAULT 1,
            estado          TEXT NOT NULL DEFAULT 'pendiente' CHECK(estado IN ('pendiente','aprobado','suspendido')),
            fecha_alta      TIMESTAMP NOT NULL DEFAULT NOW()
        )""",
        """CREATE TABLE IF NOT EXISTS categorias_menu (
            id              SERIAL PRIMARY KEY,
            restaurante_id  INTEGER NOT NULL REFERENCES restaurantes(id),
            nombre          TEXT NOT NULL,
            orden           INTEGER NOT NULL DEFAULT 0
        )""",
        """CREATE TABLE IF NOT EXISTS productos (
            id              SERIAL PRIMARY KEY,
            restaurante_id  INTEGER NOT NULL REFERENCES restaurantes(id),
            categoria_id    INTEGER REFERENCES categorias_menu(id),
            nombre          TEXT NOT NULL,
            descripcion     TEXT,
            precio          REAL NOT NULL,
            foto_url        TEXT,
            disponible      INTEGER NOT NULL DEFAULT 1,
            orden           INTEGER NOT NULL DEFAULT 0
        )""",
        """CREATE TABLE IF NOT EXISTS sabores_producto (
            id          SERIAL PRIMARY KEY,
            producto_id INTEGER NOT NULL REFERENCES productos(id) ON DELETE CASCADE,
            nombre      TEXT NOT NULL,
            disponible  INTEGER NOT NULL DEFAULT 1,
            orden       INTEGER NOT NULL DEFAULT 0
        )""",
        """CREATE TABLE IF NOT EXISTS cadetes (
            id          SERIAL PRIMARY KEY,
            usuario_id  INTEGER NOT NULL UNIQUE REFERENCES usuarios(id),
            vehiculo    TEXT CHECK(vehiculo IN ('moto','bici','auto')),
            zona        TEXT,
            disponible  INTEGER NOT NULL DEFAULT 0,
            estado      TEXT NOT NULL DEFAULT 'pendiente' CHECK(estado IN ('pendiente','aprobado','suspendido'))
        )""",
        """CREATE TABLE IF NOT EXISTS pedidos (
            id                          SERIAL PRIMARY KEY,
            restaurante_id              INTEGER NOT NULL REFERENCES restaurantes(id),
            cliente_id                  INTEGER REFERENCES usuarios(id),
            nombre_cliente_anonimo      TEXT,
            telefono_cliente_anonimo    TEXT,
            cadete_id                   INTEGER REFERENCES cadetes(id),
            tipo_entrega                TEXT NOT NULL DEFAULT 'retiro' CHECK(tipo_entrega IN ('retiro','delivery')),
            direccion_entrega           TEXT,
            estado                      TEXT NOT NULL DEFAULT 'nuevo' CHECK(estado IN ('nuevo','confirmado','en_camino','entregado','cancelado')),
            total                       REAL NOT NULL DEFAULT 0,
            notas                       TEXT,
            enviado_whatsapp            INTEGER NOT NULL DEFAULT 0,
            fecha_pedido                TIMESTAMP NOT NULL DEFAULT NOW(),
            fecha_actualizado           TIMESTAMP NOT NULL DEFAULT NOW()
        )""",
        """CREATE TABLE IF NOT EXISTS items_pedido (
            id              SERIAL PRIMARY KEY,
            pedido_id       INTEGER NOT NULL REFERENCES pedidos(id),
            producto_id     INTEGER REFERENCES productos(id),
            nombre_producto TEXT NOT NULL,
            cantidad        INTEGER NOT NULL DEFAULT 1,
            precio_unitario REAL NOT NULL,
            subtotal        REAL NOT NULL,
            notas           TEXT
        )""",
        """CREATE TABLE IF NOT EXISTS auspiciantes (
            id          SERIAL PRIMARY KEY,
            nombre      TEXT NOT NULL,
            logo_url    TEXT,
            url_destino TEXT,
            activo      INTEGER NOT NULL DEFAULT 1,
            posicion    TEXT DEFAULT 'home' CHECK(posicion IN ('header','home','listado')),
            fecha_inicio DATE,
            fecha_fin    DATE
        )""",
        """CREATE TABLE IF NOT EXISTS push_subscriptions (
            id         SERIAL PRIMARY KEY,
            usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
            endpoint   TEXT NOT NULL UNIQUE,
            p256dh     TEXT NOT NULL,
            auth       TEXT NOT NULL,
            fecha_alta TIMESTAMP NOT NULL DEFAULT NOW()
        )""",
        """CREATE TABLE IF NOT EXISTS promociones (
            id              SERIAL PRIMARY KEY,
            restaurante_id  INTEGER NOT NULL REFERENCES restaurantes(id),
            titulo          TEXT NOT NULL,
            descripcion     TEXT,
            imagen_url      TEXT,
            descuento_pct   INTEGER DEFAULT 0,
            activa          INTEGER NOT NULL DEFAULT 1,
            fecha_inicio    DATE,
            fecha_fin       DATE,
            fecha_creacion  TIMESTAMP NOT NULL DEFAULT NOW()
        )""",
        """CREATE TABLE IF NOT EXISTS valoraciones (
            id             SERIAL PRIMARY KEY,
            pedido_id      INTEGER NOT NULL UNIQUE REFERENCES pedidos(id),
            restaurante_id INTEGER NOT NULL REFERENCES restaurantes(id),
            cliente_id     INTEGER REFERENCES usuarios(id),
            estrellas      INTEGER NOT NULL CHECK(estrellas BETWEEN 1 AND 5),
            comentario     TEXT,
            fecha          TIMESTAMP NOT NULL DEFAULT NOW()
        )""",
        """CREATE TABLE IF NOT EXISTS password_reset_tokens (
            id         SERIAL PRIMARY KEY,
            usuario_id INTEGER NOT NULL REFERENCES usuarios(id),
            token      TEXT NOT NULL UNIQUE,
            expira     TIMESTAMP NOT NULL,
            usado      INTEGER NOT NULL DEFAULT 0
        )""",
    ]

    for sql in tablas:
        cur.execute(sql)
        nombre = sql.split('EXISTS')[1].split('(')[0].strip()
        print(f'✅ {nombre}')

    conn.commit()
    conn.close()
    print('\n✅ PostgreSQL inicializado correctamente')


def init_sqlite():
    import sqlite3
    DB_PATH = os.environ.get("DB_PATH", "pediaca.db")
    if os.path.exists(DB_PATH):
        r = input(f"'{DB_PATH}' ya existe. ¿Recrear? (s/N): ")
        if r.lower() != 's':
            return
        os.remove(DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    # ... (mismo que antes para local)
    conn.commit()
    conn.close()
    print(f'✅ SQLite {DB_PATH} inicializado')


if __name__ == "__main__":
    if USE_POSTGRES:
        print("Inicializando PostgreSQL...")
        init_postgres()
    else:
        print("Inicializando SQLite local...")
        init_sqlite()
