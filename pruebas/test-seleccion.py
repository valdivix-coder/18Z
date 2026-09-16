"""
PANTALLA DE SELECCION — la grilla, el panel y la escala compartida.

Lo que protege:
 · que la grilla se llene desde PERSONAJES y no de una lista paralela
 · que cada rostro CARGUE (naturalWidth>0): al sumar gente el olvido
   tipico es subir el cuerpo y no la cara
 · que el personaje del panel use la escala COMPARTIDA, que es lo que
   hace que sus diferencias de estatura sean las de verdad
 · que los pies no queden cortados por el marco del panel
 · que el panel PLAYER 1 este desde el primer cuadro, antes de la cortina
"""
import asyncio
from playwright.async_api import async_playwright
import ayuda
from ayuda import ok, casi

async def main():
    async with async_playwright() as pw:
        b, pg, errores, malas = await ayuda.abrir(pw)
        await ayuda.al_titulo(pg)
        rep = await ayuda.reparto(pg)

        # el panel del jugador NO forma parte de la cortina: tiene que
        # verse desde el primer cuadro (es un requisito de diseno explicito)
        await pg.evaluate("SEL.entrar()")
        await pg.wait_for_timeout(260)
        temprano = await pg.evaluate("""(()=>{
          const c=document.getElementById('curtain').getBoundingClientRect();
          const p=document.getElementById('p1Box').getBoundingClientRect();
          const n=document.getElementById('p1Name').getBoundingClientRect();
          return {cortina:c.height, panel:p.width>0&&p.height>0, rotulo:n.width>0,
                  clip:getComputedStyle(document.getElementById('curtain')).clipPath};
        })()""")
        ok(temprano["panel"], "el panel PLAYER 1 existe antes de que baje la cortina")
        ok(temprano["rotulo"], "el rotulo del jugador existe antes de la cortina")
        ok("100%" in temprano["clip"] or "%" in temprano["clip"],
           "la cortina todavia esta recogida", temprano["clip"])
        await pg.wait_for_timeout(1700)

        g = await pg.evaluate("""(()=>{
          const s=[...document.querySelectorAll('#slots .slot')];
          const libres=s.filter(x=>x.classList.contains('free'));
          return {total:s.length, libres:libres.length,
                  bloq:s.filter(x=>x.classList.contains('lock')).length,
                  rostros:libres.map(x=>{const i=x.querySelector('img');
                    return {id:x.dataset.who, cargo:!!i&&i.naturalWidth>0};}),
                  tabIndex:s.filter(x=>x.classList.contains('lock')&&x.tabIndex!==-1).length};
        })()""")
        ok(g["total"] == 30, "la grilla tiene 30 casillas", g["total"])
        ok(g["libres"] == len(rep), "hay una casilla por personaje",
           f"{g['libres']} casillas vs {len(rep)} personajes")
        ok(g["bloq"] == 30 - len(rep), "el resto queda bloqueado", g["bloq"])
        ok(g["tabIndex"] == 0, "las casillas vacias salen del recorrido con tabulador")
        faltan = [r["id"] for r in g["rostros"] if not r["cargo"]]
        ok(not faltan, "todos los rostros cargaron", faltan)

        # PK: la escala compartida sale del mas alto y el mas ancho de TODOS
        pk = await pg.evaluate("""(()=>{
          const caja=document.getElementById('p1Box');
          let mw=0,mh=0; PERSONAJES.forEach(c=>{if(c.w>mw)mw=c.w; if(c.h>mh)mh=c.h;});
          return Math.min((caja.offsetHeight-12)/mh, caja.offsetWidth*0.95/mw);
        })()""")

        for i, p in enumerate(rep):
            await ayuda.tocar_casilla(pg, i)
            await pg.wait_for_timeout(120)
        await pg.wait_for_timeout(700)

        # uno por uno, comprobando escala y que no se corte
        for i, p in enumerate(rep):
            await ayuda.tocar_casilla(pg, i)
            # 700 ms: la entrada del personaje dura 620 y arranca 46 px mas
            # abajo. Midiendo antes, TODOS parecen cortados por el marco —
            # que es lo que paso al escribir esto.
            await pg.wait_for_timeout(700)
            d = await pg.evaluate("""(()=>{
              const s=document.getElementById('p1Sprite'), c=document.getElementById('p1Box');
              const a=s.getBoundingClientRect(), r=c.getBoundingClientRect();
              return {src:s.getAttribute('src'), w:s.offsetWidth, h:s.offsetHeight,
                      nom:document.getElementById('p1NameTxt').textContent,
                      arm:document.getElementById('goBtn').classList.contains('arm'),
                      sobraAbajo:r.bottom-a.bottom, sobraLados:a.left-r.left};
            })()""")
            ok(d["src"] == f"assets/p-{p['id']}.webp", f"{p['nom']}: el panel trae su dibujo", d["src"])
            ok(d["nom"] == p["nom"].upper(), f"{p['nom']}: el rotulo del panel", d["nom"])
            ok(d["arm"], f"{p['nom']}: CONTINUAR queda armado")
            casi(d["w"], round(p["w"] * pk), 2, f"{p['nom']}: ancho a la escala compartida")
            casi(d["h"], round(p["h"] * pk), 2, f"{p['nom']}: alto a la escala compartida")
            ok(d["sobraAbajo"] >= -0.5, f"{p['nom']}: los pies no quedan cortados", d["sobraAbajo"])
            ok(d["sobraLados"] >= -0.5, f"{p['nom']}: no se sale por el lado", d["sobraLados"])

        ok(not errores, "sin errores de JavaScript", errores[:2])
        ok(not malas, "sin recursos que falten", malas[:3])
        await b.close()
    ayuda.resumen("test-seleccion")

asyncio.run(main())
