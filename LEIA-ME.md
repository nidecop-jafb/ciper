# Site do CIPER — PRJ-001C

Site estático (abre com dois cliques em `index.html`; não precisa de servidor).

| Arquivo | O que é |
|---|---|
| `index.html` | Página institucional: o CIPER, o CIPER no IFMG (`#ifmg`), pilares, projeto, vídeo, governança, roteiro, reuniões, documentos (só a marca) e áudios (`#audios`: 2 áudios do roteiro "O CIPER no IFMG", desde 20/11/2026) |
| `capital-humano.html` | Banco de Capital Humano: busca, filtros, exportação e ficha de adesão |
| `investimentos.html` | Apresentação para investidores (4 blocos + resumo em inglês) e falas sobre investimento com link no tempo (fonte: `PRJ-001G-CIPER-Mensagens/`) |
| `redes.html` | Redes do CIPER: QR Codes (Instagram, Facebook, Site), botões e guia para pôr o ícone na tela do celular. **Gerada** por `_scripts/gerar_redes.py` |
| `r/{rede}/` | Mini-página instalável de cada rede (manifesto, service worker sem cache, ícones com selo). O ícone instalado abre o perfil. **Gerada** |
| `assets/qr/` | QR Codes em PNG (1024 px) e SVG. Apontam para o site (`r/{rede}/`), não para a rede: o impresso continua valendo se a rede mudar |
| `documentos/` | Vazia desde 20/11/2026: os 6 PDFs citavam os parceiros e foram para `G:\CIPER\xx\2026-11-20_site-so-ifmg\documentos\` (também na tag `v-alianca-2026-11`) |
| `audios/` | 2 áudios gerados no NotebookLM a partir do roteiro `PRJ-001A-CIPER-Concepção/roteiros-audio/CIPER-Roteiro-Audio-CIPER-no-IFMG-v1.md` (originais `PRJ-001A-CIPER-13-…` e `-14-…` em PRJ-001A; transcrições conferidas em `PRJ-001A/_transcricoes/`). **Gerados** por `_scripts/gerar_audios.py` (ffmpeg: AAC mono 64 kbps, `+faststart`). Os 4 áudios de 16/11 citavam a aliança e foram para `G:\CIPER\xx\2026-11-20_site-so-ifmg\audios\` (também na tag) |
| `assets/docs/` | Fotos das capas dos cartões de documentos e de áudios (`foto-01…06.webp`; `foto-a05` e `foto-a06` para os áudios 1 e 2; `foto-a03` e `foto-a04` são dos áudios de 16/11, fora do ar; recortes de `assets/img/`). A capa é montada em HTML/CSS (foto + faixa verde com número e título curto). **Geradas** por `_scripts/gerar_capas_docs.py` (a lista `FOTOS` diz qual foto vai em cada cartão) |
| `assets/icone/` | Ícone oficial (SVG, PNG 32–1024, `favicon.ico`) e logotipos horizontais |
| `assets/video/` | Vídeo institucional em 720p (PT e EN) |
| `dados/capital-humano.csv` | O banco **público** em planilha: só IFMG e pesquisadores colaboradores (lista `COLABORADORES` em `gerar_banco.py`). O banco completo (UFOP etc.) sai em `_fontes/completo/`, fora do git e do site |
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

A pasta inteira pode ir para o GitHub Pages como está. Antes de publicar, **tirar `_fontes/` e `_scripts/`** do que vai ao ar (não são necessários no site) e confirmar com o IFMG o uso dos nomes e do conteúdo.

## Pendências conhecidas

- **IFMG**: a lista oficial de docentes (`integra.ouropreto.ifmg.edu.br`) segue fora do ar (09 e 17/11/2026). Em 17/11 entraram os servidores dos 10 grupos (espelhos CNPq em `_fontes/cnpq/`) e dos projetos do campus no SUAP (2023–2026). Faltam docentes e técnicos sem grupo nem projeto registrado.

## IFMG-OP: CNPq e SUAP (17/11/2026)

- `_fontes/cnpq/grupo_{id}.html`: espelho de cada grupo (`dgp.cnpq.br/dgp/espelhogrupo/{id}`). Lê pesquisadores e técnicos; estudantes e egressos são ignorados.
- `_fontes/suap_lotacao_op.csv` (`nome;categoria;cargo`): servidores confirmados no SUAP como lotados no Campus Ouro Preto. **Só quem está aqui entra no banco**, venha do CNPq ou do SUAP.
- `_fontes/suap_projetos_op.csv` (`nome;papel;projeto;tipo;edital;ano`): servidores de projetos do campus nos resultados de editais do SUAP. Nunca alunos, matrícula, e-mail ou telefone.
- Os três ficam fora do ar e do git (`_fontes/` está no `.gitignore`). Para refazer: baixar os espelhos de novo, refazer os dois `.csv` pelo conector `suap-ifmg` e rodar `gerar_banco.py`.
- **UFOP** (só no banco completo): faltam DEMET, DEMEC, DEARQ, DEFIS, DEQUI, DECOM e Escola de Farmácia (páginas fora do ar ou sem lista).
- **Outras instituições**: entram no banco público só depois de convênio (etapa paralela).
- Data da reunião 1 vem da data dos arquivos — conferir.

## Etapa só IFMG e a tag `v-alianca-2026-11` (20/11/2026)

Até o Conselho Superior, o site fala só do CIPER no IFMG (orientação do Prof. Caio, 18/11; briefing `PRE-site-ciper-so-ifmg-ocultar-parcerias-2026-11-20`). A versão com a aliança (IFMG, UFOP, FG e PMOP) está na tag `v-alianca-2026-11` (commit `14a314d`, também no GitHub). Para recuperar um arquivo dela na etapa dos convênios:

```powershell
git checkout v-alianca-2026-11 -- index.html
```

A única menção à UFOP que fica no ar é a do Ernani, como professor da UFOP e pesquisador colaborador.
