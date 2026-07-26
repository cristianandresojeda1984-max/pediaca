"""
insertar_datos_prueba.py
Carga 6 restaurantes "de vidriera" con menús, fotos, promociones y algunas
valoraciones, más 3 cadetes — para ver cómo queda la app con datos reales.

Las fotos son de stock (Unsplash), sólo para la demo local. Cuando un local
sea real, cada dueño sube sus propias fotos desde su panel (Mi local → Fotos).

Se puede correr las veces que quieras: si un email de prueba ya existe, borra
esos datos de prueba antes de recrearlos (no toca cuentas reales).

Contraseña para todos los usuarios de prueba: 123456
Teléfono para todos: 3417523674
"""

import sqlite3
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

DB_PATH  = "pediaca.db"
PASSWORD = "123456"
TELEFONO = "3417523674"

# ── FOTOS DE STOCK (Unsplash) ────────────────────────────────────────────────
IMG = lambda pid, w=800, q=70: f"https://images.unsplash.com/{pid}?auto=format&fit=crop&w={w}&q={q}"

FOTO_PIZZA    = IMG("photo-1513104890138-7c749659a591")
FOTO_BURGER   = IMG("photo-1568901346375-23c9450c58cd")
FOTO_SUSHI    = IMG("photo-1553621042-f6e147245754")
FOTO_HELADO   = IMG("photo-1501443762994-82bd5dace89a")
FOTO_ASADO    = IMG("photo-1529193591184-b1d58069ecdd")
FOTO_VEGGIE   = IMG("photo-1512621776951-a57141f2eefd")

TODOS_LOS_EMAILS_DEMO = [
    "pizzeria@demo.pediaca.ar", "burger@demo.pediaca.ar", "sushi@demo.pediaca.ar",
    "heladeria@demo.pediaca.ar", "parrilla@demo.pediaca.ar", "veggie@demo.pediaca.ar",
    "cliente@demo.pediaca.ar",
    "cadete1@demo.pediaca.ar", "cadete2@demo.pediaca.ar", "cadete3@demo.pediaca.ar",
]

RESTAURANTES = [
    {
        "nombre": "Pizzería La Esquina",
        "email": "pizzeria@demo.pediaca.ar",
        "categoria": "Pizzería",
        "direccion": "Av. Pellegrini 1234, Rosario",
        "descripcion": "Pizza a la piedra, receta de familia desde 1985.",
        "horario": "Lun a Dom 12:00 a 23:00",
        "hace_envio": 1, "costo_envio": 0, "tiempo_estimado": 40,
        "logo": FOTO_PIZZA, "banner": FOTO_PIZZA,
        "productos": [
            {"nombre": "Muzzarella", "descripcion": "Salsa, muzzarella, orégano y aceitunas", "precio": 4500, "categoria": "Pizzas", "foto": FOTO_PIZZA},
            {"nombre": "Napolitana", "descripcion": "Salsa, muzzarella, tomate, ajo y perejil", "precio": 5000, "categoria": "Pizzas"},
            {"nombre": "Fugazzeta rellena", "descripcion": "Doble muzzarella, cebolla caramelizada", "precio": 5800, "categoria": "Pizzas"},
            {"nombre": "Calzone", "descripcion": "Jamón, muzzarella y salsa", "precio": 4800, "categoria": "Pizzas"},
            {"nombre": "Coca-Cola 500ml", "descripcion": "", "precio": 1200, "categoria": "Bebidas"},
            {"nombre": "Agua sin gas 500ml", "descripcion": "", "precio": 800, "categoria": "Bebidas"},
        ],
        "promo": {"titulo": "-15% OFF Muzzarella", "descripcion": "Todos los lunes y martes", "tipo_descuento": "porcentaje", "descuento_pct": 15, "producto": "Muzzarella"},
    },
    {
        "nombre": "Burger Rebels",
        "email": "burger@demo.pediaca.ar",
        "categoria": "Hamburguesería",
        "direccion": "San Martín 2345, Rosario",
        "descripcion": "Smash burgers con pan de papa artesanal.",
        "horario": "Lun a Sáb 19:00 a 00:30",
        "hace_envio": 1, "costo_envio": 500, "tiempo_estimado": 35,
        "logo": FOTO_BURGER, "banner": FOTO_BURGER,
        "productos": [
            {"nombre": "Smash Simple", "descripcion": "Pan de papa, carne smash, cheddar, salsa rebel", "precio": 4200, "categoria": "Hamburguesas", "foto": FOTO_BURGER},
            {"nombre": "Smash Doble", "descripcion": "Doble carne, doble cheddar, panceta", "precio": 5800, "categoria": "Hamburguesas"},
            {"nombre": "Bacon BBQ", "descripcion": "Carne, panceta crocante, cebolla crispy, BBQ", "precio": 6200, "categoria": "Hamburguesas"},
            {"nombre": "Papas rústicas", "descripcion": "Con cheddar y panceta", "precio": 2200, "categoria": "Acompañamientos"},
            {"nombre": "Papas clásicas", "descripcion": "", "precio": 1500, "categoria": "Acompañamientos"},
            {"nombre": "Cerveza IPA 500ml", "descripcion": "", "precio": 1800, "categoria": "Bebidas"},
        ],
        "promo": {"titulo": "$500 OFF en tu pedido", "descripcion": "Válido de martes a jueves", "tipo_descuento": "monto", "descuento_monto": 500},
    },
    {
        "nombre": "Sushi Fresh",
        "email": "sushi@demo.pediaca.ar",
        "categoria": "Sushi",
        "direccion": "Rioja 3456, Rosario",
        "descripcion": "Sushi fresco preparado al momento.",
        "horario": "Mar a Dom 19:30 a 23:30",
        "hace_envio": 1, "costo_envio": 800, "tiempo_estimado": 50,
        "logo": FOTO_SUSHI, "banner": FOTO_SUSHI,
        "productos": [
            {"nombre": "California Roll (8pz)", "descripcion": "Palta, pepino, kanikama", "precio": 3200, "categoria": "Rolls", "foto": FOTO_SUSHI},
            {"nombre": "Philadelphia Roll (8pz)", "descripcion": "Salmón, queso philadelphia", "precio": 3900, "categoria": "Rolls"},
            {"nombre": "Rainbow Roll (8pz)", "descripcion": "Salmón, atún, palta por fuera", "precio": 4500, "categoria": "Rolls"},
            {"nombre": "Sushi Mix (18pz)", "descripcion": "Selección variada de rolls y nigiris", "precio": 7800, "categoria": "Combos"},
            {"nombre": "Ginger Ale 350ml", "descripcion": "", "precio": 900, "categoria": "Bebidas"},
        ],
        "promo": None,
    },
    {
        "nombre": "Heladería Polo Norte",
        "email": "heladeria@demo.pediaca.ar",
        "categoria": "Heladería",
        "direccion": "Córdoba 1890, Rosario",
        "descripcion": "Helado artesanal, todos los días recién hecho.",
        "horario": "Todos los días 14:00 a 00:00",
        "hace_envio": 1, "costo_envio": 0, "tiempo_estimado": 30,
        "logo": FOTO_HELADO, "banner": FOTO_HELADO,
        "productos": [
            {"nombre": "Pote 1/4 kg", "descripcion": "2 gustos a elección", "precio": 3200, "categoria": "Potes", "foto": FOTO_HELADO},
            {"nombre": "Pote 1/2 kg", "descripcion": "3 gustos a elección", "precio": 5600, "categoria": "Potes"},
            {"nombre": "Pote 1 kg", "descripcion": "4 gustos a elección", "precio": 9800, "categoria": "Potes"},
            {"nombre": "Cucurucho simple", "descripcion": "1 gusto", "precio": 1800, "categoria": "Cucuruchos"},
        ],
        "promo": {"titulo": "-20% OFF Pote 1/2 kg", "descripcion": "Válido de lunes a jueves", "tipo_descuento": "porcentaje", "descuento_pct": 20, "producto": "Pote 1/2 kg"},
    },
    {
        "nombre": "Parrilla Don Julio",
        "email": "parrilla@demo.pediaca.ar",
        "categoria": "Rotisería",
        "direccion": "Alberdi 456, Rosario",
        "descripcion": "Asado y achuras a la parrilla, para comer en casa.",
        "horario": "Mié a Dom 12:00 a 15:30 y 20:00 a 23:30",
        "hace_envio": 1, "costo_envio": 700, "tiempo_estimado": 45,
        "logo": FOTO_ASADO, "banner": FOTO_ASADO,
        "productos": [
            {"nombre": "Parrillada para 2", "descripcion": "Vacío, chorizo, morcilla, provoleta", "precio": 12500, "categoria": "Parrilladas", "foto": FOTO_ASADO},
            {"nombre": "Bife de chorizo", "descripcion": "Con guarnición a elección", "precio": 7800, "categoria": "Cortes"},
            {"nombre": "Pollo al spiedo", "descripcion": "Medio pollo con papas", "precio": 5200, "categoria": "Cortes"},
            {"nombre": "Ensalada mixta", "descripcion": "Lechuga, tomate, cebolla", "precio": 1800, "categoria": "Acompañamientos"},
        ],
        "promo": None,
    },
    {
        "nombre": "Verde Vida Vegano",
        "email": "veggie@demo.pediaca.ar",
        "categoria": "Vegano",
        "direccion": "Mendoza 2100, Rosario",
        "descripcion": "Cocina 100% plant-based, rica y de verdad.",
        "horario": "Lun a Sáb 11:30 a 15:00 y 19:00 a 22:30",
        "hace_envio": 1, "costo_envio": 600, "tiempo_estimado": 35,
        "logo": FOTO_VEGGIE, "banner": FOTO_VEGGIE,
        "productos": [
            {"nombre": "Bowl energía", "descripcion": "Quinoa, garbanzos, palta, vegetales grillados", "precio": 4200, "categoria": "Bowls", "foto": FOTO_VEGGIE},
            {"nombre": "Burger de lentejas", "descripcion": "Con pan integral y papas", "precio": 4600, "categoria": "Platos"},
            {"nombre": "Milanesa de soja", "descripcion": "Con puré y ensalada", "precio": 4400, "categoria": "Platos"},
            {"nombre": "Limonada natural", "descripcion": "Jarra 1L", "precio": 1600, "categoria": "Bebidas"},
        ],
        "promo": {"titulo": "-10% OFF en tu pedido", "descripcion": "Por tiempo limitado", "tipo_descuento": "porcentaje", "descuento_pct": 10},
    },
]

CADETES = [
    {"nombre": "Carlos", "apellido": "Pérez", "email": "cadete1@demo.pediaca.ar", "vehiculo": "moto", "zona": "Centro"},
    {"nombre": "Lucía",  "apellido": "Gómez", "email": "cadete2@demo.pediaca.ar", "vehiculo": "bici", "zona": "Pichincha"},
    {"nombre": "Javier", "apellido": "López", "email": "cadete3@demo.pediaca.ar", "vehiculo": "auto", "zona": "Fisherton"},
]

RESEÑAS = [
    (5, "Excelente, llegó rápido y estaba todo perfecto."),
    (5, "Como siempre, buenísimo. Recomendado."),
    (4, "Muy bueno, tardó un poco más de lo esperado."),
    (5, "Diez puntos, ideal para pedir con amigos."),
]


def limpiar_datos_previos(cur):
    emails = TODOS_LOS_EMAILS_DEMO
    placeholders = ",".join("?" * len(emails))
    usuario_ids = [r[0] for r in cur.execute(
        f"SELECT id FROM usuarios WHERE email IN ({placeholders})", emails).fetchall()]
    if not usuario_ids:
        return
    ph2 = ",".join("?" * len(usuario_ids))
    restaurante_ids = [r[0] for r in cur.execute(
        f"SELECT id FROM restaurantes WHERE usuario_id IN ({ph2})", usuario_ids).fetchall()]
    if restaurante_ids:
        ph3 = ",".join("?" * len(restaurante_ids))
        pedido_ids = [r[0] for r in cur.execute(
            f"SELECT id FROM pedidos WHERE restaurante_id IN ({ph3})", restaurante_ids).fetchall()]
        if pedido_ids:
            ph4 = ",".join("?" * len(pedido_ids))
            cur.execute(f"DELETE FROM valoraciones WHERE pedido_id IN ({ph4})", pedido_ids)
            cur.execute(f"DELETE FROM items_pedido WHERE pedido_id IN ({ph4})", pedido_ids)
            cur.execute(f"DELETE FROM pedidos WHERE id IN ({ph4})", pedido_ids)
        cur.execute(f"DELETE FROM promociones WHERE restaurante_id IN ({ph3})", restaurante_ids)
        cur.execute(f"DELETE FROM productos WHERE restaurante_id IN ({ph3})", restaurante_ids)
        cur.execute(f"DELETE FROM categorias_menu WHERE restaurante_id IN ({ph3})", restaurante_ids)
        cur.execute(f"DELETE FROM restaurantes WHERE id IN ({ph3})", restaurante_ids)
    cur.execute(f"DELETE FROM cadetes WHERE usuario_id IN ({ph2})", usuario_ids)
    cur.execute(f"DELETE FROM clientes WHERE usuario_id IN ({ph2})", usuario_ids)
    cur.execute(f"DELETE FROM usuarios WHERE id IN ({ph2})", usuario_ids)


def insertar_datos():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()

    print("🧹 Limpiando datos de prueba anteriores (si había)...")
    limpiar_datos_previos(cur)
    conn.commit()

    # ---------- CLIENTE DEMO (para dejar valoraciones) ----------
    cur.execute("""
        INSERT INTO usuarios (nombre, apellido, email, telefono, password_hash, rol)
        VALUES (?, ?, ?, ?, ?, 'cliente')
    """, ("Sofía", "Demo", "cliente@demo.pediaca.ar", TELEFONO, generate_password_hash(PASSWORD)))
    cliente_id = cur.lastrowid
    cur.execute("INSERT INTO clientes (usuario_id) VALUES (?)", (cliente_id,))

    # ---------- RESTAURANTES ----------
    for i, r in enumerate(RESTAURANTES):
        cur.execute("""
            INSERT INTO usuarios (nombre, apellido, email, telefono, password_hash, rol)
            VALUES (?, ?, ?, ?, ?, 'restaurante')
        """, (r["nombre"], "Dueño/a", r["email"], TELEFONO, generate_password_hash(PASSWORD)))
        user_id = cur.lastrowid

        cur.execute("""
            INSERT INTO restaurantes
                (usuario_id, nombre_local, descripcion, categoria, direccion, whatsapp,
                 logo_url, banner_url, horario, hace_envio, costo_envio, tiempo_estimado,
                 ciudad, estado, abierto)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'aprobado', 1)
        """, (user_id, r["nombre"], r["descripcion"], r["categoria"], r["direccion"], TELEFONO,
              r["logo"], r["banner"], r["horario"], r["hace_envio"], r["costo_envio"], r["tiempo_estimado"],
              "Rosario"))
        restaurante_id = cur.lastrowid

        categorias_creadas = {}
        productos_ids = []
        productos_por_nombre = {}
        for prod in r["productos"]:
            cat_nombre = prod["categoria"]
            if cat_nombre not in categorias_creadas:
                cur.execute("""
                    INSERT INTO categorias_menu (restaurante_id, nombre, orden)
                    VALUES (?, ?, (SELECT COALESCE(MAX(orden),0)+1 FROM categorias_menu WHERE restaurante_id=?))
                """, (restaurante_id, cat_nombre, restaurante_id))
                categorias_creadas[cat_nombre] = cur.lastrowid
            cat_id = categorias_creadas[cat_nombre]

            cur.execute("""
                INSERT INTO productos (restaurante_id, categoria_id, nombre, descripcion, precio, foto_url, disponible)
                VALUES (?, ?, ?, ?, ?, ?, 1)
            """, (restaurante_id, cat_id, prod["nombre"], prod["descripcion"], prod["precio"], prod.get("foto")))
            prod_id = cur.lastrowid
            productos_ids.append(prod_id)
            productos_por_nombre[prod["nombre"]] = prod_id

        promo = r.get("promo")
        if promo:
            tipo = promo["tipo_descuento"]
            promo_producto_id = productos_por_nombre.get(promo.get("producto"))
            cur.execute("""
                INSERT INTO promociones
                    (restaurante_id, titulo, descripcion, tipo_descuento, descuento_pct, descuento_monto, producto_id, activa)
                VALUES (?, ?, ?, ?, ?, ?, ?, 1)
            """, (restaurante_id, promo["titulo"], promo["descripcion"], tipo,
                  promo.get("descuento_pct", 0), promo.get("descuento_monto", 0), promo_producto_id))

        # 2-3 pedidos entregados con valoración, para que tenga rating y "pedidos" visibles
        n_reseñas = 2 + (i % 3)
        for j in range(n_reseñas):
            prod = r["productos"][j % len(r["productos"])]
            total = prod["precio"]
            fecha = (datetime.now() - timedelta(days=j + 1)).strftime("%Y-%m-%d %H:%M:%S")
            cur.execute("""
                INSERT INTO pedidos
                    (restaurante_id, cliente_id, tipo_entrega, estado, total,
                     enviado_whatsapp, fecha_pedido, fecha_actualizado)
                VALUES (?, ?, 'retiro', 'entregado', ?, 1, ?, ?)
            """, (restaurante_id, cliente_id, total, fecha, fecha))
            pedido_id = cur.lastrowid
            cur.execute("""
                INSERT INTO items_pedido (pedido_id, producto_id, nombre_producto, cantidad, precio_unitario, subtotal)
                VALUES (?, ?, ?, 1, ?, ?)
            """, (pedido_id, productos_ids[j % len(productos_ids)], prod["nombre"], prod["precio"], prod["precio"]))
            estrellas, comentario = RESEÑAS[(i + j) % len(RESEÑAS)]
            cur.execute("""
                INSERT INTO valoraciones (pedido_id, restaurante_id, cliente_id, estrellas, comentario, fecha)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (pedido_id, restaurante_id, cliente_id, estrellas, comentario, fecha))

        print(f"✅ {r['nombre']} — {len(r['productos'])} productos, {n_reseñas} reseñas")

    # ---------- CADETES ----------
    for c in CADETES:
        cur.execute("""
            INSERT INTO usuarios (nombre, apellido, email, telefono, password_hash, rol)
            VALUES (?, ?, ?, ?, ?, 'cadete')
        """, (c["nombre"], c["apellido"], c["email"], TELEFONO, generate_password_hash(PASSWORD)))
        user_id = cur.lastrowid
        cur.execute("""
            INSERT INTO cadetes (usuario_id, vehiculo, zona, disponible, estado)
            VALUES (?, ?, ?, 1, 'aprobado')
        """, (user_id, c["vehiculo"], c["zona"]))
        print(f"✅ Cadete {c['nombre']} {c['apellido']}")

    conn.commit()
    conn.close()

    print("\n🎉 Listo — entrá a http://127.0.0.1:5000 para verlo.")
    print(f"\nTodos los usuarios de prueba usan la contraseña: {PASSWORD}")
    print("Locales:")
    for r in RESTAURANTES:
        print(f"  {r['nombre']:<24} {r['email']}")
    print("Cliente (para ver reseñas hechas):", "cliente@demo.pediaca.ar")
    print("Cadetes:")
    for c in CADETES:
        print(f"  {c['nombre']} {c['apellido']:<10} {c['email']}")


if __name__ == "__main__":
    insertar_datos()
