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

        # --- la portada se DERIVA, no se escribe aparte ---
        port = await pg.evaluate("CAST.map(c=>c.id)")
        esperada = [p["id"] for p in sorted([q for q in rep if q["portada"] is not None],
                                            key=lambda q: q["portada"])]
        ok(port == esperada, "la portada se deriva de portada!=null y en su orden",
           f"{port} vs {esperada}")
        ok(len(port) == 6, "la portada tiene exactamente seis", len(port))
        puestos = [p["portada"] for p in rep if p["portada"] is not None]
        ok(sorted(puestos) == list(range(len(puestos))),
           "los puestos de portada son 0..n sin huecos ni repetidos", sorted(puestos))

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
