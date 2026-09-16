#!/usr/bin/env python3
"""
EL CORREDOR.

  cd pruebas && python3 correr-todo.py           corre todo
  cd pruebas && python3 correr-todo.py rotulos   corre solo las que calcen

Decide por el CODIGO DE SALIDA de cada suite y por nada mas. Y si una
suite declarada NO ESTA en el disco, esto FALLA en vez de saltarsela:
saltar una suite que falta deja a la regresion diciendo "todo en verde"
con una suite entera de menos, que es la mentira mas cara que puede
decir un arnes.
"""
import os, subprocess, sys, time

AQUI = os.path.dirname(os.path.abspath(__file__))

# El orden es deliberado: primero lo que no necesita navegador (falla en
# un segundo), despues lo lento.
SUITES = [
    "chk-arnes.py",         # el arnes se mira a si mismo, y va primero
    "chk-arte.py",          # integridad de los dibujos, sin navegador
    "test-reparto.py",      # la lista unica calza con los archivos
    "test-portada.py",      # composicion de la pantalla de inicio
    "test-seleccion.py",    # grilla, panel y escala compartida
    "test-rotulos.py",      # ningun nombre rompe su placa
    "test-transiciones.py", # el corte, la cortina y la vuelta
    "test-gestos.py",       # ningun toque se traga en silencio
    "test-audio.py",        # el ambiente no se corta, el boton no se pega
]

def main():
    filtro = sys.argv[1] if len(sys.argv) > 1 else ""
    elegidas = [s for s in SUITES if filtro in s] if filtro else list(SUITES)
    if filtro and not elegidas:
        print(f"Ninguna suite calza con «{filtro}». Hay: " +
              ", ".join(s[:-3] for s in SUITES))
        sys.exit(2)

    faltan = [s for s in elegidas if not os.path.exists(os.path.join(AQUI, s))]
    if faltan:
        print("FALTAN SUITES EN EL DISCO — no se corre nada:")
        for s in faltan:
            print(f"   ✗ {s}")
        print("\nEsto no se salta. Una suite que desaparece tiene que doler.")
        sys.exit(1)

    print(f"Zombies en el 18 — {len(elegidas)} suites\n" + "─" * 52)
    malas, total, t0 = [], 0, time.time()
    for s in elegidas:
        t = time.time()
        r = subprocess.run([sys.executable, s], cwd=AQUI,
                           capture_output=True, text=True)
        salida = (r.stdout or "") + (r.stderr or "")
        n = 0
        for linea in salida.splitlines():
            if linea.startswith("[OK]") and ":" in linea:
                try: n = int(linea.rsplit(":", 1)[1].strip().split()[0])
                except Exception: pass
        total += n
        seg = time.time() - t
        if r.returncode == 0:
            print(f"  ✓ {s[:-3]:<20} {n:>4} comprobaciones   {seg:5.1f}s")
        else:
            malas.append(s)
            print(f"  ✗ {s[:-3]:<20} FALLA                  {seg:5.1f}s")
            for linea in salida.splitlines():
                if linea.strip().startswith(("✗", "Traceback", "  File", "Error")) or "FALLA]" in linea:
                    print(f"      {linea.rstrip()}")
    print("─" * 52)
    if malas:
        print(f"HAY FALLAS en {len(malas)}: " + ", ".join(m[:-3] for m in malas))
        sys.exit(1)
    print(f"TODO EN VERDE — {total} comprobaciones en {time.time()-t0:.0f}s")
    sys.exit(0)

main()
