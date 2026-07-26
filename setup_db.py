"""
setup_db.py — OBSOLETO.

Este script era un parche manual para crear la tabla `configuraciones`
directo en la base de Render. Ya no hace falta: `app.py` la crea sola al
arrancar (ver `_init_configuraciones()`) y `init_db.py` la incluye en el
esquema completo. Se deja este archivo como no-op para no romper nada que
todavía lo invoque, pero no debería usarse.
"""
print("⚠️  setup_db.py está obsoleto. La tabla 'configuraciones' ahora se crea "
      "automáticamente al arrancar la app (ver app.py) y en init_db.py. "
      "Este script no hace nada.")
