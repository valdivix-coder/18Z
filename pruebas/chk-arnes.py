"""
EL ARNES SE MIRA A SI MISMO.

Existe porque la perdida ya ocurrio en otro proyecto, DOS VECES y en
silencio: las pruebas vivian fuera del repositorio y se fueron enteras
cuando se reciclo el entorno, con la documentacion describiendolas
semanas como si estuvieran ahi. Guardarlo todo en git era la mitad del
arreglo; la otra mitad es que una perdida haga FALLAR algo.

Y vigila la afirmacion mas peligrosa que puede hacer un arnes: «todo
bien» sobre algo que acaba de fallar. Una suite que imprime sus fallas y
sale con codigo 0 se cuenta en verde. Aqui se comprueba de verdad,
ejecutando una suite de mentira que falla a proposito.
"""
import os, re, subprocess, sys
import ayuda
from ayuda import ok

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = ayuda.RAIZ

def leer(p):
    return open(os.path.join(AQUI, p), encoding="utf-8").read()

def main():
    # ---- 1. disco ↔ corredor, en LAS DOS direcciones ----
    corredor = leer("correr-todo.py")
    declaradas = re.findall(r'^\s*"([\w-]+\.py)",', corredor, re.M)
    en_disco = sorted(f for f in os.listdir(AQUI)
                      if re.fullmatch(r"(test|chk)-[\w-]+\.py", f))
    ok(set(declaradas) == set(en_disco),
       "toda suite del disco esta en correr-todo.py y al reves",
       f"solo en disco: {sorted(set(en_disco)-set(declaradas))} | "
       f"solo declaradas: {sorted(set(declaradas)-set(en_disco))}")
    ok(len(en_disco) >= 8, "el arnes no se quedo corto", len(en_disco))

    # ---- 2. cada suite puede fallar: termina en resumen() y comprueba algo ----
    for s in en_disco:
        src = leer(s)
        ok("ayuda.resumen(" in src, f"{s} termina llamando a resumen()")
        n = len(re.findall(r"\bok\(", src))
        ok(n >= 5, f"{s} hace comprobaciones de verdad", f"{n} llamadas a ok()")
        ok("import ayuda" in src, f"{s} usa el ayudante comun")

    # ---- 3. y resumen() SALE con codigo distinto de cero. Probado. ----
    falsa = os.path.join(AQUI, "_arnes_prueba_tmp.py")
    try:
        open(falsa, "w", encoding="utf-8").write(
            "import ayuda\nayuda.ok(False,'falla a proposito')\nayuda.resumen('falsa')\n")
        r = subprocess.run([sys.executable, falsa], cwd=AQUI, capture_output=True, text=True)
        ok(r.returncode != 0, "una suite que falla SALE con codigo distinto de cero",
           f"codigo {r.returncode}")
        ok("FALLA" in r.stdout, "y lo dice por pantalla")
        open(falsa, "w", encoding="utf-8").write(
            "import ayuda\nayuda.ok(True,'pasa')\nayuda.resumen('falsa')\n")
        r = subprocess.run([sys.executable, falsa], cwd=AQUI, capture_output=True, text=True)
        ok(r.returncode == 0, "y una que pasa sale con cero", f"codigo {r.returncode}")
    finally:
        if os.path.exists(falsa):
            os.remove(falsa)

    # ---- 4. el corredor NO se salta una suite que falta ----
    #      Probado de verdad, no leyendo el codigo: se hace una copia del
    #      corredor que declara una suite inexistente y se mira que se
    #      niegue a correr. Un grep sobre el fuente no prueba conducta.
    copia = os.path.join(AQUI, "_arnes_corredor_tmp.py")
    try:
        open(copia, "w", encoding="utf-8").write(
            corredor.replace('SUITES = [', 'SUITES = [\n    "test-que-no-existe.py",', 1))
        r = subprocess.run([sys.executable, copia], cwd=AQUI, capture_output=True, text=True)
        ok(r.returncode != 0, "el corredor FALLA si falta una suite declarada",
           f"codigo {r.returncode}")
        ok("FALTAN SUITES" in r.stdout, "y dice cual falta")
        ok("comprobaciones" not in r.stdout,
           "y no corre NADA: una suite que desaparece no se compensa con las otras")
    finally:
        if os.path.exists(copia):
            os.remove(copia)

    # ---- 5. ninguna COPIA de produccion dentro de pruebas/ ----
    #      Ha pasado: un script de restauracion con el directorio cambiado
    #      deja una copia congelada del juego, con el mismo nombre que la
    #      de verdad. Commiteada, el repo pasa a tener dos juegos.
    intrusos = [f for f in os.listdir(AQUI)
                if f in ("inicio.html", "index.html") or f.endswith((".webp", ".mp4", ".webm"))]
    ok(not intrusos, "no hay copias de produccion dentro de pruebas/", intrusos)
    ok(not os.path.isdir(os.path.join(AQUI, "assets")), "no hay un assets/ dentro de pruebas/")

    # ---- 6. lo que la documentacion nombra, existe ----
    lee = leer("README.md")
    for n in set(re.findall(r"`([\w./-]+\.(?:py|html|json|md))`", lee)):
        base = n.split("/")[-1]
        ok(os.path.exists(os.path.join(AQUI, base)) or os.path.exists(os.path.join(RAIZ, n))
           or os.path.exists(os.path.join(RAIZ, "herramientas", base)),
           f"el README nombra `{n}` y existe")

    # ---- 7. TODO esta en git. Es el punto de todo esto. ----
    r = subprocess.run(["git", "ls-files"], cwd=RAIZ, capture_output=True, text=True)
    if ok(r.returncode == 0, "el proyecto vive en un repositorio git"):
        seguidos = set(r.stdout.split())
        for s in en_disco + ["correr-todo.py", "ayuda.py", "README.md"]:
            ok(f"pruebas/{s}" in seguidos, f"pruebas/{s} esta en git")
        # recorriendo el arbol: las herramientas tienen subcarpeta
        for base, _, files in os.walk(os.path.join(RAIZ, "herramientas")):
            if "__pycache__" in base:
                continue
            for t in sorted(files):
                rel = os.path.relpath(os.path.join(base, t), RAIZ).replace(os.sep, "/")
                ok(rel in seguidos, f"{rel} esta en git")
        ok("inicio.html" in seguidos, "el juego esta en git")
        ok(any(x.startswith("assets/p-") for x in seguidos), "los dibujos estan en git")
        ok("CLAUDE.md" in seguidos, "el contexto para la proxima sesion esta en git")

    # ---- 8. las herramientas de arte siguen ahi y parsean ----
    for t in ("recortar.py", "rostros.py", "sumar-personaje.py", "ajuste.json"):
        r2 = os.path.join(RAIZ, "herramientas", t)
        if ok(os.path.exists(r2), f"existe herramientas/{t}") and t.endswith(".py"):
            try:
                compile(open(r2, encoding="utf-8").read(), t, "exec")
                ok(True, f"herramientas/{t} parsea")
            except SyntaxError as e:
                ok(False, f"herramientas/{t} parsea", str(e))

    ayuda.resumen("chk-arnes")

main()
