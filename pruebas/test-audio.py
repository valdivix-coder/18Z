"""
AUDIO — que el ambiente no se corte y que el boton no se pegue.

El boton de sonido ya estuvo roto dos veces y las dos costaron rondas:
 · se apretaba una vez y quedaba pegado, porque se forzaba A.on=true
   ANTES de alternar, asi que la alternancia siempre terminaba en apagado
 · resume() es asincrono y lo que dependia de el corria en la linea
   siguiente, cuando todavia no estaba vivo
Y el requisito de producto: el ambiente de la portada SIGUE sonando en la
pantalla de seleccion. Si alguien corta el audio al cambiar de pantalla,
esto cae.
"""
import asyncio
from playwright.async_api import async_playwright
import ayuda
from ayuda import ok

async def main():
    async with async_playwright() as pw:
        b, pg, errores, malas = await ayuda.abrir(pw, con_audio=True)
        await ayuda.al_titulo(pg)

        async def estado():
            return await pg.evaluate("""({vivo:A.live(), on:A.on, arrancado:A.started,
              vol:A.master?Math.round(A.master.gain.value*100)/100:null,
              ctx:A.ctx?A.ctx.state:null})""")

        e = await estado()
        ok(e["vivo"], "el audio quedo vivo", e)
        ok(e["arrancado"], "el ambiente arranco")
        ok(e["vol"] > 0.5, "suena a volumen pleno", e["vol"])

        # --- el ambiente NO se corta en ninguna transicion ---
        await ayuda.a_seleccion(pg)
        e = await estado()
        ok(e["ctx"] == "running" and e["vol"] > 0.5, "sigue sonando en la seleccion", e)
        await ayuda.tocar_casilla(pg, 0)
        await pg.wait_for_timeout(500)
        e = await estado()
        ok(e["ctx"] == "running" and e["vol"] > 0.5, "sigue sonando al elegir personaje", e)
        await ayuda.tocar(pg, "#goBtn")
        await pg.wait_for_timeout(1600)
        e = await estado()
        ok(e["ctx"] == "running" and e["vol"] > 0.5, "sigue sonando al volver al titulo", e)

        # --- el boton alterna de verdad, seis veces seguidas ---
        vols = []
        for _ in range(6):
            await ayuda.tocar(pg, "#sndBtn")
            await pg.wait_for_timeout(330)
            vols.append(await pg.evaluate("Math.round(A.master.gain.value*100)/100"))
        alterna = all((vols[i] > 0.4) != (vols[i+1] > 0.4) for i in range(len(vols)-1))
        ok(alterna, "el boton de sonido alterna en los seis toques, sin pegarse", vols)
        # dejarlo encendido
        if await pg.evaluate("!A.on"):
            await ayuda.tocar(pg, "#sndBtn"); await pg.wait_for_timeout(330)

        # --- el boton dice en que estado esta ---
        pint = await pg.evaluate("""(()=>{const s=document.getElementById('sndBtn');
          return {on:s.classList.contains('on'), muted:s.classList.contains('muted'),
                  locked:s.classList.contains('locked'),
                  pressed:s.getAttribute('aria-pressed'), label:s.getAttribute('aria-label')};})()""")
        ok(pint["on"] and not pint["muted"] and not pint["locked"],
           "encendido, el boton se pinta encendido", pint)
        ok(pint["pressed"] == "true", "y lo dice para quien no ve la pantalla", pint["pressed"])

        # --- todos los sonidos de la seleccion existen y no revientan ---
        for s in ["shutter", "clang", "pick", "deny", "goHit", "coin", "blip", "titleHit", "step", "riser"]:
            tipo = await pg.evaluate(f"typeof A.{s}")
            ok(tipo == "function", f"existe el sonido A.{s}()", tipo)
        err = await pg.evaluate("""(()=>{ try{ A.shutter(0.3); A.clang(1); A.pick();
            A.deny(); A.goHit(); return null; }catch(e){ return String(e); } })()""")
        ok(err is None, "los sonidos de la seleccion se ejecutan sin reventar", err)

        # --- irse de la app suspende el contexto (el punto naranja de iOS) ---
        await pg.evaluate("Object.defineProperty(document,'hidden',{value:true,configurable:true});"
                          "document.dispatchEvent(new Event('visibilitychange'))")
        await pg.wait_for_timeout(400)
        ok(await pg.evaluate("A.ctx.state") != "running",
           "irse de la app suspende el audio", await pg.evaluate("A.ctx.state"))

        ok(not errores, "sin errores de JavaScript", errores[:2])
        await b.close()
    ayuda.resumen("test-audio")

asyncio.run(main())
