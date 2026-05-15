"""
PediAcá — Generador de Flyer v3
Robusto: descarga fuentes automáticamente si no están en el sistema.
"""

import qrcode
import io
import os
import urllib.request
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# ── COLORES ───────────────────────────────────────────────────────────────────
NARANJA   = (243, 156,  18)
NARANJA_D = (211, 128,   8)
AZUL      = ( 41, 128, 185)
BLANCO    = (255, 255, 255)
GRIS      = (247, 248, 250)
GRIS_L    = (230, 232, 236)
GRIS_T    = ( 90,  90,  90)
NEGRO     = ( 30,  30,  30)

W, H = 874, 1240

# ── RUTAS DEL LOGO PEDIACA ────────────────────────────────────────────────────
_BASE = os.path.dirname(os.path.abspath(__file__))
LOGO_PATHS = [
    os.path.join(_BASE, "static", "img", "logo_pediaca.png"),
    "/mnt/user-data/uploads/1000693457.png",
]

# ── FUENTES: busca en sistema, descarga si no hay ─────────────────────────────
_FONT_DIR  = os.path.join(_BASE, "static", "fonts")
_FONT_BOLD = os.path.join(_FONT_DIR, "DejaVuSans-Bold.ttf")
_FONT_REG  = os.path.join(_FONT_DIR, "DejaVuSans.ttf")

_FONT_URLS = {
    _FONT_BOLD: "https://github.com/dejavu-fonts/dejavu-fonts/raw/master/ttf/DejaVuSans-Bold.ttf",
    _FONT_REG:  "https://github.com/dejavu-fonts/dejavu-fonts/raw/master/ttf/DejaVuSans.ttf",
}

_SYSTEM_BOLD = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
]
_SYSTEM_REG = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans.ttf",
    "C:/Windows/Fonts/arial.ttf",
]


def _resolver_fuente(bold=False):
    """Busca en sistema, luego en static/fonts/, si no descarga."""
    candidatas = _SYSTEM_BOLD if bold else _SYSTEM_REG
    for p in candidatas:
        if os.path.exists(p):
            return p

    # Intentar desde static/fonts/
    local = _FONT_BOLD if bold else _FONT_REG
    if os.path.exists(local):
        return local

    # Descargar
    os.makedirs(_FONT_DIR, exist_ok=True)
    url = _FONT_URLS[local]
    try:
        print(f"Descargando fuente: {url}")
        urllib.request.urlretrieve(url, local)
        if os.path.exists(local):
            return local
    except Exception as e:
        print(f"No se pudo descargar fuente: {e}")

    return None


def _fuente(size, bold=False):
    path = _resolver_fuente(bold)
    if path:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            pass
    # Fallback absoluto
    try:
        return ImageFont.load_default(size=size)
    except Exception:
        return ImageFont.load_default()


def _centrar(draw, y, texto, fuente, color, ancho=W):
    bb = draw.textbbox((0, 0), texto, font=fuente)
    x  = (ancho - (bb[2] - bb[0])) // 2
    draw.text((x, y), texto, font=fuente, fill=color)


def _centrar_sombra(draw, y, texto, fuente, color, ancho=W):
    bb = draw.textbbox((0, 0), texto, font=fuente)
    x  = (ancho - (bb[2] - bb[0])) // 2
    draw.text((x+2, y+2), texto, font=fuente, fill=(0, 0, 0, 60))
    draw.text((x,   y),   texto, font=fuente, fill=color)


def _pegar_centrado(base, overlay, y):
    x = (base.width - overlay.width) // 2
    if overlay.mode == "RGBA":
        base.paste(overlay, (x, y), overlay)
    else:
        base.paste(overlay, (x, y))


def _circulo(img, size):
    img  = img.convert("RGBA").resize((size, size), Image.LANCZOS)
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, size-1, size-1], fill=255)
    out  = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.paste(img, mask=mask)
    return out


def _generar_qr(url, size=300):
    qr = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color=NEGRO, back_color=BLANCO).convert("RGBA")
    return img.resize((size, size), Image.LANCZOS)


def generar_flyer(
    nombre_local:   str,
    restaurante_id: int,
    logo_path:      str = None,
    categoria:      str = "",
    base_url:       str = "https://pediaca.ar"
) -> bytes:

    url_menu = f"{base_url}/local/{restaurante_id}"

    # ── CANVAS ────────────────────────────────────────────────
    flyer = Image.new("RGB", (W, H), BLANCO)
    draw  = ImageDraw.Draw(flyer)

    # Fondo gris suave
    draw.rectangle([0, 0, W, H - 180], fill=GRIS)
    # Franja top
    draw.rectangle([0, 0, W, 14],  fill=NARANJA)
    draw.rectangle([0, 14, W, 18], fill=AZUL)

    # ── LOGO PEDIACA ──────────────────────────────────────────
    lp_path = None
    for p in LOGO_PATHS:
        if p and os.path.exists(p):
            lp_path = p
            break

    pediaca_size = 180
    pediaca_y    = 32

    if lp_path:
        try:
            lp = Image.open(lp_path).convert("RGBA")
            lp = lp.resize((pediaca_size, pediaca_size), Image.LANCZOS)
            _pegar_centrado(flyer, lp, pediaca_y)
        except Exception:
            lp_path = None

    if not lp_path:
        f_brand = _fuente(60, bold=True)
        _centrar(draw, pediaca_y + 50, "PediAcá", f_brand, NARANJA)

    sep1_y = pediaca_y + pediaca_size + 16
    draw.rectangle([80, sep1_y, W-80, sep1_y+1], fill=GRIS_L)

    # ── LOGO DEL LOCAL ────────────────────────────────────────
    logo_size = 200
    logo_y    = sep1_y + 22

    logo_ok = False
    if logo_path and os.path.exists(logo_path):
        try:
            logo_local = Image.open(logo_path).convert("RGBA")
            logo_circ  = _circulo(logo_local, logo_size)
            sh = Image.new("RGBA", (logo_size+16, logo_size+16), (0,0,0,0))
            ImageDraw.Draw(sh).ellipse([4,4,logo_size+12,logo_size+12], fill=(0,0,0,25))
            sh = sh.filter(ImageFilter.GaussianBlur(5))
            flyer.paste(sh, ((W-logo_size-16)//2, logo_y-2), sh)
            flyer.paste(logo_circ, ((W-logo_size)//2, logo_y), logo_circ)
            logo_ok = True
        except Exception:
            pass

    if not logo_ok:
        r  = logo_size // 2
        cx = W // 2
        cy = logo_y + r
        draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=BLANCO, outline=NARANJA, width=6)
        f_ini = _fuente(88, bold=True)
        inicial = nombre_local[0].upper()
        bb = draw.textbbox((0,0), inicial, font=f_ini)
        draw.text((cx-(bb[2]-bb[0])//2, cy-(bb[3]-bb[1])//2-4),
                  inicial, font=f_ini, fill=NARANJA)

    # ── NOMBRE DEL LOCAL ──────────────────────────────────────
    nombre_y = logo_y + logo_size + 18
    f_nombre = _fuente(52, bold=True)
    # Auto-reducir si es largo
    for _ in range(10):
        bb = draw.textbbox((0,0), nombre_local, font=f_nombre)
        if bb[2]-bb[0] <= W - 80:
            break
        f_nombre = _fuente(max(f_nombre.size - 4, 24), bold=True)

    _centrar(draw, nombre_y, nombre_local, f_nombre, NEGRO)
    bb_n  = draw.textbbox((0,0), nombre_local, font=f_nombre)
    cat_y = nombre_y + (bb_n[3]-bb_n[1]) + 8

    if categoria:
        f_cat = _fuente(26)
        _centrar(draw, cat_y, categoria, f_cat, GRIS_T)
        cat_y += 38

    # ── SEPARADOR ─────────────────────────────────────────────
    sep2_y = cat_y + 12
    pw = 55
    draw.rectangle([W//2-pw-10, sep2_y+6, W//2-10, sep2_y+8], fill=AZUL)
    draw.ellipse([W//2-7, sep2_y+1, W//2+7, sep2_y+13], fill=NARANJA)
    draw.rectangle([W//2+10, sep2_y+6, W//2+pw+10, sep2_y+8], fill=AZUL)

    # ── TEXTO ─────────────────────────────────────────────────
    inv_y  = sep2_y + 30
    f_inv  = _fuente(29, bold=True)
    f_inv2 = _fuente(23)
    _centrar(draw, inv_y,      "Escaneá y pedí directo a nuestro", f_inv,  NEGRO)
    _centrar(draw, inv_y + 40, "WhatsApp — sin apps ni comisiones", f_inv2, GRIS_T)

    # ── QR ────────────────────────────────────────────────────
    qr_size = 294
    qr_y    = inv_y + 92
    qr_img  = _generar_qr(url_menu, size=qr_size)

    marco_size = qr_size + 30
    marco      = Image.new("RGBA", (marco_size, marco_size), (0,0,0,0))
    md         = ImageDraw.Draw(marco)
    md.rounded_rectangle([0,0,marco_size-1,marco_size-1],
                          radius=20, fill=BLANCO, outline=NARANJA, width=5)
    marco.paste(qr_img, (15, 15), qr_img)
    _pegar_centrado(flyer, marco, qr_y)

    qr_bottom = qr_y + marco_size

    # ── URL ───────────────────────────────────────────────────
    f_url = _fuente(22)
    _centrar(draw, qr_bottom + 10,
             f"pediaca.ar/local/{restaurante_id}", f_url, AZUL)

    # ── FOOTER ────────────────────────────────────────────────
    footer_y = H - 180
    draw.rectangle([0, footer_y,     W, footer_y+5], fill=NARANJA_D)
    draw.rectangle([0, footer_y + 5, W, H          ], fill=NARANJA)

    f_tag1 = _fuente(36, bold=True)
    f_tag2 = _fuente(23)
    f_tag3 = _fuente(25, bold=True)

    _centrar_sombra(draw, footer_y + 20,
                    "Sin comisiones. Sin letra chica.",
                    f_tag1, BLANCO)
    _centrar(draw, footer_y + 70,
             "Tu pedido va directo al local, gratis para vos.",
             f_tag2, (255, 238, 190))
    draw.rectangle([80, footer_y+108, W-80, footer_y+110], fill=(255,200,100,150))
    _centrar(draw, footer_y + 122, "pediaca.ar", f_tag3, BLANCO)

    draw.rectangle([0, H-14, W, H], fill=AZUL)

    # ── EXPORT ────────────────────────────────────────────────
    buf = io.BytesIO()
    flyer.save(buf, format="PNG", optimize=True, dpi=(150, 150))
    buf.seek(0)
    return buf.getvalue()


# ── TEST ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Generando flyer de prueba...")
    png = generar_flyer(
        nombre_local   = "La Esquina Pizzería",
        restaurante_id = 1,
        categoria      = "Pizzería · Rosario",
    )
    salida = "/tmp/flyer_test.png"
    with open(salida, "wb") as f:
        f.write(png)
    print(f"✅ {len(png)//1024} KB → {salida}")
