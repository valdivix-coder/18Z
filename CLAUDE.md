# Zombies en el 18 — contexto del proyecto

## Qué es
Juego de pelea arcade de zombis chilenos para **celular en horizontal**, pensado para
circular durante la semana del 18 de septiembre. Es un **único archivo HTML/CSS/JS
vanilla** (`inicio.html`), sin frameworks ni paso de compilación, publicado como
artefacto: **https://claude.ai/artifact/MqbqNLnCRz58UxP6Z7RypM**

El estándar que pide Simón, repetido en cada ronda: *digno de premios internacionales
de diseño de videojuegos*. Y lo más importante de todo: **el parecido de cada
personaje con su dibujo es innegociable**.

## ⏱️ Estado (léelo en 10 segundos)
- **Hecho:** pantalla de inicio (intro en video + coreografía de entrada + ambiente
  sintetizado) y pantalla de **selección de personaje** (cortina metálica, grilla de
  30 casillas, panel PLAYER 1 con el personaje en reposo de pelea, CONTINUAR).
- **Reparto: 15 personajes.** Seis en la portada, quince en la grilla.
- **El juego en sí NO existe todavía.** CONTINUAR vuelve a la pantalla de inicio.
- **Regresión: 9 suites, ~510 comprobaciones**, dentro del repo en `pruebas/`.
  Se corre con `cd pruebas && python3 correr-todo.py`.
- Versión publicada: **v1.4** (se ve al pie de la pantalla de inicio).

## Regla no negociable
**El arnés vive DENTRO del repositorio.** Nada que sirva para verificar el juego
puede vivir en un directorio temporal: se recicla el entorno y se pierde entero, con
la documentación describiéndolo semanas como si estuviera ahí. `chk-arnes.py` exige
que cada suite esté seguida por git.

Y su corolario: **una prueba que no puede fallar no es una prueba.** Antes de dar una
por buena, rómpela a propósito y comprueba que cae.

## El reparto es UNA sola lista
`PERSONAJES` en `inicio.html` es la única fuente de verdad. De ahí salen la portada,
la grilla, el rótulo en mayúsculas, la escala del panel y la precarga.

```js
{id:"tatan", nom:"Tatán", w:437, h:508, portada:2}
```
- `id` → sus dos archivos: `assets/p-<id>.webp` (cuerpo entero, recortado al píxel) y
  `assets/f-<id>.webp` (rostro, proporción 135×82).
- `w,h` → las medidas del dibujo. De ahí sale la **escala compartida**, en la portada
  y en el panel: por eso las diferencias de estatura son las de verdad y no las de
  encajar a cada uno en su caja.
- `portada` → su puesto en la fila de inicio, o `null` si solo va en la grilla.
  **En la portada caben SEIS**; un séptimo encoge a todos.

**Sumar a alguien es un comando y una línea:**
```bash
python3 herramientas/sumar-personaje.py dibujo.png elmario "El Mario"
cd pruebas && python3 correr-todo.py
```

**La altura NO se saca del recorte.** Cada dibujo llega encuadrado por su cuenta, así
que su alto en bruto es una decisión del encuadre y no la estatura del personaje.
Todos los altos cuelgan de **La Naya**, la única que viene de la lámina original donde
los seis estaban a una escala. Factor `488/1182 = 0,4129`, válido mientras los dibujos
sigan llegando con este encuadre (tinta de ~1170 a 1210 px de alto).

## El recorte del fondo blanco, y sus tres condiciones
Los dibujos llegan sobre blanco. El relleno desde el borde quita el fondo exterior,
pero **no** las islas que quedan encerradas entre los mechones del pelo — y esas se
leían como tajos blancos sobre el fondo oscuro del juego.

Separarlas del dibujo legítimo necesita **tres condiciones juntas**, y cada una tapa
un agujero que costó una vuelta entera:
1. **entorno oscuro** — sin esto se borra una camisa blanca dentro de un traje azul;
2. **cerca del fondo real** — sin esto se borran el cierre, la cadena y la hebilla de
   una parka, que también son blancos sobre ropa oscura pero viven en medio del pecho;
3. **en la mitad de arriba** — sin esto se borran los cordones de unas zapatillas.

**El color no sirve para separarlos:** el dibujante usa el mismo blanco para la camisa
y para el fondo (medido: hueco de pelo 250,3; camisa 252,6). Está en
`herramientas/recortar.py` y lo vigila `chk-arte.py`, que mide **superficie total** y
no islas sueltas: un destello en unos lentes cumple las mismas tres condiciones.

## Decisiones de diseño que no conviene deshacer

**El cambio de pantalla es un CORTE tapado por el destello, no un fundido.** Las
recreativas cortan; y un fundido obliga al teléfono a dibujar las dos escenas a la vez
—con sus dos lienzos de fuego y sus dos fondos— durante medio segundo. El destello
llega a su máximo a los 52 ms, así que el cambio ocurre a los 70, a plena luz.
Medido: mezcla visible **0,000**. `test-transiciones.py` lo fija.

**La cortina rebota.** Baja acelerando, toca el suelo a los ~900 ms, rebota un 3,6% y
se asienta a los 1.180. El golpe metálico suena en el toque, no al final de la
animación. El sonido de persiana no es una muestra: son cientos de chasquidos cuya
frecuencia sigue a la velocidad de la cortina. El oído reconoce una persiana por el
**ritmo**, no por el timbre de un golpe suelto.

**El panel PLAYER 1 está desde el primer cuadro**, no forma parte de la cortina. El
módulo es **una sola imagen** usada dos veces con recortes complementarios al 65,371%:
así la cortina baja sola y al terminar no hay costura.

**El botón «TOCA PARA INICIAR» se ancla a la línea de suelo MEDIDA**, no a un número
escrito. Ya se sentó una vez encima de unas botas. La composición vertical es un
presupuesto que cierra: `6 + 228 (logotipo) + 12 + 234 (personajes) = 474`, y abajo
`8 + 48 del botón + 10`. Si tocas una pieza, vuelve a cuadrar la suma.

**El cuerpo de letra de los rótulos se MIDE, no se deduce del largo del nombre.** Y si
un nombre no entra ni al mínimo legible, **se condensa en horizontal en vez de
cortarse**: la placa centra su texto, así que un recorte se comería las dos puntas.
Ojo: los rótulos se vuelven a ajustar en `document.fonts.ready`, porque lo medido
antes de que llegue Bungee fue la tipografía de respaldo.

**Ningún toque se traga en silencio.** Un `<button disabled>` ni siquiera recibe el
evento: CONTINUAR usa `aria-disabled` y avisa con zumbido y sacudida.

**La precarga va en dos tiempos.** Al arrancar solo los rostros (~16 KB cada uno,
tienen que estar en el cuadro en que la cortina termina de subir); los cuerpos de
quienes no salen en la portada, al **entrar** a la selección, donde hay 1,2 s de
cortina por delante y el gesto ya dijo que la persona está eligiendo.

## Cuatro trampas al medir (parecen fallos de la app y no lo son)
1. **El escenario está escalado** (`transform: scale`). `offsetWidth` da píxeles de
   maquetación y `getBoundingClientRect()` los ya escalados. Mezclarlos inventa
   desbordes que no existen — me pasó, y reporté un fallo que no existía.
2. **`offsetWidth` no ve las transformaciones.** Un texto condensado con `scaleX`
   sigue midiendo su ancho original.
3. **Medir a mitad de una animación.** El personaje del panel entra desde 46 px más
   abajo durante 620 ms: midiendo antes, *todos* parecen cortados por el marco.
4. **El eco de consola de un recurso que falta no trae la URL.** Los 404 los vigila el
   detector de respuestas, que sí la ve.

## Cómo trabajar con Simón
- **Cambios quirúrgicos.** Ediciones mínimas y localizadas, no reescrituras.
- **Explica el *por qué*, no solo el arreglo.**
- **Mide antes de afirmar.** Varias veces la medición desmintió lo que parecía obvio a
  ojo, y también al revés: lo que parecía un fallo era la prueba mal escrita.
- **Verifica en el navegador, no en la cabeza.** Cada ronda de arte se juzga sobre el
  fondo oscuro del juego y al tamaño real de la casilla, no a tamaño completo.
- Si un personaje nuevo es ambiguo, **pregunta cuál es cuál**. Un nombre bajo la cara
  equivocada es el error más caro de este proyecto.

## Pendientes
- **El juego en sí.** Hoy CONTINUAR vuelve al inicio.
- **La Naya es la única con arte de la primera lámina**; si llega su versión nueva, es
  reemplazar dos archivos y ajustar su ancho.
- Quedan **15 casillas libres** en la grilla.
- Nombre a confirmar: **«La Soa Janet»** está escrito tal como llegó; podría ser
  «La Sra. Janet».
