"""
insertar_datos_prueba.py
Carga 3 restaurantes con menús y 3 cadetes para pruebas.
Contraseña para todos los usuarios: 123456
Teléfono para todos: 3417523674
"""

import sqlite3
from werkzeug.security import generate_password_hash

DB_PATH = "pediaca.db"
PASSWORD = "123456"
TELEFONO = "3417523674"

def hash_pass(pwd):
    return generate_password_hash(pwd)

def insertar_datos():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()

    # Limpiar datos previos (opcional, comentar si no quieres borrar)
    # cur.execute("DELETE FROM items_pedido")
    # cur.execute("DELETE FROM pedidos")
    # cur.execute("DELETE FROM productos")
    # cur.execute("DELETE FROM categorias_menu")
    # cur.execute("DELETE FROM restaurantes")
    # cur.execute("DELETE FROM cadetes")
    # cur.execute("DELETE FROM usuarios WHERE rol IN ('restaurante','cadete')")
    # conn.commit()

    # ---------- RESTAURANTES ----------
    restaurantes_data = [
        {
            "nombre": "Pizzería La Esquina",
            "email": "restaurante1@test.com",
            "categoria": "Pizzería",
            "direccion": "Av. Pellegrini 1234, Rosario",
            "whatsapp": TELEFONO,
            "horario": "Lun a Dom 12:00 a 23:00",
            "hace_envio": 1,
            "costo_envio": 0,
            "tiempo_estimado": 45,
            "productos": [
                {"nombre": "Muzzarella", "descripcion": "Salsa, muzzarella, orégano", "precio": 4500, "categoria": "Pizzas"},
                {"nombre": "Napolitana", "descripcion": "Salsa, muzzarella, tomate", "precio": 5000, "categoria": "Pizzas"},
                {"nombre": "Fugazzeta", "descripcion": "Muzzarella, cebolla", "precio": 5200, "categoria": "Pizzas"},
                {"nombre": "Coca Cola 500ml", "descripcion": "", "precio": 1200, "categoria": "Bebidas"},
                {"nombre": "Agua 500ml", "descripcion": "", "precio": 800, "categoria": "Bebidas"}
            ]
        },
        {
            "nombre": "Hamburguesería El Rey",
            "email": "restaurante2@test.com",
            "categoria": "Hamburguesería",
            "direccion": "San Martín 2345, Rosario",
            "whatsapp": TELEFONO,
            "horario": "Lun a Sab 19:00 a 00:00",
            "hace_envio": 1,
            "costo_envio": 500,
            "tiempo_estimado": 35,
            "productos": [
                {"nombre": "Hamburguesa Simple", "descripcion": "Pan, carne, lechuga, tomate", "precio": 3800, "categoria": "Hamburguesas"},
                {"nombre": "Hamburguesa Doble", "descripcion": "Doble carne, queso cheddar", "precio": 5200, "categoria": "Hamburguesas"},
                {"nombre": "Papas fritas", "descripcion": "Papas rústicas", "precio": 1500, "categoria": "Acompañamientos"},
                {"nombre": "Cerveza IPA", "descripcion": "Botella 500ml", "precio": 1800, "categoria": "Bebidas"}
            ]
        },
        {
            "nombre": "Sushi Fresh",
            "email": "restaurante3@test.com",
            "categoria": "Sushi",
            "direccion": "Rioja 3456, Rosario",
            "whatsapp": TELEFONO,
            "horario": "Mar a Dom 19:30 a 23:30",
            "hace_envio": 1,
            "costo_envio": 800,
            "tiempo_estimado": 55,
            "productos": [
                {"nombre": "California Roll (8pz)", "descripcion": "Palta, pepino, kanikama", "precio": 3200, "categoria": "Rolls"},
                {"nombre": "Philadelphia Roll (8pz)", "descripcion": "Salmón, queso filadelfia", "precio": 3800, "categoria": "Rolls"},
                {"nombre": "Sushi Mix (12pz)", "descripcion": "Variado de sushi y sashimi", "precio": 5500, "categoria": "Combos"},
                {"nombre": "Ginger Ale", "descripcion": "Lata 350ml", "precio": 900, "categoria": "Bebidas"}
            ]
        }
    ]

    restaurante_ids = []

    for r in restaurantes_data:
        # Crear usuario restaurante
        password_hash = hash_pass(PASSWORD)
        cur.execute("""
            INSERT INTO usuarios (nombre, apellido, email, telefono, password_hash, rol)
            VALUES (?, ?, ?, ?, ?, 'restaurante')
        """, (r["nombre"], "Dueño", r["email"], TELEFONO, password_hash))
        user_id = cur.lastrowid

        # Crear restaurante
        cur.execute("""
            INSERT INTO restaurantes
                (usuario_id, nombre_local, categoria, direccion, whatsapp, horario, hace_envio, costo_envio, tiempo_estimado, estado, abierto)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'aprobado', 1)
        """, (user_id, r["nombre"], r["categoria"], r["direccion"], r["whatsapp"], r["horario"], r["hace_envio"], r["costo_envio"], r["tiempo_estimado"]))
        restaurante_id = cur.lastrowid
        restaurante_ids.append(restaurante_id)

        # Crear categorías dinámicas y mapear
        categorias_creadas = {}
        for prod in r["productos"]:
            cat_nombre = prod["categoria"]
            if cat_nombre not in categorias_creadas:
                cur.execute("""
                    INSERT INTO categorias_menu (restaurante_id, nombre, orden)
                    VALUES (?, ?, (SELECT COALESCE(MAX(orden),0)+1 FROM categorias_menu WHERE restaurante_id=?))
                """, (restaurante_id, cat_nombre, restaurante_id))
                cat_id = cur.lastrowid
                categorias_creadas[cat_nombre] = cat_id
            else:
                cat_id = categorias_creadas[cat_nombre]

            cur.execute("""
                INSERT INTO productos (restaurante_id, categoria_id, nombre, descripcion, precio, disponible)
                VALUES (?, ?, ?, ?, ?, 1)
            """, (restaurante_id, cat_id, prod["nombre"], prod["descripcion"], prod["precio"]))

        print(f"✅ Restaurante '{r['nombre']}' creado (ID {restaurante_id})")

    # ---------- CADETES ----------
    cadetes_data = [
        {"nombre": "Carlos", "apellido": "Pérez", "email": "cadete1@test.com", "vehiculo": "moto", "zona": "Centro"},
        {"nombre": "Lucía", "apellido": "Gómez", "email": "cadete2@test.com", "vehiculo": "bici", "zona": "Pichincha"},
        {"nombre": "Javier", "apellido": "López", "email": "cadete3@test.com", "vehiculo": "auto", "zona": "Fisherton"}
    ]

    for c in cadetes_data:
        password_hash = hash_pass(PASSWORD)
        cur.execute("""
            INSERT INTO usuarios (nombre, apellido, email, telefono, password_hash, rol)
            VALUES (?, ?, ?, ?, ?, 'cadete')
        """, (c["nombre"], c["apellido"], c["email"], TELEFONO, password_hash))
        user_id = cur.lastrowid

        cur.execute("""
            INSERT INTO cadetes (usuario_id, vehiculo, zona, disponible, estado)
            VALUES (?, ?, ?, 1, 'aprobado')
        """, (user_id, c["vehiculo"], c["zona"]))

        print(f"✅ Cadete '{c['nombre']} {c['apellido']}' creado (email {c['email']})")

    conn.commit()
    conn.close()
    print("\n🎉 Datos de prueba cargados correctamente.")
    print("\nResumen de accesos:")
    for r in restaurantes_data:
        print(f"  Restaurante: {r['email']} / {PASSWORD}")
    for c in cadetes_data:
        print(f"  Cadete: {c['email']} / {PASSWORD}")

if __name__ == "__main__":
    insertar_datos()