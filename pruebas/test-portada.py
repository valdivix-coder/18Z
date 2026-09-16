"""
PANTALLA DE INICIO — la composicion vertical.

Protege el presupuesto de 540 px que ya se descuadro una vez: el boton
"TOCA PARA INICIAR" se sento encima de las botas de La Mon, y el arreglo
fue anclarlo a la linea de suelo MEDIDA en vez de a un numero escrito.
Si alguien cambia la escala del reparto, el logotipo o el cuerpo de letra
del boton, esto cae antes de que se vea en el telefono.
"""
import asyncio, sys
from playwright.async_api import async_playwright
import ayuda
from ayuda import ok, casi

MEDIDAS = [(667, 375), (844, 390), (1280, 540)]

async def main():
    async with async_playwright() as pw:
        for ancho, alto in MEDIDAS:
            b, pg, errores, malas = await ayuda.abrir(pw, ancho, alto)
            await ayuda.al_titulo(pg)
            g = await pg.evaluate("""(()=>{
              const st=document.getElementById('stage').getBoundingClientRect();
              const esc=st.height/540, E=v=>v/esc;
              const r=e=>{const b=e.getBoundingClientRect();
                return {x:E(b.x-st.left),y:E(b.y-st.top),w:E(b.width),h:E(b.height),
                        abajo:E(b.bottom-st.top),der:E(b.right-st.left)};};
              const pies=CAST.map(c=>r(document.getElementById('fig-'+c.id)).abajo);
              return {portada:CAST.map(c=>c.nom), pies,
                      cta:r(document.getElementById('cta')),
                      logo:r(document.getElementById('logoWrap')),
                      figs:CAST.map(c=>r(document.getElementById('fig-'+c.id))),
                      ctaVisible:document.getElementById('cta').classList.contains('in')};
            })()""")
            m = f"[{ancho}x{alto}]"
            esperado = [p["nom"] for p in await ayuda.reparto(pg) if p["portada"] is not None]
            ok(len(g["portada"]) == len(esperado), f"{m} la portada trae a los de portada!=null",
               f"{len(g['portada'])} vs {len(esperado)}")

            # todos pisan la MISMA linea: es lo que hace que la fila se lea
            casi(max(g["pies"]), min(g["pies"]), 1.5, f"{m} los seis pisan la misma linea de suelo")

            # el boton no toca a nadie ni se sale del escenario
            hueco = g["cta"]["y"] - max(g["pies"])
            ok(hueco >= 5, f"{m} hueco entre los pies y el boton", f"{hueco:.1f} px")
            borde = 540 - g["cta"]["abajo"]
            ok(borde >= 5, f"{m} hueco entre el boton y el borde de abajo", f"{borde:.1f} px")
            ok(g["ctaVisible"], f"{m} el boton esta encendido")

            # el boton tiene que ser GRANDE: crecio a proposito y no puede
            # encogerse sin que alguien se entere
            ok(g["cta"]["h"] >= 44, f"{m} el boton mide al menos 44 px de alto", f"{g['cta']['h']:.0f}")
            ok(g["cta"]["w"] >= 300, f"{m} el boton mide al menos 300 px de ancho", f"{g['cta']['w']:.0f}")

            # el logotipo no se mete con los personajes
            techo = min(f["y"] for f in g["figs"])
            ok(g["logo"]["abajo"] <= techo + 1, f"{m} el logotipo no pisa a los personajes",
               f"logo hasta {g['logo']['abajo']:.0f}, personajes desde {techo:.0f}")
            ok(g["logo"]["h"] >= 140, f"{m} el logotipo conserva su tamano", f"{g['logo']['h']:.0f}")

            # nadie se sale por los lados
            ok(min(f["x"] for f in g["figs"]) >= 0, f"{m} nadie se sale por la izquierda")
            ok(max(f["der"] for f in g["figs"]) <= ancho / (alto/540) + 1,
               f"{m} nadie se sale por la derecha")

            ok(not errores, f"{m} sin errores de JavaScript", errores[:2])
            ok(not malas, f"{m} sin recursos que falten", malas[:3])
            await b.close()
    ayuda.resumen("test-portada")

asyncio.run(main())
