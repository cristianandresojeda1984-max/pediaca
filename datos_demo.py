"""
PediAcá — Datos de Demo
Carga 10 restaurantes con menús, fotos placeholder y usuarios de prueba.
Ejecutar: python datos_demo.py
"""

import os
import sys

DATABASE_URL = os.environ.get("DATABASE_URL", "")
USE_POSTGRES = bool(DATABASE_URL)

if USE_POSTGRES:
    import psycopg2
    import psycopg2.extras
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = False

    def query(sql, args=()):
        sql = sql.replace("?", "%s")
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, args)
        return cur.fetchall()

    def execute(sql, args=()):
        sql = sql.replace("?", "%s")
        cur = conn.cursor()
        if "INSERT" in sql.upper() and "RETURNING" not in sql.upper():
            sql = sql.rstrip().rstrip(";") + " RETURNING id"
        cur.execute(sql, args)
        row = cur.fetchone() if "RETURNING" in sql.upper() else None
        conn.commit()
        return row[0] if row else None
else:
    import sqlite3
    DB_PATH = os.environ.get("DB_PATH", "pediaca.db")
    if not os.path.exists(DB_PATH):
        print(f"❌ No existe {DB_PATH}. Ejecutá primero: python init_db.py")
        sys.exit(1)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")

    def query(sql, args=()):
        return conn.execute(sql, args).fetchall()

    def execute(sql, args=()):
        cur = conn.execute(sql, args)
        conn.commit()
        return cur.lastrowid

from werkzeug.security import generate_password_hash

# ── FOTOS PLACEHOLDER (URLs públicas de Unsplash) ─────────────────────────────
LOGOS = {
    "pizzeria":      "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=200&h=200&fit=crop",
    "hamburguesa":   "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=200&h=200&fit=crop",
    "sushi":         "https://images.unsplash.com/photo-1579584425555-c3ce17fd4351?w=200&h=200&fit=crop",
    "empanadas":     "https://images.unsplash.com/photo-1604467715878-83e57e8bc129?w=200&h=200&fit=crop",
    "rotiseria":     "https://images.unsplash.com/photo-1544025162-d76694265947?w=200&h=200&fit=crop",
    "helado":        "https://images.unsplash.com/photo-1497034825429-c343d7c6a68f?w=200&h=200&fit=crop",
    "vegano":        "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=200&h=200&fit=crop",
    "panaderia":     "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=200&h=200&fit=crop",
    "bar":           "https://images.unsplash.com/photo-1514362545857-3bc16c4c7d1b?w=200&h=200&fit=crop",
    "milanesa":      "https://images.unsplash.com/photo-1601342630314-8427c38bf5e6?w=200&h=200&fit=crop",
}

BANNERS = {
    "pizzeria":    "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=800&h=300&fit=crop",
    "hamburguesa": "https://images.unsplash.com/photo-1550547660-d9450f859349?w=800&h=300&fit=crop",
    "sushi":       "https://images.unsplash.com/photo-1611143669185-af224c5e3252?w=800&h=300&fit=crop",
    "empanadas":   "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&h=300&fit=crop",
    "rotiseria":   "https://images.unsplash.com/photo-1529692236671-f1f6cf9683ba?w=800&h=300&fit=crop",
    "helado":      "https://images.unsplash.com/photo-1501443762994-82bd5dace89a?w=800&h=300&fit=crop",
    "vegano":      "https://images.unsplash.com/photo-1540189549336-e6e99c3679fe?w=800&h=300&fit=crop",
    "panaderia":   "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&h=300&fit=crop",
    "bar":         "https://images.unsplash.com/photo-1543007630-9710e4a00a20?w=800&h=300&fit=crop",
    "milanesa":    "https://images.unsplash.com/photo-1529692236671-f1f6cf9683ba?w=800&h=300&fit=crop",
}

FOTOS_PRODUCTOS = {
    "pizza":        "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=400&h=300&fit=crop",
    "hamburguesa":  "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=400&h=300&fit=crop",
    "sushi":        "https://images.unsplash.com/photo-1579584425555-c3ce17fd4351?w=400&h=300&fit=crop",
    "empanada":     "https://images.unsplash.com/photo-1604467715878-83e57e8bc129?w=400&h=300&fit=crop",
    "milanesa":     "https://images.unsplash.com/photo-1601342630314-8427c38bf5e6?w=400&h=300&fit=crop",
    "pollo":        "https://images.unsplash.com/photo-1598103442097-8b74394b95c8?w=400&h=300&fit=crop",
    "ensalada":     "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=400&h=300&fit=crop",
    "helado":       "https://images.unsplash.com/photo-1497034825429-c343d7c6a68f?w=400&h=300&fit=crop",
    "medialunas":   "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=400&h=300&fit=crop",
    "cerveza":      "https://images.unsplash.com/photo-1535958636474-b021ee887b13?w=400&h=300&fit=crop",
    "coca":         "https://images.unsplash.com/photo-1554866585-cd94860890b7?w=400&h=300&fit=crop",
    "papas":        "https://images.unsplash.com/photo-1573080496219-bb080dd4f877?w=400&h=300&fit=crop",
}

# ── DATOS DE LOS 10 RESTAURANTES ──────────────────────────────────────────────
RESTAURANTES = [
    {
        "nombre": "La Mamma Pizzería",
        "email": "lamamma@demo.com",
        "telefono": "3412000001",
        "whatsapp": "3412000001",
        "categoria": "Pizzería",
        "direccion": "Córdoba 1234, Rosario",
        "horario": "Lun-Dom 18:00-23:30",
        "hace_envio": 1, "costo_envio": 0, "tiempo_estimado": 40,
        "logo": LOGOS["pizzeria"], "banner": BANNERS["pizzeria"],
        "descripcion": "La mejor pizza a la piedra de Rosario desde 1985",
        "categorias_menu": [
            {
                "nombre": "Pizzas",
                "productos": [
                    {"nombre": "Pizza Muzzarella", "precio": 5500, "desc": "Salsa, muzzarella y orégano", "foto": FOTOS_PRODUCTOS["pizza"]},
                    {"nombre": "Pizza Napolitana", "precio": 6200, "desc": "Salsa, muzzarella, tomate y ajo", "foto": FOTOS_PRODUCTOS["pizza"]},
                    {"nombre": "Pizza Fugazzeta", "precio": 6500, "desc": "Cebolla, muzzarella y aceitunas", "foto": FOTOS_PRODUCTOS["pizza"]},
                    {"nombre": "Pizza 4 Quesos", "precio": 7200, "desc": "Muzzarella, cheddar, azul y parmesano", "foto": FOTOS_PRODUCTOS["pizza"]},
                ]
            },
            {
                "nombre": "Bebidas",
                "productos": [
                    {"nombre": "Coca-Cola 500ml", "precio": 1200, "desc": "", "foto": FOTOS_PRODUCTOS["coca"]},
                    {"nombre": "Agua mineral", "precio": 900, "desc": "", "foto": None},
                ]
            }
        ]
    },
    {
        "nombre": "Burger Bros",
        "email": "burgerbros@demo.com",
        "telefono": "3412000002",
        "whatsapp": "3412000002",
        "categoria": "Hamburguesería",
        "direccion": "Pellegrini 567, Rosario",
        "horario": "Lun-Dom 12:00-00:00",
        "hace_envio": 1, "costo_envio": 500, "tiempo_estimado": 35,
        "logo": LOGOS["hamburguesa"], "banner": BANNERS["hamburguesa"],
        "descripcion": "Burgers artesanales con carne 100% rosarina",
        "categorias_menu": [
            {
                "nombre": "Hamburguesas",
                "productos": [
                    {"nombre": "Clásica", "precio": 4800, "desc": "Pan brioche, carne, lechuga, tomate y cheddar", "foto": FOTOS_PRODUCTOS["hamburguesa"]},
                    {"nombre": "Doble Cheese", "precio": 6200, "desc": "Doble carne, doble cheddar, bacon", "foto": FOTOS_PRODUCTOS["hamburguesa"]},
                    {"nombre": "Pollo Crispy", "precio": 5400, "desc": "Pollo crocante, mayo de ajo y pepinillos", "foto": FOTOS_PRODUCTOS["pollo"]},
                    {"nombre": "Veggie", "precio": 5000, "desc": "Medallón de garbanzo, aguacate y rúcula", "foto": FOTOS_PRODUCTOS["ensalada"]},
                ]
            },
            {
                "nombre": "Extras",
                "productos": [
                    {"nombre": "Papas fritas", "precio": 1800, "desc": "Con alioli casero", "foto": FOTOS_PRODUCTOS["papas"]},
                    {"nombre": "Cerveza Quilmes", "precio": 1500, "desc": "500ml bien fría", "foto": FOTOS_PRODUCTOS["cerveza"]},
                ]
            }
        ]
    },
    {
        "nombre": "Sushi Rosario",
        "email": "sushirosario@demo.com",
        "telefono": "3412000003",
        "whatsapp": "3412000003",
        "categoria": "Sushi",
        "direccion": "Corrientes 890, Rosario",
        "horario": "Mar-Dom 19:00-23:00",
        "hace_envio": 1, "costo_envio": 600, "tiempo_estimado": 50,
        "logo": LOGOS["sushi"], "banner": BANNERS["sushi"],
        "descripcion": "Sushi fresco preparado al momento. Rolls, nigiris y más",
        "categorias_menu": [
            {
                "nombre": "Rolls",
                "productos": [
                    {"nombre": "California Roll x8", "precio": 5200, "desc": "Crab, palta y pepino", "foto": FOTOS_PRODUCTOS["sushi"]},
                    {"nombre": "Spicy Tuna x8", "precio": 6400, "desc": "Atún, mayo picante y sésamo", "foto": FOTOS_PRODUCTOS["sushi"]},
                    {"nombre": "Dragon Roll x8", "precio": 7200, "desc": "Langostino tempura y palta", "foto": FOTOS_PRODUCTOS["sushi"]},
                ]
            },
            {
                "nombre": "Combos",
                "productos": [
                    {"nombre": "Combo 2 personas", "precio": 14500, "desc": "40 piezas variadas + 2 bebidas", "foto": FOTOS_PRODUCTOS["sushi"]},
                    {"nombre": "Combo 4 personas", "precio": 26000, "desc": "80 piezas variadas + 4 bebidas", "foto": FOTOS_PRODUCTOS["sushi"]},
                ]
            }
        ]
    },
    {
        "nombre": "La Rotisería de Pepe",
        "email": "pepe@demo.com",
        "telefono": "3412000004",
        "whatsapp": "3412000004",
        "categoria": "Rotisería",
        "direccion": "San Martín 345, Rosario",
        "horario": "Lun-Sab 11:00-15:00 y 19:00-22:00",
        "hace_envio": 0, "costo_envio": 0, "tiempo_estimado": 20,
        "logo": LOGOS["rotiseria"], "banner": BANNERS["rotiseria"],
        "descripcion": "Cocina casera de siempre. Milanesas, pollo y más",
        "categorias_menu": [
            {
                "nombre": "Platos principales",
                "productos": [
                    {"nombre": "Milanesa napolitana", "precio": 6800, "desc": "Con papas fritas y ensalada", "foto": FOTOS_PRODUCTOS["milanesa"]},
                    {"nombre": "Pollo al horno", "precio": 5900, "desc": "Con guarnición a elección", "foto": FOTOS_PRODUCTOS["pollo"]},
                    {"nombre": "Milanesa a caballo", "precio": 7200, "desc": "Con dos huevos fritos y papas", "foto": FOTOS_PRODUCTOS["milanesa"]},
                ]
            },
            {
                "nombre": "Guarniciones",
                "productos": [
                    {"nombre": "Papas fritas", "precio": 1500, "desc": "", "foto": FOTOS_PRODUCTOS["papas"]},
                    {"nombre": "Ensalada mixta", "precio": 1200, "desc": "Lechuga, tomate y zanahoria", "foto": FOTOS_PRODUCTOS["ensalada"]},
                ]
            }
        ]
    },
    {
        "nombre": "El Rincón de las Empanadas",
        "email": "empanadas@demo.com",
        "telefono": "3412000005",
        "whatsapp": "3412000005",
        "categoria": "Empanadas",
        "direccion": "Balcarce 678, Rosario",
        "horario": "Lun-Dom 12:00-15:00 y 19:00-23:00",
        "hace_envio": 1, "costo_envio": 400, "tiempo_estimado": 30,
        "logo": LOGOS["empanadas"], "banner": BANNERS["empanadas"],
        "descripcion": "Empanadas artesanales, receta familiar de Tucumán",
        "categorias_menu": [
            {
                "nombre": "Empanadas",
                "productos": [
                    {"nombre": "Carne cortada a cuchillo", "precio": 850, "desc": "La clásica de siempre", "foto": FOTOS_PRODUCTOS["empanada"]},
                    {"nombre": "Pollo y verdura", "precio": 800, "desc": "Suave y sabrosa", "foto": FOTOS_PRODUCTOS["empanada"]},
                    {"nombre": "Jamón y queso", "precio": 800, "desc": "Para los más clásicos", "foto": FOTOS_PRODUCTOS["empanada"]},
                    {"nombre": "Caprese", "precio": 820, "desc": "Tomate, muzzarella y albahaca", "foto": FOTOS_PRODUCTOS["empanada"]},
                    {"nombre": "Humita", "precio": 780, "desc": "Vegetariana y sabrosa", "foto": FOTOS_PRODUCTOS["empanada"]},
                ]
            },
            {
                "nombre": "Docenas",
                "productos": [
                    {"nombre": "Docena a elección", "precio": 9000, "desc": "12 empanadas a elección", "foto": FOTOS_PRODUCTOS["empanada"]},
                    {"nombre": "Dos docenas", "precio": 16500, "desc": "24 empanadas + 2 bebidas", "foto": FOTOS_PRODUCTOS["empanada"]},
                ]
            }
        ]
    },
    {
        "nombre": "Helados Ricos",
        "email": "helados@demo.com",
        "telefono": "3412000006",
        "whatsapp": "3412000006",
        "categoria": "Heladería",
        "direccion": "Italia 1170, Rosario",
        "horario": "Lun-Dom 14:00-23:00",
        "hace_envio": 1, "costo_envio": 300, "tiempo_estimado": 25,
        "logo": LOGOS["helado"], "banner": BANNERS["helado"],
        "descripcion": "Helados artesanales elaborados con leche fresca",
        "categorias_menu": [
            {
                "nombre": "Potes",
                "productos": [
                    {"nombre": "1/4 kg de helado", "precio": 2200, "desc": "Hasta 2 gustos", "foto": FOTOS_PRODUCTOS["helado"]},
                    {"nombre": "1/2 kg de helado", "precio": 4000, "desc": "Hasta 3 gustos", "foto": FOTOS_PRODUCTOS["helado"]},
                    {"nombre": "1 kg de helado", "precio": 7500, "desc": "Hasta 4 gustos", "foto": FOTOS_PRODUCTOS["helado"]},
                ]
            },
            {
                "nombre": "Postres",
                "productos": [
                    {"nombre": "Banana Split", "precio": 3200, "desc": "Con crema, salsa y chips de chocolate", "foto": FOTOS_PRODUCTOS["helado"]},
                    {"nombre": "Copa americana", "precio": 2800, "desc": "3 gustos con crema chantilly", "foto": FOTOS_PRODUCTOS["helado"]},
                ]
            }
        ]
    },
    {
        "nombre": "Verde Vital",
        "email": "verdevital@demo.com",
        "telefono": "3412000007",
        "whatsapp": "3412000007",
        "categoria": "Vegano",
        "direccion": "Sarmiento 432, Rosario",
        "horario": "Lun-Sab 12:00-16:00 y 19:00-22:00",
        "hace_envio": 1, "costo_envio": 500, "tiempo_estimado": 40,
        "logo": LOGOS["vegano"], "banner": BANNERS["vegano"],
        "descripcion": "Cocina plant-based, orgánica y de temporada",
        "categorias_menu": [
            {
                "nombre": "Platos",
                "productos": [
                    {"nombre": "Bowl proteico", "precio": 5200, "desc": "Quinoa, legumbres, semillas y vegetales asados", "foto": FOTOS_PRODUCTOS["ensalada"]},
                    {"nombre": "Burger vegana", "precio": 4800, "desc": "Medallón de lentejas, palta y mayonesa vegana", "foto": FOTOS_PRODUCTOS["hamburguesa"]},
                    {"nombre": "Wrap integral", "precio": 4200, "desc": "Hummus, rúcula, tomate cherry y zanahoria", "foto": FOTOS_PRODUCTOS["ensalada"]},
                ]
            },
            {
                "nombre": "Extras",
                "productos": [
                    {"nombre": "Jugo verde", "precio": 1800, "desc": "Espinaca, manzana, jengibre y limón", "foto": None},
                    {"nombre": "Brownie vegano", "precio": 1500, "desc": "Con chocolate negro 70%", "foto": None},
                ]
            }
        ]
    },
    {
        "nombre": "La Panadería del Centro",
        "email": "panaderia@demo.com",
        "telefono": "3412000008",
        "whatsapp": "3412000008",
        "categoria": "Panadería",
        "direccion": "Entre Ríos 234, Rosario",
        "horario": "Lun-Sab 07:00-13:00 y 16:00-20:00",
        "hace_envio": 0, "costo_envio": 0, "tiempo_estimado": 15,
        "logo": LOGOS["panaderia"], "banner": BANNERS["panaderia"],
        "descripcion": "Pan artesanal horneado todas las mañanas",
        "categorias_menu": [
            {
                "nombre": "Facturería",
                "productos": [
                    {"nombre": "Medialunas x6", "precio": 2400, "desc": "De grasa, bien hojaldradas", "foto": FOTOS_PRODUCTOS["medialunas"]},
                    {"nombre": "Vigilantes x6", "precio": 2200, "desc": "Rellenos de membrillo o batata", "foto": FOTOS_PRODUCTOS["medialunas"]},
                    {"nombre": "Cañoncitos x6", "precio": 2800, "desc": "Con dulce de leche", "foto": FOTOS_PRODUCTOS["medialunas"]},
                ]
            },
            {
                "nombre": "Pan",
                "productos": [
                    {"nombre": "Pan francés (kg)", "precio": 1800, "desc": "Horneado en el día", "foto": FOTOS_PRODUCTOS["medialunas"]},
                    {"nombre": "Pan de campo", "precio": 2200, "desc": "Grande, para toda la familia", "foto": FOTOS_PRODUCTOS["medialunas"]},
                ]
            }
        ]
    },
    {
        "nombre": "Bar El Farol",
        "email": "elfaol@demo.com",
        "telefono": "3412000009",
        "whatsapp": "3412000009",
        "categoria": "Bar",
        "direccion": "Laprida 789, Rosario",
        "horario": "Mar-Dom 18:00-02:00",
        "hace_envio": 0, "costo_envio": 0, "tiempo_estimado": 10,
        "logo": LOGOS["bar"], "banner": BANNERS["bar"],
        "descripcion": "El bar de barrio de siempre. Picadas, birra y buena onda",
        "categorias_menu": [
            {
                "nombre": "Picadas",
                "productos": [
                    {"nombre": "Picada chica", "precio": 6500, "desc": "Fiambres, quesos, aceitunas y pan", "foto": FOTOS_PRODUCTOS["cerveza"]},
                    {"nombre": "Picada grande", "precio": 11000, "desc": "Versión XL para 4 personas", "foto": FOTOS_PRODUCTOS["cerveza"]},
                    {"nombre": "Papas con cheddar", "precio": 3200, "desc": "Con salsa barbacoa y cebolla caramelizada", "foto": FOTOS_PRODUCTOS["papas"]},
                ]
            },
            {
                "nombre": "Bebidas",
                "productos": [
                    {"nombre": "Cerveza artesanal", "precio": 2200, "desc": "Rubia o roja, 500ml", "foto": FOTOS_PRODUCTOS["cerveza"]},
                    {"nombre": "Porron Quilmes", "precio": 1600, "desc": "Bien fría", "foto": FOTOS_PRODUCTOS["cerveza"]},
                    {"nombre": "Fernet con Coca", "precio": 2800, "desc": "El clásico rosarino", "foto": None},
                ]
            }
        ]
    },
    {
        "nombre": "La Milanesa de Oro",
        "email": "milanese@demo.com",
        "telefono": "3412000010",
        "whatsapp": "3412000010",
        "categoria": "Rotisería",
        "direccion": "Ovidio Lagos 456, Rosario",
        "horario": "Lun-Sab 12:00-15:00 y 19:30-22:30",
        "hace_envio": 1, "costo_envio": 600, "tiempo_estimado": 35,
        "logo": LOGOS["milanesa"], "banner": BANNERS["milanesa"],
        "descripcion": "Las mejores milanesas de Rosario desde 1998",
        "categorias_menu": [
            {
                "nombre": "Milanesas",
                "productos": [
                    {"nombre": "Milanesa clásica", "precio": 5800, "desc": "Ternera 200g con guarnición", "foto": FOTOS_PRODUCTOS["milanesa"]},
                    {"nombre": "Napolitana", "precio": 6500, "desc": "Con salsa, jamón y muzzarella", "foto": FOTOS_PRODUCTOS["milanesa"]},
                    {"nombre": "Suprema", "precio": 6200, "desc": "Pollo relleno con jamón y queso", "foto": FOTOS_PRODUCTOS["pollo"]},
                    {"nombre": "A caballo", "precio": 7000, "desc": "Con dos huevos fritos", "foto": FOTOS_PRODUCTOS["milanesa"]},
                    {"nombre": "Milanesa vegana", "precio": 5500, "desc": "De soja, crocante y sabrosa", "foto": FOTOS_PRODUCTOS["ensalada"]},
                ]
            },
            {
                "nombre": "Guarniciones",
                "productos": [
                    {"nombre": "Papas fritas", "precio": 1600, "desc": "Crocantes y doradas", "foto": FOTOS_PRODUCTOS["papas"]},
                    {"nombre": "Puré de papas", "precio": 1400, "desc": "Casero con manteca", "foto": None},
                    {"nombre": "Ensalada mixta", "precio": 1300, "desc": "", "foto": FOTOS_PRODUCTOS["ensalada"]},
                ]
            }
        ]
    },
]

# ── CARGAR DATOS ──────────────────────────────────────────────────────────────
def cargar():
    print("🚀 Cargando datos de demo en PediAcá...\n")

    for i, r in enumerate(RESTAURANTES, 1):
        # Verificar si ya existe
        existe = query("SELECT id FROM usuarios WHERE email = ?", (r["email"],))
        if existe:
            print(f"⚠️  {r['nombre']} ya existe, saltando...")
            continue

        # Crear usuario
        uid = execute("""
            INSERT INTO usuarios (nombre, apellido, email, telefono, password_hash, rol)
            VALUES (?, ?, ?, ?, ?, 'restaurante')
        """, (r["nombre"], "Demo", r["email"], r["telefono"],
              generate_password_hash("demo123")))

        # Crear restaurante
        rid = execute("""
            INSERT INTO restaurantes
                (usuario_id, nombre_local, descripcion, categoria, direccion,
                 whatsapp, logo_url, banner_url, horario, hace_envio,
                 costo_envio, tiempo_estimado, estado, abierto)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,'aprobado',1)
        """, (uid, r["nombre"], r["descripcion"], r["categoria"],
              r["direccion"], r["whatsapp"], r["logo"], r["banner"],
              r["horario"], r["hace_envio"], r["costo_envio"],
              r["tiempo_estimado"]))

        # Crear categorías y productos
        for cat in r["categorias_menu"]:
            cid = execute("""
                INSERT INTO categorias_menu (restaurante_id, nombre, orden)
                VALUES (?, ?, ?)
            """, (rid, cat["nombre"], r["categorias_menu"].index(cat)))

            for j, prod in enumerate(cat["productos"]):
                execute("""
                    INSERT INTO productos
                        (restaurante_id, categoria_id, nombre, descripcion,
                         precio, foto_url, disponible, orden)
                    VALUES (?,?,?,?,?,?,1,?)
                """, (rid, cid, prod["nombre"], prod["desc"],
                      prod["precio"], prod["foto"], j))

        print(f"✅ {i:2d}. {r['nombre']} — {r['categoria']}")
        print(f"      📧 {r['email']} / 🔑 demo123")

    print("\n✅ ¡Listo! Los 10 restaurantes están cargados.")
    print("\n📋 Credenciales de acceso:")
    print("   Todos los restaurantes: contraseña = demo123")
    print("   Email = el que figura arriba para cada uno")

if __name__ == "__main__":
    cargar()
