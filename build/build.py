"""Genera index.html (el menú que abre la tele) a partir de la página original y de build/apps.json.

Uso:  python build/build.py        (necesita Pillow: pip install pillow)

- build/upstream-index.html  página de cleanyourtv-vidaa con el ajuste de tamaño para esta tele (1280x720).
- build/apps.json            apps que se muestran, en orden; las cuatro de "dock" van en la barra.
- icons/                     iconos de esas apps.

La página resultante no necesita ningún programa auxiliar: abre cada app cargando su dirección web.
"""
import base64
import io
import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "build" / "upstream-index.html"
CONF = json.loads((ROOT / "build" / "apps.json").read_text(encoding="utf-8"))


def colours(path):
    """Los mismos colores que calcula sample() en la página: borde, fondo 2x5 de las columnas exteriores y color vivo."""
    im = Image.open(path).convert("RGBA")
    px = im.resize((24, 24), Image.BILINEAR).load()
    er = eg = eb = en = 0
    vr = vg = vb = vw = 0.0
    for y in range(24):
        for x in range(24):
            r, g, b, a = px[x, y]
            if a < 200:
                continue
            if x in (0, 23):
                er += r; eg += g; eb += b; en += 1
            mx, mn = max(r, g, b), min(r, g, b)
            sat = (mx - mn) / mx if mx else 0
            w = sat * sat * (mx / 255)
            vr += r * w; vg += g * w; vb += b * w; vw += w
    iw, ih = im.size
    strip = Image.new("RGBA", (2, 5))
    strip.paste(im.crop((0, 0, 2, ih)).resize((1, 5), Image.BILINEAR), (0, 0))
    strip.paste(im.crop((iw - 2, 0, iw, ih)).resize((1, 5), Image.BILINEAR), (1, 0))
    buf = io.BytesIO()
    strip.save(buf, "PNG", optimize=True)
    out = {"backdrop": "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode(),
           "glow": [round(vr / vw), round(vg / vw), round(vb / vw)] if vw > 2 else [150, 150, 160]}
    if en > 20:
        out["bg"] = f"rgb({round(er / en)},{round(eg / en)},{round(eb / en)})"
    return out


def swap(html, old, new):
    if html.count(old) != 1:
        raise SystemExit(f"la página original ha cambiado: {html.count(old)} coincidencias de {old[:70]!r}")
    return html.replace(old, new)


def main():
    apps = []
    for a in CONF["apps"]:
        entry = {"appId": a["appId"], "name": a["name"], "icon": "icons/" + a["icon"], "url": a["url"]}
        entry.update(colours(ROOT / "icons" / a["icon"]))
        apps.append(entry)
    data = {"apps": apps, "dock": CONF["dock"], "sources": [], "browser": {},
            "greeting_name": CONF.get("greeting_name", ""), "clock_24h": True}
    blob = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")

    h = SRC.read_text(encoding="utf-8")
    h = swap(h, '<html lang="en">', '<html lang="es">')
    h = swap(h, "<title>Home</title>", '<title>Inicio</title>\n<meta name="robots" content="noindex,nofollow">')
    # La fuente va con la página: sin peticiones a Google al abrir.
    h = swap(h, '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Outfit:wght@200..600&display=swap">\n',
             '<link rel="preload" href="fonts/outfit.ttf" as="font" type="font/ttf" crossorigin>\n')
    h = swap(h, 'src: url(fonts/outfit.ttf) format("truetype"); font-weight: 100 900; }',
             'src: url(fonts/outfit.ttf) format("truetype"); font-weight: 100 900; font-display: swap; }')

    # Textos en español.
    h = swap(h, "var DAYS = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];",
             "var DAYS = ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'];")
    h = swap(h, "var MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];",
             "var MONTHS = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'];")
    h = swap(h, "d.getDate() + ' ' + (fit > 1 ? month.slice(0, 3) : month);",
             "d.getDate() + (fit > 1 ? ' ' + month.slice(0, 3) : ' de ' + month);")
    h = swap(h, "var g = h < 12 ? 'Good morning' : h < 17 ? 'Good afternoon' : 'Good evening';",
             "var g = h < 6 ? 'Buenas noches' : h < 13 ? 'Buenos días' : h < 21 ? 'Buenas tardes' : 'Buenas noches';")
    h = swap(h, "[{ label: 'Move', act: 'move' }, { label: 'Remove from Home', act: 'remove' }]",
             "[{ label: 'Mover', act: 'move' }, { label: 'Quitar del inicio', act: 'remove' }]")
    h = swap(h, "{ label: 'Reset the order', act: 'reset-order' }", "{ label: 'Volver al orden original', act: 'reset-order' }")
    h = swap(h, "{ label: 'Restore removed apps (' + state.removedCount + ')', act: 'restore' }",
             "{ label: 'Recuperar las apps quitadas (' + state.removedCount + ')', act: 'restore' }")
    h = swap(h, "    items.push({ label: 'Cancel', act: 'cancel' });\n    showMenu(app.name, items);",
             "    items.push({ label: 'Cancelar', act: 'cancel' });\n    showMenu(app.name, items);")
    h = swap(h, "toast(app.name + ' removed from Home. It is still installed on the TV.');",
             "toast(app.name + ' ya no sale en el inicio. Sigue instalada en la tele.');")
    h = swap(h, "toast('Use the arrows to move ' + state.apps[focus.index].name + ', then OK to place it. Back cancels.');",
             "toast('Mueve ' + state.apps[focus.index].name + ' con las flechas y pulsa OK para dejarla. Atrás cancela.');")
    h = swap(h, "toast(ids ? 'Saved. Your tiles stay in this order.' : 'Back to the original order.');",
             "toast(ids ? 'Guardado. Las apps se quedan en este orden.' : 'Orden original recuperado.');")

    # Sin auxiliar: la lista de apps va dentro de la página (una petición menos) y no se pregunta por /api/state.
    h = swap(h, """  function startStatic() {
    state.static = true;
    load('apps.json').then(start, function () { toast('Could not load the app list'); });
  }
  if (/[?&]static=1/.test(location.search)) startStatic();
  else load('/api/state').then(start, startStatic);
""", """  state.static = true;
  start(""" + blob + """);
  // Copia guardada en la tele: las siguientes veces abre al instante, también si falla internet.
  if ('serviceWorker' in navigator) { try { navigator.serviceWorker.register('sw.js').catch(function () {}); } catch (e) {} }
""")
    (ROOT / "index.html").write_text(h, encoding="utf-8")
    print(f"index.html: {len(apps)} apps, {len(h.encode()) // 1024} KB")


if __name__ == "__main__":
    main()
