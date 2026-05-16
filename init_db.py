"""
PediAcá — Inicialización de Base de Datos (versión completa)
Ejecutar una sola vez para crear todas las tablas necesarias.
"""

import sqlite3
import os

DB_PATH = "pediaca.db"

def init_db():
    if os.path.exists(DB_PATH):
        respuesta = input(f"La base de datos '{DB_PATH}' ya existe. ¿Recrearla? (s/N): ")
        if respuesta.lower() != "s":
            print("Operación cancelada.")
            return
        os.remove(DB_PATH)
        print("Base de datos anterior eliminada.")

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()

    # ── USUARIOS ──────────────────────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE usuarios (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre          TEXT NOT NULL,
            apellido        TEXT NOT NULL,
            email           TEXT NOT NULL UNIQUE,
            telefono        TEXT,
            password_hash   TEXT NOT NULL,
            rol             TEXT NOT NULL CHECK(rol IN ('cliente','restaurante','cadete','admin')),
            activo          INTEGER NOT NULL DEFAULT 1,
            fecha_registro  TEXT NOT NULL DEFAULT (datetime('now','localtime'))
        )
    """)

    # ── CLIENTES ──────────────────────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE clientes (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id          INTEGER NOT NULL UNIQUE REFERENCES usuarios(id),
            direccion_default   TEXT,
            notas_default       TEXT
        )
    """)

    # ── RESTAURANTES (incluye columna 'abierto') ──────────────────────────────
    cur.execute("""
        CREATE TABLE restaurantes (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
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
            estado          TEXT NOT NULL DEFAULT 'pendiente'
                            CHECK(estado IN ('pendiente','aprobado','suspendido')),
            fecha_alta      TEXT NOT NULL DEFAULT (datetime('now','localtime'))
        )
    """)

    # ── CATEGORIAS DEL MENÚ ───────────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE categorias_menu (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            restaurante_id  INTEGER NOT NULL REFERENCES restaurantes(id),
            nombre          TEXT NOT NULL,
            orden           INTEGER NOT NULL DEFAULT 0
        )
    """)

    # ── PRODUCTOS ─────────────────────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE productos (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            restaurante_id  INTEGER NOT NULL REFERENCES restaurantes(id),
            categoria_id    INTEGER REFERENCES categorias_menu(id),
            nombre          TEXT NOT NULL,
            descripcion     TEXT,
            precio          REAL NOT NULL,
            foto_url        TEXT,
            disponible      INTEGER NOT NULL DEFAULT 1,
            orden           INTEGER NOT NULL DEFAULT 0
        )
    """)

    # ── CADETES ───────────────────────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE cadetes (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id  INTEGER NOT NULL UNIQUE REFERENCES usuarios(id),
            vehiculo    TEXT CHECK(vehiculo IN ('moto','bici','auto')),
            zona        TEXT,
            disponible  INTEGER NOT NULL DEFAULT 0,
            estado      TEXT NOT NULL DEFAULT 'pendiente'
                        CHECK(estado IN ('pendiente','aprobado','suspendido'))
        )
    """)

    # ── PEDIDOS ───────────────────────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE pedidos (
            id                          INTEGER PRIMARY KEY AUTOINCREMENT,
            restaurante_id              INTEGER NOT NULL REFERENCES restaurantes(id),
            cliente_id                  INTEGER REFERENCES usuarios(id),
            nombre_cliente_anonimo      TEXT,
            telefono_cliente_anonimo    TEXT,
            cadete_id                   INTEGER REFERENCES cadetes(id),
            tipo_entrega                TEXT NOT NULL DEFAULT 'retiro'
                                        CHECK(tipo_entrega IN ('retiro','delivery')),
            direccion_entrega           TEXT,
            estado                      TEXT NOT NULL DEFAULT 'nuevo'
                                        CHECK(estado IN ('nuevo','confirmado','en_camino','entregado','cancelado')),
            total                       REAL NOT NULL DEFAULT 0,
            notas                       TEXT,
            enviado_whatsapp            INTEGER NOT NULL DEFAULT 0,
            fecha_pedido                TEXT NOT NULL DEFAULT (datetime('now','localtime')),
            fecha_actualizado           TEXT NOT NULL DEFAULT (datetime('now','localtime'))
        )
    """)

    # ── ITEMS DEL PEDIDO ──────────────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE items_pedido (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            pedido_id       INTEGER NOT NULL REFERENCES pedidos(id),
            producto_id     INTEGER REFERENCES productos(id),
            nombre_producto TEXT NOT NULL,
            cantidad        INTEGER NOT NULL DEFAULT 1,
            precio_unitario REAL NOT NULL,
            subtotal        REAL NOT NULL,
            notas           TEXT
        )
    """)

    # ── AUSPICIANTES ──────────────────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE auspiciantes (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre      TEXT NOT NULL,
            logo_url    TEXT,
            url_destino TEXT,
            activo      INTEGER NOT NULL DEFAULT 1,
            posicion    TEXT DEFAULT 'home'
                        CHECK(posicion IN ('header','home','listado')),
            fecha_inicio TEXT,
            fecha_fin    TEXT
        )
    """)

    # ── SABORES PRODUCTO ──────────────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS sabores_producto (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            producto_id INTEGER NOT NULL REFERENCES productos(id) ON DELETE CASCADE,
            nombre      TEXT NOT NULL,
            disponible  INTEGER NOT NULL DEFAULT 1,
            orden       INTEGER NOT NULL DEFAULT 0
        )
    """)

    # ── PROMOCIONES ───────────────────────────────────────────────────────────
    cur.execute("""
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
    """)

    # ── TOKENS PARA RECUPERAR CONTRASEÑA ──────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS password_reset_tokens (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL REFERENCES usuarios(id),
            token      TEXT NOT NULL UNIQUE,
            expira     TEXT NOT NULL,
            usado      INTEGER NOT NULL DEFAULT 0
        )
    """)

    # ── VALORACIONES DE CLIENTES ──────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS valoraciones (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            pedido_id      INTEGER NOT NULL UNIQUE REFERENCES pedidos(id),
            restaurante_id INTEGER NOT NULL REFERENCES restaurantes(id),
            cliente_id     INTEGER REFERENCES usuarios(id),
            estrellas      INTEGER NOT NULL CHECK(estrellas BETWEEN 1 AND 5),
            comentario     TEXT,
            fecha          TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ── SUSCRIPCIONES A NOTIFICACIONES PUSH ───────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS push_subscriptions (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id  INTEGER NOT NULL REFERENCES usuarios(id),
            endpoint    TEXT NOT NULL UNIQUE,
            p256dh      TEXT NOT NULL,
            auth        TEXT NOT NULL,
            fecha_creacion TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
    print(f"✅ Base de datos '{DB_PATH}' creada con todas las tablas.")
    print("\nTablas creadas:")
    tablas = [
        "  • usuarios", "  • clientes", "  • restaurantes (con columna 'abierto')",
        "  • categorias_menu", "  • productos", "  • cadetes",
        "  • pedidos", "  • items_pedido", "  • auspiciantes",
        "  • sabores_producto", "  • promociones", "  • password_reset_tokens",
        "  • valoraciones", "  • push_subscriptions"
    ]
    for t in tablas:
        print(t)

if __name__ == "__main__":
    init_db()