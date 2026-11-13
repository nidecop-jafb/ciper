# -*- coding: utf-8 -*-
"""PNGs dos logos horizontais do CIPER, a partir dos SVGs de assets/icone/ (rode antes gerar_icone.py).
Rasteriza com o Edge/Chrome em modo headless, fundo transparente, fonte Montserrat (Google Fonts).
Saida: ciper-logo-horizontal[-claro]-{largura}.png em assets/icone/.
Uso: python _scripts/gerar_png_horizontal.py
"""
import re, subprocess, tempfile
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets" / "icone"
LARGURAS = (1200, 2400)
NAVEGADORES = [r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
               r"C:\Program Files\Google\Chrome\Application\chrome.exe"]
NAV = next(p for p in NAVEGADORES if Path(p).exists())
FONTE = '<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@500;700&display=block" rel="stylesheet">'

with tempfile.TemporaryDirectory() as tmp:
    for nome in ("ciper-logo-horizontal", "ciper-logo-horizontal-claro"):
        svg = (OUT / f"{nome}.svg").read_text(encoding="utf-8")
        _, _, vw, vh = map(float, re.search(r'viewBox="([^"]+)"', svg).group(1).split())
        for w in LARGURAS:
            h = round(w * vh / vw)
            html = Path(tmp) / f"{nome}-{w}.html"
            html.write_text(f'<!doctype html><meta charset="utf-8">{FONTE}<style>html,body{{margin:0;background:transparent}}'
                            f'svg{{display:block;width:{w}px;height:{h}px}}</style>{svg}', encoding="utf-8")
            png = OUT / f"{nome}-{w}.png"
            subprocess.run([NAV, "--headless", "--disable-gpu", "--hide-scrollbars", "--default-background-color=00000000",
                            "--virtual-time-budget=8000", f"--window-size={w},{h}", f"--screenshot={png}", html.as_uri()],
                           check=True, capture_output=True, timeout=120)
            print("ok", png.name, f"{w}x{h}")
