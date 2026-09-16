"""
ROTULOS — que ningun nombre rompa su placa, por largo que sea.

El cuerpo de letra se MIDE, no se deduce del largo del nombre. La regla
anterior contaba caracteres con umbrales escritos a mano; con personajes
entrando de a poco, acertar el umbral es cuestion de tiempo.

OJO AL MEDIR: la placa vive dentro de un escenario con `transform:scale`.
Hay que comparar rectangulos RENDERIZADOS con rectangulos renderizados;
mezclar offsetWidth (sin escalar) con getBoundingClientRect (escalado) da
falsas alarmas — ya paso.
"""
import asyncio
from playwright.async_api import async_playwright
import ayuda
from ayuda import ok

LARGOS = ["Maximiliano Bustamante", "La Chinganera del 18", "Doña Berta de la Cruz"]

async def medir(pg):
    return await pg.evaluate("""[...document.querySelectorAll('#slots .plate')]
      .filter(p=>p.textContent).map(p=>({
        n:p.textContent,
        texto:p.firstChild.getBoundingClientRect().width,
        placa:p.getBoundingClientRect().width,
        alto:p.firstChild.getBoundingClientRect().height,
        cajaAlto:p.getBoundingClientRect().height,
        letra:parseFloat(getComputedStyle(p).fontSize)}))""")

async def main():
    async with async_playwright() as pw:
        # ---- los nombres de verdad ----
        b, pg, errores, malas = await ayuda.abrir(pw)
        await ayuda.al_titulo(pg)
        await ayuda.a_seleccion(pg)
        rep = await ayuda.grilla(pg)
        filas = await medir(pg)
        ok(len(filas) == len(rep), "hay un rotulo por personaje", f"{len(filas)} vs {len(rep)}")
        for f in filas:
            ok(f["texto"] <= f["placa"] + 0.5, f"«{f['n']}» cabe en su placa",
               f"{f['texto']:.1f} / {f['placa']:.1f}")
            ok(f["alto"] <= f["cajaAlto"] + 0.5, f"«{f['n']}» no desborda de alto")
            ok(f["letra"] >= 6.0, f"«{f['n']}» no bajo de un cuerpo legible", f["letra"])
        ok(all(f["n"] == f["n"].upper() for f in filas), "los rotulos van en mayusculas")
        # el nombre del panel tambien
        await ayuda.tocar_casilla(pg, 0)
        await pg.wait_for_timeout(700)
        p1 = await pg.evaluate("""({texto:p1NameTxt.getBoundingClientRect().width,
          caja:document.getElementById('p1Name').getBoundingClientRect().width,
          letra:parseFloat(getComputedStyle(document.getElementById('p1Name')).fontSize)})""")
        ok(p1["texto"] <= p1["caja"] + 0.5, "el nombre grande del panel cabe", p1)
        ok(p1["letra"] >= 12, "y no bajo de 12 px", p1["letra"])
        ok(not errores, "sin errores de JavaScript", errores[:2])
        await b.close()

        # ---- nombres deliberadamente largos: el camino de ENCOGER ----
        # Ningun nombre actual lo ejercita, asi que sin esto ese camino no
        # estaria probado hasta que alguien lo estrene en produccion.
        b, pg, errores, _ = await ayuda.abrir(pw)
        # sobre GRILLA: son los MISMOS objetos, pero en el orden en que se
        # pintan las casillas, asi las tres primeras placas son estas
        await pg.evaluate("GRILLA.slice(0,%d).forEach((p,i)=>{p.nom=%s[i];})"
                          % (len(LARGOS), str(LARGOS)))
        await ayuda.al_titulo(pg)
        await ayuda.a_seleccion(pg)
        filas = await medir(pg)
        for f in filas[:len(LARGOS)]:
            ok(f["texto"] <= f["placa"] + 0.5, f"nombre largo «{f['n']}» sigue cabiendo",
               f"{f['texto']:.1f} / {f['placa']:.1f}")
        chicos = [f for f in filas[:len(LARGOS)] if f["letra"] < 10]
        ok(len(chicos) == len(LARGOS), "los nombres largos encogieron de verdad",
           [(f["n"], f["letra"]) for f in filas[:len(LARGOS)]])
        # y el ultimo recurso: condensar en vez de cortar
        cond = await pg.evaluate("""[...document.querySelectorAll('#slots .plate')]
          .filter(p=>p.textContent).slice(0,3).map(p=>getComputedStyle(p.firstChild).transform)""")
        ok(any(c != "none" for c in cond),
           "al tope, el nombre se CONDENSA en vez de cortarse", cond)
        ok(not errores, "sin errores de JavaScript (nombres largos)", errores[:2])
        await b.close()
    ayuda.resumen("test-rotulos")

asyncio.run(main())
