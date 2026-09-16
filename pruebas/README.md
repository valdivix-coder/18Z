# Regresión de *Zombies en el 18*

```bash
cd pruebas && python3 correr-todo.py            # todo
cd pruebas && python3 correr-todo.py rotulos    # una sola
```

Decide por el **código de salida** de cada suite y por nada más. Si una
suite declarada no está en el disco, **falla** en vez de saltársela.

## Qué protege cada suite

| Suite | Qué vigila | De qué fallo real nació |
|---|---|---|
| `chk-arnes.py` | El arnés mismo: disco ↔ corredor, que cada suite pueda fallar, que todo esté en git | Las pruebas vivían fuera del repo y se perdieron enteras al reciclarse el entorno. Y una suite imprimía sus fallas saliendo con código 0: la regresión la contaba en verde |
| `chk-arte.py` | Los dibujos: recorte aplicado, sin fondo colado entre el pelo, rostros en proporción | Quedaban medialunas blancas entre los mechones de La Primera y La Mon |
| `test-reparto.py` | `PERSONAJES` es la única lista; lo declarado calza con el archivo | Había dos listas paralelas con los nombres escritos dos veces |
| `test-portada.py` | El presupuesto vertical de 540 px: suelo, botón, logotipo | El botón «TOCA PARA INICIAR» se sentó encima de las botas de La Mon |
| `test-seleccion.py` | Grilla, panel PLAYER 1 desde el primer cuadro, escala compartida, pies sin cortar | El personaje no aparecía: un `opacity` en línea le ganaba a la regla del reposo |
| `test-rotulos.py` | Ningún nombre rompe su placa, por largo que sea | La regla deducía el cuerpo de letra del largo del nombre con umbrales a mano |
| `test-transiciones.py` | El corte tapado por el destello, el rebote de la cortina, la vuelta | Se fundían las dos escenas: el momento más caro de la app |
| `test-gestos.py` | Que ningún toque se trague en silencio | `<button disabled>` ni recibe el evento; y dos sacudidas seguidas se anulaban |
| `test-audio.py` | El ambiente no se corta; el botón no se pega | Se apretaba una vez y quedaba pegado |

## Cuatro trampas al medir — parecen fallos de la app y no lo son

1. **El escenario está escalado** (`transform: scale`). `offsetWidth` da
   píxeles de maquetación y `getBoundingClientRect()` los ya escalados.
   Mezclarlos inventa desbordes que no existen. Pasó.
2. **`offsetWidth` no ve las transformaciones.** Un texto condensado con
   `scaleX` sigue midiendo su ancho original. Para lo renderizado, el
   rectángulo.
3. **Medir a mitad de una animación.** El personaje del panel entra desde
   46 px más abajo durante 620 ms: midiendo antes, *todos* parecen
   cortados por el marco. Pasó.
4. **El eco de consola de un recurso que falta no trae la URL**, así que
   no se puede filtrar el favicon por ahí. Los 404 los vigila el
   detector de respuestas, que sí la ve.

## Cómo escribir una suite nueva

Parte de `ayuda.py`: levanta el juego en un puerto libre, abre el
navegador y salta la intro. Registra con `ok(condición, etiqueta,
detalle)` y termina con `ayuda.resumen("nombre")` — que **sale con
código distinto de cero** si algo falló. Después súmala a `SUITES` en
`correr-todo.py`: `chk-arnes.py` exige que disco y corredor calcen en
las dos direcciones.

**Una prueba que no puede fallar no es una prueba.** Antes de darla por
buena, rómpela a propósito y comprueba que cae.
