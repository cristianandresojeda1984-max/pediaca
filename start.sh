#!/bin/bash
echo "🚀 Iniciando PediAcá..."

mkdir -p static/uploads/logos static/uploads/banners \
         static/uploads/productos static/uploads/promociones \
         static/img static/fonts

# Inicializar DB (PostgreSQL o SQLite)
echo "📦 Inicializando base de datos..."
python init_db.py

echo "▶️  Iniciando servidor..."
gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120
