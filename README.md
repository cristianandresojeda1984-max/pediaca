# PediAcá — Deploy en Render

## Estructura del proyecto

```
pediaca/
├── app.py                  # Backend Flask principal
├── init_db.py              # Crea la base de datos
├── flyer.py                # Generador de flyers con QR
├── start.sh                # Script de inicio para Render
├── requirements.txt        # Dependencias Python
├── render.yaml             # Configuración de Render
├── static/
│   ├── img/
│   │   └── logo_pediaca.png   ← Copiar el logo acá
│   └── uploads/            # Fotos subidas por los locales
└── templates/              # Páginas HTML
    ├── base.html
    ├── home.html
    ├── login.html
    ├── registro.html
    ├── ver_local.html
    ├── restaurante_panel.html
    ├── restaurante_espera.html
    ├── admin_panel.html
    ├── cadete_panel.html
    └── cliente_panel.html
```

## Pasos para subir a Render

### 1. Subir el código a GitHub

```bash
# En tu PC, en la carpeta del proyecto:
git init
git add .
git commit -m "PediAcá v1.0"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/pediaca.git
git push -u origin main
```

### 2. Crear el servicio en Render

1. Entrá a **render.com** y creá una cuenta (gratis)
2. → New → Web Service
3. Conectá tu repositorio de GitHub
4. Render detecta el `render.yaml` automáticamente
5. Hacé clic en **Deploy**

### 3. Variables de entorno (en Render)

| Variable | Valor |
|---|---|
| `SECRET_KEY` | Una clave larga y aleatoria |
| `DB_PATH` | `pediaca.db` |

### 4. Crear el admin

Después del primer deploy, en la consola de Render:
```bash
python -c "
from werkzeug.security import generate_password_hash
import sqlite3
conn = sqlite3.connect('pediaca.db')
conn.execute('''INSERT INTO usuarios (nombre, apellido, email, telefono, password_hash, rol)
VALUES (?, ?, ?, ?, ?, ?)''',
('Cristian', 'Ojeda', 'admin@pediaca.ar', '3417523674',
generate_password_hash('TU_PASSWORD'), 'admin'))
conn.commit()
conn.close()
print('Admin creado')
"
```

### 5. Subir el logo

Copiar `logo_pediaca.png` a la carpeta `static/img/` del proyecto antes del deploy.

## ⚠️ Importante sobre el almacenamiento

Render en el plan gratuito **no persiste archivos** entre deploys.
Esto significa que las fotos subidas por los locales se pierden al hacer un nuevo deploy.

**Para producción real**, usar un servicio de almacenamiento externo:
- **Cloudinary** (gratis hasta 25GB) — recomendado
- AWS S3
- Backblaze B2

Por ahora para la demo funciona perfectamente.

## Acceso al sistema

| Rol | URL |
|---|---|
| Clientes | `pediaca.ar/` |
| Locales | `pediaca.ar/mi-local` |
| Cadetes | `pediaca.ar/mi-panel-cadete` |
| Admin | `pediaca.ar/admin` |
