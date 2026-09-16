"""
Piezas compartidas por todas las suites.

REGLA QUE SOSTIENE TODO ESTO: una prueba que no puede FALLAR no es una
prueba. `resumen()` termina el proceso con codigo distinto de cero cuando
hay fallas, y `correr-todo.py` decide por ese codigo y por nada mas. En
otro proyecto esto ya costo caro: una suite imprimia "HAY FALLAS" y salia
con codigo 0, asi que la regresion la contaba en verde. `chk-arnes.py`
vigila justamente eso.
"""
import glob, http.server, os, socket, socketserver, sys, threading

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JUEGO = os.path.join(RAIZ, "inicio.html")

# ---------------------------------------------------------------- contador
_ok, _fallas, _notas = 0, [], []

def ok(cond, etiqueta, detalle=""):
    """Registra una comprobacion. `detalle` se imprime solo si falla."""
    global _ok
    if cond:
        _ok += 1
    else:
        _fallas.append((etiqueta, str(detalle)))
    return bool(cond)

def casi(a, b, tol, etiqueta):
    return ok(abs(a - b) <= tol, etiqueta, f"{a} vs {b} (tolerancia {tol})")

def nota(txt):
    _notas.append(txt)

def resumen(nombre):
    for n in _notas:
        print(f"   · {n}")
    if _fallas:
        print(f"\n[FALLA] {nombre}: {_ok} OK, {len(_fallas)} FALLAS")
        for e, d in _fallas:
            print(f"   ✗ {e}" + (f"  → {d}" if d else ""))
        sys.exit(1)
    print(f"[OK] {nombre}: {_ok} comprobaciones")
    sys.exit(0)

# ---------------------------------------------------------------- servidor
class _H(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=RAIZ, **k)
    def guess_type(self, path):
        t = super().guess_type(path)
        # el anfitrion real manda charset; sin esto salen acentos rotos y
        # una prueba de texto falla por el motivo equivocado
        return "text/html; charset=utf-8" if t == "text/html" else t
    def log_message(self, *a):
        pass

def servidor():
    """Levanta el juego en un puerto libre. Uno por proceso, asi que las
    suites no se estorban entre si al correr en serie o en paralelo."""
    s = socket.socket(); s.bind(("127.0.0.1", 0)); puerto = s.getsockname()[1]; s.close()
    srv = socketserver.TCPServer(("127.0.0.1", puerto), _H)
    srv.allow_reuse_address = True
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return f"http://127.0.0.1:{puerto}/inicio.html"

# ---------------------------------------------------------------- navegador
def chromium_path():
    for p in sorted(glob.glob("/opt/pw-browsers/chromium-*/chrome-linux/chrome"), reverse=True):
        return p
    return None

async def navegador(pw, **kw):
    ruta = chromium_path()
    args = ["--no-sandbox", "--disable-dev-shm-usage"] + kw.pop("args", [])
    if ruta:
        return await pw.chromium.launch(executable_path=ruta, args=args, **kw)
    return await pw.chromium.launch(args=args, **kw)

# ---------------------------------------------------------------- escenario
async def abrir(pw, ancho=844, alto=390, con_audio=False, **kw):
    """Devuelve (navegador, pagina, errores, respuestas_malas) con el juego
    cargado y la intro ya saltada, que es donde empiezan casi todas las
    comprobaciones."""
    args = ["--autoplay-policy=no-user-gesture-required"] if con_audio else []
    b = await navegador(pw, args=args, **kw)
    pg = await b.new_page(viewport={"width": ancho, "height": alto})
    errores, malas = [], []
    pg.on("pageerror", lambda e: errores.append(str(e)))
    # El eco de consola de un recurso que falta NO trae la URL, asi que no
    # se puede filtrar el favicon por ahi. Los recursos que faltan los
    # vigila `malas`, que si ve la direccion; aqui solo interesan los
    # errores de JavaScript de verdad.
    pg.on("console", lambda m: errores.append("console.error: " + m.text)
          if m.type == "error" and "Failed to load resource" not in m.text
          and "CERT" not in m.text else None)
    pg.on("response", lambda r: malas.append((r.status, r.url.rsplit("/", 1)[-1]))
          if r.status >= 400 and "favicon" not in r.url else None)
    await pg.goto(servidor())
    await pg.wait_for_timeout(900)
    return b, pg, errores, malas

async def al_titulo(pg, espera=2400):
    """Salta la intro y espera a que termine la coreografia de entrada."""
    await pg.evaluate("toTitle()")
    await pg.wait_for_timeout(espera)

async def a_seleccion(pg, espera=1900):
    """Entra a la pantalla de seleccion y espera a que la cortina termine."""
    await pg.evaluate("SEL.entrar()")
    await pg.wait_for_timeout(espera)

async def tocar(pg, sel):
    """Toque sintetico: la app atiende pointerdown, no click."""
    await pg.evaluate(
        f"document.querySelector({sel!r}).dispatchEvent("
        "new PointerEvent('pointerdown',{bubbles:true}))")

async def tocar_casilla(pg, i):
    await pg.evaluate(
        f"document.querySelectorAll('#slots .slot')[{i}]"
        ".dispatchEvent(new PointerEvent('pointerdown',{bubbles:true}))")

async def reparto(pg):
    """La lista de personajes tal como la ve el juego."""
    return await pg.evaluate("PERSONAJES.map(p=>({id:p.id,nom:p.nom,w:p.w,h:p.h,portada:p.portada}))")
