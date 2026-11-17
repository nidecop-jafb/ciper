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
AUDIOS = {
    "01-CIPER-Ouro-Preto-Historia-e-Futuro.m4a":
        "PRJ-001A-CIPER-06-Ouro Preto-Onde a história se entrelaça com o futuro-v1.m4a",
    "02-CIPER-Simbiose-Parque-Tecnologico-FG.m4a":
        "PRJ-001A-CIPER-08-CIPER-Simbiose com o Parque Tecnológico da FG-A1.m4a",
    "03-CIPER-Ouro-Preto-Minerio-por-Conhecimento-Renovavel.m4a":
        "PRJ-001A-CIPER-09-Ouro_Preto_troca_minério_por_conhecimento_renovável-v1.m4a",
    "04-CIPER-Ouro-Preto-Tecnologia-Verde.m4a":
        "PRJ-001A-CIPER-11-Ouro_Preto_se_reinventa_com_tecnologia_verde.m4a",
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
