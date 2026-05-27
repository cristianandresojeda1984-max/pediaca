#!/usr/bin/env python3
"""
Corrector de promociones - Versión Python puro
"""

import os
import sqlite3
import re

def actualizar_bd():
    """Actualiza la estructura de la tabla promociones usando Python"""
    ruta_db = "pediaca.db"
    
    if not os.path.exists(ruta_db):
        print(f"❌ No se encuentra {ruta_db}")
        print("   Asegurate de estar en la carpeta correcta")
        return False
    
    conn = sqlite3.connect(ruta_db)
    cursor = conn.cursor()
    
    # Obtener columnas actuales
    cursor.execute("PRAGMA table_info(promociones)")
    columnas = [col[1] for col in cursor.fetchall()]
    
    print(f"📋 Columnas actuales en promociones: {columnas}")
    
    # Agregar columna tipo_descuento si no existe
    if 'tipo_descuento' not in columnas:
        try:
            cursor.execute("ALTER TABLE promociones ADD COLUMN tipo_descuento TEXT DEFAULT 'porcentaje'")
            print("✅ Columna 'tipo_descuento' agregada")
        except Exception as e:
            print(f"⚠️ Error al agregar tipo_descuento: {e}")
    
    # Agregar columna descuento_monto si no existe
    if 'descuento_monto' not in columnas:
        try:
            cursor.execute("ALTER TABLE promociones ADD COLUMN descuento_monto INTEGER DEFAULT 0")
            print("✅ Columna 'descuento_monto' agregada")
        except Exception as e:
            print(f"⚠️ Error al agregar descuento_monto: {e}")
    
    # Verificar que la tabla existe y tiene datos
    cursor.execute("SELECT COUNT(*) FROM promociones")
    count = cursor.fetchone()[0]
    print(f"📊 Hay {count} promociones en la base de datos")
    
    conn.commit()
    conn.close()
    return True

def corregir_app_py():
    """Corrige las funciones de promociones en app.py"""
    ruta = "app.py"
    
    if not os.path.exists(ruta):
        print(f"❌ No se encuentra {ruta}")
        return False
    
    with open(ruta, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Verificar si las funciones ya están corregidas
    if 'tipo_descuento' in contenido and 'descuento_monto' in contenido:
        print("✅ app.py ya tiene las funciones corregidas")
        return True
    
    # Buscar la función promocion_nueva y reemplazarla
    patron_nueva = r'(@app\.route\("/mi-local/promocion/nueva", methods=\["POST"\]\).*?def promocion_nueva\(\):.*?)(?=@app\.route)'
    
    nueva_funcion = '''@app.route("/mi-local/promocion/nueva", methods=["POST"])
@login_required
@rol_required("restaurante")
def promocion_nueva():
    restaurante = get_restaurante_aprobado()
    if not restaurante:
        return redirect(url_for("restaurante_panel"))
    
    titulo = request.form.get("titulo", "").strip()
    descripcion = request.form.get("descripcion", "").strip()
    tipo_descuento = request.form.get("tipo_descuento", "porcentaje")
    descuento_pct = int(request.form.get("descuento_pct", 0) or 0)
    descuento_monto = int(request.form.get("descuento_monto", 0) or 0)
    fecha_inicio = request.form.get("fecha_inicio") or None
    fecha_fin = request.form.get("fecha_fin") or None
    archivo = request.files.get("imagen")
    imagen_url = guardar_imagen(archivo, "promociones") if archivo and archivo.filename else None
    
    if not titulo:
        flash("El título es obligatorio.", "danger")
        return redirect(url_for("restaurante_panel") + "#sec-promociones")
    
    execute("""
        INSERT INTO promociones
            (restaurante_id, titulo, descripcion, imagen_url, tipo_descuento,
             descuento_pct, descuento_monto, fecha_inicio, fecha_fin, activa)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
    """, (restaurante["id"], titulo, descripcion, imagen_url, tipo_descuento,
          descuento_pct, descuento_monto, fecha_inicio, fecha_fin))
    
    flash(f"Promoción '{titulo}' creada.", "success")
    return redirect(url_for("restaurante_panel") + "#sec-promociones")'''
    
    # Reemplazar
    if re.search(patron_nueva, contenido, re.DOTALL):
        contenido = re.sub(patron_nueva, nueva_funcion + '\n\n', contenido, flags=re.DOTALL)
        print("✅ Función promocion_nueva actualizada")
    else:
        print("⚠️ No se encontró la función promocion_nueva para reemplazar")
    
    # Corregir promocion_editar
    patron_editar = r'(@app\.route\("/mi-local/promocion/<int:promo_id>/editar", methods=\["POST"\]\).*?def promocion_editar\(promo_id\):.*?)(?=@app\.route)'
    
    nueva_editar = '''@app.route("/mi-local/promocion/<int:promo_id>/editar", methods=["POST"])
@login_required
@rol_required("restaurante")
def promocion_editar(promo_id):
    restaurante = get_restaurante_aprobado()
    if not restaurante:
        return redirect(url_for("restaurante_panel"))
    
    titulo = request.form.get("titulo", "").strip()
    descripcion = request.form.get("descripcion", "").strip()
    tipo_descuento = request.form.get("tipo_descuento", "porcentaje")
    descuento_pct = int(request.form.get("descuento_pct", 0) or 0)
    descuento_monto = int(request.form.get("descuento_monto", 0) or 0)
    fecha_inicio = request.form.get("fecha_inicio") or None
    fecha_fin = request.form.get("fecha_fin") or None
    archivo = request.files.get("imagen")
    
    promo = query("SELECT * FROM promociones WHERE id=? AND restaurante_id=?",
                  (promo_id, restaurante["id"]), one=True)
    if not promo:
        return redirect(url_for("restaurante_panel"))
    
    nueva_imagen = guardar_imagen(archivo, "promociones") if archivo and archivo.filename else promo["imagen_url"]
    
    execute("""
        UPDATE promociones SET
            titulo=?, descripcion=?, imagen_url=?,
            tipo_descuento=?, descuento_pct=?, descuento_monto=?,
            fecha_inicio=?, fecha_fin=?
        WHERE id=? AND restaurante_id=?
    """, (titulo, descripcion, nueva_imagen, tipo_descuento,
          descuento_pct, descuento_monto, fecha_inicio, fecha_fin,
          promo_id, restaurante["id"]))
    
    flash("Promoción actualizada.", "success")
    return redirect(url_for("restaurante_panel") + "#sec-promociones")'''
    
    if re.search(patron_editar, contenido, re.DOTALL):
        contenido = re.sub(patron_editar, nueva_editar + '\n\n', contenido, flags=re.DOTALL)
        print("✅ Función promocion_editar actualizada")
    
    # Guardar cambios
    with open(ruta, 'w', encoding='utf-8') as f:
        f.write(contenido)
    
    return True

def agregar_js_template():
    """Agrega el JavaScript para toggle de descuento en el template"""
    ruta = "templates/restaurante_panel.html"
    
    if not os.path.exists(ruta):
        print(f"❌ No se encuentra {ruta}")
        return
    
    with open(ruta, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Verificar si ya tiene el toggle
    if 'toggleTipoDescuento' in contenido:
        print("✅ El template ya tiene el toggle de descuento")
        return
    
    # JavaScript para agregar
    js_toggle = '''
<script>
function toggleTipoDescuento() {
    var tipo = document.getElementById('tipoDescuento').value;
    var campoPorcentaje = document.getElementById('campoPorcentaje');
    var campoMonto = document.getElementById('campoMonto');
    if (tipo === 'porcentaje') {
        if (campoPorcentaje) campoPorcentaje.style.display = '';
        if (campoMonto) campoMonto.style.display = 'none';
    } else {
        if (campoPorcentaje) campoPorcentaje.style.display = 'none';
        if (campoMonto) campoMonto.style.display = '';
    }
}
</script>
'''
    
    # Agregar antes de </body>
    if '</body>' in contenido:
        contenido = contenido.replace('</body>', js_toggle + '\n</body>')
        with open(ruta, 'w', encoding='utf-8') as f:
            f.write(contenido)
        print("✅ JavaScript toggle agregado al template")
    else:
        print("⚠️ No se encontró </body> en el template")

def main():
    print("=" * 60)
    print("🔧 CORRECTOR DE PROMOCIONES (Python puro)")
    print("=" * 60)
    
    print("\n📋 Acciones:")
    print("   • Actualiza la base de datos (agrega columnas)")
    print("   • Corrige las funciones en app.py")
    print("   • Agrega JavaScript al template")
    
    print("\n🔍 Procesando...\n")
    
    # 1. Actualizar BD
    if actualizar_bd():
        print("  ✅ Base de datos actualizada")
    
    # 2. Corregir app.py
    if corregir_app_py():
        print("  ✅ app.py corregido")
    
    # 3. Agregar JS al template
    agregar_js_template()
    
    print("\n" + "=" * 60)
    print("✨ ¡CORRECCIÓN COMPLETADA!")
    print("   📌 Reiniciá el servidor: python app.py")
    print("   🎁 Ahora las promociones deberían guardarse correctamente")
    print("=" * 60)

if __name__ == "__main__":
    main()