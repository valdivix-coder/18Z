"""
RECORTAR EL FONDO de un dibujo de personaje. Reconoce TRES entradas:

  1. fondo BLANCO plano        (lo habitual)
  2. fondo TRANSPARENTE ya     (solo recorta a la tinta)
  3. DAMERO INCRUSTADO en los pixeles — un PNG sin canal alfa donde el
     damero de "transparente" quedo pintado. Llega cuando el archivo se
     exporta desde un editor por el camino equivocado, y es peor que el
     fondo blanco: no se ve como fondo hasta que se pone sobre oscuro.
     Se reconoce por NEUTRALIDAD (gris sin color) y se desmatiza contra
     el gris LOCAL, no contra blanco: el damero baja hasta 219 y contra
     255 el borde del personaje sale aclarado.

    from recortar import recortar
    im, (w, h), islas = recortar("dibujo.png")

Quita el fondo Y las islas de fondo que quedan ENCERRADAS entre los
mechones del pelo. Esas islas son el fallo que motivo todo esto: el
relleno desde el borde no las alcanza, y la regla de "conservar los
blancos internos" —la que salva una camisa blanca o unas zapatillas— las
daba por buenas. Sobre el fondo oscuro del juego se leian como tajos.

Separarlas del dibujo legitimo necesita TRES condiciones juntas. Cada
una tapa un agujero que costo una vuelta entera, asi que no aflojes
ninguna sin volver a mirar los quince dibujos:

  1) entorno oscuro        · sin esto se borra una camisa blanca dentro
                             de un traje azul
  2) cerca del fondo real  · sin esto se borran el cierre, la cadena y la
                             hebilla de una parka: tambien son blancos
                             sobre ropa oscura, pero viven en medio del
                             pecho, a 100 px del borde
  3) en la mitad de arriba · sin esto se borran los cordones de unas
                             zapatillas, que quedan cerca del borde
                             porque el zapato es angosto

Y el color NO sirve para separarlos: el dibujante usa el mismo blanco
para la camisa y para el fondo. Medido: hueco de pelo 250,3 de media;
camisa blanca 252,6.
"""
import numpy as np
from PIL import Image
from scipy import ndimage

POR_DEFECTO = 85.0   # luminancia del entorno bajo la cual se da por fondo
DIST_MAX = 45.0      # px hasta el fondo real (calibrado a ~1200 px de alto)
ALTO_MAX = 0.45      # solo la mitad de arriba de la figura

def _limpiar_motas(alpha, minimo=200):
    """Quita pixeles sueltos que no se ven pero ESTIRAN la caja de recorte
    —y la caja es lo que fija la proporcion del personaje—. El umbral
    respeta las piezas separadas de verdad, como una aureola que no toca
    el cuerpo, y se lleva solo la basura."""
    op = alpha > 0.35
    lab, k = ndimage.label(op)
    if k <= 1:
        return alpha
    tam = ndimage.sum(op, lab, range(1, k + 1))
    vivos = [i + 1 for i, t in enumerate(tam) if t >= minimo]
    limpio = np.isin(lab, vivos)
    return np.where(ndimage.binary_dilation(limpio, iterations=2), alpha, 0.0)

def _recortar_a_tinta(rgb, alpha):
    alpha = _limpiar_motas(alpha)
    out = np.dstack([np.clip(rgb, 0, 255), alpha * 255]).astype(np.uint8)
    ys, xs = np.where(alpha > 0.08)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    return Image.fromarray(out[y0:y1, x0:x1], "RGBA"), (int(x1 - x0), int(y1 - y0))

def recortar_alfa(ruta):
    """Caso 2: el dibujo ya viene con transparencia. Solo se recorta."""
    a = np.array(Image.open(ruta).convert("RGBA")).astype(np.float32)
    im, wh = _recortar_a_tinta(a[..., :3], a[..., 3] / 255.0)
    return im, wh, 0

def recortar_damero(ruta):
    """Caso 3: el damero quedo pintado en los pixeles."""
    a = np.array(Image.open(ruta).convert("RGB")).astype(np.float32)
    mx, mn = a.max(2), a.min(2)
    neutro = ((mx - mn) <= 8) & (mn >= 186)
    lab, k = ndimage.label(neutro)
    borde = set(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]).tolist()) - {0}
    fondo = np.isin(lab, list(borde))
    banda = ndimage.binary_dilation(fondo, iterations=3) & ~fondo
    base = float(np.median(a[fondo])) if fondo.sum() else 250.0
    cob = np.clip((base - 4 - mn) / 16.0, 0, 1)
    alpha = np.ones(mn.shape, np.float32); alpha[fondo] = 0.0; alpha[banda] = cob[banda]
    a3 = alpha[..., None]
    col = np.where(a3 > 0.004, (a - (1 - a3) * base) / np.maximum(a3, 0.004), a)
    im, wh = _recortar_a_tinta(col, alpha)
    return im, wh, 0

def que_fondo(ruta):
    """Decide cual de los tres casos es, mirando el archivo."""
    im = Image.open(ruta)
    a = np.array(im.convert("RGBA"))
    if a[..., 3].min() < 250:
        return "alfa"
    rgb = a[..., :3].astype(int)
    borde = np.concatenate([rgb[0], rgb[-1], rgb[:, 0], rgb[:, -1]])
    return "blanco" if borde.min() >= 230 and borde.std() < 6 else "damero"

def recortar(ruta, umbral=None, marcar=False):
    """Recorta el fondo de un dibujo y devuelve (RGBA, (w,h), islas quitadas).
    Elige solo entre los tres casos."""
    if not marcar:
        caso = que_fondo(ruta)
        if caso == "alfa":
            return recortar_alfa(ruta)
        if caso == "damero":
            return recortar_damero(ruta)
    rgb = np.array(Image.open(ruta).convert("RGB")).astype(np.float32)
    mx, mn = rgb.max(2), rgb.min(2)
    blanco = (mn >= 236) & ((mx - mn) <= 12)
    lab, k = ndimage.label(blanco)
    borde = set(np.concatenate([lab[0],lab[-1],lab[:,0],lab[:,-1]]).tolist()) - {0}
    # islas ENCERRADAS que en realidad son fondo asomando entre mechones
    lum = rgb.mean(2); u = POR_DEFECTO if umbral is None else umbral
    # DOS condiciones, y hacen falta las dos:
    #  1) el entorno es oscuro  -> descarta camisas y zapatillas
    #  2) esta CERCA del fondo real -> descarta el cierre, la cadena y la
    #     hebilla de Kidd, que tambien son blancos sobre ropa oscura pero
    #     viven en medio del pecho, a 100 px del borde. Un hueco entre
    #     mechones esta a 10-25 px: lo unico que lo separa del fondo es
    #     el trazo del propio mechon.
    fondo0 = np.isin(lab, list(borde))
    dist = ndimage.distance_transform_edt(~fondo0)
    # 3) esta en la mitad de ARRIBA de la figura. El unico elemento que
    #    encierra fondo del todo es el PELO, que se dibuja en mechones
    #    superpuestos; abajo, lo blanco sobre oscuro son los cordones de
    #    las zapatillas de Kidd, que tambien quedan cerca del borde
    #    porque el zapato es angosto.
    yy, xx = np.where(~fondo0)
    yTope = yy.min() + (yy.max() - yy.min()) * ALTO_MAX
    extra = []
    tam = ndimage.sum(blanco, lab, range(1, k+1))
    for i, t in enumerate(tam):
        idx = i+1
        if idx in borde or t < 12: continue
        m = lab == idx
        anillo = ndimage.binary_dilation(m, iterations=3) & ~m
        if not anillo.sum(): continue
        ys_ = np.where(m)[0]
        if lum[anillo].mean() < u and dist[m].mean() < DIST_MAX and ys_.mean() < yTope:
            extra.append(idx)
    fondo = np.isin(lab, list(borde) + extra)
    if marcar: return rgb, np.isin(lab, extra), extra
    # a partir de aqui, identico al recorte de siempre: la isla nueva
    # recibe el MISMO tratamiento que el contorno exterior, asi que su
    # borde queda suavizado y sin halo claro
    banda = ndimage.binary_dilation(fondo, iterations=3) & ~fondo
    cob = np.clip((250.0 - mn)/18.0, 0, 1)
    alpha = np.ones(mn.shape, np.float32); alpha[fondo]=0.0; alpha[banda]=cob[banda]
    a3 = alpha[...,None]
    col = np.where(a3>0.004, (rgb-(1-a3)*255.0)/np.maximum(a3,0.004), rgb)
    im, wh = _recortar_a_tinta(col, alpha)
    return im, wh, len(extra)

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("uso: python3 recortar.py <dibujo.png> <salida.webp> [alto_logico]")
        raise SystemExit(2)
    im, wh, ne = recortar(sys.argv[1])
    alto = int(sys.argv[3]) if len(sys.argv) > 3 else wh[1]
    fh = round(alto * 1.42)
    im.resize((round(fh * wh[0] / wh[1]), fh), Image.LANCZOS).save(
        sys.argv[2], "WEBP", quality=86, method=6)
    print(f"{sys.argv[2]}  tinta {wh[0]}x{wh[1]}  proporcion {wh[0]/wh[1]:.3f}  "
          f"islas de fondo quitadas: {ne}")
