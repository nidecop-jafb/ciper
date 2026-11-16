"""Gera as redes do CIPER no site: mini-páginas instaláveis, ícones, QR Codes e prancha A4.

Briefing: PRE-site-ciper-redes-qrcodes-2026-11-14 (PRJ_0001_CIPER/_planejamento/_pre/).

Uso, na pasta do site:
    python _scripts/gerar_redes.py            # gera tudo
    python _scripts/gerar_redes.py --sem-pdf  # pula a prancha A4 em PDF

Para ligar uma rede nova (LinkedIn, X, WhatsApp): preencher `perfil` e trocar `ativa` para True
na lista REDES e rodar de novo. Os QRs já impressos continuam valendo, porque apontam para
as mini-páginas do site, não para a rede.
"""
from __future__ import annotations

import base64
import html
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import qrcode
from PIL import Image, ImageDraw, ImageFont

SITE = Path(__file__).resolve().parents[1]
PROJETOS = SITE.parent
SAIDA_E = PROJETOS / "PRJ-001E-CIPER-Redes-Sociais" / "qrcodes"
BASE = "https://nidecop-jafb.github.io/ciper/"
CHROME = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
FONTE = r"C:\Windows\Fonts\arialbd.ttf"

NOTA_IA = ("<strong>Transparência sobre IA:</strong> textos, imagens, áudios e vídeos, quando elaborados "
           "com auxílio de inteligência artificial (IA), são revisados, conferidos e aprovados pelo(s) "
           "autor(es). A responsabilidade é humana.")

REDES = [
    dict(chave="instagram", nome="Instagram", conta="@ciper.ouropreto", curto="CIPER Insta",
         perfil="https://www.instagram.com/ciper.ouropreto/", pacote="com.instagram.android", ativa=True),
    dict(chave="facebook", nome="Facebook", conta="CIPER Ouro Preto", curto="CIPER Face",
         perfil="https://www.facebook.com/ciper.ouropreto", pacote="com.facebook.katana", ativa=True),
    # Desligadas até a conta existir (kit de contas, seção 5):
    dict(chave="linkedin", nome="LinkedIn", conta="CIPER Ouro Preto", curto="CIPER Linked",
         perfil="https://www.linkedin.com/company/ciper-ouropreto/", pacote="com.linkedin.android", ativa=False),
    dict(chave="x", nome="X", conta="@ciper_ouropreto", curto="CIPER X",
         perfil="https://x.com/ciper_ouropreto", pacote="com.twitter.android", ativa=False),
    dict(chave="whatsapp", nome="WhatsApp", conta="Canal CIPER Ouro Preto", curto="CIPER Zap",
         perfil="", pacote="com.whatsapp", ativa=False),
]
ATIVAS = [r for r in REDES if r["ativa"]]
SITE_QR = dict(chave="site", nome="Site do CIPER", conta="Página oficial do CIPER", alvo=BASE)


# ---------------------------------------------------------------- ícones
def _circulo(S: int) -> Image.Image:
    m = Image.new("L", (S, S), 0)
    ImageDraw.Draw(m).ellipse((0, 0, S - 1, S - 1), fill=255)
    return m


def _texto_centro(d: ImageDraw.ImageDraw, S: int, txt: str, tam: float, dx=0.0, dy=0.0):
    f = ImageFont.truetype(FONTE, int(S * tam))
    x0, y0, x1, y1 = d.textbbox((0, 0), txt, font=f)
    d.text(((S - (x1 - x0)) / 2 - x0 + dx * S, (S - (y1 - y0)) / 2 - y0 + dy * S), txt, font=f, fill="white")


def selo(chave: str, D: int) -> Image.Image:
    """Selo redondo da rede, desenhado por código em 4x e reduzido (nítido em qualquer tamanho)."""
    S = D * 4
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if chave == "instagram":
        stops = [(0.0, (254, 218, 117)), (0.25, (250, 126, 30)), (0.5, (214, 41, 118)),
                 (0.75, (150, 47, 191)), (1.0, (79, 91, 213))]
        y, x = np.mgrid[0:S, 0:S]
        t = (x + (S - y)) / (2 * S)
        rgb = np.zeros((S, S, 3))
        for c in range(3):
            rgb[..., c] = np.interp(t, [p for p, _ in stops], [col[c] for _, col in stops])
        im = Image.fromarray(rgb.astype("uint8"), "RGB").convert("RGBA")
        d = ImageDraw.Draw(im)
        w = int(S * 0.06)
        a, b = int(S * 0.26), int(S * 0.74)
        d.rounded_rectangle((a, a, b, b), radius=int(S * 0.14), outline="white", width=w)
        r = S * 0.115
        d.ellipse((S / 2 - r, S / 2 - r, S / 2 + r, S / 2 + r), outline="white", width=w)
        r2 = S * 0.035
        cx, cy = S * 0.635, S * 0.365
        d.ellipse((cx - r2, cy - r2, cx + r2, cy + r2), fill="white")
    elif chave == "facebook":
        d.rectangle((0, 0, S, S), fill=(8, 102, 255))
        _texto_centro(d, S, "f", 0.95, dx=0.04, dy=0.12)
    elif chave == "linkedin":
        d.rectangle((0, 0, S, S), fill=(10, 102, 194))
        _texto_centro(d, S, "in", 0.5)
    elif chave == "x":
        d.rectangle((0, 0, S, S), fill=(0, 0, 0))
        _texto_centro(d, S, "X", 0.55)
    elif chave == "whatsapp":
        d.rectangle((0, 0, S, S), fill=(37, 211, 102))
        r = S * 0.27
        d.ellipse((S / 2 - r, S / 2 - r, S / 2 + r, S / 2 + r), outline="white", width=int(S * 0.06))
        d.polygon([(S * 0.27, S * 0.62), (S * 0.22, S * 0.80), (S * 0.40, S * 0.75)], fill="white")
    else:
        raise ValueError(f"sem selo desenhado para a rede {chave!r}")
    im.putalpha(_circulo(S))
    return im.resize((D, D), Image.LANCZOS)


def _fundo_verde(base: Image.Image) -> Image.Image:
    """Fundo cheio com o degradê do ícone (para maskable e apple-touch, que não aceitam transparência)."""
    n = base.size[0]
    c1 = np.array(base.getpixel((int(n * .15), int(n * .15)))[:3], float)
    c2 = np.array(base.getpixel((int(n * .85), int(n * .85)))[:3], float)
    y, x = np.mgrid[0:n, 0:n]
    t = (((x + y) / (2 * n) - .15) / .7)[..., None]  # estende o degradê do ícone até os cantos
    return Image.fromarray(np.clip(c1 * (1 - t) + c2 * t, 0, 255).astype("uint8"), "RGB").convert("RGBA")


def icones(rede: dict, pasta: Path):
    base = Image.open(SITE / "assets/icone/ciper-icone-1024.png").convert("RGBA")
    n = base.size[0]
    # "any": ícone oficial inteiro + selo no canto superior esquerdo, com aro branco
    D, aro, c = int(n * 0.30), int(n * 0.016), int(n * 0.19)
    qualquer = base.copy()
    dd = ImageDraw.Draw(qualquer)
    R = D // 2 + aro
    dd.ellipse((c - R, c - R, c + R, c + R), fill="white")
    qualquer.alpha_composite(selo(rede["chave"], D), (c - D // 2, c - D // 2))
    # apple-touch: o iOS arredonda sozinho; fundo cheio para não sair preto
    apple = _fundo_verde(base)
    apple.alpha_composite(qualquer)
    # "maskable": só o desenho (pico, arco, pontos) a 72% sobre o degradê cheio, para tudo caber
    # na zona segura (círculo de raio 40%) sem emenda de fundo; selo menor, também dentro dela
    mask = _fundo_verde(base)
    b = np.asarray(base, float)
    dif = np.abs(b[..., :3] - np.asarray(mask, float)[..., :3]).sum(-1)
    alfa = np.clip((dif - 12) / 40, 0, 1) * b[..., 3] / 255
    desenho = Image.fromarray(np.dstack([b[..., :3], alfa * 255]).astype("uint8"), "RGBA")
    s = int(n * 0.72)
    mask.alpha_composite(desenho.resize((s, s), Image.LANCZOS), ((n - s) // 2, (n - s) // 2))
    D2, c2 = int(n * 0.18), int(n * 0.30)
    R2 = D2 // 2 + aro
    ImageDraw.Draw(mask).ellipse((c2 - R2, c2 - R2, c2 + R2, c2 + R2), fill="white")
    mask.alpha_composite(selo(rede["chave"], D2), (c2 - D2 // 2, c2 - D2 // 2))
    pasta.mkdir(parents=True, exist_ok=True)
    qualquer.resize((512, 512), Image.LANCZOS).save(pasta / "icone-512.png", optimize=True)
    qualquer.resize((192, 192), Image.LANCZOS).save(pasta / "icone-192.png", optimize=True)
    mask.resize((512, 512), Image.LANCZOS).convert("RGB").save(pasta / "icone-512-maskable.png", optimize=True)
    apple.resize((180, 180), Image.LANCZOS).convert("RGB").save(pasta / "icone-180.png", optimize=True)


# ---------------------------------------------------------------- QR Codes
def matriz_qr(url: str):
    q = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, border=4, box_size=1)
    q.add_data(url)
    q.make(fit=True)
    return q.get_matrix()


def qr_svg(url: str, rotulo: str) -> str:
    m = matriz_qr(url)
    n = len(m)
    partes = []
    for y, linha in enumerate(m):
        x = 0
        while x < n:
            if linha[x]:
                ini = x
                while x < n and linha[x]:
                    x += 1
                partes.append(f"M{ini} {y}h{x - ini}v1h-{x - ini}z")
            else:
                x += 1
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {n} {n}" shape-rendering="crispEdges" '
            f'role="img" aria-label="{html.escape(rotulo)}"><rect width="{n}" height="{n}" fill="#fff"/>'
            f'<path fill="#000" d="{"".join(partes)}"/></svg>')


def qr_png(url: str, destino: Path, lado=1024):
    m = np.array(matriz_qr(url), dtype=bool)
    n = m.shape[0]
    box = lado // n
    img = Image.fromarray(np.where(m, 0, 255).astype("uint8"), "L").resize((n * box, n * box), Image.NEAREST)
    tela = Image.new("L", (lado, lado), 255)
    tela.paste(img, ((lado - n * box) // 2, (lado - n * box) // 2))
    tela.save(destino, optimize=True)


def alvos_qr():
    itens = [dict(chave=r["chave"], nome=r["nome"], conta=r["conta"], alvo=f"{BASE}r/{r['chave']}/") for r in ATIVAS]
    return itens + [dict(SITE_QR)]


# ---------------------------------------------------------------- HTML
GLIFOS = {
    "instagram": '<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2">'
                 '<rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/>'
                 '<circle cx="17.5" cy="6.5" r="1.2" fill="currentColor" stroke="none"/></svg>',
    "facebook": '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M13.5 22v-8h2.7l.4-3.2h-3.1'
                'V8.8c0-.9.3-1.6 1.6-1.6h1.7V4.4c-.3 0-1.3-.1-2.5-.1-2.5 0-4.1 1.5-4.1 4.2v2.3H7.4V14h2.8v8z"/></svg>',
    "qr": '<svg viewBox="0 0 24 24" aria-hidden="true" fill="currentColor"><path d="M3 3h8v8H3zm2 2v4h4V5zm8-2h8v8h-8z'
          'm2 2v4h4V5zM3 13h8v8H3zm2 2v4h4v-4zm8-2h2v2h-2zm2 2h2v2h-2zm2-2h4v2h-4zm-4 4h2v4h-2zm4 0h4v4h-2v-2h-2z"/></svg>',
}
GLIFO_GENERICO = ('<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2">'
                  '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18"/></svg>')


def bloco_rodape(prefixo: str = "") -> str:
    links = [f'<a href="{r["perfil"]}" target="_blank" rel="noopener">{GLIFOS.get(r["chave"], GLIFO_GENERICO)}'
             f'{r["nome"]}</a>' for r in ATIVAS]
    links.append(f'<a href="{prefixo}redes.html">{GLIFOS["qr"]}QR Codes e ícones</a>')
    return ("<!-- REDES:INICIO (gerado por _scripts/gerar_redes.py) -->\n"
            f'    <p class="redes-rodape"><span>Siga o CIPER:</span> {" ".join(links)}</p>\n'
            "    <!-- REDES:FIM -->")


def aplica_rodape(pagina: Path):
    txt = pagina.read_text(encoding="utf-8")
    bloco = bloco_rodape()
    if "<!-- REDES:INICIO" in txt:
        novo = re.sub(r"<!-- REDES:INICIO.*?<!-- REDES:FIM -->", lambda _: bloco, txt, flags=re.S)
    else:
        i = txt.index("<footer")
        j = txt.index('<p class="fim">', i)
        novo = txt[:j] + bloco + "\n    " + txt[j:]
    if novo != txt:
        pagina.write_text(novo, encoding="utf-8", newline="\n")


def bloco_topo() -> str:
    """Ícones das redes no cabeçalho fixo (PRE-site-ciper-redes-no-topo-2026-11-16).
    Fica fora do <nav>: aparece com o menu aberto (PC) e recolhido (celular)."""
    links = [f'<a href="{r["perfil"]}" target="_blank" rel="noopener" title="{r["nome"]}" '
             f'aria-label="{r["nome"]} do CIPER (abre em nova aba)">{GLIFOS.get(r["chave"], GLIFO_GENERICO)}</a>'
             for r in ATIVAS]
    return ("<!-- REDES-TOPO:INICIO (gerado por _scripts/gerar_redes.py) -->\n"
            f'    <div class="redes-topo">{"".join(links)}</div>\n'
            "    <!-- REDES-TOPO:FIM -->")


def aplica_topo(pagina: Path):
    """Troca o item de texto "Redes" do menu pelos ícones no cabeçalho."""
    txt = pagina.read_text(encoding="utf-8")
    bloco = bloco_topo()
    novo = re.sub(r'\n[ \t]*<a href="redes\.html">Redes</a>', "", txt)
    if "<!-- REDES-TOPO:INICIO" in novo:
        novo = re.sub(r"<!-- REDES-TOPO:INICIO.*?<!-- REDES-TOPO:FIM -->", lambda _: bloco, novo, flags=re.S)
    else:
        i = novo.index('<header class="topo">')
        j = novo.index("</nav>", i) + len("</nav>")
        novo = novo[:j] + "\n    " + bloco + novo[j:]
    if novo != txt:
        pagina.write_text(novo, encoding="utf-8", newline="\n")


def intent(r: dict) -> str:
    sem = r["perfil"].split("://", 1)[1]
    volta = r["perfil"].replace(":", "%3A").replace("/", "%2F")
    return f"intent://{sem}#Intent;scheme=https;package={r['pacote']};S.browser_fallback_url={volta};end"


def mini_pagina(r: dict) -> str:
    nome, curto = r["nome"], r["curto"]
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>CIPER · {nome}</title>
<meta name="description" content="Abra o {nome} do CIPER ou ponha o ícone CIPER · {nome} na tela do celular.">
<meta name="theme-color" content="#0E3B2E">
<link rel="icon" type="image/png" href="icone-192.png">
<link rel="apple-touch-icon" href="icone-180.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="{curto}">
<link rel="manifest" href="manifest.webmanifest">
<link rel="stylesheet" href="../../assets/css/site.css">
</head>
<body>
<!-- Gerado por _scripts/gerar_redes.py: edite o script, não esta página. -->
<header class="topo">
  <div class="wrap">
    <a class="marca" href="../../index.html"><img src="../../assets/icone/ciper-icone.svg" alt="">CIPER</a>
    <a class="rp-volta" href="../../redes.html">Todas as redes</a>
  </div>
</header>

<main class="rede-pagina">
  <img class="rp-ico" src="icone-512.png" width="120" height="120" alt="Ícone CIPER · {nome}">
  <p class="olho">Redes do CIPER</p>
  <h1>CIPER · {nome}</h1>
  <p class="lead">{html.escape(r["conta"])}</p>
  <p class="aviso" id="abrindo" hidden>Abrindo o {nome} do CIPER…</p>
  <a class="btn verde" id="abrir" href="{r["perfil"]}" rel="noopener">Abrir o {nome} do CIPER</a>
  <button class="btn claro" id="instalar" type="button" hidden>Instalar o ícone na tela do celular</button>
  <div class="cartao guia">
    <h3>Para pôr o ícone na tela do celular</h3>
    <p><b>Android (Chrome):</b> toque em “Instalar o ícone” acima ou, no menu ⋮ do Chrome, em “Instalar app” ou “Adicionar à tela inicial”.</p>
    <p><b>iPhone (Safari):</b> toque em Compartilhar e depois em “Adicionar à Tela de Início”.</p>
    <p>O ícone “{curto}” abre o {nome} do CIPER com um toque. Nada é instalado sem a sua confirmação.</p>
  </div>
</main>

<footer>
  <div class="wrap">
    <p class="nota-ia">{NOTA_IA}</p>
  </div>
</footer>

<script>
(function () {{
  var perfil = {json.dumps(r["perfil"])}, intent = {json.dumps(intent(r))};
  var abrir = document.getElementById('abrir'), instalar = document.getElementById('instalar');
  if (/Android/i.test(navigator.userAgent)) abrir.href = intent;
  var app = (window.matchMedia && matchMedia('(display-mode: standalone)').matches) || navigator.standalone === true;
  if (app || /[?&]abrir=1/.test(location.search)) {{
    document.getElementById('abrindo').hidden = false;
    location.replace(perfil);
  }}
  var adiado = null;
  window.addEventListener('beforeinstallprompt', function (e) {{ e.preventDefault(); adiado = e; instalar.hidden = false; }});
  instalar.addEventListener('click', function () {{
    if (!adiado) return;
    adiado.prompt();
    adiado.userChoice.then(function () {{ adiado = null; instalar.hidden = true; }});
  }});
  window.addEventListener('appinstalled', function () {{ instalar.hidden = true; }});
  if ('serviceWorker' in navigator) navigator.serviceWorker.register('sw.js').catch(function () {{}});
}})();
</script>
</body>
</html>
"""


def manifesto(r: dict) -> str:
    return json.dumps({
        "id": f"/ciper/r/{r['chave']}/",
        "name": f"CIPER · {r['nome']}",
        "short_name": r["curto"],
        "description": f"{r['nome']} do CIPER Ouro Preto",
        "lang": "pt-BR",
        "start_url": "./?abrir=1",
        "scope": "./",
        "display": "standalone",
        "background_color": "#F6F2E8",
        "theme_color": "#0E3B2E",
        "icons": [
            {"src": "icone-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
            {"src": "icone-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
            {"src": "icone-512-maskable.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
        ],
    }, ensure_ascii=False, indent=2) + "\n"


SW = """// Gerado por _scripts/gerar_redes.py. Service worker mínimo: só existe para o Chrome oferecer
// "Instalar app". Vai sempre à rede e não guarda cache (lição de 2026-09-16: o Pages manda
// max-age=600 e um fetch() comum devolveria a cópia velha do navegador).
self.addEventListener('install', function () { self.skipWaiting(); });
self.addEventListener('activate', function (e) { e.waitUntil(self.clients.claim()); });
self.addEventListener('fetch', function (e) {
  if (e.request.mode !== 'navigate') return;
  var u = new URL(e.request.url);
  u.searchParams.set('_sw', Date.now());
  e.respondWith(fetch(u.href, { cache: 'no-store', credentials: 'same-origin' }).catch(function () { return fetch(e.request); }));
});
"""


def cartao_rede(item: dict, svg: str) -> str:
    if item["chave"] == "site":
        ico, abrir, rot_abrir = "assets/icone/ciper-icone-192.png", "index.html", "Abrir o site"
        instalar = '<a class="btn claro" id="instalar-site" href="#instalar">Instalar o ícone</a>'
        alvo_attr = ""
    else:
        r = next(x for x in ATIVAS if x["chave"] == item["chave"])
        ico, abrir, rot_abrir = f"r/{r['chave']}/icone-192.png", r["perfil"], f"Abrir o {r['nome']}"
        instalar = f'<a class="btn claro" href="r/{r["chave"]}/">Instalar o ícone</a>'
        alvo_attr = ' target="_blank" rel="noopener"'
    url_curta = item["alvo"].replace("https://", "").rstrip("/")
    return f"""      <article class="cartao rede" id="rede-{item['chave']}">
        <img class="rede-ico" src="{ico}" width="72" height="72" alt="">
        <h3>{item['nome']}</h3>
        <p class="rede-conta">{html.escape(item['conta'])}</p>
        <div class="qr">{svg}</div>
        <p class="qr-url">{url_curta}</p>
        <div class="rede-botoes">
          <a class="btn verde" href="{abrir}"{alvo_attr}>{rot_abrir}</a>
          {instalar}
        </div>
      </article>"""


def pagina_redes(itens) -> str:
    cartoes = "\n".join(cartao_rede(i, qr_svg(i["alvo"], f"QR Code: {i['nome']} do CIPER")) for i in itens)
    baixar = "\n".join(
        f'        <li><b>{i["nome"]}</b><a href="assets/qr/ciper-qr-{i["chave"]}.png" download>PNG (1024 px)</a>'
        f'<a href="assets/qr/ciper-qr-{i["chave"]}.svg" download>SVG (vetor)</a></li>' for i in itens)
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Redes — CIPER</title>
<meta name="description" content="Siga o CIPER no Instagram e no Facebook. QR Codes para abrir as redes e pôr os ícones do CIPER na tela do celular.">
<meta name="theme-color" content="#0E3B2E">
<link rel="icon" href="assets/icone/favicon.ico" sizes="any">
<link rel="icon" type="image/svg+xml" href="assets/icone/ciper-icone.svg">
<link rel="apple-touch-icon" href="assets/icone/ciper-icone-180.png">
<link rel="manifest" href="manifest.webmanifest">
<link rel="stylesheet" href="assets/css/site.css">
</head>
<body>
<!-- Gerado por _scripts/gerar_redes.py: edite o script, não esta página. -->
<header class="topo">
  <div class="wrap">
    <a class="marca" href="index.html"><img src="assets/icone/ciper-icone.svg" alt="">CIPER</a>
    <button id="abre-menu" aria-controls="menu" aria-expanded="false">Menu</button>
    <nav class="menu" id="menu" aria-label="Seções">
      <a href="index.html">Início</a>
      <a href="#instalar">Como instalar</a>
      <a href="#baixar">QR Codes para imprimir</a>
      <a class="cta" href="capital-humano.html">Capital humano</a>
      <a class="cta2" href="investimentos.html">Investimentos</a>
    </nav>
    {bloco_topo()}
  </div>
</header>

<main>
<div class="cabeca-banco">
  <div class="wrap">
    <p class="olho" style="color:var(--ouro2)">Redes</p>
    <h1>Siga o CIPER</h1>
    <p class="lead" style="color:#CFE0D6">Aponte a câmera do celular para um QR Code. Ele abre a página da rede, de onde você vai ao perfil do CIPER ou põe o ícone do CIPER na tela do celular.</p>
  </div>
</div>

<section id="redes">
  <div class="wrap">
    <!-- REDES:INICIO (gerado por _scripts/gerar_redes.py) -->
    <div class="redes">
{cartoes}
    </div>
    <!-- REDES:FIM -->
  </div>
</section>

<section id="instalar" class="alt">
  <div class="wrap">
    <p class="olho">Como instalar</p>
    <h2>O ícone do CIPER na tela do celular</h2>
    <p class="lead">Cada ícone abre a rede do CIPER com um toque. Nenhum site instala nada sozinho: o ícone só aparece depois que você confirma.</p>
    <div class="grade g2">
      <div class="cartao">
        <h3>Android (Chrome)</h3>
        <ol class="passos">
          <li>Leia o QR Code com a câmera e abra o link.</li>
          <li>Toque em “Instalar o ícone” ou, no menu ⋮ do Chrome, em “Instalar app” ou “Adicionar à tela inicial”.</li>
          <li>Confirme. O ícone aparece na tela, com o selo da rede no canto.</li>
        </ol>
      </div>
      <div class="cartao">
        <h3>iPhone (Safari)</h3>
        <ol class="passos">
          <li>Leia o QR Code com a câmera e abra o link no Safari.</li>
          <li>Toque em Compartilhar (o quadrado com a seta para cima).</li>
          <li>Toque em “Adicionar à Tela de Início” e depois em “Adicionar”.</li>
        </ol>
      </div>
    </div>
  </div>
</section>

<section id="baixar">
  <div class="wrap">
    <p class="olho">QR Codes para imprimir</p>
    <h2>Leve o CIPER para cartazes, slides e papelaria</h2>
    <p class="lead">Os QR Codes apontam para este site, que leva à rede. Se o endereço de uma rede mudar, o QR já impresso continua valendo.</p>
    <ul class="baixar">
{baixar}
    </ul>
  </div>
</section>
</main>

<footer>
  <div class="wrap">
    <p><strong style="color:#fff">CIPER — Centro de Inovação e Pesquisa de Energias Renováveis de Ouro Preto.</strong> IFMG · UFOP · Fundação Gorceix · PMOP.</p>
    {bloco_rodape()}
    <p class="fim">Projeto em fase de concepção e estruturação. Instagram e Facebook são marcas de seus donos; os selos nos ícones só indicam a rede.</p>
    <p class="nota-ia">{NOTA_IA}</p>
  </div>
</footer>

<script src="assets/js/site.js"></script>
<script>
(function () {{
  var botao = document.getElementById('instalar-site'), adiado = null;
  window.addEventListener('beforeinstallprompt', function (e) {{ e.preventDefault(); adiado = e; }});
  botao.addEventListener('click', function (e) {{
    if (!adiado) return;
    e.preventDefault();
    adiado.prompt();
    adiado.userChoice.then(function () {{ adiado = null; }});
  }});
}})();
</script>
</body>
</html>
"""


def prancha_html(itens) -> str:
    logo = base64.b64encode((SITE / "assets/icone/ciper-logo-horizontal-1200.png").read_bytes()).decode()
    linhas = []
    for i in itens:
        url_curta = i["alvo"].replace("https://", "").rstrip("/")
        dica = ("Aponte a câmera do celular. O site abre e pode virar um ícone na tela do celular."
                if i["chave"] == "site" else
                "Aponte a câmera do celular. A página leva ao perfil do CIPER e oferece o ícone para a tela do celular.")
        linhas.append(f"""  <div class="linha">
    <div class="qr">{qr_svg(i['alvo'], 'QR Code: ' + i['nome'])}</div>
    <div class="txt"><h2>{i['nome']}</h2><p class="conta">{html.escape(i['conta'])}</p>
      <p class="url">{url_curta}</p>
      <p class="dica">{dica}</p></div>
  </div>""")
    return f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><title>CIPER · QR Codes das redes</title>
<style>
@page{{size:A4;margin:14mm 15mm}}
*{{box-sizing:border-box}}
body{{margin:0;font-family:"Segoe UI",Arial,sans-serif;color:#16241F}}
header{{display:flex;align-items:center;justify-content:space-between;border-bottom:3px solid #DE9B1E;padding-bottom:5mm;margin-bottom:6mm}}
header img{{height:16mm}}
header h1{{font:700 20pt Georgia,serif;color:#0E3B2E;margin:0}}
.linha{{display:flex;gap:9mm;align-items:center;padding:5mm 0;border-bottom:1px solid #D9D2BF;break-inside:avoid}}
.qr{{width:60mm;height:60mm;flex:0 0 60mm}}
.qr svg{{width:60mm;height:60mm;display:block}}
h2{{font:700 18pt Georgia,serif;color:#0E3B2E;margin:0 0 1mm}}
.conta{{font-size:13pt;margin:0 0 2mm;color:#4A5852}}
.url{{font:600 11pt Consolas,monospace;margin:0 0 3mm;color:#17614A}}
.dica{{font-size:10pt;margin:0;color:#4A5852}}
footer{{margin-top:5mm;font-size:8pt;color:#4A5852}}
</style></head><body>
<header><img src="data:image/png;base64,{logo}" alt="CIPER"><h1>Siga o CIPER</h1></header>
{chr(10).join(linhas)}
<footer>CIPER — Centro de Inovação e Pesquisa de Energias Renováveis de Ouro Preto · IFMG · UFOP · Fundação Gorceix · PMOP · nidecop-jafb.github.io/ciper/redes.html<br>
{re.sub('<[^>]+>', '', NOTA_IA)}</footer>
</body></html>
"""


def gera_pdf(html_path: Path, pdf_path: Path):
    if not CHROME.exists():
        print("  ! Chrome não encontrado: prancha só em HTML")
        return
    perfil = Path(os.environ.get("PUBLIC", r"C:\Users\Public")) / "ciper-chrome-tmp"
    subprocess.run([str(CHROME), "--headless=new", "--disable-gpu", f"--user-data-dir={perfil}",
                    "--no-pdf-header-footer", f"--print-to-pdf={pdf_path}", html_path.resolve().as_uri()],
                   check=True, capture_output=True, timeout=120)
    shutil.rmtree(perfil, ignore_errors=True)


# ---------------------------------------------------------------- principal
def main():
    sem_pdf = "--sem-pdf" in sys.argv
    for r in ATIVAS:
        pasta = SITE / "r" / r["chave"]
        icones(r, pasta)
        (pasta / "index.html").write_text(mini_pagina(r), encoding="utf-8", newline="\n")
        (pasta / "manifest.webmanifest").write_text(manifesto(r), encoding="utf-8", newline="\n")
        (pasta / "sw.js").write_text(SW, encoding="utf-8", newline="\n")
        print(f"  r/{r['chave']}/: página, manifesto, sw e 4 ícones")

    itens = alvos_qr()
    qrdir = SITE / "assets" / "qr"
    qrdir.mkdir(parents=True, exist_ok=True)
    SAIDA_E.mkdir(parents=True, exist_ok=True)
    for i in itens:
        svg = '<?xml version="1.0" encoding="UTF-8"?>\n' + qr_svg(i["alvo"], f"QR Code: {i['nome']} do CIPER") + "\n"
        for pasta in (qrdir, SAIDA_E):
            (pasta / f"ciper-qr-{i['chave']}.svg").write_text(svg, encoding="utf-8", newline="\n")
            qr_png(i["alvo"], pasta / f"ciper-qr-{i['chave']}.png")
        print(f"  QR {i['chave']}: {i['alvo']}")

    (SITE / "redes.html").write_text(pagina_redes(itens), encoding="utf-8", newline="\n")
    for nome in ("index.html", "capital-humano.html", "investimentos.html"):
        aplica_rodape(SITE / nome)
        aplica_topo(SITE / nome)
    print("  redes.html, rodapés e ícones do topo das 3 páginas")

    if not sem_pdf:
        h = SAIDA_E / "CIPER-QR-redes-A4-v1.html"
        h.write_text(prancha_html(itens), encoding="utf-8", newline="\n")
        gera_pdf(h, SAIDA_E / "CIPER-QR-redes-A4-v1.pdf")
        print("  prancha A4: " + str(SAIDA_E / "CIPER-QR-redes-A4-v1.pdf"))


if __name__ == "__main__":
    main()
