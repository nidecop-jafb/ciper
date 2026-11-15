"""Confere o que o gerar_redes.py produziu (critérios 1, 2, 3 e 7 do PRE-site-ciper-redes-qrcodes-2026-11-14).

Uso, na pasta do site:  python _scripts/conferir_redes.py
Sai com código 1 se alguma conferência falhar.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
import gerar_redes as G  # noqa: E402

SITE = G.SITE
TMP = Path(os.environ.get("PUBLIC", r"C:\Users\Public")) / "ciper-conferir-tmp"
falhas: list[str] = []


def ok(cond: bool, msg: str):
    print(("  OK   " if cond else "  FALHA ") + msg)
    if not cond:
        falhas.append(msg)


def le_qr(img: np.ndarray) -> str:
    det = cv2.QRCodeDetector()
    txt, _, _ = det.detectAndDecode(img)
    return txt


def chrome_png(arquivo: Path, saida: Path):
    subprocess.run([str(G.CHROME), "--headless=new", "--disable-gpu", f"--user-data-dir={TMP / 'perfil'}",
                    "--hide-scrollbars", "--window-size=700,700", f"--screenshot={saida}", arquivo.resolve().as_uri()],
                   check=True, capture_output=True, timeout=120)


def hashes() -> dict:
    alvo = [SITE / "redes.html", *(SITE / "assets/qr").glob("*"), *(SITE / "r").rglob("*"),
            SITE / "index.html", SITE / "capital-humano.html", SITE / "investimentos.html"]
    return {str(p.relative_to(SITE)): hashlib.sha256(p.read_bytes()).hexdigest() for p in alvo if p.is_file()}


def main():
    TMP.mkdir(parents=True, exist_ok=True)
    print("1. Arquivos e gerador estável")
    for r in G.ATIVAS:
        p = SITE / "r" / r["chave"]
        for f in ("index.html", "manifest.webmanifest", "sw.js", "icone-192.png", "icone-512.png",
                  "icone-512-maskable.png", "icone-180.png"):
            ok((p / f).is_file(), f"r/{r['chave']}/{f}")
    itens = G.alvos_qr()
    for i in itens:
        for ext in ("png", "svg"):
            ok((SITE / f"assets/qr/ciper-qr-{i['chave']}.{ext}").is_file(), f"assets/qr/ciper-qr-{i['chave']}.{ext}")
    antes = hashes()
    subprocess.run([sys.executable, str(SITE / "_scripts/gerar_redes.py"), "--sem-pdf"], check=True,
                   capture_output=True, cwd=SITE)
    ok(antes == hashes(), f"gerador rodado de novo: {len(antes)} arquivos idênticos")

    print("2. QR Codes lidos por máquina")
    for i in itens:
        png = cv2.imread(str(SITE / f"assets/qr/ciper-qr-{i['chave']}.png"))
        ok(le_qr(png) == i["alvo"], f"PNG {i['chave']} -> {i['alvo']}")
        shot = TMP / f"svg-{i['chave']}.png"
        chrome_png(SITE / f"assets/qr/ciper-qr-{i['chave']}.svg", shot)
        ok(le_qr(cv2.imread(str(shot))) == i["alvo"], f"SVG {i['chave']} (renderizado pelo Chrome) -> {i['alvo']}")

    print("3. Manifestos e service workers")
    ids = []
    for nome in ["manifest.webmanifest", *(f"r/{r['chave']}/manifest.webmanifest" for r in G.ATIVAS)]:
        m = json.loads((SITE / nome).read_text(encoding="utf-8"))
        ids.append(m.get("id"))
        ok(bool(m.get("name")) and 0 < len(m.get("short_name", "")) <= 12 and m.get("display") == "standalone",
           f"{nome}: name, short_name '{m.get('short_name')}' ({len(m.get('short_name', ''))} car.), standalone")
        pasta = (SITE / nome).parent
        for ic in m["icons"]:
            w, h = (int(v) for v in ic["sizes"].split("x"))
            ok(Image.open(pasta / ic["src"]).size == (w, h), f"{nome}: {ic['src']} {ic['sizes']} {ic.get('purpose', 'any')}")
        if nome != "manifest.webmanifest":
            ok(any(ic.get("purpose") == "maskable" for ic in m["icons"]), f"{nome}: tem ícone maskable")
    ok(len(set(ids)) == len(ids) and None not in ids, f"ids distintos: {ids}")
    for r in G.ATIVAS:
        res = subprocess.run(["node", "--check", str(SITE / f"r/{r['chave']}/sw.js")], capture_output=True, text=True,
                             shell=True)
        ok(res.returncode == 0, f"node --check r/{r['chave']}/sw.js")
        sw = (SITE / f"r/{r['chave']}/sw.js").read_text(encoding="utf-8")
        ok("no-store" in sw and "caches.put" not in sw, f"r/{r['chave']}/sw.js sem cache")

    print("7. Prancha A4 (PDF)")
    pdf = G.SAIDA_E / "CIPER-QR-redes-A4-v1.pdf"
    if pdf.is_file():
        import pymupdf
        doc = pymupdf.open(pdf)
        ok(doc.page_count == 1, f"prancha com {doc.page_count} página(s)")
        pag = doc[0]
        ok(abs(pag.rect.width - 595) < 2 and abs(pag.rect.height - 842) < 2, "tamanho A4")
        pix = pag.get_pixmap(dpi=200)
        img = cv2.cvtColor(np.frombuffer(pix.samples, np.uint8).reshape(pix.h, pix.w, pix.n), cv2.COLOR_RGB2BGR)
        det = cv2.QRCodeDetector()
        achou, textos, _, _ = det.detectAndDecodeMulti(img)
        lidos = sorted(t for t in (textos if achou else []) if t)
        ok(lidos == sorted(i["alvo"] for i in itens), f"QRs lidos no PDF: {lidos}")
    else:
        ok(False, "prancha PDF não encontrada")

    shutil.rmtree(TMP, ignore_errors=True)
    print(f"\n{'TUDO OK' if not falhas else str(len(falhas)) + ' FALHA(S)'}")
    sys.exit(1 if falhas else 0)


if __name__ == "__main__":
    main()
