#!/usr/bin/env python3
"""
Extrae los assets del juego desde las tres imagenes fuente.

Las fuentes son arte aprobado por Simon y NO se versionan aqui: se pasan por
argumento. Lo que se versiona es este guion, para que la extraccion se pueda
repetir exactamente igual si hay que rehacerla.

    python3 extraer-assets.py ROSTER.png PORTADA.png LOGO.png ../assets

Que saca, y por que asi:

  roster-atlas.png  Las 30 caras recortadas de la rejilla del roster, en un
                    solo archivo 6x5 de celdas 126x100. La rejilla del arte
                    original tiene paso 138.0 x 133.0 desde (258,142); el
                    margen de 6 px por lado se descarta para no arrastrar el
                    borde del azulejo vecino. A la celda de CAMILITA se le
                    quita el anillo naranja de seleccion que trae pintado,
                    reemplazando esos pixeles por la MEDIANA de las 30 celdas
                    -que en el marco es el azul liso del azulejo-.

  bg-city.webp      La portada completa. Se usa tal cual en la pantalla de
                    inicio (el logotipo y el boton vienen pintados en el arte)
                    y atenuada de fondo en la seleccion.

  logo.webp         El logotipo vectorizado, recortado a su caja de tinta.

  spr-camilita.png  Cuerpo completo recortado con alfa del panel PLAYER 1 del
                    roster. Sale limpio con GrabCut porque el fondo del panel
                    es un muro liso.

  spr-eltono.png    NO existe en ninguna fuente, asi que se construye:
                    torso de Tatan (la portada, unico traje en guardia a esa
                    escala) + la cabeza exacta de El Tono sacada de su celda
                    del roster + piernas y zapatos dibujados. Lo hace
                    tono_final.py. Es un marcador de posicion: cuando llegue
                    el arte definitivo de El Tono, se reemplaza el PNG y el
                    juego no cambia ni una linea -solo el valor `waist` de
                    PLAYABLE, que dice por donde se parte el sprite-.
"""
import sys, os
import numpy as np, cv2
from PIL import Image

ROSTER_GRID = dict(x0=258, y0=142, pw=138.0, ph=133.0, inset_x=6, inset_y=5,
                   cw=126, ch=100, cols=6, rows=5)
CAMI_INDEX = 26


def celdas(roster):
    g = ROSTER_GRID
    out = []
    for i in range(g['cols'] * g['rows']):
        r, c = divmod(i, g['cols'])
        x = int(round(g['x0'] + c * g['pw'])) + g['inset_x']
        y = int(round(g['y0'] + r * g['ph'])) + g['inset_y']
        out.append(np.array(roster.crop((x, y, x + g['cw'], y + g['ch']))).astype(np.uint8))
    return out


def quitar_anillo(cells):
    """El anillo dorado de CAMILITA vive solo en el marco exterior."""
    g = ROSTER_GRID
    med = np.median(np.stack(cells), axis=0).astype(np.uint8)
    cell = cells[CAMI_INDEX].astype(int)
    R, B = cell[:, :, 0], cell[:, :, 2]
    ys, xs = np.mgrid[0:g['ch'], 0:g['cw']]
    marco = (ys < 11) | (ys > g['ch'] - 12) | (xs < 11) | (xs > g['cw'] - 12)
    m = (((R > 150) & (R - B > 30)) & marco).astype(np.uint8)
    m = cv2.dilate(m, np.ones((3, 3), np.uint8))
    m = (m.astype(bool) & marco).astype(np.uint8)
    out = np.where(m[..., None] > 0, med, cells[CAMI_INDEX]).astype(np.uint8)
    borde = cv2.dilate(m, np.ones((3, 3), np.uint8)) - m
    out = np.where(borde[..., None] > 0, cv2.GaussianBlur(out, (3, 3), 0), out)
    cells[CAMI_INDEX] = out
    return cells


def grabcut(pil, box, inset=(14, 10, 14, 10), iters=8):
    src = np.array(pil.crop(box))[:, :, ::-1].copy()
    h, w = src.shape[:2]
    mask = np.zeros((h, w), np.uint8)
    rect = (inset[0], inset[1], w - inset[0] - inset[2], h - inset[1] - inset[3])
    cv2.grabCut(src, mask, rect, np.zeros((1, 65), np.float64),
                np.zeros((1, 65), np.float64), iters, cv2.GC_INIT_WITH_RECT)
    a = np.where((mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD), 255, 0).astype(np.uint8)
    a = cv2.morphologyEx(a, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    a = cv2.morphologyEx(a, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    n, lab, stats, _ = cv2.connectedComponentsWithStats(a, 8)
    if n > 1:
        a = np.where(lab == 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA]), 255, 0).astype(np.uint8)
    img = Image.fromarray(np.dstack([np.array(pil.crop(box)), a]))
    return img.crop(img.getchannel('A').getbbox())


def main():
    if len(sys.argv) < 5:
        print(__doc__)
        sys.exit(1)
    roster = Image.open(sys.argv[1]).convert('RGB')
    portada = Image.open(sys.argv[2]).convert('RGB')
    logo = Image.open(sys.argv[3]).convert('RGBA')
    out = sys.argv[4]
    os.makedirs(out, exist_ok=True)

    g = ROSTER_GRID
    cells = quitar_anillo(celdas(roster))
    atlas = Image.new('RGB', (g['cw'] * g['cols'], g['ch'] * g['rows']))
    for i, cl in enumerate(cells):
        r, c = divmod(i, g['cols'])
        atlas.paste(Image.fromarray(cl), (c * g['cw'], r * g['ch']))
    atlas.save(os.path.join(out, 'roster-atlas.png'))

    portada.save(os.path.join(out, 'bg-city.webp'), 'WEBP', quality=88, method=6)

    logo = logo.crop(logo.getchannel('A').getbbox())
    logo.resize((900, round(900 * logo.height / logo.width)), Image.LANCZOS) \
        .save(os.path.join(out, 'logo.webp'), 'WEBP', quality=92, method=6)

    grabcut(roster, (1132, 290, 1466, 702)).save(os.path.join(out, 'spr-camilita.png'))

    print('Listo. spr-eltono.png se arma aparte con tono_final.py '
          '(ver el encabezado de este archivo).')


if __name__ == '__main__':
    main()
