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
- **Reparto: 18 personajes.** La grilla los muestra a todos en orden alfabético; la
  portada sortea **cinco** en cada carga, alternando hombre y mujer.
- **El juego en sí NO existe todavía.** CONTINUAR vuelve a la pantalla de inicio.
- **Regresión: 10 suites, 791 comprobaciones**, dentro del repo en `pruebas/`.
  Se corre con `cd pruebas && python3 correr-todo.py`.
- Versión publicada: **v1.8** (se ve al pie de la pantalla de inicio).

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

**Un dibujo más caricaturesco se va al SUELO de la banda, y está bien.** Juancho está
dibujado con cinco cabezas de alto —achaparrado y con la cabeza enorme— mientras el
resto anda en siete. Medido a la misma escala, su cabeza da 52 px contra los ~35 de
Tatán y Don Alberto: igualarlas pediría bajarlo a 316, muy por debajo del mínimo. Así
que el tope lo deja en **470**, el suelo, y se lee como lo que el dibujo dice que es —
un tipo bajo y ancho— en vez de como alguien más grande que el resto. La proporción del
dibujo daba 541: **el número que imprime `sumar-personaje.py` no es una estatura**, es
la proporción de la lámina, y hay que medirlo contra otros dos antes de dejarlo.

**El orden de la lista no significa nada.** La grilla se ordena sola por nombre
(`GRILLA`, con `localeCompare` en español para que Tatán y La Tía Evelyn caigan donde
corresponde) y la portada se sortea (`portadaDelDia()`). Se puede pegar una línea
nueva donde caiga.

## La portada no tiene protagonista
Cada carga sortea **cinco** alternando hombre y mujer, centrados, empezando al azar
por uno u otro. Elegir unos fijos sería decidir quiénes son los importantes, y aquí
todos lo son. Con 18 hay decenas de miles de combinaciones y crecen solas: no hay
nada que ajustar al sumar gente.

**La escala se mide contra el techo FIJO del reparto** (`ALTO_MAYOR`), no contra el
más alto de los cinco de hoy. Si se midiera contra el subconjunto, un mismo personaje
se vería de distinto tamaño según la compañía y el logotipo cambiaría de porte en cada
carga. Lo único que cambia es **quiénes** salen. `test-portada.py` lo comprueba
recargando doce veces y exigiendo que cada personaje mida siempre lo mismo.

Un efecto secundario conocido: con 12 hombres y 6 mujeres, una mujer sale **2,0 veces**
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
al cuerpo actual**, regenerándolo y comparando. Cuando el detector de cara falla se ancla a mano en
`herramientas/ajuste.json`: `[alto, subida, x opcional, y opcional]`. Falla de dos
maneras ya vistas: a La Primera le puso el centro en el 34 % del ancho cuando estaba en
el 51 %, y con Juancho se fue a la **cresta del gallo** que lleva bajo el brazo —es roja
y cumple la regla de piel—, dejando la cara en el 32 % cuando está en el 51,5 %. Ahí el
ajuste lleva sus cuatro números.

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

## El icono de la app, y por qué falla en silencio
El arte del icono **lo entregó Simón** —«18Z» sobre Santiago ardiendo— y el maestro es
`assets/icon-512.png`. No hay copia aparte del original: guardar las dos cosas era
pagar dos veces por la misma imagen, y 512 px ya es el tamaño más grande que pide
cualquier sistema (Android 512, iPhone 180). De ahí salen los otros tres con
`herramientas/icono.py`; pasándole una imagen se cambia el maestro y se rehace todo:

```bash
python3 herramientas/icono.py arte-nuevo.png
```

**El maestro va en color directo, sin paleta.** Con 256 colores pesaba 176 KB en vez
de 528, pero el cielo se bandeaba (error medio 4,8 y picos de 141 medidos sobre este
arte). Es la cara de la app; los 350 KB se pagan.

**Dos reglas de Android que no se pueden saltar:**
1. **Sin canal alfa.** El lanzador compone lo transparente sobre BLANCO, así que un
   icono transparente se ve como un cuadrado blanco. Todo se aplana antes de guardar.
   En iPhone `apple-touch-icon` siempre fue opaco, así que la regla lo cubre de paso.
2. **El `maskable` se recorta.** Android le aplica la forma del sistema —círculo,
   cuadrado redondeado, gota— y solo garantiza el **80% central**. En este arte el «1»
   arranca a un 6% del borde y la «Z» termina a un 95%: sin encoger, la forma del
   sistema se come las dos puntas. El arte entra al 78% y el hueco lo rellena una copia
   **ampliada y desenfocada de sí mismo**, que continúa el cielo y el escombro en el
   sitio que les toca. Un marco de color plano habría dibujado un borde donde el arte
   se acaba, que es justo lo que un maskable no puede tener.

**El nombre instalado está en TRES sitios y tienen que decir lo mismo:** `name` y
`short_name` del manifiesto (Android) y `apple-mobile-web-app-title` (iOS). Si se
separan, la app se llama distinto según el aparato.

**Y el nombre instalado es «18-Z», no «Zombies en el 18».** El escritorio de Android
corta la etiqueta cerca de los 12 caracteres, así que el nombre largo se vería
«Zombies en…». El nombre completo vive en el `<title>` de la página —«18-Z: Zombies en
el 18»—, que es lo que se ve en la pestaña y lo que se comparte. `chk-icono.py` **no
fija el texto**: fija que los tres coincidan y que quepa bajo el icono. Un nombre puede
cambiar; que la app se instale con dos nombres distintos, no.

**El service worker existe por la instalación, no por la velocidad:** Android no ofrece
instalar (WebAPK) sin uno que atienda `fetch`. Va a la **red primero** siempre —
sirviendo desde la caché, un teléfono se queda con la versión vieja, arte incluido, y en
una app instalada eso no se arregla recargando. Por lo mismo, `vercel.json` prohíbe
cachear `manifest.json` y `sw.js`.

Nada de esto se ve desde el escritorio: un manifiesto que apunta a un archivo que ya no
está no da ningún error, Android simplemente cae a su icono de respaldo. Por eso hay una
suite entera vigilándolo — y comprueba la zona segura **devolviendo a su tamaño el 80%
central del maskable y comparándolo con el maestro**, que es la única forma de afirmar
que el arte cabe entero.

**Una sola puerta de entrada, un solo manifiesto, un solo service worker.** Convivieron
un rato dos montajes de PWA hechos en paralelo —`index.html` envolviendo el juego en un
iframe, con `manifest.webmanifest`, `service-worker.js` e `icons/`— y eso no es
redundancia sino un fallo: dos service workers en el mismo ámbito se pisan (gana el
último que se registra) y **cada puerta trae su propio manifiesto y su propio
`apple-mobile-web-app-title`**, así que la app se instalaba con un nombre u otro según
por dónde hubiera entrado la persona — «18Z» desde el envoltorio y «Zombies en el 18»
desde el juego. Se quedó el juego directo: sin iframe, el título de iOS y el manifiesto
que se leen son los suyos. `chk-icono.py` lo fija.

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
- Quedan **12 casillas libres** en la grilla.
- Nombre a confirmar: **«La Soa Janet»** está escrito tal como llegó; podría ser
  «La Sra. Janet».
