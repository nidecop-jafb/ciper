"""Gera as capas (miniaturas da 1a pagina) dos PDFs da secao "Para ler com calma".

Saida: assets/docs/capa-NN.webp, 184 x 260 px (exibidas a 92 x 130 px).
PDF retrato: pagina inteira. PDF paisagem (prancha A0): recorte central em retrato.
Uso: python _scripts/gerar_capas_docs.py   (a partir da pasta do site)
"""
from pathlib import Path
import io

import pymupdf
from PIL import Image

SITE = Path(__file__).resolve().parent.parent
DOCS = SITE / "documentos"
SAIDA = SITE / "assets" / "docs"
L, A = 184, 260

PDFS = {
    "01": "01-CIPER-Ouro-Preto-Historia-e-Futuro-v2.pdf",
    "02": "02-CIPER-Simbiose-Parque-Tecnologico-FG-v2.pdf",
    "03": "03-CIPER-Objetivos-Estrategias-e-Metas-v2.pdf",
    "04": "04-CIPER-Dossie-Executivo-v2.pdf",
    "05": "CIPER-Projeto-Arquitetonico.pdf",
    "06": "CIPER-Ouro-Preto-Vale-do-Silicio-Verde.pdf",
}


def capa(pdf: Path) -> Image.Image:
    pg = pymupdf.open(pdf)[0]
    r = pg.rect
    escala = max(L / r.width, A / r.height) * 1.0001
    pix = pg.get_pixmap(matrix=pymupdf.Matrix(escala, escala), alpha=False)
    im = Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")
    x = (im.width - L) // 2
    y = (im.height - A) // 2
    return im.crop((x, y, x + L, y + A))


def main() -> None:
    SAIDA.mkdir(parents=True, exist_ok=True)
    for n, nome in PDFS.items():
        destino = SAIDA / f"capa-{n}.webp"
        capa(DOCS / nome).save(destino, "WEBP", quality=82, method=6)
        print(f"{destino.name}: {destino.stat().st_size // 1024} KB  <- {nome}")


if __name__ == "__main__":
    main()
