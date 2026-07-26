# Desplegar PediAcá en DonWeb (Cloud Server)

Registro de la infraestructura contratada y guía de lo que falta para dejar PediAcá funcionando en `pediaca.ar`.

## Lo que ya está hecho

- Cuenta DonWeb creada e identidad verificada.
- Cloud Server contratado: **2 vCPU / 2 GB RAM / 10 GB NVMe**, $14.498/mes (IVA incluido), facturado en pesos.
- Sistema operativo: **Ubuntu 22.04 (Instalación Mínima)**.
- Acceso: usuario `root` con contraseña (generada y guardada — no se reenvía por email, así que si se pierde hay que resetearla desde el panel de DonWeb).
- ID del servicio en DonWeb: `6198875`.

## Lo que falta

1. Esperar que el servidor termine de aprovisionarse y tenga IP pública asignada (columna "Información" del panel).
2. Conectarse por SSH (o por la "Consola" web que trae el panel de DonWeb, sin necesidad de cliente SSH).
3. Abrir los puertos 80/443 en el **Firewall** del panel de DonWeb (tiene una sección propia para esto, más simple que Oracle).
4. Instalar dependencias: Python, nginx, PostgreSQL, certbot.
5. Configurar PostgreSQL (base + usuario).
6. Subir el código de PediAcá.
7. Entorno virtual + `requirements.txt`.
8. Variables de entorno (`SECRET_KEY`, `SETUP_KEY`, `ADMIN_PASSWORD`, `DATABASE_URL`).
9. Servicio `systemd` con gunicorn (reinicio automático).
10. Nginx como reverse proxy.
11. Apuntar el dominio `pediaca.ar` (registro DNS tipo A a la IP del servidor) y pedir certificado HTTPS gratis con certbot.
12. Crear el usuario admin vía `/setup/<clave>`.
13. Backups automáticos diarios de la base.

## Comandos de referencia (se van a ir ejecutando a medida que avancemos)

```bash
# Sistema
apt update && apt upgrade -y
apt install -y python3-venv python3-pip nginx postgresql postgresql-contrib git certbot python3-certbot-nginx

# Postgres
sudo -u postgres psql -c "CREATE DATABASE pediaca;"
sudo -u postgres psql -c "CREATE USER pediaca_user WITH PASSWORD 'CAMBIAR';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE pediaca TO pediaca_user;"

# App
cd /root
git clone <repo> pediaca   # o subir por scp/rsync si no hay repo
cd pediaca
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Variables de entorno (`/etc/pediaca.env`):

```
DATABASE_URL=postgresql://pediaca_user:CAMBIAR@localhost/pediaca
SECRET_KEY=<generada con secrets.token_hex(32)>
SETUP_KEY=<clave elegida>
ADMIN_PASSWORD=<contraseña del admin>
PORT=8000
```

Servicio `systemd` (`/etc/systemd/system/pediaca.service`):

```ini
[Unit]
Description=PediAca Flask App
After=network.target postgresql.service

[Service]
User=root
WorkingDirectory=/root/pediaca
EnvironmentFile=/etc/pediaca.env
ExecStart=/root/pediaca/venv/bin/gunicorn app:app --bind 127.0.0.1:8000 --workers 2 --timeout 120
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Nginx (`/etc/nginx/sites-available/pediaca`):

```nginx
server {
    listen 80;
    server_name pediaca.ar www.pediaca.ar;

    client_max_body_size 20M;

    location /static/ {
        alias /root/pediaca/static/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

HTTPS:

```bash
certbot --nginx -d pediaca.ar -d www.pediaca.ar
```

Backup diario (crontab):

```
0 3 * * * mkdir -p /root/backups && PGPASSWORD='CAMBIAR' pg_dump -U pediaca_user -h localhost pediaca | gzip > /root/backups/pediaca_$(date +\%Y\%m\%d).sql.gz && find /root/backups -mtime +14 -delete
```

---

Este documento se va a ir actualizando a medida que se completen los pasos, con los valores reales (contraseñas no se guardan acá en texto plano — se referencian como "ya configurado").
