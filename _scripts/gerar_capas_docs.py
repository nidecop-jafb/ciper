"""Gera as fotos das capas dos cartoes de "Para ler com calma" (index.html#documentos)
e de "Para ouvir com calma" (index.html#audios: foto-a05 e foto-a06).

A capa e montada em HTML/CSS (foto em cima, faixa verde com numero e titulo curto);
este script so recorta as fotos: assets/docs/foto-NN.webp, 208 x 168 px (exibidas a 104 x 84).
O cartao 7 (marca) nao tem foto: usa assets/icone/ciper-logo-horizontal-claro.svg.
Briefing: _planejamento/_pre/PRE-site-ciper-capas-docs-e-doc6-2026-11-16.md
Uso: python _scripts/gerar_capas_docs.py   (a partir da pasta do site)
"""
from pathlib import Path

from PIL import Image

SITE = Path(__file__).resolve().parent.parent
IMG = SITE / "assets" / "img"
SAIDA = SITE / "assets" / "docs"
L, A = 208, 168

# numero do cartao -> (foto de assets/img, foco horizontal 0..1, foco vertical 0..1)
FOTOS = {
    "01": ("ouro-preto-amanhecer.jpg", 0.5, 0.5),
    "02": ("escola-de-minas.jpg", 0.5, 0.5),
    "03": ("pendulo-de-foucault.jpg", 0.5, 0.5),
    "04": ("ciper-vista-aerea.jpg", 0.5, 0.5),
    "05": ("fachada-perspectiva.jpg", 0.5, 0.5),
    "06": ("serra-amanhecer.jpg", 0.5, 0.5),
    # "Para ouvir com calma" (index.html#audios): os audios 1 e 2 reusam foto-01 e foto-02
    # (PRE-site-ciper-audios-2026-11-16)
    "a03": ("igreja-sao-francisco.jpg", 0.5, 0.5),
    "a04": ("claraboia-jardim.jpg", 0.5, 0.5),
    # audios 1 e 2 do roteiro "O CIPER no IFMG" (PRE-site-ciper-audio-ciper-no-ifmg-2026-11-20)
    "a05": ("zde-vista-aerea.jpg", 0.5, 0.5),
    "a06": ("serra-entardecer.jpg", 0.5, 0.5),
}


def recorte(foto: Path, fx: float, fy: float) -> Image.Image:
    im = Image.open(foto).convert("RGB")
    escala = max(L / im.width, A / im.height)
    im = im.resize((round(im.width * escala), round(im.height * escala)), Image.LANCZOS)
    x = round((im.width - L) * fx)
    y = round((im.height - A) * fy)
    return im.crop((x, y, x + L, y + A))


def main() -> None:
    SAIDA.mkdir(parents=True, exist_ok=True)
    for n, (nome, fx, fy) in FOTOS.items():
        destino = SAIDA / f"foto-{n}.webp"
        recorte(IMG / nome, fx, fy).save(destino, "WEBP", quality=80, method=6)
        print(f"{destino.name}: {destino.stat().st_size / 1024:.1f} KB  <- {nome}")


if __name__ == "__main__":
    main()
