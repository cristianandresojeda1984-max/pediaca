import psycopg2

# 🔴 CAMBIÁ ESTA URL por la que está en Render
DATABASE_URL = "postgresql://pediaca_db_user:TU_CONTRASEÑA@dpg-d8749pp9rddc73840ja0-a.frankfurt-postgres.render.com:5432/pediaca_db"

try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    # Crear tabla
    cur.execute("""
        CREATE TABLE IF NOT EXISTS configuraciones (
            id SERIAL PRIMARY KEY,
            clave TEXT UNIQUE,
            valor TEXT,
            tipo TEXT DEFAULT 'text',
            actualizado TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Insertar valores
    valores = [
        ('hero_tipo', 'gradiente', 'text'),
        ('hero_imagen_url', '', 'text'),
        ('hero_blur', '6', 'number'),
        ('hero_opacidad_overlay', '75', 'number'),
        ('hero_color_overlay', '#1E3A5F', 'text'),
        ('hero_gradiente', '135deg, #1A1A2E, #1E3A5F', 'text'),
        ('usar_overlay', 'true', 'text'),
    ]
    
    for clave, valor, tipo in valores:
        cur.execute("""
            INSERT INTO configuraciones (clave, valor, tipo)
            VALUES (%s, %s, %s)
            ON CONFLICT (clave) DO NOTHING
        """, (clave, valor, tipo))
    
    conn.commit()
    print("✅ Tabla configuraciones creada exitosamente")
    
    # Verificar
    cur.execute("SELECT * FROM configuraciones")
    for row in cur.fetchall():
        print(row)
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")