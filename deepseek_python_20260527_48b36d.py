#!/usr/bin/env python3
"""
FIX TOTAL PROMOCIONES
- Elimina modales fantasma que mostraban "Cargando promociones"
- Agrega columnas faltantes en la BD
- Corrige las rutas de promociones en app.py
- Actualiza el panel del restaurante para mostrar/crear promociones correctamente
"""

import os
import re
import sqlite3
import shutil

# ============================================================
# 1. CORREGIR BASE DE DATOS
# ============================================================
def fix_database():
    db_path = "pediaca.db"
    if not os.path.exists(db_path):
        print("⚠️ No se encontró pediaca.db, omitiendo...")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(promociones)")
    columns = [c[1] for c in cursor.fetchall()]
    
    if 'tipo_descuento' not in columns:
        cursor.execute("ALTER TABLE promociones ADD COLUMN tipo_descuento TEXT DEFAULT 'porcentaje'")
        print("✅ Columna 'tipo_descuento' agregada")
    if 'descuento_monto' not in columns:
        cursor.execute("ALTER TABLE promociones ADD COLUMN descuento_monto INTEGER DEFAULT 0")
        print("✅ Columna 'descuento_monto' agregada")
    
    conn.commit()
    conn.close()

# ============================================================
# 2. ELIMINAR MODALES FANTASMA DE TODOS LOS TEMPLATES
# ============================================================
def eliminar_modales_fantasma():
    templates = ["base.html", "home.html", "ver_local.html"]
    for tpl in templates:
        path = os.path.join("templates", tpl)
        if not os.path.exists(path):
            continue
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Eliminar div modal y scripts relacionados
        content = re.sub(r'<div class="promo-modal-overlay"[^>]*>.*?</div>\s*</div>\s*<script>.*?mostrarPromociones.*?</script>', '', content, flags=re.DOTALL)
        content = re.sub(r'<button[^>]*onclick="mostrarPromociones\(\)"[^>]*>.*?</button>', '', content, flags=re.DOTALL)
        content = re.sub(r'<script>\s*async function mostrarPromociones.*?</script>', '', content, flags=re.DOTALL)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Modales eliminados en {tpl}")

# ============================================================
# 3. CORREGIR FUNCIONES EN APP.PY
# ============================================================
def fix_app_py():
    app_path = "app.py"
    if not os.path.exists(app_path):
        print("❌ No se encuentra app.py")
        return
    
    with open(app_path, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Reemplazar la función promocion_nueva
    nueva_nueva = '''@app.route("/mi-local/promocion/nueva", methods=["POST"])
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
    
    # Reemplazar promocion_editar
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
    
    # Reemplazar en el archivo usando regex más seguro
    # Buscar el bloque actual de promocion_nueva y reemplazarlo
    pattern_nueva = r'@app\.route\("/mi-local/promocion/nueva", methods=\["POST"\]\)\s*\n@login_required\s*\n@rol_required\("restaurante"\)\s*\ndef promocion_nueva\(\):.*?(?=@app\.route|$)'
    if re.search(pattern_nueva, contenido, re.DOTALL):
        contenido = re.sub(pattern_nueva, nueva_nueva + '\n\n', contenido, flags=re.DOTALL)
        print("✅ promocion_nueva actualizada")
    
    pattern_editar = r'@app\.route\("/mi-local/promocion/<int:promo_id>/editar", methods=\["POST"\]\)\s*\n@login_required\s*\n@rol_required\("restaurante"\)\s*\ndef promocion_editar\(promo_id\):.*?(?=@app\.route|$)'
    if re.search(pattern_editar, contenido, re.DOTALL):
        contenido = re.sub(pattern_editar, nueva_editar + '\n\n', contenido, flags=re.DOTALL)
        print("✅ promocion_editar actualizada")
    
    # Asegurar que en restaurante_panel se pase la variable promociones
    if 'promociones=promociones' not in contenido:
        # Modificar la línea render_template
        patron_render = r'render_template\("restaurante_panel\.html",(.*?)\)'
        def agregar_promos(match):
            args = match.group(1)
            if 'promociones=' not in args:
                args += ', promociones=promociones'
            return f'render_template("restaurante_panel.html",{args})'
        contenido = re.sub(patron_render, agregar_promos, contenido, flags=re.DOTALL)
        print("✅ Se agregó 'promociones' al render_template de restaurante_panel")
    
    with open(app_path, 'w', encoding='utf-8') as f:
        f.write(contenido)

# ============================================================
# 4. ACTUALIZAR LA SECCIÓN DE PROMOCIONES EN RESTAURANTE_PANEL.HTML
# ============================================================
def fix_restaurante_panel():
    path = "templates/restaurante_panel.html"
    if not os.path.exists(path):
        print("❌ No se encuentra restaurante_panel.html")
        return
    
    with open(path, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Verificar si ya existe la sección mejorada
    if 'tipo_descuento' in contenido and 'tipoDescuento' in contenido:
        print("✅ El panel ya tiene la sección de promociones actualizada")
        return
    
    # Reemplazar el bloque completo de sec-promociones
    nueva_seccion = '''
  <div class="seccion" id="sec-promociones">
    <div class="card">
      <div class="card-titulo">🎉 Crear nueva promoción</div>
      <form method="POST" action="/mi-local/promocion/nueva" enctype="multipart/form-data">
        <div class="form-group">
          <label>Título *</label>
          <input class="form-control" name="titulo" required>
        </div>
        <div class="form-group">
          <label>Descripción</label>
          <textarea class="form-control" name="descripcion" rows="2"></textarea>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label>Tipo de descuento</label>
            <select class="form-control" name="tipo_descuento" id="tipoDescuento" onchange="toggleTipoDescuento()">
              <option value="porcentaje">% Porcentaje</option>
              <option value="monto">💰 Monto fijo</option>
            </select>
          </div>
          <div class="form-group" id="campoPorcentaje">
            <label>% Descuento</label>
            <input class="form-control" type="number" name="descuento_pct" min="0" max="100" value="0">
          </div>
          <div class="form-group" id="campoMonto" style="display:none;">
            <label>$ Monto fijo</label>
            <input class="form-control" type="number" name="descuento_monto" min="0" value="0">
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label>Válida desde</label>
            <input class="form-control" type="date" name="fecha_inicio">
          </div>
          <div class="form-group">
            <label>Válida hasta</label>
            <input class="form-control" type="date" name="fecha_fin">
          </div>
        </div>
        <div class="form-group">
          <label>Imagen (opcional)</label>
          <input class="form-control" type="file" name="imagen" accept="image/*">
        </div>
        <button class="btn btn-primary btn-block" type="submit">🎁 Crear promoción</button>
      </form>
    </div>

    <div class="card">
      <div class="card-titulo">📋 Mis promociones</div>
      {% if promociones %}
        {% for promo in promociones %}
          <div style="border:1px solid #ddd; border-radius:10px; padding:12px; margin-bottom:12px;">
            <div style="font-weight:800;">{{ promo.titulo }}</div>
            {% if promo.descripcion %}<div style="font-size:0.85rem; color:#666;">{{ promo.descripcion }}</div>{% endif %}
            <div style="margin-top:8px;">
              {% if promo.tipo_descuento == 'porcentaje' and promo.descuento_pct > 0 %}
                <span style="background:#EA580C; color:white; padding:2px 10px; border-radius:99px;">{{ promo.descuento_pct }}% OFF</span>
              {% elif promo.tipo_descuento == 'monto' and promo.descuento_monto > 0 %}
                <span style="background:#EA580C; color:white; padding:2px 10px; border-radius:99px;">${{ promo.descuento_monto }} OFF</span>
              {% endif %}
              <span style="background:{% if promo.activa %}#27AE60{% else %}#95A5A6{% endif %}; color:white; padding:2px 10px; border-radius:99px;">
                {{ 'Activa' if promo.activa else 'Inactiva' }}
              </span>
            </div>
            <div style="margin-top:10px;">
              <a href="/mi-local/promocion/{{ promo.id }}/toggle" style="font-size:0.75rem; margin-right:8px;">{% if promo.activa %}Desactivar{% else %}Activar{% endif %}</a>
              <form method="POST" action="/mi-local/promocion/{{ promo.id }}/eliminar" style="display:inline;" onsubmit="return confirm('¿Eliminar esta promoción?')">
                <button type="submit" style="background:#FADBD8; border:none; padding:4px 12px; border-radius:99px; cursor:pointer;">Eliminar</button>
              </form>
            </div>
          </div>
        {% endfor %}
      {% else %}
        <div style="text-align:center; padding:40px; color:#999;">
          <div style="font-size:3rem;">🎁</div>
          <div>No hay promociones aún. Creá una con el formulario de arriba.</div>
        </div>
      {% endif %}
    </div>
  </div>

<script>
function toggleTipoDescuento() {
  const tipo = document.getElementById('tipoDescuento').value;
  const campoPorcentaje = document.getElementById('campoPorcentaje');
  const campoMonto = document.getElementById('campoMonto');
  if (tipo === 'porcentaje') {
    campoPorcentaje.style.display = '';
    campoMonto.style.display = 'none';
  } else {
    campoPorcentaje.style.display = 'none';
    campoMonto.style.display = '';
  }
}
</script>'''
    
    # Buscar la sección actual y reemplazarla
    patron_seccion = r'(<div class="seccion" id="sec-promociones">)(.*?)(</div><!-- /promociones -->)'
    if re.search(patron_seccion, contenido, re.DOTALL):
        nuevo_contenido = re.sub(patron_seccion, nueva_seccion, contenido, flags=re.DOTALL)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(nuevo_contenido)
        print("✅ Sección de promociones actualizada en restaurante_panel.html")
    else:
        print("⚠️ No se encontró la sección sec-promociones. Revisá el archivo manualmente.")

# ============================================================
# 5. MAIN
# ============================================================
def main():
    print("=" * 60)
    print("🔧 FIX TOTAL DE PROMOCIONES")
    print("=" * 60)
    
    print("\n📋 Acciones:")
    print("   • Elimina modales flotantes de promociones")
    print("   • Corrige la base de datos")
    print("   • Actualiza las funciones en app.py")
    print("   • Renueva el panel de promociones en el restaurante")
    print("\n🔍 Ejecutando...\n")
    
    fix_database()
    eliminar_modales_fantasma()
    fix_app_py()
    fix_restaurante_panel()
    
    print("\n" + "=" * 60)
    print("✨ ¡FIX COMPLETADO!")
    print("   📌 Reiniciá el servidor: python app.py")
    print("   🎁 Ahora las promociones se guardan y se muestran en el panel")
    print("=" * 60)

if __name__ == "__main__":
    main()