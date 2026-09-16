"""
EL ICONO Y LA INSTALACION — sin navegador.

Esta suite existe porque lo que vigila FALLA EN SILENCIO. Un icono con
canal alfa no rompe nada: se ve perfecto en el escritorio y aparece como
un CUADRADO BLANCO en el lanzador de Android, que compone lo transparente
sobre blanco. Un manifiesto que apunta a un archivo que ya no esta no da
ningun error visible: Android cae a su icono de respaldo. Y un nombre
escrito en un solo sitio deja la app llamandose distinto segun el
telefono. Nada de eso se ve desde aqui; solo se ve con el juego ya
instalado, que es tarde.

QUE MIDE:
 1. Los cuatro archivos existen, miden lo declarado y NO TIENEN ALFA.
 2. Los derivados salen del maestro de ahora. Es la misma idea con la
    que chk-arte regenera cada rostro: si se cambia el arte y se olvida
    rehacer los tamanos chicos, esto tiene que doler.
 3. El arte entero cabe en la zona segura del «maskable» —el 80% central
    que Android garantiza—, comprobado devolviendo ese recorte a su
    tamano y comparandolo con el maestro. Y el normal NO cabe, que es
    justamente por lo que hacen falta los dos.
 4. El manifiesto apunta a archivos que existen con las medidas que
    declara, y trae un icono `maskable`.
 5. LOS TRES SITIOS QUE DECIDEN EL NOMBRE INSTALADO DICEN LO MISMO:
    `name` y `short_name` del manifiesto (Android) y
    `apple-mobile-web-app-title` (iOS). NO se fija el texto, se fija que
    COINCIDAN: el nombre puede cambiar —cambió, de «Zombies en el 18» a
    «18-Z»— y lo que no puede pasar es que la app se instale llamandose
    distinto segun el aparato. Ademas tiene que ser CORTO: el escritorio
    de Android corta la etiqueta cerca de los 12 caracteres, que es
    justo por lo que se acorto. El titulo de la pagina, en cambio, si
    tiene que decir el nombre completo del juego: es lo que se ve en la
    pestana y lo que se comparte.
 6. El service worker existe, se registra, atiende `fetch` —sin eso
    Android no ofrece instalar— y va a la RED PRIMERO.
 7. Vercel no deja cachear ni el manifiesto ni el service worker, y la
    raiz sirve el juego.
 8. Hay UN manifiesto y UN service worker, no dos. Dos registrados en el
    mismo ambito se pisan —gana el ultimo— y dos manifiestos dan dos
    nombres de instalacion distintos segun por donde se entre. Ya pasó:
    convivieron un `manifest.json` y un `manifest.webmanifest`, y el
    segundo instalaba la app como «18Z».
"""
import json, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "herramientas"))
import numpy as np
from PIL import Image
import ayuda
from ayuda import ok
import icono

RAIZ = ayuda.RAIZ
ASSETS = os.path.join(RAIZ, "assets")
JUEGO = "Zombies en el 18"     # el nombre publico, el del titulo
NOMBRE_MAX = 12                # lo que cabe bajo un icono de Android
ZONA = 0.80           # lo unico que Android garantiza de un maskable


def recorte_central(ruta, frac):
    """Devuelve el frac central de una imagen, a tamano de maestro."""
    im = Image.open(ruta).convert("RGB")
    lado = im.width
    n = int(lado * frac)
    o = (lado - n) // 2
    return im.crop((o, o, o + n, o + n)).resize((512, 512), Image.LANCZOS)


def dif(a, b):
    return float(np.abs(np.array(a).astype(int) - np.array(b).astype(int)).mean())


def main():
    # ---- 1. los archivos ------------------------------------------------
    for nombre, lado, zona in icono.SALIDAS:
        r = os.path.join(ASSETS, nombre)
        if not ok(os.path.exists(r), f"existe {nombre}"):
            continue
        im = Image.open(r)
        ok(im.size == (lado, lado), f"{nombre}: mide {lado}x{lado}", str(im.size))
        # LA REGLA DE ANDROID: nada de alfa, ni por canal ni por indice.
        tiene = im.mode in ("RGBA", "LA", "PA") or "transparency" in im.info
        ok(not tiene, f"{nombre}: sin canal alfa (o el lanzador lo pinta blanco)", im.mode)

        # ---- 2. sale del maestro de AHORA ------------------------------
        d = dif(im.convert("RGB"), icono.componer(lado, zona))
        ok(d < 1.0, f"{nombre}: corresponde al arte maestro de ahora",
           f"diferencia media {d:.2f}")

    # El maestro va en color directo: con paleta de 256 el cielo se bandea
    # (error medio 4,8 y picos de 141 medidos sobre este arte).
    ok(Image.open(os.path.join(ASSETS, "icon-512.png")).mode == "RGB",
       "el maestro va en color directo, sin paleta")

    # ---- 3. la zona segura ----------------------------------------------
    maestro = icono.arte()
    dentro = dif(recorte_central(os.path.join(ASSETS, "icon-maskable-512.png"),
                                 icono.ZONA_SEGURA), maestro)
    ok(dentro < 6.0, "el arte entero cabe en el 80% central del maskable",
       f"diferencia media {dentro:.2f} contra el maestro")
    # Si el normal tambien cupiera, el maskable no haria falta y estariamos
    # regalando el 22% del icono en los lanzadores que no recortan.
    fuera = dif(recorte_central(os.path.join(ASSETS, "icon-512.png"),
                                icono.ZONA_SEGURA), maestro)
    ok(fuera > 20.0, "el normal, en cambio, aprovecha el lienzo entero",
       f"diferencia media {fuera:.2f}")

    # ---- 4. el manifiesto ----------------------------------------------
    rm = os.path.join(RAIZ, "manifest.json")
    if ok(os.path.exists(rm), "existe manifest.json"):
        m = json.load(open(rm, encoding="utf-8"))
        nombre = m.get("name")
        ok(bool(nombre), "el manifiesto declara un nombre", nombre)
        ok(m.get("short_name") == nombre,
           "el nombre corto del manifiesto dice lo mismo que el largo",
           f'{nombre!r} contra {m.get("short_name")!r}')
        ok(len(nombre or "") <= NOMBRE_MAX,
           f"el nombre instalado cabe bajo el icono (<= {NOMBRE_MAX})",
           f"{nombre!r} son {len(nombre or '')}")
        ok(m.get("display") == "standalone", "abre como app y no como pestana", m.get("display"))
        ok(m.get("start_url") == "/", "arranca en la raiz", m.get("start_url"))
        for c in ("background_color", "theme_color"):
            ok(bool(m.get(c)), f"declara {c}")
        ics = m.get("icons", [])
        ok(any(i.get("purpose") == "maskable" for i in ics), "declara un icono maskable")
        ok({i.get("sizes") for i in ics} >= {"192x192", "512x512"},
           "trae los dos tamanos que Android pide")
        for i in ics:
            ri = os.path.join(RAIZ, i["src"])
            if ok(os.path.exists(ri), f"el manifiesto apunta a {i['src']}, que existe"):
                w, h = Image.open(ri).size
                ok(f"{w}x{h}" == i["sizes"], f"{i['src']}: mide lo que el manifiesto declara",
                   f"{w}x{h} contra {i['sizes']}")

    # ---- 5. el HTML ----------------------------------------------------
    s = open(ayuda.JUEGO, encoding="utf-8").read()
    ok('rel="manifest" href="manifest.json"' in s, "el HTML enlaza el manifiesto")
    ok('rel="apple-touch-icon" href="assets/apple-touch-icon.png"' in s,
       "el HTML enlaza el icono de iOS")
    t = re.search(r'name="apple-mobile-web-app-title" content="([^"]+)"', s)
    ok(t is not None, "el HTML declara el nombre de instalacion de iOS")
    if t:
        man = json.load(open(rm, encoding="utf-8")) if os.path.exists(rm) else {}
        ok(t.group(1) == man.get("name"),
           "iOS y Android instalan con el MISMO nombre",
           f'iOS {t.group(1)!r} contra manifiesto {man.get("name")!r}')
    ok('name="apple-mobile-web-app-capable" content="yes"' in s, "iOS lo abre a pantalla completa")
    ok('name="viewport"' in s, "trae viewport (sin el, el telefono maqueta a 980 px)")
    ti = re.search(r"<title>([^<]+)</title>", s)
    ok(ti and JUEGO in ti.group(1),
       f"el titulo de la pagina dice «{JUEGO}» entero", ti and ti.group(1))

    # ---- 6. el service worker ------------------------------------------
    rs = os.path.join(RAIZ, "sw.js")
    if ok(os.path.exists(rs), "existe sw.js"):
        w = open(rs, encoding="utf-8").read()
        ok('addEventListener("fetch"' in w,
           "atiende fetch (sin eso Android no ofrece instalar)")
        # RED PRIMERO: el fetch tiene que ir ANTES que la cache, o un
        # telefono se queda con la version vieja sin enterarse.
        ok(w.index("fetch(req)") < w.index("caches.match"),
           "va a la red primero y a la cache solo si no hay red")
    ok('navigator.serviceWorker.register("sw.js")' in s, "el HTML lo registra")

    # ---- 7. Vercel ------------------------------------------------------
    v = json.load(open(os.path.join(RAIZ, "vercel.json"), encoding="utf-8"))
    reglas = {h["source"]: h["headers"] for h in v.get("headers", [])}
    clave = [k for k in reglas if "manifest.json" in k]
    ok(bool(clave), "vercel.json tiene una regla para el manifiesto")
    if clave:
        vals = " ".join(x["value"] for x in reglas[clave[0]])
        ok("no-cache" in vals, "el manifiesto no se sirve desde la cache", vals)

    # ---- 8. uno solo de cada cosa --------------------------------------
    # Dos service workers en el mismo ambito se pisan; dos manifiestos
    # dan dos nombres de instalacion segun por donde se entre.
    manis = [f for f in os.listdir(RAIZ) if f.startswith("manifest")]
    ok(manis == ["manifest.json"], "hay un solo manifiesto en la raiz", manis)
    sws = [f for f in os.listdir(RAIZ)
           if f.endswith(".js") and ("sw" in f or "service-worker" in f)]
    ok(sws == ["sw.js"], "hay un solo service worker en la raiz", sws)
    # Y una sola puerta de entrada: con dos, cada una trae su manifiesto y
    # su titulo de iOS, asi que la app se instalaria distinto segun cual
    # abrio la persona.
    htmls = sorted(f for f in os.listdir(RAIZ) if f.endswith(".html")
                   and f != "juego-fase1-historico.html")
    ok(htmls == ["inicio.html"], "hay una sola puerta de entrada", htmls)
    v2 = json.load(open(os.path.join(RAIZ, "vercel.json"), encoding="utf-8"))
    ok(any(r.get("source") == "/" and r.get("destination") == "/inicio.html"
           for r in v2.get("rewrites", [])), "la raiz del sitio sirve el juego")

    ayuda.resumen("chk-icono")

main()
