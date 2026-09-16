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
- **Reparto: 17 personajes.** La grilla los muestra a todos en orden alfabético; la
  portada sortea **cinco** en cada carga, alternando hombre y mujer.
- **El juego en sí NO existe todavía.** CONTINUAR vuelve a la pantalla de inicio.
- **Regresión: 9 suites, ~660 comprobaciones**, dentro del repo en `pruebas/`.
  Se corre con `cd pruebas && python3 correr-todo.py`.
- Versión publicada: **v1.6** (se ve al pie de la pantalla de inicio).

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
{id:"tatan", nom:"Tatán", w:437, h:508, sexo:"h"}
```
- `id` → sus dos archivos: `assets/p-<id>.webp` (cuerpo entero, recortado al píxel) y
  `assets/f-<id>.webp` (rostro, proporción 135×82).
- `w,h` → de ahí sale la **escala compartida**, en la portada y en el panel.

**Cómo se fija el alto — es lo que decide si alguien "se ve más grande".** El alto de
la tinta NO sirve: incluye aureolas, boinas y melenas, así que normalizar por él
encoge el cuerpo de quien lleva algo encima y deja entero el de quien no lleva nada.
De ahí venía que Don Francis se viera más grande. Lo que hace que un reparto se lea
como uno es que las **cabezas** midan parecido. Medido en un mismo cuadro, con todos a
234 px: Don Francis 35 px de cara, Tatán 33, Pedrito 31, Don Alberto 31, La Primera 27
— un 30 % de diferencia. Igualar del todo daría alturas de 436 a 579 y La Primera
pasaría por encima de todos, así que se iguala **con tope**: la altura se acerca a la
que igualaría las caras pero se acota a **[470, 530]**. La disparidad de caras baja de
1,30 a 1,18 y la de estaturas se queda en 1,13.
- `sexo` → `"h"` o `"m"`. Lo usa la alternancia de la portada, nada más.

**El orden de la lista no significa nada.** La grilla se ordena sola por nombre
(`GRILLA`, con `localeCompare` en español para que Tatán y La Tía Evelyn caigan donde
corresponde) y la portada se sortea (`portadaDelDia()`). Se puede pegar una línea
nueva donde caiga.

## La portada no tiene protagonista
Cada carga sortea **cinco** alternando hombre y mujer, centrados, empezando al azar
por uno u otro. Elegir unos fijos sería decidir quiénes son los importantes, y aquí
todos lo son. Con 15 hay miles de combinaciones y crecen solas: no hay nada que
ajustar al sumar gente.

**La escala se mide contra el techo FIJO del reparto** (`ALTO_MAYOR`), no contra el
más alto de los cinco de hoy. Si se midiera contra el subconjunto, un mismo personaje
se vería de distinto tamaño según la compañía y el logotipo cambiaría de porte en cada
carga. Lo único que cambia es **quiénes** salen. `test-portada.py` lo comprueba
recargando doce veces y exigiendo que cada personaje mida siempre lo mismo.

Un efecto secundario conocido: con 9 hombres y 6 mujeres, una mujer sale ~1,9 veces
más seguido que un hombre — no es un fallo sino la consecuencia de exigir alternancia
con un reparto desparejo. Se empareja solo a medida que el reparto se equilibra.

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
`herramientas/recortar.py` reconoce **tres** entradas y elige sola: fondo blanco
plano, fondo ya transparente, y **damero incrustado** — un PNG sin canal alfa donde el
damero de "transparente" quedó pintado. El tercero llega cuando el archivo se exporta
por el camino equivocado y es el peor de los tres: no se ve como fondo hasta ponerlo
sobre oscuro. Se reconoce por neutralidad y se desmatiza contra el gris **local**,
porque el damero baja hasta 219 y contra 255 el borde sale aclarado.

También limpia **motas sueltas**: píxeles aislados que no se ven pero estiran la caja
de recorte, y la caja es lo que fija la proporción. El Compadre llegó con 2 px en su
columna izquierda y las seis siguientes vacías: su proporción salía 0,993 en vez de
0,831.

**El encuadre del rostro se verifica a ojo, no hay comprobación automática.** Se
probaron dos métricas —piel al centro del recorte y piel pegada al borde de arriba— y
**ninguna separa** un recorte bien puesto de uno con la cara fuera de cuadro (23,3 %
el malo contra 22,6 % el bueno). Lo que sí se comprueba es que el rostro **corresponda
al cuerpo actual**, regenerándolo y comparando. Cuando el detector de cara falla —a La
Primera le puso el centro en el 34 % del ancho cuando estaba en el 51 %— se ancla a
mano en `herramientas/ajuste.json`: `[alto, subida, x opcional, y opcional]`.

Cuando el fondo es blanco plano, el relleno desde el borde quita el fondo exterior,
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
