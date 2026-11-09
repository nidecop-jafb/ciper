# Site do CIPER — PRJ-001C

Site estático (abre com dois cliques em `index.html`; não precisa de servidor).

| Arquivo | O que é |
|---|---|
| `index.html` | Página institucional: o CIPER, aliança, pilares, projeto, vídeo, governança, roteiro, reuniões, documentos |
| `capital-humano.html` | Banco de Capital Humano: busca, filtros, exportação e ficha de adesão |
| `assets/icone/` | Ícone oficial (SVG, PNG 32–1024, `favicon.ico`) e logotipos horizontais |
| `assets/video/` | Vídeo institucional em 720p (PT e EN) |
| `dados/capital-humano.csv` | O banco em planilha (abre no Excel) |
| `dados/adesoes.csv` | Fichas de adesão recebidas — uma linha por pessoa |
| `_fontes/` | Cópia das páginas públicas usadas na coleta (09/11/2026) |
| `_scripts/` | `gerar_banco.py` (monta o banco) e `gerar_icone.py` (redesenha o ícone) |

## Atualizar o banco

1. Recebeu uma ficha de adesão (`adesao-ciper-nome.csv`)? Copie a **segunda linha** dela para o fim de `dados/adesoes.csv`.
2. Rode, nesta pasta:

```powershell
python _scripts\gerar_banco.py
```

O site passa a mostrar a pessoa com “Adesão registrada” e os eixos que ela declarou.

## Publicar

A pasta inteira pode ir para o GitHub Pages como está. Antes de publicar, **tirar `_fontes/` e `_scripts/`** do que vai ao ar (não são necessários no site) e confirmar com as quatro instituições o uso dos nomes e do conteúdo.

## Pendências conhecidas

- **IFMG**: a lista oficial de docentes (`integra.ouropreto.ifmg.edu.br`) estava fora do ar na coleta; entraram só os líderes de grupos de pesquisa e a equipe da DPIPG.
- **UFOP**: faltam DEMET, DEMEC, DEARQ, DEFIS, DEQUI, DECOM e Escola de Farmácia (páginas fora do ar ou sem lista).
- **Fundação Gorceix e PMOP**: sem lista pública; dependem de indicação das instituições.
- Datas das reuniões 1, 3, 5 e 6 vêm das datas dos arquivos — conferir.
