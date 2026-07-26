"""
PediAcá — Inicialización de Base de Datos
Soporta SQLite (local) y PostgreSQL (producción).

El esquema vive en un solo lugar (_tablas_sql) para evitar que las dos bases
de datos se desincronicen entre sí, algo que ya pasó antes (funciones de
fecha, tipos de columna, etc. que sólo existían en un motor).
"""
import os

DATABASE_URL = os.environ.get("DATABASE_URL", "")
USE_POSTGRES = bool(DATABASE_URL)


def _tablas_sql(postgres):
    """Devuelve la lista de sentencias CREATE TABLE, adaptadas al motor."""
    id_col = "SERIAL PRIMARY KEY" if postgres else "INTEGER PRIMARY KEY AUTOINCREMENT"
    ts_now = "NOW()" if postgres else "CURRENT_TIMESTAMP"

    return [
        f"""CREATE TABLE IF NOT EXISTS usuarios (
            id              {id_col},
            nombre          TEXT NOT NULL,
            apellido        TEXT NOT NULL,
            email           TEXT NOT NULL UNIQUE,
            telefono        TEXT,
            password_hash   TEXT NOT NULL,
            rol             TEXT NOT NULL CHECK(rol IN ('cliente','restaurante','cadete','admin')),
            activo          INTEGER NOT NULL DEFAULT 1,
            fecha_registro  TIMESTAMP NOT NULL DEFAULT {ts_now}
        )""",
        """CREATE TABLE IF NOT EXISTS clientes (
            id                  {id_col},
            usuario_id          INTEGER NOT NULL UNIQUE REFERENCES usuarios(id),
            direccion_default   TEXT,
            notas_default       TEXT
        )""".replace("{id_col}", id_col),
        f"""CREATE TABLE IF NOT EXISTS restaurantes (
            id              {id_col},
            usuario_id      INTEGER NOT NULL UNIQUE REFERENCES usuarios(id),
            nombre_local    TEXT NOT NULL,
            descripcion     TEXT,
            categoria       TEXT,
            ciudad          TEXT NOT NULL DEFAULT 'Rosario',
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
            fecha_alta      TIMESTAMP NOT NULL DEFAULT {ts_now}
        )""",
        f"""CREATE TABLE IF NOT EXISTS categorias_menu (
            id              {id_col},
            restaurante_id  INTEGER NOT NULL REFERENCES restaurantes(id),
            nombre          TEXT NOT NULL,
            orden           INTEGER NOT NULL DEFAULT 0
        )""",
        f"""CREATE TABLE IF NOT EXISTS productos (
            id              {id_col},
            restaurante_id  INTEGER NOT NULL REFERENCES restaurantes(id),
            categoria_id    INTEGER REFERENCES categorias_menu(id),
            nombre          TEXT NOT NULL,
            descripcion     TEXT,
            precio          REAL NOT NULL,
            foto_url        TEXT,
            disponible      INTEGER NOT NULL DEFAULT 1,
            orden           INTEGER NOT NULL DEFAULT 0,
            sabores_por_kilo INTEGER
        )""",
        f"""CREATE TABLE IF NOT EXISTS sabores_producto (
            id          {id_col},
            producto_id INTEGER NOT NULL REFERENCES productos(id) ON DELETE CASCADE,
            nombre      TEXT NOT NULL,
            disponible  INTEGER NOT NULL DEFAULT 1,
            orden       INTEGER NOT NULL DEFAULT 0
        )""",
        f"""CREATE TABLE IF NOT EXISTS cadetes (
            id          {id_col},
            usuario_id  INTEGER NOT NULL UNIQUE REFERENCES usuarios(id),
            vehiculo    TEXT CHECK(vehiculo IN ('moto','bici','auto')),
            zona        TEXT,
            ciudad      TEXT NOT NULL DEFAULT 'Rosario',
            disponible  INTEGER NOT NULL DEFAULT 0,
            estado      TEXT NOT NULL DEFAULT 'pendiente' CHECK(estado IN ('pendiente','aprobado','suspendido'))
        )""",
        f"""CREATE TABLE IF NOT EXISTS pedidos (
            id                          {id_col},
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
            fecha_pedido                TIMESTAMP NOT NULL DEFAULT {ts_now},
            fecha_actualizado           TIMESTAMP NOT NULL DEFAULT {ts_now}
        )""",
        f"""CREATE TABLE IF NOT EXISTS items_pedido (
            id              {id_col},
            pedido_id       INTEGER NOT NULL REFERENCES pedidos(id),
            producto_id     INTEGER REFERENCES productos(id),
            nombre_producto TEXT NOT NULL,
            cantidad        INTEGER NOT NULL DEFAULT 1,
            precio_unitario REAL NOT NULL,
            subtotal        REAL NOT NULL,
            notas           TEXT,
            peso_kg         REAL
        )""",
        f"""CREATE TABLE IF NOT EXISTS auspiciantes (
            id          {id_col},
            nombre      TEXT NOT NULL,
            logo_url    TEXT,
            url_destino TEXT,
            activo      INTEGER NOT NULL DEFAULT 1,
            posicion    TEXT DEFAULT 'home' CHECK(posicion IN ('header','home','listado')),
            fecha_inicio DATE,
            fecha_fin    DATE
        )""",
        f"""CREATE TABLE IF NOT EXISTS push_subscriptions (
            id         {id_col},
            usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
            endpoint   TEXT NOT NULL UNIQUE,
            p256dh     TEXT NOT NULL,
            auth       TEXT NOT NULL,
            fecha_alta TIMESTAMP NOT NULL DEFAULT {ts_now}
        )""",
        f"""CREATE TABLE IF NOT EXISTS promociones (
            id              {id_col},
            restaurante_id  INTEGER NOT NULL REFERENCES restaurantes(id),
            producto_id     INTEGER REFERENCES productos(id),
            titulo          TEXT NOT NULL,
            descripcion     TEXT,
            imagen_url      TEXT,
            tipo_descuento  TEXT DEFAULT 'porcentaje',
            descuento_pct   INTEGER DEFAULT 0,
            descuento_monto REAL DEFAULT 0,
            precio_con_descuento REAL,
            activa          INTEGER NOT NULL DEFAULT 1,
            fecha_inicio    DATE,
            fecha_fin       DATE,
            fecha_creacion  TIMESTAMP NOT NULL DEFAULT {ts_now}
        )""",
        f"""CREATE TABLE IF NOT EXISTS valoraciones (
            id             {id_col},
            pedido_id      INTEGER NOT NULL UNIQUE REFERENCES pedidos(id),
            restaurante_id INTEGER NOT NULL REFERENCES restaurantes(id),
            cliente_id     INTEGER REFERENCES usuarios(id),
            estrellas      INTEGER NOT NULL CHECK(estrellas BETWEEN 1 AND 5),
            comentario     TEXT,
            vista          INTEGER NOT NULL DEFAULT 0,
            fecha          TIMESTAMP NOT NULL DEFAULT {ts_now}
        )""",
        f"""CREATE TABLE IF NOT EXISTS password_reset_tokens (
            id         {id_col},
            usuario_id INTEGER NOT NULL REFERENCES usuarios(id),
            token      TEXT NOT NULL UNIQUE,
            expira     TIMESTAMP NOT NULL,
            usado      INTEGER NOT NULL DEFAULT 0
        )""",
        f"""CREATE TABLE IF NOT EXISTS favoritos (
            id             {id_col},
            usuario_id     INTEGER NOT NULL REFERENCES usuarios(id),
            restaurante_id INTEGER NOT NULL REFERENCES restaurantes(id),
            fecha          TIMESTAMP NOT NULL DEFAULT {ts_now},
            UNIQUE(usuario_id, restaurante_id)
        )""",
        f"""CREATE TABLE IF NOT EXISTS configuraciones (
            id          {id_col},
            clave       TEXT UNIQUE,
            valor       TEXT,
            tipo        TEXT DEFAULT 'text',
            actualizado TIMESTAMP DEFAULT {ts_now if postgres else 'CURRENT_TIMESTAMP'}
        )""",
    ]


def init_postgres():
    import psycopg2
    conn = psycopg2.connect(DATABASE_URL)
    cur  = conn.cursor()

    for sql in _tablas_sql(postgres=True):
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

    for sql in _tablas_sql(postgres=False):
        conn.execute(sql)
        nombre = sql.split('EXISTS')[1].split('(')[0].strip()
        print(f'✅ {nombre}')

    conn.commit()
    conn.close()
    print(f'\n✅ SQLite {DB_PATH} inicializado correctamente')


if __name__ == "__main__":
    if USE_POSTGRES:
        print("Inicializando PostgreSQL...")
        init_postgres()
    else:
        print("Inicializando SQLite local...")
        init_sqlite()
