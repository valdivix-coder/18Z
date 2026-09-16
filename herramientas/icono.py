#!/usr/bin/env python3
"""
LOS ICONOS DEL LANZADOR, sacados del arte que entrego Simon.

    python3 herramientas/icono.py                 rehace los derivados
    python3 herramientas/icono.py arte.png        cambia el arte maestro

EL MAESTRO ES `assets/icon-512.png` y no hay copia aparte del original.
Guardar las dos cosas era pagar dos veces por la misma imagen —y el
maestro ya es el tamano mas grande que pide cualquier sistema: Android
512, iOS 180—. Va en PNG RGB sin comprimir por paleta: con 256 colores
pesaba 176 KB en vez de 528, pero el cielo se bandeaba (error medio 4,8,
picos de 141). Es la cara de la app; los 350 KB se pagan.

QUE HACE CADA SALIDA:
  icon-512  · el maestro. Android lo usa tal cual.
  icon-192  · el que de verdad se ve en la mayoria de los lanzadores.
  apple-touch-icon (180) · iPhone. NO recorta, asi que lleva el arte
              entero.
  icon-maskable-512 · Android le aplica la forma del sistema —circulo,
              cuadrado redondeado, gota— y solo garantiza el 80%
              CENTRAL. En este arte el "1" arranca a un 6% del borde y
              la "Z" termina a un 95%: sin encoger, la forma del sistema
              se come las dos puntas. Asi que el arte entra al 78% y el
              hueco lo rellena una copia AMPLIADA Y DESENFOCADA de si
              mismo, que continua el cielo y el escombro en el sitio que
              les toca. Un marco de color plano habria dibujado un borde
              donde el arte se acaba, que es justo lo que un maskable no
              puede tener.

LA REGLA QUE NO SE PUEDE SALTAR: LOS ICONOS VAN SIN CANAL ALFA. El
lanzador de Android compone lo transparente sobre BLANCO, asi que un
icono con fondo transparente se ve como un cuadrado blanco. Todo se
aplana antes de guardar. En iPhone `apple-touch-icon` siempre fue opaco,
asi que la regla lo cubre de paso.
"""
import os
import sys
from PIL import Image, ImageFilter, ImageEnhance

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
ASSETS = os.path.join(RAIZ, "assets")
MAESTRO = os.path.join(ASSETS, "icon-512.png")

LADO_MAESTRO = 512
ZONA_SEGURA = 0.78      # lo unico que Android garantiza de un maskable


def cuadrar(im, lado):
    """Recorta al cuadrado CENTRAL y escala. El arte ya llega cuadrado;
    esto solo protege de que un dia llegue con otra proporcion."""
    im = im.convert("RGB")
    c = min(im.size)
    im = im.crop(((im.width - c) // 2, (im.height - c) // 2,
                  (im.width + c) // 2, (im.height + c) // 2))
    return im.resize((lado, lado), Image.LANCZOS)


def arte():
    return Image.open(MAESTRO).convert("RGB")


def componer(lado, zona=1.0):
    a = arte()
    if zona >= 1.0:
        return a.resize((lado, lado), Image.LANCZOS)
    # Relleno: el mismo arte ampliado y desenfocado, para que el borde
    # del lienzo no se note bajo la forma del sistema.
    z = 1.0 / zona
    g = a.resize((int(lado * z * 1.15), int(lado * z * 1.15)), Image.LANCZOS)
    g = g.crop(((g.width - lado) // 2, (g.height - lado) // 2,
                (g.width + lado) // 2, (g.height + lado) // 2))
    g = g.filter(ImageFilter.GaussianBlur(lado * 0.045))
    g = ImageEnhance.Brightness(g).enhance(0.62)
    n = int(lado * zona)
    g.paste(a.resize((n, n), Image.LANCZOS), ((lado - n) // 2, (lado - n) // 2))
    return g


SALIDAS = [
    ("icon-512.png", 512, 1.0),
    ("icon-192.png", 192, 1.0),
    ("icon-maskable-512.png", 512, ZONA_SEGURA),
    ("apple-touch-icon.png", 180, 1.0),
]

if __name__ == "__main__":
    if len(sys.argv) > 1:
        cuadrar(Image.open(sys.argv[1]), LADO_MAESTRO).save(MAESTRO, "PNG", optimize=True)
        print(f"  maestro nuevo desde {os.path.basename(sys.argv[1])}")
    for nombre, lado, zona in SALIDAS:
        r = os.path.join(ASSETS, nombre)
        componer(lado, zona).save(r, "PNG", optimize=True)   # RGB: sin alfa
        print(f"  {nombre:26} {lado}x{lado}  {os.path.getsize(r)//1024:>4} KB"
              + ("   (el arte, dentro de la zona segura)" if zona < 1 else ""))
