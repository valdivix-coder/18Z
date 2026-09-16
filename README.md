# Zombies en el 18

Juego de pelea arcade de zombis chilenos para celular en horizontal.
Un solo archivo: **`inicio.html`**. Sin frameworks, sin compilación.

**Jugar:** https://claude.ai/artifact/MqbqNLnCRz58UxP6Z7RypM

```
inicio.html          el juego entero
assets/              dibujos, rostros, módulo, fondos, intro, logotipo
pruebas/             la regresión — 9 suites. `python3 correr-todo.py`
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
