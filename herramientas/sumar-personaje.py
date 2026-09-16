#!/usr/bin/env python3
"""
SUMAR UN PERSONAJE — la tubería completa, de la imagen a los dos webp.

    python3 herramientas/sumar-personaje.py dibujo.png tatan

Hace el recorte, saca el rostro, y dice la LÍNEA exacta que hay que pegar
en `PERSONAJES` dentro de inicio.html. Eso es todo lo que hay que tocar:
de esa lista salen la portada, la grilla, el rótulo en mayúsculas, la
escala del panel y la precarga.

LA ALTURA NO SE SACA DEL RECORTE. Cada dibujo llega encuadrado por su
cuenta, así que su alto en bruto es una decisión del encuadre y no la
estatura del personaje. Todos los altos del reparto cuelgan de La Naya,
que es la única que viene de la lámina original donde los seis estaban a
una escala. El factor es 488/1182 = 0,4129 y vale mientras los dibujos
sigan llegando con este encuadre (alto de tinta ~1170-1210 px). Si un
lote llega con otro encuadre, hay que recalibrar contra alguien conocido.
"""
import os, sys
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from recortar import recortar
from rostros import recorta as recorta_rostro

FACTOR = 488 / 1182.0     # el patrón de La Naya
RES = 1.42                # el archivo va a 1,42x lo lógico (retina)
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def main():
    if len(sys.argv) < 3:
        print(__doc__); raise SystemExit(2)
    origen, cid = sys.argv[1], sys.argv[2]
    nom = sys.argv[3] if len(sys.argv) > 3 else cid.capitalize()
    assets = os.path.join(RAIZ, "assets")

    im, (tw, th), islas = recortar(origen)
    if not (1100 <= th <= 1290):
        print(f"OJO: la tinta mide {th} px de alto y el lote conocido va de 1170 a 1210.")
        print("     El factor de escala se calibró con ese encuadre; revísalo antes de seguir.")
    h = round(th * FACTOR); w = round(tw * FACTOR)
    fh = round(h * RES)
    pr = os.path.join(assets, f"p-{cid}.webp")
    im.resize((round(fh * tw / th), fh), Image.LANCZOS).save(pr, "WEBP", quality=86, method=6)
    fr = os.path.join(assets, f"f-{cid}.webp")
    recorta_rostro(pr, cid).save(fr, "WEBP", quality=88, method=6)

    print(f"  {os.path.relpath(pr, RAIZ)}   {os.path.getsize(pr)//1024} KB   "
          f"islas de fondo quitadas: {islas}")
    print(f"  {os.path.relpath(fr, RAIZ)}   {os.path.getsize(fr)//1024} KB")
    print("\nPega esta línea en PERSONAJES, dentro de inicio.html:\n")
    print(f'  {{id:"{cid}", nom:"{nom}", w:{w}, h:{h}, portada:null}},')
    print("\n(portada:null = solo en la grilla. La portada ya tiene sus seis;")
    print(" un séptimo ahí encoge a todos los demás.)")
    print("\nDespués:  cd pruebas && python3 correr-todo.py")

main()
