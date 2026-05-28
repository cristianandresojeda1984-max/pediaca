import os
import psycopg2

try:
    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    cur = conn.cursor()
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS configuraciones (
            id SERIAL PRIMARY KEY,
            clave TEXT UNIQUE,
            valor TEXT,
            tipo TEXT DEFAULT 'text',
            actualizado TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cur.execute("""
        INSERT INTO configuraciones (clave, valor, tipo) VALUES
        ('hero_tipo', 'gradiente', 'text'),
        ('hero_imagen_url', '', 'text'),
        ('hero_blur', '6', 'number'),
        ('hero_opacidad_overlay', '75', 'number'),
        ('hero_color_overlay', '#1E3A5F', 'text'),
        ('hero_gradiente', '135deg, #1A1A2E, #1E3A5F', 'text'),
        ('usar_overlay', 'true', 'text')
        ON CONFLICT (clave) DO NOTHING
    """)
    
    conn.commit()
    print("✅ Tabla configuraciones creada exitosamente")
    
except Exception as e:
    print(f"❌ Error: {e}")