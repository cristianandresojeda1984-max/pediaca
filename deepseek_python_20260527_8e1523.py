#!/usr/bin/env python3
"""
Actualizador automático de PediAcá para PostgreSQL
Corrige GROUP_CONCAT → STRING_AGG y otros problemas de compatibilidad
"""

import re
import os

def fix_app_py():
    """Corrige todas las consultas SQL en app.py"""
    path = "app.py"
    if not os.path.exists(path):
        print(f"❌ No se encuentra {path}")
        return False
    
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    cambios = 0
    
    # 1. GROUP_CONCAT(p.id, ',') → STRING_AGG(p.id::text, ',')
    pattern1 = r"GROUP_CONCAT\(([^,]+),\s*['\"]([^'\"]+)['\"]\)"
    replacement1 = r"STRING_AGG(\1::text, '\2')"
    new_content, count1 = re.subn(pattern1, replacement1, content)
    cambios += count1
    
    # 2. GROUP_CONCAT(p.id) sin separador → STRING_AGG(p.id::text, ',')
    pattern2 = r"GROUP_CONCAT\(([^)]+)\)"
    replacement2 = r"STRING_AGG(\1::text, ',')"
    new_content, count2 = re.subn(pattern2, replacement2, new_content)
    cambios += count2
    
    # 3. Agregar ORDER BY dentro de STRING_AGG donde sea necesario
    # (opcional, mejora la consistencia)
    
    if cambios > 0:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"✅ app.py: {cambios} corrección(es) aplicada(s)")
        return True
    else:
        print("✅ app.py: No se encontraron GROUP_CONCAT para corregir")
        return True

def fix_ver_local_html():
    """Corrige las consultas en ver_local.html (si las hay embebidas)"""
    path = "templates/ver_local.html"
    if not os.path.exists(path):
        print(f"⚠️ No se encuentra {path}, omitiendo")
        return
    
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar consultas SQL en el template
    pattern = r"GROUP_CONCAT\(([^,]+),\s*['\"]([^'\"]+)['\"]\)"
    replacement = r"STRING_AGG(\1::text, '\2')"
    new_content, count = re.subn(pattern, replacement, content)
    
    if count > 0:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"✅ ver_local.html: {count} corrección(es) aplicada(s)")

def fix_other_files():
    """Corrige otros archivos que puedan tener GROUP_CONCAT"""
    files_to_check = [
        "templates/restaurante_panel.html",
        "templates/admin_panel.html",
        "templates/cadete_panel.html"
    ]
    
    for path in files_to_check:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            pattern = r"GROUP_CONCAT\(([^,]+),\s*['\"]([^'\"]+)['\"]\)"
            replacement = r"STRING_AGG(\1::text, '\2')"
            new_content, count = re.subn(pattern, replacement, content)
            
            if count > 0:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"✅ {path}: {count} corrección(es) aplicada(s)")

def create_postgres_helper():
    """Crea una función helper para PostgreSQL que emula GROUP_CONCAT si es necesario"""
    sql_path = "postgres_helper.sql"
    sql_content = """
-- Función helper para emular GROUP_CONCAT en PostgreSQL
-- Ejecutar en la base de datos PostgreSQL una sola vez

CREATE OR REPLACE FUNCTION group_concat(text, text)
RETURNS text AS $$
    SELECT string_agg($1, $2)
$$ LANGUAGE sql IMMUTABLE;

CREATE AGGREGATE group_concat(text) (
    SFUNC = textcat,
    STYPE = text,
    INITCOND = ''
);

-- Nota: Recomendamos usar STRING_AGG directamente en el código
-- Esta función es solo para compatibilidad temporal
"""
    with open(sql_path, 'w', encoding='utf-8') as f:
        f.write(sql_content)
    print(f"✅ Creado {sql_path} - Ejecutalo en PostgreSQL si necesitas compatibilidad")

def main():
    print("=" * 60)
    print("🔧 Actualizador automático de PediAcá para PostgreSQL")
    print("=" * 60)
    
    print("\n📋 Corrigiendo archivos...\n")
    
    fix_app_py()
    fix_ver_local_html()
    fix_other_files()
    create_postgres_helper()
    
    print("\n" + "=" * 60)
    print("✅ ¡Corrección completada!")
    print("\n📌 Próximos pasos:")
    print("   1. Subí los archivos modificados a tu servidor")
    print("   2. Ejecutá en PostgreSQL (opcional): psql DATABASE_URL < postgres_helper.sql")
    print("   3. Reiniciá el servidor: bash start.sh")
    print("=" * 60)

if __name__ == "__main__":
    main()