# Herramientas de la primera fase

De cuando los personajes se recortaban de **una sola lámina** con los seis
juntos, antes de que empezaran a llegar dibujados por separado. Están
superadas por `../recortar.py`, que reconoce los tres fondos con los que
llegan hoy.

Se guardan porque el recorte por semillas (`seedcut.py`, GrabCut) es la
única salida si algún día llega un dibujo sobre un fondo complejo, donde
el relleno desde el borde no sirve.

- `extraer-assets.py` — partía las tres imágenes fuente en assets
- `seedcut.py` — recorte por semillas (GrabCut) para fondos difíciles
- `tono_final.py` — componía una cabeza sobre un torso, a escala
