"""
EL REPARTO — una sola lista, y que lo declarado calce con los archivos.

PERSONAJES es la unica fuente de verdad: de ahi salen la portada, la
grilla, el rotulo en mayusculas, la escala del panel y la precarga. Antes
habia DOS listas paralelas con los nombres escritos dos veces en dos
mayusculas distintas; esto existe para que eso no vuelva.

Tambien comprueba lo que de verdad se rompe al sumar gente: que el w/h
declarado calce con la proporcion REAL del archivo. Si no calzan, el
personaje sale estirado y nadie se entera hasta verlo en el telefono.
"""
import asyncio, json, os, re, struct
from playwright.async_api import async_playwright
import ayuda
from ayuda import ok

ASSETS = os.path.join(ayuda.RAIZ, "assets")

def medir_webp(ruta):
    """Lee el tamano de un .webp sin dependencias externas."""
    with open(ruta, "rb") as f:
        d = f.read(40)
    if d[:4] != b"RIFF" or d[8:12] != b"WEBP":
        return None
    t = d[12:16]
    if t == b"VP8X":
        w = int.from_bytes(d[24:27], "little") + 1
        h = int.from_bytes(d[27:30], "little") + 1
        return w, h
    if t == b"VP8L":
        b = struct.unpack("<I", d[21:25])[0]
        return (b & 0x3FFF) + 1, ((b >> 14) & 0x3FFF) + 1
    if t == b"VP8 ":
        return struct.unpack("<HH", d[26:30])[0] & 0x3FFF, struct.unpack("<HH", d[26:30])[1] & 0x3FFF
    return None

async def main():
    async with async_playwright() as pw:
        b, pg, errores, malas = await ayuda.abrir(pw)
        rep = await ayuda.reparto(pg)
        ok(len(rep) >= 6, "hay reparto", len(rep))

        # --- ids sanos y unicos ---
        ids = [p["id"] for p in rep]
        ok(len(set(ids)) == len(ids), "no hay ids repetidos",
           [i for i in ids if ids.count(i) > 1])
        nombres = [p["nom"] for p in rep]
        ok(len(set(nombres)) == len(nombres), "no hay nombres repetidos")
        ok(all(re.fullmatch(r"[a-z][a-z0-9]*", i) for i in ids),
           "los ids son minusculas sin espacios", [i for i in ids if not re.fullmatch(r"[a-z][a-z0-9]*", i)])

        # --- archivos: los dos por personaje, y sin huerfanos ---
        for p in rep:
            for pre, que in (("p", "cuerpo entero"), ("f", "rostro")):
                r = os.path.join(ASSETS, f"{pre}-{p['id']}.webp")
                ok(os.path.exists(r), f"{p['nom']}: existe su {que}", r)
        en_disco = {f[2:-5] for f in os.listdir(ASSETS) if f.startswith("p-") and f.endswith(".webp")}
        huerf = en_disco - set(ids)
        ok(not huerf, "no hay dibujos de nadie que ya no este en la lista", huerf)

        # --- lo declarado calza con el archivo ---
        for p in rep:
            m = medir_webp(os.path.join(ASSETS, f"p-{p['id']}.webp"))
            if not ok(m is not None, f"{p['nom']}: su cuerpo es un webp legible"):
                continue
            real, dec = m[0] / m[1], p["w"] / p["h"]
            ok(abs(real - dec) < 0.02, f"{p['nom']}: la proporcion declarada calza con el dibujo",
               f"declarada {dec:.3f}, real {real:.3f} ({m[0]}x{m[1]})")
            ok(m[1] >= p["h"], f"{p['nom']}: el archivo tiene resolucion suficiente",
               f"{m[1]} px de alto para {p['h']} logicos")
        for p in rep:
            m = medir_webp(os.path.join(ASSETS, f"f-{p['id']}.webp"))
            if m:
                ok(abs(m[0]/m[1] - 135/82) < 0.03, f"{p['nom']}: el rostro tiene la proporcion de la casilla",
                   f"{m[0]}x{m[1]} = {m[0]/m[1]:.3f}")

        # --- cada personaje declara su sexo: de ahi sale la alternancia ---
        ok(all(p["sexo"] in ("h", "m") for p in rep),
           "todos declaran su sexo", [p["id"] for p in rep if p["sexo"] not in ("h", "m")])
        hs = [p for p in rep if p["sexo"] == "h"]; ms = [p for p in rep if p["sexo"] == "m"]
        ayuda.nota(f"reparto: {len(hs)} hombres, {len(ms)} mujeres")
        n = await pg.evaluate("PORTADA_N")
        ok(len(hs) >= -(-n // 2) and len(ms) >= n // 2,
           "el reparto da para alternar empezando por cualquiera de los dos",
           f"{len(hs)}h / {len(ms)}m para filas de {n}")

        # --- la GRILLA va en orden alfabetico, y se DERIVA ---
        gr = [p["nom"] for p in await ayuda.grilla(pg)]
        esp = sorted(gr, key=lambda x: __import__("locale").strxfrm(x))
        ok(len(gr) == len(rep), "la grilla trae a todo el reparto", f"{len(gr)} vs {len(rep)}")
        ok(set(gr) == {p["nom"] for p in rep}, "y a los mismos, sin inventar ni perder")
        orden_js = await pg.evaluate("""(()=>{
          const a=GRILLA.map(p=>p.nom);
          const b=a.slice().sort((x,y)=>x.localeCompare(y,'es',{sensitivity:'base'}));
          return a.join('|')===b.join('|');
        })()""")
        ok(orden_js, "la grilla esta en orden alfabetico", gr)

        # --- el sorteo de la portada cumple sus reglas, 200 veces ---
        pr = await pg.evaluate("""(()=>{
          const out=[]; for(let i=0;i<200;i++){const c=portadaDelDia();
            out.push({n:c.length, s:c.map(p=>p.sexo).join(''),
                      ids:c.map(p=>p.id).join(','), unicos:new Set(c.map(p=>p.id)).size});}
          return out;})()""")
        ok(all(x["n"] == n for x in pr), f"todo sorteo trae {n}",
           sorted({x["n"] for x in pr}))
        ok(all(x["unicos"] == n for x in pr), "ningun sorteo repite personaje")
        ok(all(all(x["s"][i] != x["s"][i+1] for i in range(len(x["s"])-1)) for x in pr),
           "todo sorteo alterna hombre y mujer",
           sorted({x["s"] for x in pr})[:4])
        ok(len({x["ids"] for x in pr}) > 150, "los sorteos son variados",
           f"{len({x['ids'] for x in pr})} filas distintas en 200")
        salen = set()
        for x in pr: salen.update(x["ids"].split(","))
        ok(len(salen) == len(rep), "con el tiempo salen TODOS: no hay protagonista fijo",
           f"{len(salen)}/{len(rep)}")
        patr = {x["s"] for x in pr}
        ok(len(patr) == 2, "se usan los dos arranques, no siempre el mismo", patr)

        # --- el nombre vive UNA vez: la grilla lo pone en mayusculas sola ---
        fuente = open(ayuda.JUEGO, encoding="utf-8").read()
        # sin los comentarios: la prosa nombra personajes a proposito y no
        # es una segunda fuente de verdad
        codigo = re.sub(r"/\*.*?\*/", "", fuente, flags=re.S)
        for p in rep:
            ok(codigo.count('"' + p["nom"] + '"') == 1,
               f"{p['nom']}: su nombre esta escrito una sola vez en el codigo",
               codigo.count('"' + p["nom"] + '"'))
        ok("toUpperCase()" in fuente, "la mayuscula del rotulo se calcula")

        ok(not errores, "sin errores de JavaScript", errores[:2])
        await b.close()
    ayuda.resumen("test-reparto")

asyncio.run(main())
