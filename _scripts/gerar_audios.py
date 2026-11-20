"""Gera os audios da secao "Para ouvir com calma" (index.html#audios).

Recodifica os originais de PRJ-001A (AAC estereo ~256 kbps) para AAC mono 64 kbps,
44,1 kHz, com o moov no inicio (+faststart: o play comeca antes do fim do download).
Os originais nao sao alterados.
Briefing: _planejamento/_pre/PRE-site-ciper-audios-2026-11-16.md
Uso: python _scripts/gerar_audios.py   (a partir da pasta do site; precisa do ffmpeg no PATH)
"""
import subprocess
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent
ORIGEM = SITE.parent / "PRJ-001A-CIPER-Concepção"
SAIDA = SITE / "audios"

# arquivo publicado -> original em PRJ-001A
# Os 4 audios de 16/11 citavam a alianca e sairam em 20/11 (tag v-alianca-2026-11).
# Briefing dos atuais (2, do roteiro "O CIPER no IFMG"): PRE-site-ciper-audio-ciper-no-ifmg-2026-11-20
AUDIOS = {
    "01-Ouro-Preto-mineracao-energias-renovaveis.m4a":
        "PRJ-001A-CIPER-13-Ouro-Preto-da-mineracao-as-energias-renovaveis-v1.m4a",
    "02-CIPER-energias-renovaveis-Ouro-Preto.m4a":
        "PRJ-001A-CIPER-14-CIPER-e-energias-renovaveis-em-Ouro-Preto-v1.m4a",
}


def main() -> None:
    SAIDA.mkdir(parents=True, exist_ok=True)
    for destino, original in AUDIOS.items():
        entrada = ORIGEM / original
        saida = SAIDA / destino
        subprocess.run(
            ["ffmpeg", "-v", "error", "-y", "-i", str(entrada), "-vn", "-map_metadata", "-1",
             "-ac", "1", "-ar", "44100", "-c:a", "aac", "-b:a", "64k",
             "-movflags", "+faststart", str(saida)],
            check=True,
        )
        print(f"{destino}: {saida.stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
