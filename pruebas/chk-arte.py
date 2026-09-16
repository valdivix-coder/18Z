"""
ARTE — la integridad de los dibujos, sin navegador.

Existe por un fallo real: quedaban MEDIALUNAS DE FONDO entre los mechones
del pelo. El recorte rellena desde el borde de la imagen, asi que lo
blanco ENCERRADO por el contorno del pelo nunca se alcanzaba, y la regla
de "conservar los blancos internos" —la que salva la camisa del Boris y
las zapatillas de La Naya— las daba por buenas. Sobre el fondo oscuro del
juego se leian como tajos blancos.

QUE MIDE ESTA SUITE, exactamente: no que no quede NI UN pixel blanco
sospechoso —eso es imposible, porque un destello en unos lentes, un aro
o un puno de camisa cumple las mismas tres condiciones que un hueco de
pelo y mide lo mismo—, sino que la SUPERFICIE total de islas sospechosas
se quede en el ruido. Un recorte sin aplicar no deja destellos: deja
medialunas. La Primera tenia 31 islas y 6.454 px en el original; el ruido
de destellos de todo el reparto anda en 100-150 px por dibujo. Entre una
cosa y la otra hay un factor diez, y el limite va justo en medio.

La regla que los separa necesita TRES condiciones juntas, y cada una
tapa un agujero que costo una vuelta:
  1) entorno oscuro        · sin esto se borraba la camisa de El Toño
  2) cerca del fondo real  · sin esto se borraban el cierre y la cadena
                             de Kidd, que tambien son blancos sobre ropa
                             oscura pero viven en medio del pecho
  3) en la mitad de arriba · sin esto se borraban los cordones de las
                             zapatillas, que estan cerca del borde porque
                             el zapato es angosto
Aflojar cualquiera de las tres borra algo legitimo. Esta suite comprueba
que ningun dibujo publicado tenga islas que cumplan las tres.
"""
import json, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "herramientas"))
import numpy as np
from PIL import Image
from scipy import ndimage
import ayuda
from ayuda import ok

ASSETS = os.path.join(ayuda.RAIZ, "assets")
ENTORNO_MAX, ALTO_MAX = 85.0, 0.45
# Calibrados sobre los originales (~1200 px de alto) y expresados como
# fraccion, porque el sprite publicado mide ~700: en pixeles absolutos
# esta prueba saldria MAS FLOJA que el recorte y acusaria de "fondo" al
# panuelo del bolsillo de Felipito, que es legitimo.
DIST_FRAC = 45.0 / 1200.0
MIN_FRAC = 12.0 / (1200.0 ** 2)
# Superficie sospechosa tolerada, como fraccion del lienzo. El ruido de
# destellos medido en los 15 dibujos llega a 0,031%; una regresion del
# recorte pasa de 0,30%. El limite va a 0,08%: diez veces sobre el ruido
# y cuatro veces bajo el fallo que viene a cazar.
LIMITE_FRAC = 0.0008

def ids_del_juego():
    s = open(ayuda.JUEGO, encoding="utf-8").read()
    blo = re.search(r"var PERSONAJES = \[(.*?)\n\];", s, re.S).group(1)
    return re.findall(r'id:"(\w+)"', blo)

def islas_de_fondo(ruta):
    """Las que cumplen las TRES condiciones: fondo que se colo, no dibujo."""
    a = np.array(Image.open(ruta).convert("RGBA"))
    al, rgb = a[..., 3].astype(int), a[..., :3].astype(int)
    opaco = al > 160
    blanco = opaco & (rgb.min(2) >= 230) & ((rgb.max(2) - rgb.min(2)) <= 12)
    lab, k = ndimage.label(blanco)
    if not k:
        return [], 0
    lum = rgb.mean(2)
    fuera = ~opaco
    dist = ndimage.distance_transform_edt(~fuera)
    ys = np.where(opaco)[0]
    if not len(ys):
        return [], 0
    tope = ys.min() + (ys.max() - ys.min()) * ALTO_MAX
    alto = a.shape[0]
    dist_max = DIST_FRAC * alto
    min_px = max(5, round(MIN_FRAC * alto * alto))
    malas, tot = [], 0
    for i, t in enumerate(ndimage.sum(blanco, lab, range(1, k + 1))):
        if t < min_px:
            continue
        m = lab == (i + 1)
        anillo = ndimage.binary_dilation(m, iterations=3) & ~m & opaco
        if not anillo.sum():
            continue
        yy = np.where(m)[0]
        if (lum[anillo].mean() < ENTORNO_MAX and dist[m].mean() < dist_max
                and yy.mean() < tope):
            malas.append(int(t)); tot += int(t)
    return malas, tot

def main():
    ids = ids_del_juego()
    ok(len(ids) > 0, "se pudo leer el reparto del juego")
    for cid in ids:
        pr = os.path.join(ASSETS, f"p-{cid}.webp")
        fr = os.path.join(ASSETS, f"f-{cid}.webp")
        if not ok(os.path.exists(pr), f"{cid}: existe su cuerpo"):
            continue
        im = Image.open(pr).convert("RGBA")
        a = np.array(im)
        al = a[..., 3]

        # tiene transparencia de verdad (no es un rectangulo opaco)
        ok((al < 40).mean() > 0.15, f"{cid}: el dibujo esta recortado, no es un rectangulo",
           f"{(al<40).mean()*100:.0f}% transparente")
        # recortado a la tinta: sin franjas vacias a los lados
        ys, xs = np.where(al > 40)
        ok(ys.min() <= 2 and xs.min() <= 2 and ys.max() >= im.height - 3 and xs.max() >= im.width - 3,
           f"{cid}: el dibujo esta recortado a la tinta",
           f"tinta en x {xs.min()}-{xs.max()} de {im.width}, y {ys.min()}-{ys.max()} de {im.height}")
        # y lo que motiva esta suite
        malas, tot = islas_de_fondo(pr)
        frac = tot / float(im.width * im.height)
        ok(frac < LIMITE_FRAC, f"{cid}: sin fondo colado entre el pelo",
           f"{len(malas)} islas, {tot} px = {frac*100:.3f}% (limite {LIMITE_FRAC*100:.2f}%)")

        if ok(os.path.exists(fr), f"{cid}: existe su rostro"):
            f = Image.open(fr)
            ok(abs(f.width / f.height - 135 / 82) < 0.03,
               f"{cid}: el rostro tiene la proporcion de la casilla", f"{f.width}x{f.height}")
            g = np.array(f.convert("L"))
            ok(g.std() > 25, f"{cid}: el rostro no esta en blanco", f"desviacion {g.std():.1f}")
            # El rostro tiene que poder REGENERARSE del cuerpo actual. Si
            # no coincide, quedo viejo: alguien cambio el dibujo del cuerpo
            # y no rehizo la cara, que es como se cuelan rostros de una
            # version anterior.
            # (Que el encuadre sea BUENO no se puede comprobar solo: se
            # probaron dos metricas —piel al centro y piel pegada al borde
            # de arriba— y ninguna separa un recorte bien puesto de uno
            # con la cara fuera de cuadro. Eso se mira, y los anclajes a
            # mano viven en herramientas/ajuste.json.)
            try:
                from rostros import recorta as _rec
                import numpy as _np
                nuevo = _np.array(_rec(pr, cid).convert("RGB")).astype(int)
                viejo = _np.array(f.convert("RGB")).astype(int)
                if ok(nuevo.shape == viejo.shape, f"{cid}: su rostro tiene la medida esperada"):
                    dif = float(_np.abs(nuevo - viejo).mean())
                    # 18 sale de medir los dos extremos: recomprimir el
                    # mismo recorte en WebP ya mueve la imagen hasta 10,7,
                    # y el rostro de OTRO personaje da 43,6 como minimo.
                    ok(dif < 18.0, f"{cid}: su rostro corresponde al cuerpo de ahora",
                       f"diferencia media {dif:.1f} (ruido de recompresion llega a 10,7; "
                       f"un rostro ajeno, a 43,6)")
            except Exception as e:
                ok(False, f"{cid}: se pudo regenerar su rostro", str(e))
            fm, ft = islas_de_fondo(fr)
            ffrac = ft / float(f.width * f.height)
            ok(ffrac < LIMITE_FRAC * 3, f"{cid}: su rostro tampoco trae fondo colado",
               f"{ft} px = {ffrac*100:.3f}%")

    # los archivos fijos que la app necesita
    for n in ["sel-mod.webp", "sel-bg.webp", "logo.webp", "intro-frame0.webp", "intro-anim.webp"]:
        ok(os.path.exists(os.path.join(ASSETS, n)), f"existe {n}")
    # nada muerto: todo p-/f- corresponde a alguien de la lista
    sueltos = sorted({f[2:-5] for f in os.listdir(ASSETS)
                      if re.fullmatch(r"[pf]-\w+\.webp", f)} - set(ids))
    ok(not sueltos, "no hay dibujos de nadie que ya no este en la lista", sueltos)
    ayuda.resumen("chk-arte")

main()
