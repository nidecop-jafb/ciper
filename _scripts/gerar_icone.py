# -*- coding: utf-8 -*-
"""Icone oficial do CIPER: SVG (fonte) + PNG/ICO derivados.
Geometria: a marca do video institucional (arco + tres pontos), redesenhada em vetor.
Arco = quarto de circulo que sobe (do ouro a energia); quatro pontos = as instituicoes da alianca
(de baixo para cima: IFMG, UFOP, FG, PMOP). Versao de 3 pontos arquivada em assets/icone/xx/.
Uso: python _scripts/gerar_icone.py
"""
import math
from pathlib import Path
from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parent.parent / "assets" / "icone"
VERDE, VERDE2, OURO, OURO2, BRANCO = "#0E3B2E", "#17614A", "#F4C95D", "#DE9B1E", "#FFFFFF"
CX, CY, R, ESP = 412.9, 357.1, 201.5, 46.5          # centro, raio e espessura do arco (tela 512)
RD = 297.6                                           # raio da orbita dos pontos
PONTOS = [(180 + i * 43 / 3, 17.0) for i in range(4)]  # 4 pontos iguais, espacados de 180 a 223 graus

def pt(ang, r):
    a = math.radians(ang)
    return CX + r * math.cos(a), CY + r * math.sin(a)

def marca_svg(cor_arco, cor_pontos):
    x0, y0 = pt(180, R); x1, y1 = pt(270, R)
    s = f'<path d="M {x0:.1f} {y0:.1f} A {R} {R} 0 0 1 {x1:.1f} {y1:.1f}" fill="none" stroke="{cor_arco}" stroke-width="{ESP}" stroke-linecap="round"/>'
    for ang, r in PONTOS:
        x, y = pt(ang, RD)
        s += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{cor_pontos}"/>'
    return s

GRAD = (f'<defs><linearGradient id="f" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{VERDE2}"/><stop offset="1" stop-color="{VERDE}"/></linearGradient>'
        f'<linearGradient id="o" x1="0" y1="1" x2="1" y2="0"><stop offset="0" stop-color="{OURO2}"/><stop offset="1" stop-color="{OURO}"/></linearGradient></defs>')

def svg(conteudo, vb="0 0 512 512", extra=""):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" role="img" aria-label="CIPER"{extra}>{conteudo}</svg>\n'

OUT.mkdir(parents=True, exist_ok=True)
(OUT / "ciper-icone.svg").write_text(svg(GRAD + '<rect width="512" height="512" rx="112" fill="url(#f)"/>' + marca_svg("url(#o)", BRANCO)), encoding="utf-8")
(OUT / "ciper-marca.svg").write_text(svg(marca_svg("currentColor", "currentColor"), vb="80 120 372 275"), encoding="utf-8")
(OUT / "ciper-marca-ouro.svg").write_text(svg(GRAD + marca_svg("url(#o)", VERDE), vb="80 120 372 275"), encoding="utf-8")
txt = ('<text x="560" y="330" font-family="Montserrat, \'Segoe UI\', Arial, sans-serif" font-weight="700" font-size="190" letter-spacing="26" fill="{c}">CIPER</text>'
       '<text x="566" y="400" font-family="Montserrat, \'Segoe UI\', Arial, sans-serif" font-weight="500" font-size="40" letter-spacing="2" fill="{c}">Centro de Inovação e Pesquisa de Energias Renováveis</text>')
(OUT / "ciper-logo-horizontal.svg").write_text(svg(GRAD + marca_svg("url(#o)", VERDE) + txt.format(c=VERDE), vb="60 100 1640 340"), encoding="utf-8")
(OUT / "ciper-logo-horizontal-claro.svg").write_text(svg(GRAD + marca_svg("url(#o)", BRANCO) + txt.format(c=BRANCO), vb="60 100 1640 340"), encoding="utf-8")

def png(tam, fundo=True):
    k = 4 * tam / 512; n = 4 * tam
    im = Image.new("RGBA", (n, n), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    if fundo:
        g = Image.new("RGBA", (n, n)); gp = g.load()
        a, b = [int(VERDE2[i:i+2], 16) for i in (1, 3, 5)], [int(VERDE[i:i+2], 16) for i in (1, 3, 5)]
        for y in range(n):
            for x in range(n):
                t = (x + y) / (2 * n); gp[x, y] = tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3)) + (255,)
        m = Image.new("L", (n, n), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, n - 1, n - 1], radius=int(112 * k), fill=255)
        im.paste(g, (0, 0), m); d = ImageDraw.Draw(im)
    ouro = "#EDB73F"
    d.arc([(CX - R) * k - ESP * k / 2, (CY - R) * k - ESP * k / 2, (CX + R) * k + ESP * k / 2, (CY + R) * k + ESP * k / 2], 180, 270, fill=ouro, width=int(ESP * k))
    for ang in (180, 270):
        x, y = pt(ang, R); d.ellipse([x * k - ESP * k / 2, y * k - ESP * k / 2, x * k + ESP * k / 2, y * k + ESP * k / 2], fill=ouro)
    for ang, r in PONTOS:
        x, y = pt(ang, RD); d.ellipse([(x - r) * k, (y - r) * k, (x + r) * k, (y + r) * k], fill=BRANCO if fundo else VERDE)
    return im.resize((tam, tam), Image.LANCZOS)

for t in (512, 192, 180, 64, 32):
    png(t).save(OUT / f"ciper-icone-{t}.png")
png(64).save(OUT / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48), (64, 64)])
png(1024).save(OUT / "ciper-icone-1024.png")
print("icone ok", sorted(p.name for p in OUT.iterdir()))
