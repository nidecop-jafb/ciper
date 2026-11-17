# Site do CIPER — PRJ-001C

Site estático (abre com dois cliques em `index.html`; não precisa de servidor).

| Arquivo | O que é |
|---|---|
| `index.html` | Página institucional: o CIPER, aliança, pilares, projeto, vídeo, governança, roteiro, reuniões, documentos, áudios |
| `capital-humano.html` | Banco de Capital Humano: busca, filtros, exportação e ficha de adesão |
| `investimentos.html` | Apresentação para investidores (4 blocos + resumo em inglês) e falas sobre investimento com link no tempo (fonte: `PRJ-001G-CIPER-Mensagens/`) |
| `redes.html` | Redes do CIPER: QR Codes (Instagram, Facebook, Site), botões e guia para pôr o ícone na tela do celular. **Gerada** por `_scripts/gerar_redes.py` |
| `r/{rede}/` | Mini-página instalável de cada rede (manifesto, service worker sem cache, ícones com selo). O ícone instalado abre o perfil. **Gerada** |
| `assets/qr/` | QR Codes em PNG (1024 px) e SVG. Apontam para o site (`r/{rede}/`), não para a rede: o impresso continua valendo se a rede mudar |
| `documentos/` | PDFs de "Para ler com calma". `01`–`04` e `06` são cópias dos v2 de `PRJ-001A-CIPER-Concepção/` (00, 07, 01, 04, 12); os anteriores estão em `G:\CIPER\xx\2026-11-16_site-docs-v2\` e `…\2026-11-16_site-capas-doc6\` |
| `audios/` | Áudios de "Para ouvir com calma" (`#audios`, player no cartão): AAC mono 64 kbps com `+faststart`, recodificados dos `.m4a` 06, 08, 09 e 11 de `PRJ-001A-CIPER-Concepção/` (os originais ficam lá, intactos). **Gerados** por `_scripts/gerar_audios.py` (precisa do ffmpeg) |
| `assets/docs/` | Fotos das capas dos cartões de documentos e de áudios (`foto-01…06.webp`; `foto-a03` e `foto-a04` para os áudios 3 e 4; os áudios 1 e 2 reusam `foto-01` e `foto-02`; recortes de `assets/img/`). A capa é montada em HTML/CSS (foto + faixa verde com número e título curto). **Geradas** por `_scripts/gerar_capas_docs.py` (a lista `FOTOS` diz qual foto vai em cada cartão) |
| `assets/icone/` | Ícone oficial (SVG, PNG 32–1024, `favicon.ico`) e logotipos horizontais |
| `assets/video/` | Vídeo institucional em 720p (PT e EN) |
| `dados/capital-humano.csv` | O banco em planilha (abre no Excel) |
| `dados/adesoes.csv` | Fichas de adesão recebidas — uma linha por pessoa |
| `_fontes/` | Cópia das páginas públicas usadas na coleta (09/11/2026) |
| `_scripts/` | `gerar_banco.py` (monta o banco), `gerar_icone.py` (redesenha o ícone), `gerar_redes.py` (redes, QRs, prancha A4), `conferir_redes.py` (lê os QRs e confere manifestos), `gerar_capas_docs.py` (capas dos documentos e dos áudios) e `gerar_audios.py` (áudios) |

## Ligar uma rede nova (LinkedIn, X, WhatsApp)

Em `_scripts/gerar_redes.py`, na lista `REDES`, preencha `perfil` e troque `ativa` para `True`. Depois rode `python _scripts\gerar_redes.py` e `python _scripts\conferir_redes.py`. A página Redes, os rodapés (entre `<!-- REDES:INICIO -->` e `<!-- REDES:FIM -->`), os ícones do topo (entre `<!-- REDES-TOPO:INICIO -->` e `<!-- REDES-TOPO:FIM -->`, no lugar do antigo item "Redes" do menu), os QRs e a prancha A4 (`PRJ-001E-CIPER-Redes-Sociais/qrcodes/`) saem juntos.

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

- **IFMG**: a lista oficial de docentes (`integra.ouropreto.ifmg.edu.br`) segue fora do ar (09 e 17/11/2026). Em 17/11 entraram os servidores dos 10 grupos (espelhos CNPq em `_fontes/cnpq/`) e dos projetos do campus no SUAP (2023–2026). Faltam docentes e técnicos sem grupo nem projeto registrado.

## IFMG-OP: CNPq e SUAP (17/11/2026)

- `_fontes/cnpq/grupo_{id}.html`: espelho de cada grupo (`dgp.cnpq.br/dgp/espelhogrupo/{id}`). Lê pesquisadores e técnicos; estudantes e egressos são ignorados.
- `_fontes/suap_lotacao_op.csv` (`nome;categoria;cargo`): servidores confirmados no SUAP como lotados no Campus Ouro Preto. **Só quem está aqui entra no banco**, venha do CNPq ou do SUAP.
- `_fontes/suap_projetos_op.csv` (`nome;papel;projeto;tipo;edital;ano`): servidores de projetos do campus nos resultados de editais do SUAP. Nunca alunos, matrícula, e-mail ou telefone.
- Os três ficam fora do ar e do git (`_fontes/` está no `.gitignore`). Para refazer: baixar os espelhos de novo, refazer os dois `.csv` pelo conector `suap-ifmg` e rodar `gerar_banco.py`.
- **UFOP**: faltam DEMET, DEMEC, DEARQ, DEFIS, DEQUI, DECOM e Escola de Farmácia (páginas fora do ar ou sem lista).
- **Fundação Gorceix e PMOP**: sem lista pública; dependem de indicação das instituições.
- Datas das reuniões 1, 3, 5 e 6 vêm das datas dos arquivos — conferir.
