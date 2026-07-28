# Desplegar PediAcá en DonWeb (Cloud Server)

Registro de la infraestructura contratada y guía de lo que falta para dejar PediAcá funcionando en `pediaca.ar`.

## Lo que ya está hecho

- Cuenta DonWeb creada e identidad verificada.
- Cloud Server contratado: **2 vCPU / 2 GB RAM / 10 GB NVMe**, $14.498/mes (IVA incluido), facturado en pesos.
- Sistema operativo: **Ubuntu 22.04 (Instalación Mínima)**.
- Acceso: usuario `root` con contraseña (generada y guardada — no se reenvía por email, así que si se pierde hay que resetearla desde el panel de DonWeb).
- ID del servicio en DonWeb: `6198875`.

## Estado actual (25/07/2026)

**La app ya está en producción y funcionando en `http://149.50.156.88`** (probado desde afuera, carga bien).

Completado:
- Servidor aprovisionado, IP pública `149.50.156.88`, puerto SSH 5859.
- PostgreSQL instalado, base `pediaca` y usuario `pediacauser` creados con permisos.
- Código clonado desde GitHub (`cristianandresojeda1984-max/pediaca`, rama `main`) en `/root/pediaca`.
- Entorno virtual creado, `requirements.txt` instalado sin errores.
- `/etc/pediaca.env` con `DATABASE_URL`, `SECRET_KEY` (generada al azar), `SETUP_KEY`, `ADMIN_PASSWORD`, `PORT=8000` — ya configurado (valores reales no se guardan acá).
- Base de datos inicializada (`init_db.py`) y migrada (`migrate_db.py`).
- Servicio `systemd` `pediaca.service` activo, habilitado para iniciar en cada reinicio del servidor.
- Nginx configurado como reverse proxy en el puerto 80, sitio activo (`sites-enabled/pediaca`).
- Usuario admin creado vía `/setup/<SETUP_KEY>` (`admin@pediaca.ar`, contraseña ya configurada — avisada por chat, no en este archivo).
- Puerto 80 accesible públicamente sin tocar ningún firewall extra de DonWeb.

## Dominio y HTTPS — completado

`pediaca.ar` está delegado a Cloudflare (nameservers `demi.ns.cloudflare.com` / `sam.ns.cloudflare.com`, gestionado en la cuenta de Cloudflare de Cristian). Los registros DNS (antes apuntaban al viejo deploy en Render) se actualizaron:

- `pediaca.ar` — A → `149.50.156.88` (proxied, nube naranja)
- `www.pediaca.ar` — CNAME → `pediaca.ar` (proxied)

SSL/TLS de Cloudflare configurado en modo **Flexible** (visitante ↔ Cloudflare va cifrado con el certificado de Cloudflare; Cloudflare ↔ servidor de origen va por HTTP plano, que es justo lo que nginx sirve en el puerto 80). No hizo falta correr certbot en el servidor — Cloudflare provee el candado gratis. Probado y funcionando: `https://pediaca.ar` y `https://www.pediaca.ar`.

(Nota: si en el futuro se quiere subir a modo "Full", primero hay que instalar un certificado en nginx — por ejemplo con certbot — para que Cloudflare pueda validar HTTPS también contra el origen.)

## Backups y actualizaciones

- Backup automático diario de Postgres a las 3am vía `/etc/cron.d/pediacabackup` (dump comprimido en `/root/backups`, se borran los de más de 14 días).
- Para subir cambios de código: `git push` desde la compu, y en el servidor `cd /root/pediaca && git pull` + reinstalar dependencias si cambiaron + `systemctl restart pediaca`.

### Nota técnica sobre la consola web de DonWeb

El teclado remoto de la consola VNC de DonWeb no transmite bien mayúsculas ni símbolos con Shift (`: { } $ | > < &`, etc.) — es una limitación conocida de esa consola, confirmada por el soporte de DonWeb. Para sortearlo: los archivos con símbolos especiales (config de nginx, servicio systemd) se subieron por GitHub y se bajaron con `git pull`; para escribir `/etc/pediaca.env` (con la `:` de la URL de Postgres) se usó un script chico (`deploy/write_hex.py`) que decodifica contenido pasado en hexadecimal, evitando escribir símbolos prohibidos directamente en la consola.

## Acceso al servidor y credenciales (actualizado 27/07/2026)

**Incidente:** entre el 25 y el 27/07/2026 se perdió el acceso root al servidor (nunca se había guardado la contraseña original en un lugar seguro, y el botón de reset de contraseña del panel de DonWeb + la consola VNC tuvieron fallas simultáneas que extendieron la salida de servicio varias horas). Detalle completo conversado por chat. Se resolvió el 27/07 reseteando la contraseña desde el panel de DonWeb.

**Estado actual de los accesos:**

- **Usuario:** `root`
- **Host:** `149.50.156.88` (o `vps-6198875-x.dattaweb.com`), **puerto SSH: `5859`** (no es el 22 por defecto)
- **Contraseña root:** rotada el 27/07/2026 — guardada en el password manager personal de Cristian. No está escrita en ningún archivo del proyecto ni en ningún otro lado.
- **Clave SSH (acceso alternativo, agregado 27/07/2026):** par de claves ed25519 generado en la PC de Cristian (`C:\Users\Julirina\.ssh\pediaca_key` / `pediaca_key.pub`). La pública ya está instalada en `~/.ssh/authorized_keys` del servidor. Login sin contraseña: `ssh -p 5859 -i $HOME\.ssh\pediaca_key root@149.50.156.88`. **Recomendado:** hacer una copia de `pediaca_key` (la privada) en el password manager de Cristian, por si se pierde o se formatea esa PC — hoy es la única copia.
- **Consola VNC del panel DonWeb:** sigue teniendo un bug conocido (no transmite bien Shift/mayúsculas/símbolos — ver nota técnica más abajo). Usarla solo como último recurso si SSH no está disponible; para escribir algo con símbolos ahí, mejor bajarlo por `git pull` o pegarlo generado por script, no tipearlo a mano.

**Si se vuelve a perder el acceso:** con la clave SSH ya instalada, no debería depender más pura y exclusivamente de la contraseña + la consola VNC. Si aun así se pierde todo acceso, el camino es: panel DonWeb → Cloud Servers → Gestionar → Software y Accesos → resetear contraseña (requiere apagar el servidor un momento) → Consola VNC solo si SSH no conecta.

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
