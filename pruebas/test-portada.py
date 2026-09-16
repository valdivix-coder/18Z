"""
PANTALLA DE INICIO — la composicion vertical y el SORTEO de la fila.

La fila son CINCO y cambian en cada carga, alternando hombre y mujer. No
hay protagonista: elegir unos fijos seria decidir quienes son los
importantes, y aqui todos lo son.

Lo delicado de sortear la fila es que la ESCALA no puede depender de a
quien le toque salir. Si se midiera contra el mas alto de los cinco de
hoy, un mismo personaje se veria de distinto tamano segun la compania y
el logotipo cambiaria de porte en cada carga. Por eso se mide contra el
techo FIJO del reparto, y esta suite lo comprueba recargando.

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
            rep = await ayuda.reparto(pg)
            n_esp = await pg.evaluate("PORTADA_N")
            ok(len(g["portada"]) == n_esp, f"{m} la fila trae {n_esp} personajes",
               f"{len(g['portada'])}")
            ok(len(set(g["portada"])) == len(g["portada"]), f"{m} sin nadie repetido en la fila")
            sexos = await pg.evaluate("CAST.map(p=>p.sexo).join('')")
            alterna = all(sexos[i] != sexos[i+1] for i in range(len(sexos)-1))
            ok(alterna, f"{m} la fila alterna hombre y mujer", sexos)
            # centrada: el aire de los dos lados tiene que ser el mismo
            izq = min(f["x"] for f in g["figs"])
            der = (ancho / (alto/540)) - max(f["der"] for f in g["figs"])
            ok(abs(izq - der) <= 2, f"{m} la fila queda centrada",
               f"izquierda {izq:.1f}, derecha {der:.1f}")

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

        # ---- el sorteo cambia, pero la COMPOSICION no se mueve ----
        b, pg, errores, _ = await ayuda.abrir(pw, 844, 390)
        await ayuda.al_titulo(pg)
        vistas, tallas, logos = set(), set(), set()
        for _ in range(12):
            d = await pg.evaluate("""(()=>{
              CAST = portadaDelDia();
              document.getElementById('cast').innerHTML='';
              CAST.forEach(function(c,i){
                var sh=document.createElement('div'); sh.className='fsh'; sh.id='sh-'+c.id;
                document.getElementById('cast').appendChild(sh); });
              CAST.forEach(function(c,i){
                var f=document.createElement('div'); f.className='fig'; f.id='fig-'+c.id;
                c.wait=0.14+i*0.075; c.dx='0px';
                var sw=document.createElement('div'); sw.className='sway';
                var im=document.createElement('img'); im.src='assets/p-'+c.id+'.webp';
                sw.appendChild(im); f.appendChild(sw);
                document.getElementById('cast').appendChild(f); });
              layout();
              var lg=document.getElementById('logoWrap');
              var alto=CAST.map(c=>Math.round(parseFloat(
                document.getElementById('fig-'+c.id).style.height)));
              return {ids:CAST.map(c=>c.id).join(','), sexos:CAST.map(c=>c.sexo).join(''),
                      altos:CAST.map(c=>c.id+':'+Math.round(parseFloat(
                        document.getElementById('fig-'+c.id).style.height))).join(','),
                      logo:lg.style.width+'x'+lg.style.height, mayor:Math.max.apply(null,alto)};
            })()""")
            vistas.add(d["ids"]); logos.add(d["logo"])
            for par in d["altos"].split(","):
                tallas.add(par)
            ok(all(d["sexos"][i] != d["sexos"][i+1] for i in range(len(d["sexos"])-1)),
               "cada sorteo alterna hombre y mujer", d["sexos"])
        ok(len(vistas) >= 8, "la fila cambia de verdad entre cargas",
           f"{len(vistas)} filas distintas en 12 sorteos")
        ok(len(logos) == 1, "el logotipo NO cambia de tamano segun quien salga", logos)
        # cada personaje mide siempre lo mismo, salga con quien salga
        porId = {}
        malos = []
        for par in tallas:
            cid, h = par.split(":")
            if cid in porId and porId[cid] != h:
                malos.append(f"{cid}: {porId[cid]} y {h}")
            porId[cid] = h
        ok(not malos, "cada personaje mide siempre lo mismo, salga con quien salga", malos)
        ok(not errores, "sin errores de JavaScript en el sorteo", errores[:2])
        await b.close()
    ayuda.resumen("test-portada")

asyncio.run(main())
