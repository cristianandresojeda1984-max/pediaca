# PediAcá — Deploy en Render

## ⚠️ Restricción de diseño: PediAcá NO maneja pagos

**Decisión de producto de Cristian (27/07/2026), no negociable salvo que él mismo la cambie explícitamente:**

PediAcá **no procesa ni intermedia pagos de ningún tipo** dentro de la plataforma. Esto significa:

- No hay pasarela de pago integrada (nada de Mercado Pago, tarjetas de crédito/débito, ni ningún otro procesador).
- No hay facturación centralizada ni integración con AFIP.
- La plataforma no cobra comisión ni retiene dinero de ninguna transacción.

El rol de PediAcá es exclusivamente ser el **punto de encuentro/vidriera** entre cliente, local y cadete: mostrar el menú, armar el pedido, coordinar la logística (incluido el seguimiento GPS) y comunicar los datos del pedido (por ejemplo vía WhatsApp). El pago en sí —efectivo, transferencia, o lo que acuerden las partes— queda **100% por fuera del sistema**, arreglado directamente entre cliente y local/cadete.

**Cualquier feature nueva debe respetar esto**: no agregar checkout de pago, no guardar datos de tarjetas, no integrar pasarelas, no generar facturas dentro de la app. Si en algún momento surge una necesidad relacionada (por ejemplo, algo que roce cobros), hay que confirmarlo explícitamente con Cristian antes de implementar nada, porque contradice esta decisión de base.

### Cómo circula la plata en el modelo de negocio (aunque no la toque la plataforma)

Para que quede claro el flujo real, aunque no lo procese el sistema:

- **El local cobra todo, incluido el envío.** El cliente le paga al local el total del pedido (productos + costo de envío) directamente, por fuera de la plataforma (efectivo, transferencia, etc.).
- **El local le paga al cadete por el reparto**, también por fuera de la plataforma, una vez que el cadete hace la entrega.
- La razón de este esquema: así el local siempre cobra el pedido completo, sin depender de que el cliente le pague el envío por separado al cadete (evita el riesgo de que el cadete quede sin cobrar o el local pierda el control del cobro).
- **PediAcá solo tiene que reflejar esto en el pedido**: mostrar el total correcto con el envío incluido, para que quede claro cuánto le tiene que cobrar el local al cliente. La plataforma **no procesa ni intermedia ningún pago**, ni entre cliente y local, ni entre local y cadete — sigue aplicando la restricción de arriba en los dos sentidos.

### Requisito de transparencia: el cadete tiene que ver el costo de envío de cada pedido

Como el local es quien cobra el envío y después le paga al cadete por fuera de la plataforma, el cadete necesita poder verificar ese monto para poder reclamarlo con seguridad. Por eso:

- En el panel/vista del cadete, **cada pedido tiene que mostrar de forma clara y visible el costo de envío correspondiente** (no escondido en un desglose colapsado, no ambiguo, no mezclado sin aclarar dentro del total).
- Esto aplica tanto a los pedidos disponibles para tomar como a los que el cadete ya tiene asignados/en curso y a su historial.
- Objetivo: que el cadete pueda, en cualquier momento, decirle al local "este pedido tenía $X de envío" sin tener que adivinar o pedir el dato por otro lado.

## 💡 Feature futura (no implementar todavía): carrusel de publicidad

**Idea de Cristian (27/07/2026), anotada para más adelante — primero hay que consolidar la base de locales:**

Un carrusel de anuncios publicitarios opcional en el portal (Cristian lo prende/apaga desde algún panel), donde al hacer click en un anuncio lleva al link de la marca anunciante.

Es un **modelo de ingresos separado**: acá PediAcá le cobraría a marcas anunciantes por mostrar el anuncio, no a los locales por vender — no contradice la regla de "cero comisión a los locales" documentada arriba, porque es una fuente de ingresos totalmente distinta (publicidad, no intermediación de pagos de pedidos).

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
| `SECRET_KEY` | Se genera sola (`render.yaml`) |
| `DB_PATH` | `pediaca.db` |
| `SETUP_KEY` | Elegí una clave secreta propia — la vas a necesitar para crear el admin |
| `ADMIN_PASSWORD` | La contraseña que va a tener la cuenta admin |

`SETUP_KEY` y `ADMIN_PASSWORD` son **obligatorias**: sin ellas la ruta de creación del admin queda deshabilitada (para que nadie pueda crear una cuenta admin adivinando una clave por defecto).

### 4. Crear el admin

Después del primer deploy, entrá una sola vez a:

```
https://tu-app.onrender.com/setup/TU_SETUP_KEY
```

Te va a mostrar el email y la contraseña del admin (la que pusiste en `ADMIN_PASSWORD`). La ruta se autodesactiva apenas existe un admin, así que solo funciona la primera vez.

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
