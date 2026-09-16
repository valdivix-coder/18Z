# Zombies en el 18

Juego de pelea arcade de zombis chilenos para celular en horizontal.
Un solo archivo: **`inicio.html`**. Sin frameworks, sin compilación.

**Jugar:** https://claude.ai/artifact/MqbqNLnCRz58UxP6Z7RypM

```
inicio.html          el juego entero
manifest.json        para instalarlo en el teléfono (nombre e iconos)
sw.js                service worker: red primero, caché solo sin señal
assets/              dibujos, rostros, módulo, fondos, intro, logotipo
pruebas/             la regresión — 10 suites. `python3 correr-todo.py`
herramientas/        recorte de fondo, rostros y alta de personajes
CLAUDE.md            el contexto y las decisiones, para retomarlo
```

## Sumar un personaje

```bash
python3 herramientas/sumar-personaje.py dibujo.png elmario "El Mario"
# pega la línea que imprime en PERSONAJES, dentro de inicio.html
cd pruebas && python3 correr-todo.py
```

## Antes de publicar

```bash
cd pruebas && python3 correr-todo.py
```

## Publicar en Vercel

El juego vive en `inicio.html`, así que `vercel.json` reescribe `/` hacia él
para que la raíz del sitio sirva el juego. Los `assets/` van con caché de una
semana —sus nombres no cambian de contenido— y el HTML con `no-cache`, para
que al publicar una versión nueva el teléfono la vea sin trucos.

## El icono de la app

```bash
python3 herramientas/icono.py              # rehace los tamaños derivados
python3 herramientas/icono.py arte.png     # cambia el arte maestro
```

El maestro es `assets/icon-512.png`. Instalado, el juego se llama **Zombies en el
18** en los dos sistemas: Android lo lee de `manifest.json` y iOS de
`apple-mobile-web-app-title`, así que los dos tienen que decir lo mismo.

Los iconos van **sin canal alfa** —el lanzador de Android compone lo transparente
sobre blanco y se vería como un cuadrado blanco— y el `maskable` mete el arte en el
80% central, que es lo único que Android garantiza al aplicarle la forma del
sistema. Nada de esto se nota desde el escritorio, así que lo vigila `chk-icono.py`.
