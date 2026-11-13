# -*- coding: utf-8 -*-
"""Icone oficial do CIPER: SVG (fonte) + PNG/ICO derivados.
Geometria (Proposta B "Arco da energia", PRE-site-ciper-icone-itacolomi-B-2026-11-12):
silhueta geometrica do Pico do Itacolomi (pico + "filho", vista do centro de Ouro Preto);
arco ouro ascendente por cima do pico (do ouro a energia); quatro pontos iguais na base =
as instituicoes da alianca (esquerda -> direita: IFMG, UFOP, FG, PMOP).
Versoes anteriores: assets/icone/xx/ (3 pontos) e assets/icone/xx/arco-4-pontos/.
Uso: python _scripts/gerar_icone.py
"""
import math
from pathlib import Path
from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parent.parent / "assets" / "icone"
VERDE, VERDE2, OURO, OURO2, BRANCO = "#0E3B2E", "#17614A", "#F4C95D", "#DE9B1E", "#FFFFFF"
DY = -14                                             # desloca a marca para centralizar no quadro 512
ARCO = (420, 372, 270, 196, 268, 40)                 # centro x, y, raio, angulo inicial/final, espessura
                                                     # (inicio em 196 graus: o arco nasce atras da encosta, sem ponta abaixo da base)
FOLGA = 14                                           # largura da folga recortada em volta do monte
PONTOS_X, PONTOS_Y, PONTOS_R = (181, 231, 281, 331), 420, 19
# Silhueta: encosta esquerda, pico (bloco maior), fenda, "filho", encosta direita; base y = 372
MONTE = [("M", (64, 372)), ("L", (150, 318)), ("L", (190, 300)), ("L", (234, 286)), ("L", (238, 180)),
         ("Q", (240, 162), (258, 160)), ("L", (274, 158)), ("Q", (292, 160), (293, 178)), ("L", (296, 286)),
         ("L", (307, 286)), ("L", (309, 228)), ("Q", (310, 212), (323, 212)), ("Q", (336, 213), (337, 228)),
         ("L", (339, 288)), ("L", (382, 304)), ("L", (448, 372))]

def monte_d():
    return " ".join(f"{c} " + " ".join(f"{x} {y + DY}" for x, y in pts) for c, *pts in MONTE) + " Z"

def monte_pts(k, passos=12):
    """Silhueta como poligono (curvas Q amostradas), em pixels na escala k."""
    out = []
    for c, *pts in MONTE:
        if c == "Q":
            (x0, y0), (cx, cy), (x1, y1) = out[-1], pts[0], pts[1]
            for i in range(1, passos + 1):
                t = i / passos
                out.append(((1 - t) ** 2 * x0 + 2 * (1 - t) * t * cx + t * t * x1,
                            (1 - t) ** 2 * y0 + 2 * (1 - t) * t * cy + t * t * y1))
        else:
            out.append(pts[0])
    return [(x * k, (y + DY) * k) for x, y in out]

def pt_arco(ang):
    cx, cy, r = ARCO[:3]
    return cx + r * math.cos(math.radians(ang)), cy + DY + r * math.sin(math.radians(ang))

def marca_svg(cor_arco, cor_monte, cor_pontos):
    cx, cy, r, a0, a1, esp = ARCO
    (x0, y0), (x1, y1), d = pt_arco(a0), pt_arco(a1), monte_d()
    # mascara: o arco perde uma folga em volta do monte (funciona em qualquer fundo, inclusive currentColor)
    s = (f'<mask id="m" maskUnits="userSpaceOnUse" x="0" y="0" width="512" height="512"><rect width="512" height="512" fill="#fff"/>'
         f'<path d="{d}" fill="#000" stroke="#000" stroke-width="{2 * FOLGA}" stroke-linejoin="round"/></mask>'
         f'<path d="M {x0:.1f} {y0:.1f} A {r} {r} 0 0 1 {x1:.1f} {y1:.1f}" fill="none" stroke="{cor_arco}" '
         f'stroke-width="{esp}" stroke-linecap="round" mask="url(#m)"/>'
         f'<path d="{d}" fill="{cor_monte}"/>')
    for x in PONTOS_X:
        s += f'<circle cx="{x}" cy="{PONTOS_Y + DY}" r="{PONTOS_R}" fill="{cor_pontos}"/>'
    return s

GRAD = (f'<defs><linearGradient id="f" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{VERDE2}"/><stop offset="1" stop-color="{VERDE}"/></linearGradient>'
        f'<linearGradient id="o" x1="0" y1="1" x2="1" y2="0"><stop offset="0" stop-color="{OURO2}"/><stop offset="1" stop-color="{OURO}"/></linearGradient></defs>')

def svg(conteudo, vb="0 0 512 512", extra=""):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" role="img" aria-label="CIPER"{extra}>{conteudo}</svg>\n'

VB_MARCA, VB_LOGO = "44 54 424 380", "40 54 1780 392"
OUT.mkdir(parents=True, exist_ok=True)
(OUT / "ciper-icone.svg").write_text(svg(GRAD + '<rect width="512" height="512" rx="112" fill="url(#f)"/>' + marca_svg("url(#o)", BRANCO, BRANCO)), encoding="utf-8")
(OUT / "ciper-marca.svg").write_text(svg(marca_svg("currentColor", "currentColor", "currentColor"), vb=VB_MARCA), encoding="utf-8")
(OUT / "ciper-marca-ouro.svg").write_text(svg(GRAD + marca_svg("url(#o)", VERDE, VERDE), vb=VB_MARCA), encoding="utf-8")
txt = ('<text x="540" y="318" font-family="Montserrat, \'Segoe UI\', Arial, sans-serif" font-weight="700" font-size="190" letter-spacing="26" fill="{c}">CIPER</text>'
       '<text x="546" y="388" font-family="Montserrat, \'Segoe UI\', Arial, sans-serif" font-weight="500" font-size="40" letter-spacing="2" fill="{c}">Centro de Inovação e Pesquisa de Energias Renováveis</text>')
(OUT / "ciper-logo-horizontal.svg").write_text(svg(GRAD + marca_svg("url(#o)", VERDE, VERDE) + txt.format(c=VERDE), vb=VB_LOGO), encoding="utf-8")
(OUT / "ciper-logo-horizontal-claro.svg").write_text(svg(GRAD + marca_svg("url(#o)", BRANCO, BRANCO) + txt.format(c=BRANCO), vb=VB_LOGO), encoding="utf-8")

def png(tam):
    k = 4 * tam / 512; n = 4 * tam                   # desenha em 4x e reduz (antisserrilhado)
    im = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    g = Image.new("RGBA", (n, n)); gp = g.load()
    a, b = [int(VERDE2[i:i+2], 16) for i in (1, 3, 5)], [int(VERDE[i:i+2], 16) for i in (1, 3, 5)]
    for y in range(n):
        for x in range(n):
            t = (x + y) / (2 * n); gp[x, y] = tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3)) + (255,)
    m = Image.new("L", (n, n), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, n - 1, n - 1], radius=int(112 * k), fill=255)
    im.paste(g, (0, 0), m)
    # arco ouro em camada propria, com a folga em volta do monte recortada
    cx, cy, r, a0, a1, esp = ARCO; cy += DY; ouro = "#EDB73F"
    arco = Image.new("L", (n, n), 0); da = ImageDraw.Draw(arco)
    da.arc([(cx - r - esp / 2) * k, (cy - r - esp / 2) * k, (cx + r + esp / 2) * k, (cy + r + esp / 2) * k], a0, a1, fill=255, width=int(esp * k))
    for ang in (a0, a1):
        x, y = pt_arco(ang); da.ellipse([(x - esp / 2) * k, (y - esp / 2) * k, (x + esp / 2) * k, (y + esp / 2) * k], fill=255)
    pol = monte_pts(k)
    folga = Image.new("L", (n, n), 0); df = ImageDraw.Draw(folga)
    df.polygon(pol, fill=255); df.line(pol + [pol[0]], fill=255, width=int(2 * FOLGA * k), joint="curve")
    for x, y in pol:
        df.ellipse([x - FOLGA * k, y - FOLGA * k, x + FOLGA * k, y + FOLGA * k], fill=255)
    arco.paste(0, (0, 0), folga)
    im.paste(Image.new("RGBA", (n, n), ouro), (0, 0), arco)
    d = ImageDraw.Draw(im)
    d.polygon(pol, fill=BRANCO)
    for x in PONTOS_X:
        y = PONTOS_Y + DY; d.ellipse([(x - PONTOS_R) * k, (y - PONTOS_R) * k, (x + PONTOS_R) * k, (y + PONTOS_R) * k], fill=BRANCO)
    return im.resize((tam, tam), Image.LANCZOS)

for t in (512, 192, 180, 64, 32):
    png(t).save(OUT / f"ciper-icone-{t}.png")
png(64).save(OUT / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48), (64, 64)])
png(1024).save(OUT / "ciper-icone-1024.png")
print("icone ok", sorted(p.name for p in OUT.iterdir()))
