# martina-tv

Menú de inicio limpio para una tele con VIDAA. Es una página web: la tele la abre desde un icono y cada app se abre cargando su dirección. No necesita ningún ordenador encendido.

Basado en [cleanyourtv-vidaa](https://github.com/gilbertmsipha/cleanyourtv-vidaa) de Gilbert (licencia MIT, ver `LICENSE`). Cambios sobre el original:

- Ajuste de tamaño para teles cuyo navegador dibuja a 1280×720.
- Textos en español.
- La lista de apps va dentro de la página y la fuente y los iconos se sirven desde aquí, sin peticiones a terceros al abrir.
- `sw.js` guarda una copia en la tele para que abra al instante.

## Cambiar las apps

1. Edita `build/apps.json` (las cuatro de `dock` son la barra; el resto sigue el orden de la lista) y pon el icono en `icons/`.
2. `pip install pillow && python build/build.py` vuelve a generar `index.html`.
3. Sube los cambios. La tele muestra la versión nueva la segunda vez que se abre el menú.

Netflix, Prime Video y la TV en directo son apps propias de la tele y una página no puede abrirlas: siguen en el inicio normal de la tele y en los botones del mando.

## Quitarlo

Borra el icono desde la tele. No cambia nada más en ella.
