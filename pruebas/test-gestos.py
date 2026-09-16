"""
GESTOS — que nada se trague un toque en silencio.

La regla de esta pantalla: si un toque no hace lo que se espera, tiene
que DECIRLO. Dos fallos reales que esto vigila:
 · CONTINUAR era un <button disabled>, y un boton deshabilitado ni
   siquiera recibe el evento: pulsarlo sin haber elegido no hacia NADA y
   nada explicaba por que. Ahora usa aria-disabled y avisa.
 · Dos sacudidas seguidas se anulaban, porque el temporizador PENDIENTE
   de la primera le quitaba la clase a la segunda. Pasa de verdad al
   pulsar CONTINUAR justo cuando la cortina toca el suelo.
"""
import asyncio
from playwright.async_api import async_playwright
import ayuda
from ayuda import ok

async def main():
    async with async_playwright() as pw:
        b, pg, errores, malas = await ayuda.abrir(pw)
        await ayuda.al_titulo(pg)

        # un toque en cualquier parte del titulo entra a la seleccion
        await pg.evaluate("document.dispatchEvent(new PointerEvent('pointerdown',{bubbles:true}))")
        await pg.wait_for_timeout(1900)
        ok(await pg.evaluate("SEL.abierta"), "un toque en el titulo lleva a la seleccion")

        # CONTINUAR sin haber elegido: avisa y NO sale
        est = await pg.evaluate("document.getElementById('goBtn').getAttribute('aria-disabled')")
        ok(est == "true", "CONTINUAR nace anunciandose como no disponible", est)
        await ayuda.tocar(pg, "#goBtn")
        await pg.wait_for_timeout(110)
        ok(await pg.evaluate("document.getElementById('selMod').classList.contains('shake')"),
           "CONTINUAR sin elegir SACUDE el modulo")
        await pg.wait_for_timeout(700)
        ok(await pg.evaluate("SEL.abierta"), "y no se sale de la pantalla")

        # sacudidas encadenadas: la segunda no puede anularse con la primera
        await ayuda.tocar(pg, "#goBtn")
        await pg.wait_for_timeout(330)
        await ayuda.tocar(pg, "#goBtn")
        await pg.wait_for_timeout(120)
        ok(await pg.evaluate("document.getElementById('selMod').classList.contains('shake')"),
           "dos sacudidas seguidas no se anulan entre si")
        await pg.wait_for_timeout(500)

        # casilla bloqueada: sacude ella, no el modulo
        n = len(await ayuda.reparto(pg))
        await ayuda.tocar_casilla(pg, 29)
        await pg.wait_for_timeout(110)
        ok(await pg.evaluate("document.querySelectorAll('#slots .slot')[29].classList.contains('no')"),
           "una casilla bloqueada avisa al tocarla")
        ok(await pg.evaluate("!p1Sprite.getAttribute('src')"),
           "y no pone a nadie en el panel")
        await pg.wait_for_timeout(400)

        # elegir, y volver a tocar al MISMO no rompe nada
        await ayuda.tocar_casilla(pg, 0)
        await pg.wait_for_timeout(800)
        uno = await pg.evaluate("p1NameTxt.textContent")
        await ayuda.tocar_casilla(pg, 0)
        await pg.wait_for_timeout(300)
        ok(await pg.evaluate("p1NameTxt.textContent") == uno,
           "volver a tocar al mismo personaje lo deja igual")

        # cambiar de personaje limpia el aro del anterior
        await ayuda.tocar_casilla(pg, 1)
        await pg.wait_for_timeout(800)
        sel = await pg.evaluate("document.querySelectorAll('#slots .slot.sel').length")
        ok(sel == 1, "solo una casilla queda marcada a la vez", sel)

        # un toque al aire de la seleccion no elige ni continua
        antes = await pg.evaluate("p1NameTxt.textContent")
        await pg.evaluate("document.dispatchEvent(new PointerEvent('pointerdown',{bubbles:true}))")
        await pg.wait_for_timeout(400)
        ok(await pg.evaluate("SEL.abierta"), "un toque al aire no saca de la seleccion")
        ok(await pg.evaluate("p1NameTxt.textContent") == antes, "ni cambia de personaje")

        # doble toque rapido en CONTINUAR: sale UNA vez
        await ayuda.tocar(pg, "#goBtn")
        await ayuda.tocar(pg, "#goBtn")
        await pg.wait_for_timeout(1700)
        ok(not await pg.evaluate("SEL.abierta"), "un doble toque en CONTINUAR sale una sola vez")
        ok(await pg.evaluate("document.getElementById('logoWrap').classList.contains('in')"),
           "y deja el titulo en pie")

        # Escape tambien sale (teclado)
        await ayuda.a_seleccion(pg)
        await pg.keyboard.press("Escape")
        await pg.wait_for_timeout(900)
        ok(not await pg.evaluate("SEL.abierta"), "Escape sale de la seleccion")

        # el teclado no le roba Enter a un boton enfocado
        await ayuda.a_seleccion(pg)
        await pg.evaluate("document.querySelectorAll('#slots .slot.free')[2].focus()")
        await pg.keyboard.press("Enter")
        await pg.wait_for_timeout(800)
        ok(await pg.evaluate("SEL.abierta"), "Enter sobre una casilla no cierra la pantalla")
        ok(await pg.evaluate("!!p1Sprite.getAttribute('src')"), "Enter sobre una casilla elige")

        ok(not errores, "sin errores de JavaScript", errores[:2])
        ok(not malas, "sin recursos que falten", malas[:3])
        await b.close()
    ayuda.resumen("test-gestos")

asyncio.run(main())
