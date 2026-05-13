#!/bin/bash
# start.sh — Se ejecuta en Render antes de levantar el servidor

echo "🚀 Iniciando PediAcá..."

# Crear la base de datos si no existe
if [ ! -f "pediaca.db" ]; then
    echo "📦 Creando base de datos..."
    python init_db.py <<< "s"
    echo "✅ Base de datos creada"
fi

# Crear carpetas de uploads
mkdir -p static/uploads/logos
mkdir -p static/uploads/banners
mkdir -p static/uploads/productos
mkdir -p static/uploads/promociones
mkdir -p static/img

# Copiar logo si existe
echo "▶️  Iniciando servidor..."
gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120
