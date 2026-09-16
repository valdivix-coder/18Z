"""
RECORTAR EL ROSTRO para la casilla de la grilla (proporcion 135x82).

    python3 rostros.py ../assets/p-tatan.webp ../assets/f-tatan.webp tatan

Centra la caja en la CARA y no en el centro de masa: el pelo se va a un
lado y arrastra el centro. Para ubicar la cara aisla la piel y toma el
grupo MAS ALTO — la mediana de toda la piel incluye brazos y escote, y
con ella el recorte se come la frente.

`ajuste.json` guarda el ajuste fino por personaje: {alto del recorte como
fraccion del dibujo, cuanto sube sobre la coronilla}. Con quince
personajes, medir a mano gana a una heuristica que falla en dos. Los que
llevan algo ENCIMA de la cara —aureola, boina, jockey— necesitan caja mas
alta aunque la cara les quede mas chica: perder la boina es perder al
personaje.
"""
import json, os
import numpy as np
from PIL import Image
from scipy import ndimage

AQUI = os.path.dirname(os.path.abspath(__file__))
AR = 135 / 82.0        # la proporcion de la casilla
ALTO = 200             # retina: la casilla mide 77 px CSS
AJUSTE = json.load(open(os.path.join(AQUI, "ajuste.json"), encoding="utf-8"))

def cara(ruta):
    """Devuelve (imagen, ancho, alto, x de la cara, y de la coronilla)."""
    im = Image.open(ruta).convert("RGBA")
    a = np.array(im); W, H = im.size
    op = a[..., 3] > 90
    r, g, b = a[..., 0].astype(int), a[..., 1].astype(int), a[..., 2].astype(int)
    piel = op & (r > 120) & (r > g + 12) & (g >= b) & (r - b > 28) & (r - b < 135)
    piel[int(H * 0.55):, :] = False
    piel = ndimage.binary_opening(piel, np.ones((3, 3)))
    lab, k = ndimage.label(piel)
    mejor = None
    for i in range(1, k + 1):
        ys, xs = np.where(lab == i)
        if len(ys) < 0.0012 * W * H:
            continue
        if mejor is None or ys.mean() < mejor[0]:
            mejor = (ys.mean(), xs.mean(), ys.min())
    return (im, W, H) + ((mejor[1], mejor[2]) if mejor else (W / 2, H * 0.10))

def recorta(ruta, cid):
    im, W, H, cx, cy = cara(ruta)
    f, dy = AJUSTE.get(cid, [0.30, 0.30])
    ch = int(H * f); cw = int(round(ch * AR))
    if cw > W:
        cw = W; ch = int(round(cw / AR))
    y0 = max(0, min(H - ch, int(cy - ch * dy)))
    x0 = max(0, min(W - cw, int(cx - cw / 2)))
    return im.crop((x0, y0, x0 + cw, y0 + ch)).resize((round(ALTO * AR), ALTO), Image.LANCZOS)

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 4:
        print("uso: python3 rostros.py <p-id.webp> <f-id.webp> <id>")
        raise SystemExit(2)
    recorta(sys.argv[1], sys.argv[3]).save(sys.argv[2], "WEBP", quality=88, method=6)
    print(f"{sys.argv[2]}  ajuste {AJUSTE.get(sys.argv[3], [0.30, 0.30])}")
