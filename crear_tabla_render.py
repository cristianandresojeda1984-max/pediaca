"""
crear_tabla_render.py — OBSOLETO.

Era un parche manual con la URL de conexión de Postgres de Render
hardcodeada en el archivo (no ideal tenerla en el repo). Superado por
`_init_configuraciones()` en app.py e `init_db.py`, que usan la variable
de entorno DATABASE_URL. Se deja como no-op y sin credenciales.
"""
print("⚠️  crear_tabla_render.py está obsoleto y ya no hace falta. "
      "La tabla 'configuraciones' se crea sola al arrancar la app, "
      "usando la variable de entorno DATABASE_URL.")
