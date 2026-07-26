# Desplegar PediAcá en Oracle Cloud (Always Free)

Guía paso a paso para levantar PediAcá en una VM gratuita para siempre de Oracle Cloud, sin que se duerma ni tenga límite de tiempo/CPU diario. Es más trabajo inicial que un botón de "deploy" tipo Render, pero después de configurado queda funcionando solo.

No hace falta correr nada de esto en tu compu — todo se ejecuta conectado por SSH a la VM de Oracle.

---

## 0. Qué vamos a armar

- Una VM Ubuntu (Ampere/ARM, 2 OCPU / 12 GB RAM, gratis para siempre).
- PostgreSQL corriendo en la misma VM (la app ya soporta Postgres, solo hay que apuntarla).
- Gunicorn corriendo la app como servicio de sistema (`systemd`), que se reinicia solo si se cae o si reiniciás el servidor.
- Nginx como reverse proxy adelante, con HTTPS gratis (Let's Encrypt).

---

## 1. Crear la cuenta Oracle Cloud

1. Andá a https://www.oracle.com/cloud/free/ y registrate.
2. Te va a pedir una tarjeta para verificar identidad. **No te cobra nada** mientras te quedes en los recursos "Always Free" (los que vamos a usar acá).
3. Elegí una región cercana (por ejemplo, alguna de Brasil o Chile si estás en Argentina — la disponibilidad de VMs ARM gratis varía por región, si una región dice "Out of capacity" probá con otra).

---

## 2. Crear la VM (Compute Instance)

1. En el menú, andá a **Compute → Instances → Create Instance**.
2. **Image**: Canonical Ubuntu 22.04 (Minimal si aparece la opción).
3. **Shape**: hacé clic en "Change shape" → pestaña **Ampere** → elegí `VM.Standard.A1.Flex` → subí los sliders a **2 OCPU / 12 GB RAM** (o los valores máximos "Always Free" que te muestre — pueden variar levemente según cuándo leas esto).
4. **Boot volume**: dejá el default (hasta 200GB entran en el free tier, con 50GB alcanza de sobra).
5. **SSH keys**: si no tenés un par de claves, elegí "Generate a key pair for me" y descargá la clave privada (`.key`). Si ya tenés una, subí tu clave pública.
6. **Networking**: dejá que cree una VCN nueva con subnet pública y que te asigne una **IP pública**. Anotá esa IP.
7. Creá la instancia y esperá a que el estado pase a "Running" (1-2 minutos).

---

## 3. Abrir los puertos (esto se olvida siempre y después no entra nada)

Oracle bloquea el tráfico en dos capas: la Security List de la nube, y el firewall interno de Ubuntu. Hay que abrir en las dos.

**A. Security List (en la consola de Oracle):**

1. Andá a la VCN de tu instancia → **Security Lists** → la lista default → **Add Ingress Rules**.
2. Agregá dos reglas, ambas con source `0.0.0.0/0`:
   - Puerto **80** (HTTP)
   - Puerto **443** (HTTPS)
   - (el 22 de SSH ya debería estar abierto por default)

**B. Firewall interno de Ubuntu** (lo hacemos por SSH en el paso siguiente).

---

## 4. Conectarte por SSH

Desde tu compu (PowerShell):

```powershell
ssh -i "ruta\a\tu-clave.key" ubuntu@TU_IP_PUBLICA
```

Si Windows se queja de permisos de la clave, click derecho al archivo `.key` → Propiedades → Seguridad → dejá que solo tu usuario tenga acceso.

---

## 5. Preparar el servidor

Ya conectado por SSH, corré todo esto:

```bash
sudo apt update && sudo apt upgrade -y

# Firewall interno: abrir HTTP/HTTPS/SSH
sudo iptables -I INPUT -p tcp --dport 80 -j ACCEPT
sudo iptables -I INPUT -p tcp --dport 443 -j ACCEPT
sudo netfilter-persistent save 2>/dev/null || sudo apt install -y iptables-persistent

# Paquetes necesarios
sudo apt install -y python3-venv python3-pip nginx postgresql postgresql-contrib git certbot python3-certbot-nginx
```

---

## 6. Configurar PostgreSQL

```bash
sudo -u postgres psql
```

Dentro del prompt de psql:

```sql
CREATE DATABASE pediaca;
CREATE USER pediaca_user WITH PASSWORD 'ELEGÍ-UNA-CONTRASEÑA-FUERTE-ACÁ';
GRANT ALL PRIVILEGES ON DATABASE pediaca TO pediaca_user;
\q
```

---

## 7. Subir el código de PediAcá

**Opción A — si tenés el proyecto en GitHub:**

```bash
cd /home/ubuntu
git clone https://github.com/tu-usuario/pediaca.git
cd pediaca
```

**Opción B — si no tenés GitHub todavía:** avisame y armamos un repo privado, o subimos el código directo por `scp` desde tu compu:

```powershell
# Desde PowerShell, en tu compu:
scp -i "ruta\a\tu-clave.key" -r "C:\Users\Julirina\Desktop\Cristian\Proyectos\pediaca" ubuntu@TU_IP_PUBLICA:/home/ubuntu/
```

---

## 8. Entorno Python

```bash
cd /home/ubuntu/pediaca
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 9. Variables de entorno

Creá el archivo de entorno que va a leer el servicio:

```bash
sudo nano /etc/pediaca.env
```

Pegá esto (reemplazando los valores marcados):

```
DATABASE_URL=postgresql://pediaca_user:ELEGÍ-UNA-CONTRASEÑA-FUERTE-ACÁ@localhost/pediaca
SECRET_KEY=GENERÁ-UNA-CLAVE-LARGA-Y-ALEATORIA-ACÁ
SETUP_KEY=ELEGÍ-UNA-CLAVE-PARA-CREAR-EL-ADMIN
ADMIN_PASSWORD=ELEGÍ-LA-CONTRASEÑA-DEL-ADMIN
PORT=8000
```

Para generar una `SECRET_KEY` random, podés correr en la terminal:

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

Guardá el archivo (Ctrl+O, Enter, Ctrl+X en nano).

---

## 10. Servicio systemd (para que corra siempre y se reinicie solo)

```bash
sudo nano /etc/systemd/system/pediaca.service
```

Contenido:

```ini
[Unit]
Description=PediAca Flask App
After=network.target postgresql.service

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/pediaca
EnvironmentFile=/etc/pediaca.env
ExecStart=/home/ubuntu/pediaca/venv/bin/gunicorn app:app --bind 127.0.0.1:8000 --workers 2 --timeout 120
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Antes de arrancarlo, corré una vez a mano la inicialización de la base (crea las tablas):

```bash
cd /home/ubuntu/pediaca
source venv/bin/activate
set -a; source /etc/pediaca.env; set +a
python init_db.py
python migrate_db.py
deactivate
```

Ahora activá el servicio:

```bash
sudo systemctl daemon-reload
sudo systemctl enable pediaca
sudo systemctl start pediaca
sudo systemctl status pediaca
```

Si algo falla, mirá los logs con: `sudo journalctl -u pediaca -f`

---

## 11. Nginx como reverse proxy

```bash
sudo nano /etc/nginx/sites-available/pediaca
```

Contenido:

```nginx
server {
    listen 80;
    server_name TU_DOMINIO_O_IP;

    client_max_body_size 20M;

    location /static/ {
        alias /home/ubuntu/pediaca/static/;
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

Activarlo:

```bash
sudo ln -s /etc/nginx/sites-available/pediaca /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

En este punto, entrando a `http://TU_IP_PUBLICA` en el navegador ya debería cargar PediAcá.

---

## 12. Dominio + HTTPS (recomendado)

Un candado (HTTPS) es importante porque el navegador va a bloquear cosas como las notificaciones push sin él.

- **Si tenés un dominio propio**: creá un registro DNS tipo `A` apuntando a la IP pública de la VM.
- **Si no tenés dominio todavía**: podés usar uno gratis de https://www.duckdns.org (te da algo tipo `pediaca.duckdns.org` apuntando a tu IP).

Una vez que el dominio resuelve a la IP, pedí el certificado gratis:

```bash
sudo certbot --nginx -d tu-dominio.com
```

Certbot edita el `nginx` config solo y renueva el certificado automáticamente cada 90 días.

---

## 13. Crear el usuario admin

Con todo arriba, entrá desde el navegador a:

```
http://tu-dominio.com/setup/LA-CLAVE-QUE-PUSISTE-EN-SETUP_KEY
```

Te va a mostrar el email (`admin@pediaca.ar`) y la contraseña (la de `ADMIN_PASSWORD`). Esa ruta se autodesactiva sola después de la primera vez.

---

## 14. Actualizar la app en el futuro

Cada vez que quieras subir cambios de código:

```bash
cd /home/ubuntu/pediaca
git pull
source venv/bin/activate
pip install -r requirements.txt
python migrate_db.py
deactivate
sudo systemctl restart pediaca
```

(Si no usás git y subís por `scp`, es lo mismo pero reemplazando `git pull` por volver a copiar los archivos).

---

## 15. Backups de la base (importante — Oracle no te lo hace solo)

Un cron diario que guarda un dump comprimido:

```bash
crontab -e
```

Agregá esta línea (dump todos los días a las 3am, se guarda en `/home/ubuntu/backups`):

```
0 3 * * * mkdir -p /home/ubuntu/backups && PGPASSWORD='ELEGÍ-UNA-CONTRASEÑA-FUERTE-ACÁ' pg_dump -U pediaca_user -h localhost pediaca | gzip > /home/ubuntu/backups/pediaca_$(date +\%Y\%m\%d).sql.gz && find /home/ubuntu/backups -mtime +14 -delete
```

Eso guarda los últimos 14 días de backups y borra los más viejos.

---

## Chequeos rápidos si algo no anda

| Síntoma | Dónde mirar |
|---|---|
| La página no carga / timeout | `sudo systemctl status nginx` y que los puertos 80/443 estén abiertos en la Security List de Oracle |
| Error 502 Bad Gateway | `sudo systemctl status pediaca` y `sudo journalctl -u pediaca -f` — la app no está corriendo o crasheó |
| No conecta a la base | Revisá `DATABASE_URL` en `/etc/pediaca.env` y que `postgresql` esté activo (`sudo systemctl status postgresql`) |
| Cambios que no se ven | Te faltó `sudo systemctl restart pediaca` después del `git pull` |

---

Cualquier paso que se trabe, pasame el mensaje de error tal cual aparece y seguimos desde ahí.
