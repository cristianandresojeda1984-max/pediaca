"""
insertar_datos_demo.py
Carga 6 restaurantes "de vidriera" con menus, fotos, promociones y algunas
valoraciones, mas 3 cadetes -- para mostrar la app funcionando con datos
de ejemplo. Se puede borrar todo despues desde el panel de administrador
(o volviendo a correr este script, que limpia y recrea los mismos datos
de prueba sin tocar cuentas reales).

A diferencia de insertar_datos_prueba.py (que usa sqlite3 directo, solo
sirve en local), este script usa las mismas funciones query()/execute()
de app.py, que ya saben hablar tanto SQLite como PostgreSQL segun la
variable de entorno DATABASE_URL. Por eso funciona igual en la compu
que en el servidor de produccion.

Contrasena para todos los usuarios de prueba: 123456
Telefono para todos: 3417523674
"""

from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

from app import app, query, execute

PASSWORD = "123456"
TELEFONO = "3417523674"

IMG = lambda pid, w=800, q=70: f"https://images.unsplash.com/{pid}?auto=format&fit=crop&w={w}&q={q}"

FOTO_PIZZA  = IMG("photo-1513104890138-7c749659a591")
FOTO_BURGER = IMG("photo-1568901346375-23c9450c58cd")
FOTO_SUSHI  = IMG("photo-1553621042-f6e147245754")
FOTO_HELADO = IMG("photo-1501443762994-82bd5dace89a")
FOTO_ASADO  = IMG("photo-1529193591184-b1d58069ecdd")
FOTO_VEGGIE = IMG("photo-1512621776951-a57141f2eefd")

TODOS_LOS_EMAILS_DEMO = [
    "pizzeria@demo.pediaca.ar", "burger@demo.pediaca.ar", "sushi@demo.pediaca.ar",
    "heladeria@demo.pediaca.ar", "parrilla@demo.pediaca.ar", "veggie@demo.pediaca.ar",
    "cliente@demo.pediaca.ar",
    "cadete1@demo.pediaca.ar", "cadete2@demo.pediaca.ar", "cadete3@demo.pediaca.ar",
]

RESTAURANTES = [
    {
        "nombre": "Pizzeria La Esquina",
        "email": "pizzeria@demo.pediaca.ar",
        "categoria": "Pizzeria",
        "direccion": "Av. Pellegrini 1234, Rosario",
        "descripcion": "Pizza a la piedra, receta de familia desde 1985.",
        "horario": "Lun a Dom 12:00 a 23:00",
        "hace_envio": 1, "costo_envio": 0, "tiempo_estimado": 40,
        "logo": FOTO_PIZZA, "banner": FOTO_PIZZA,
        "productos": [
            {"nombre": "Muzzarella", "descripcion": "Salsa, muzzarella, oregano y aceitunas", "precio": 4500, "categoria": "Pizzas", "foto": FOTO_PIZZA},
            {"nombre": "Napolitana", "descripcion": "Salsa, muzzarella, tomate, ajo y perejil", "precio": 5000, "categoria": "Pizzas"},
            {"nombre": "Fugazzeta rellena", "descripcion": "Doble muzzarella, cebolla caramelizada", "precio": 5800, "categoria": "Pizzas"},
            {"nombre": "Calzone", "descripcion": "Jamon, muzzarella y salsa", "precio": 4800, "categoria": "Pizzas"},
            {"nombre": "Coca-Cola 500ml", "descripcion": "", "precio": 1200, "categoria": "Bebidas"},
            {"nombre": "Agua sin gas 500ml", "descripcion": "", "precio": 800, "categoria": "Bebidas"},
        ],
        "promo": {"titulo": "-15% OFF Muzzarella", "descripcion": "Todos los lunes y martes", "tipo_descuento": "porcentaje", "descuento_pct": 15, "producto": "Muzzarella"},
    },
    {
        "nombre": "Burger Rebels",
        "email": "burger@demo.pediaca.ar",
        "categoria": "Hamburgueseria",
        "direccion": "San Martin 2345, Rosario",
        "descripcion": "Smash burgers con pan de papa artesanal.",
        "horario": "Lun a Sab 19:00 a 00:30",
        "hace_envio": 1, "costo_envio": 500, "tiempo_estimado": 35,
        "logo": FOTO_BURGER, "banner": FOTO_BURGER,
        "productos": [
            {"nombre": "Smash Simple", "descripcion": "Pan de papa, carne smash, cheddar, salsa rebel", "precio": 4200, "categoria": "Hamburguesas", "foto": FOTO_BURGER},
            {"nombre": "Smash Doble", "descripcion": "Doble carne, doble cheddar, panceta", "precio": 5800, "categoria": "Hamburguesas"},
            {"nombre": "Bacon BBQ", "descripcion": "Carne, panceta crocante, cebolla crispy, BBQ", "precio": 6200, "categoria": "Hamburguesas"},
            {"nombre": "Papas rusticas", "descripcion": "Con cheddar y panceta", "precio": 2200, "categoria": "Acompanamientos"},
            {"nombre": "Papas clasicas", "descripcion": "", "precio": 1500, "categoria": "Acompanamientos"},
            {"nombre": "Cerveza IPA 500ml", "descripcion": "", "precio": 1800, "categoria": "Bebidas"},
        ],
        "promo": {"titulo": "$500 OFF en tu pedido", "descripcion": "Valido de martes a jueves", "tipo_descuento": "monto", "descuento_monto": 500},
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
            {"nombre": "Philadelphia Roll (8pz)", "descripcion": "Salmon, queso philadelphia", "precio": 3900, "categoria": "Rolls"},
            {"nombre": "Rainbow Roll (8pz)", "descripcion": "Salmon, atun, palta por fuera", "precio": 4500, "categoria": "Rolls"},
            {"nombre": "Sushi Mix (18pz)", "descripcion": "Seleccion variada de rolls y nigiris", "precio": 7800, "categoria": "Combos"},
            {"nombre": "Ginger Ale 350ml", "descripcion": "", "precio": 900, "categoria": "Bebidas"},
        ],
        "promo": None,
    },
    {
        "nombre": "Heladeria Polo Norte",
        "email": "heladeria@demo.pediaca.ar",
        "categoria": "Heladeria",
        "direccion": "Cordoba 1890, Rosario",
        "descripcion": "Helado artesanal, todos los dias recien hecho.",
        "horario": "Todos los dias 14:00 a 00:00",
        "hace_envio": 1, "costo_envio": 0, "tiempo_estimado": 30,
        "logo": FOTO_HELADO, "banner": FOTO_HELADO,
        "productos": [
            {"nombre": "Pote 1/4 kg", "descripcion": "2 gustos a eleccion", "precio": 3200, "categoria": "Potes", "foto": FOTO_HELADO},
            {"nombre": "Pote 1/2 kg", "descripcion": "3 gustos a eleccion", "precio": 5600, "categoria": "Potes"},
            {"nombre": "Pote 1 kg", "descripcion": "4 gustos a eleccion", "precio": 9800, "categoria": "Potes"},
            {"nombre": "Cucurucho simple", "descripcion": "1 gusto", "precio": 1800, "categoria": "Cucuruchos"},
        ],
        "promo": {"titulo": "-20% OFF Pote 1/2 kg", "descripcion": "Valido de lunes a jueves", "tipo_descuento": "porcentaje", "descuento_pct": 20, "producto": "Pote 1/2 kg"},
    },
    {
        "nombre": "Parrilla Don Julio",
        "email": "parrilla@demo.pediaca.ar",
        "categoria": "Roticeria",
        "direccion": "Alberdi 456, Rosario",
        "descripcion": "Asado y achuras a la parrilla, para comer en casa.",
        "horario": "Mie a Dom 12:00 a 15:30 y 20:00 a 23:30",
        "hace_envio": 1, "costo_envio": 700, "tiempo_estimado": 45,
        "logo": FOTO_ASADO, "banner": FOTO_ASADO,
        "productos": [
            {"nombre": "Parrillada para 2", "descripcion": "Vacio, chorizo, morcilla, provoleta", "precio": 12500, "categoria": "Parrilladas", "foto": FOTO_ASADO},
            {"nombre": "Bife de chorizo", "descripcion": "Con guarnicion a eleccion", "precio": 7800, "categoria": "Cortes"},
            {"nombre": "Pollo al spiedo", "descripcion": "Medio pollo con papas", "precio": 5200, "categoria": "Cortes"},
            {"nombre": "Ensalada mixta", "descripcion": "Lechuga, tomate, cebolla", "precio": 1800, "categoria": "Acompanamientos"},
        ],
        "promo": None,
    },
    {
        "nombre": "Verde Vida Vegano",
        "email": "veggie@demo.pediaca.ar",
        "categoria": "Vegano",
        "direccion": "Mendoza 2100, Rosario",
        "descripcion": "Cocina 100% plant-based, rica y de verdad.",
        "horario": "Lun a Sab 11:30 a 15:00 y 19:00 a 22:30",
        "hace_envio": 1, "costo_envio": 600, "tiempo_estimado": 35,
        "logo": FOTO_VEGGIE, "banner": FOTO_VEGGIE,
        "productos": [
            {"nombre": "Bowl energia", "descripcion": "Quinoa, garbanzos, palta, vegetales grillados", "precio": 4200, "categoria": "Bowls", "foto": FOTO_VEGGIE},
            {"nombre": "Burger de lentejas", "descripcion": "Con pan integral y papas", "precio": 4600, "categoria": "Platos"},
            {"nombre": "Milanesa de soja", "descripcion": "Con pure y ensalada", "precio": 4400, "categoria": "Platos"},
            {"nombre": "Limonada natural", "descripcion": "Jarra 1L", "precio": 1600, "categoria": "Bebidas"},
        ],
        "promo": {"titulo": "-10% OFF en tu pedido", "descripcion": "Por tiempo limitado", "tipo_descuento": "porcentaje", "descuento_pct": 10},
    },
]

CADETES = [
    {"nombre": "Carlos", "apellido": "Perez", "email": "cadete1@demo.pediaca.ar", "vehiculo": "moto", "zona": "Centro"},
    {"nombre": "Lucia",  "apellido": "Gomez", "email": "cadete2@demo.pediaca.ar", "vehiculo": "bici", "zona": "Pichincha"},
    {"nombre": "Javier", "apellido": "Lopez", "email": "cadete3@demo.pediaca.ar", "vehiculo": "auto", "zona": "Fisherton"},
]

RESENAS = [
    (5, "Excelente, llego rapido y estaba todo perfecto."),
    (5, "Como siempre, buenisimo. Recomendado."),
    (4, "Muy bueno, tardo un poco mas de lo esperado."),
    (5, "Diez puntos, ideal para pedir con amigos."),
]


def limpiar_datos_previos():
    usuarios = query(
        f"SELECT id FROM usuarios WHERE email IN ({','.join('?' * len(TODOS_LOS_EMAILS_DEMO))})",
        TODOS_LOS_EMAILS_DEMO,
    )
    usuario_ids = [u["id"] for u in usuarios]
    if not usuario_ids:
        return

    ph2 = ",".join("?" * len(usuario_ids))
    restaurantes = query(f"SELECT id FROM restaurantes WHERE usuario_id IN ({ph2})", usuario_ids)
    restaurante_ids = [r["id"] for r in restaurantes]

    if restaurante_ids:
        ph3 = ",".join("?" * len(restaurante_ids))
        pedidos = query(f"SELECT id FROM pedidos WHERE restaurante_id IN ({ph3})", restaurante_ids)
        pedido_ids = [p["id"] for p in pedidos]
        if pedido_ids:
            ph4 = ",".join("?" * len(pedido_ids))
            execute(f"DELETE FROM valoraciones WHERE pedido_id IN ({ph4})", pedido_ids)
            execute(f"DELETE FROM items_pedido WHERE pedido_id IN ({ph4})", pedido_ids)
            execute(f"DELETE FROM pedidos WHERE id IN ({ph4})", pedido_ids)
        execute(f"DELETE FROM promociones WHERE restaurante_id IN ({ph3})", restaurante_ids)
        execute(f"DELETE FROM productos WHERE restaurante_id IN ({ph3})", restaurante_ids)
        execute(f"DELETE FROM categorias_menu WHERE restaurante_id IN ({ph3})", restaurante_ids)
        execute(f"DELETE FROM restaurantes WHERE id IN ({ph3})", restaurante_ids)

    execute(f"DELETE FROM cadetes WHERE usuario_id IN ({ph2})", usuario_ids)
    execute(f"DELETE FROM clientes WHERE usuario_id IN ({ph2})", usuario_ids)
    execute(f"DELETE FROM usuarios WHERE id IN ({ph2})", usuario_ids)


def insertar_datos():
    print("Limpiando datos de prueba anteriores (si habia)...")
    limpiar_datos_previos()

    # ---------- CLIENTE DEMO (para dejar valoraciones) ----------
    cliente_id = execute("""
        INSERT INTO usuarios (nombre, apellido, email, telefono, password_hash, rol)
        VALUES (?, ?, ?, ?, ?, 'cliente')
    """, ("Sofia", "Demo", "cliente@demo.pediaca.ar", TELEFONO, generate_password_hash(PASSWORD)))
    execute("INSERT INTO clientes (usuario_id) VALUES (?)", (cliente_id,))

    for i, r in enumerate(RESTAURANTES):
        user_id = execute("""
            INSERT INTO usuarios (nombre, apellido, email, telefono, password_hash, rol)
            VALUES (?, ?, ?, ?, ?, 'restaurante')
        """, (r["nombre"], "Dueno/a", r["email"], TELEFONO, generate_password_hash(PASSWORD)))

        restaurante_id = execute("""
            INSERT INTO restaurantes
                (usuario_id, nombre_local, descripcion, categoria, direccion, whatsapp,
                 logo_url, banner_url, horario, hace_envio, costo_envio, tiempo_estimado,
                 ciudad, estado, abierto)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'aprobado', 1)
        """, (user_id, r["nombre"], r["descripcion"], r["categoria"], r["direccion"], TELEFONO,
              r["logo"], r["banner"], r["horario"], r["hace_envio"], r["costo_envio"], r["tiempo_estimado"],
              "Rosario"))

        categorias_creadas = {}
        productos_ids = []
        productos_por_nombre = {}
        for prod in r["productos"]:
            cat_nombre = prod["categoria"]
            if cat_nombre not in categorias_creadas:
                cat_id = execute("""
                    INSERT INTO categorias_menu (restaurante_id, nombre, orden)
                    VALUES (?, ?, (SELECT COALESCE(MAX(orden),0)+1 FROM categorias_menu WHERE restaurante_id=?))
                """, (restaurante_id, cat_nombre, restaurante_id))
                categorias_creadas[cat_nombre] = cat_id
            cat_id = categorias_creadas[cat_nombre]

            prod_id = execute("""
                INSERT INTO productos (restaurante_id, categoria_id, nombre, descripcion, precio, foto_url, disponible)
                VALUES (?, ?, ?, ?, ?, ?, 1)
            """, (restaurante_id, cat_id, prod["nombre"], prod["descripcion"], prod["precio"], prod.get("foto")))
            productos_ids.append(prod_id)
            productos_por_nombre[prod["nombre"]] = prod_id

        promo = r.get("promo")
        if promo:
            tipo = promo["tipo_descuento"]
            promo_producto_id = productos_por_nombre.get(promo.get("producto"))
            execute("""
                INSERT INTO promociones
                    (restaurante_id, titulo, descripcion, tipo_descuento, descuento_pct, descuento_monto, producto_id, activa)
                VALUES (?, ?, ?, ?, ?, ?, ?, 1)
            """, (restaurante_id, promo["titulo"], promo["descripcion"], tipo,
                  promo.get("descuento_pct", 0), promo.get("descuento_monto", 0), promo_producto_id))

        n_resenas = 2 + (i % 3)
        for j in range(n_resenas):
            prod = r["productos"][j % len(r["productos"])]
            total = prod["precio"]
            fecha = (datetime.now() - timedelta(days=j + 1)).strftime("%Y-%m-%d %H:%M:%S")
            pedido_id = execute("""
                INSERT INTO pedidos
                    (restaurante_id, cliente_id, tipo_entrega, estado, total,
                     enviado_whatsapp, fecha_pedido, fecha_actualizado)
                VALUES (?, ?, 'retiro', 'entregado', ?, 1, ?, ?)
            """, (restaurante_id, cliente_id, total, fecha, fecha))
            execute("""
                INSERT INTO items_pedido (pedido_id, producto_id, nombre_producto, cantidad, precio_unitario, subtotal)
                VALUES (?, ?, ?, 1, ?, ?)
            """, (pedido_id, productos_ids[j % len(productos_ids)], prod["nombre"], prod["precio"], prod["precio"]))
            estrellas, comentario = RESENAS[(i + j) % len(RESENAS)]
            execute("""
                INSERT INTO valoraciones (pedido_id, restaurante_id, cliente_id, estrellas, comentario, fecha)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (pedido_id, restaurante_id, cliente_id, estrellas, comentario, fecha))

        print(f"OK {r['nombre']} -- {len(r['productos'])} productos, {n_resenas} resenas")

    for c in CADETES:
        user_id = execute("""
            INSERT INTO usuarios (nombre, apellido, email, telefono, password_hash, rol)
            VALUES (?, ?, ?, ?, ?, 'cadete')
        """, (c["nombre"], c["apellido"], c["email"], TELEFONO, generate_password_hash(PASSWORD)))
        execute("""
            INSERT INTO cadetes (usuario_id, vehiculo, zona, disponible, estado)
            VALUES (?, ?, ?, 1, 'aprobado')
        """, (user_id, c["vehiculo"], c["zona"]))
        print(f"OK Cadete {c['nombre']} {c['apellido']}")

    print("\nListo -- entra a https://pediaca.ar para verlo.")
    print(f"Todos los usuarios de prueba usan la contrasena: {PASSWORD}")
    print("Locales:")
    for r in RESTAURANTES:
        print(f"  {r['nombre']:<24} {r['email']}")
    print("Cliente (para ver resenas hechas):", "cliente@demo.pediaca.ar")
    print("Cadetes:")
    for c in CADETES:
        print(f"  {c['nombre']} {c['apellido']:<10} {c['email']}")


if __name__ == "__main__":
    with app.app_context():
        insertar_datos()
