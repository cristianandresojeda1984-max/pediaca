#!/usr/bin/env python3
"""
Utilidad de despliegue: escribe contenido binario/texto en un archivo a partir
de una cadena hexadecimal pasada por linea de comandos.

Uso: python3 write_hex.py /ruta/al/archivo <contenido_en_hex>

Se usa durante el despliegue en la consola web de DonWeb, donde el teclado
remoto no puede transmitir mayusculas ni simbolos con Shift (:, {, }, etc.).
Codificar el contenido real en hexadecimal permite escribirlo sin depender
de esas teclas.
"""
import sys

def main():
    if len(sys.argv) != 3:
        print("Uso: write_hex.py <archivo_destino> <hex>")
        sys.exit(1)
    dest = sys.argv[1]
    hex_data = sys.argv[2]
    data = bytes.fromhex(hex_data)
    with open(dest, "wb") as f:
        f.write(data)
    print(f"Escrito {len(data)} bytes en {dest}")

if __name__ == "__main__":
    main()
