"""
TRANSICIONES — el corte, la cortina y la vuelta.

El cambio de pantalla es un CORTE tapado por el destello, no un fundido.
Dos razones: es el idioma de una recreativa, y un fundido obliga al
telefono a dibujar las DOS escenas a la vez —con sus dos lienzos de fuego
y sus dos fondos— durante medio segundo. Esta suite mide que eso no pase:
si alguien vuelve a poner una transicion de opacidad, la mezcla deja de
ser cero y esto cae.
"""
import asyncio
from playwright.async_api import async_playwright
import ayuda
from ayuda import ok

async def main():
    async with async_playwright() as pw:
        b, pg, errores, malas = await ayuda.abrir(pw)
        await ayuda.al_titulo(pg)

        # ---- ENTRADA: las dos escenas nunca se ven juntas ----
        muestras = await pg.evaluate("""new Promise(res=>{
          const g=id=>parseFloat(getComputedStyle(document.getElementById(id)).opacity);
          const out=[]; let t0=null;
          function tick(ts){ if(t0===null)t0=ts;
            out.push([Math.round(ts-t0), g('pg-sel'), g('flash'),
              document.getElementById('fx').classList.contains('on'),
              document.getElementById('selFx').classList.contains('on')]);
            if(ts-t0<1000) requestAnimationFrame(tick); else res(out); }
          SEL.entrar(); requestAnimationFrame(tick);
        })""")
        peor = 0.0
        dosfuegos = 0
        for ms, sel, fl, fx, sfx in muestras:
            if 0.02 < sel < 0.98:
                peor = max(peor, (1 - sel) * (1 - fl))
            if fx and sfx:
                dosfuegos += 1
        ok(peor < 0.02, "al entrar, las dos escenas nunca se ven mezcladas", f"peor {peor:.3f}")
        ok(dosfuegos == 0, "los dos lienzos de fuego nunca corren a la vez", dosfuegos)
        ok(any(f for _, _, _, _, f in muestras), "el fuego de la fonda se enciende")

        await pg.wait_for_timeout(1400)
        # ---- la cortina bajo entera y se asento ----
        est = await pg.evaluate("""({clip:getComputedStyle(document.getElementById('curtain')).clipPath,
          riel:getComputedStyle(document.getElementById('rail')).top,
          rodando:SEL.rodando, abierta:SEL.abierta})""")
        ok("0%" in est["clip"] or "0px" in est["clip"], "la cortina termino abajo", est["clip"])
        ok(not est["rodando"], "la cortina dejo de rodar")
        ok(est["abierta"], "la pantalla de seleccion quedo abierta")

        # ---- la cortina pasa por el rebote: es lo que la hace metalica ----
        await ayuda.tocar_casilla(pg, 0)
        await pg.wait_for_timeout(300)
        await pg.evaluate("SEL.salir()")
        await pg.wait_for_timeout(1500)
        curva = await pg.evaluate("""new Promise(res=>{
          const c=document.getElementById('curtain'); const out=[]; let t0=null;
          function tick(ts){ if(t0===null)t0=ts;
            const m=getComputedStyle(c).clipPath.match(/([\\d.]+)%\\s*0(px)?\\)/);
            out.push([Math.round(ts-t0), m?parseFloat(m[1]):-1]);
            if(ts-t0<2100) requestAnimationFrame(tick); else res(out); }
          SEL.entrar(); requestAnimationFrame(tick);
        })""")
        vals = [v for _, v in curva if v >= 0]
        if ok(len(vals) > 20, "se pudo seguir la cortina", len(vals)):
            # el PRIMER toque, no el minimo global: el minimo global es el
            # asentamiento final y mirando ahi el rebote se pierde entero
            primero = next((i for i, v in enumerate(vals) if v < 1.0), None)
            if ok(primero is not None, "la cortina llega abajo"):
                despues = vals[primero:]
                ok(max(despues) > 2.0, "la cortina REBOTA al tocar el suelo",
                   f"maximo tras tocar: {max(despues):.1f}%")
                ok(vals[-1] < 1.0, "y se asienta abajo del todo", vals[-1])
        await pg.wait_for_timeout(400)

        # ---- VUELTA: CONTINUAR devuelve al titulo y rehace la coreografia ----
        await ayuda.tocar_casilla(pg, 1)
        await pg.wait_for_timeout(400)
        await ayuda.tocar(pg, "#goBtn")
        await pg.wait_for_timeout(1600)
        v = await pg.evaluate("""({sel:SEL.abierta,
          on:document.getElementById('pg-sel').classList.contains('on'),
          roll:document.getElementById('curtain').classList.contains('roll'),
          logo:document.getElementById('logoWrap').classList.contains('in'),
          fuegoPortada:document.getElementById('fx').classList.contains('on'),
          fuegoSel:document.getElementById('selFx').classList.contains('on'),
          replay:document.getElementById('replayBtn').style.display})""")
        ok(not v["sel"], "CONTINUAR cierra la seleccion")
        ok(not v["on"], "la pantalla de seleccion queda apagada")
        ok(not v["roll"], "la cortina queda rearmada para la proxima vez")
        ok(v["logo"], "el titulo rehizo su coreografia de entrada")
        ok(v["fuegoPortada"] and not v["fuegoSel"], "el fuego volvio a la portada")
        ok(v["replay"] != "none", "el boton de repetir la intro vuelve a estar")

        ok(not errores, "sin errores de JavaScript", errores[:2])
        ok(not malas, "sin recursos que falten", malas[:3])
        await b.close()
    ayuda.resumen("test-transiciones")

asyncio.run(main())
