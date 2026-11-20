# -*- coding: utf-8 -*-
"""Banco de Capital Humano do CIPER - gerador.

Le as paginas publicas salvas em _fontes/ (sites oficiais da UFOP e do IFMG-OP),
extrai nome, unidade, categoria, area e Lattes, junta com dados/adesoes.csv
(cadastros recebidos pelo formulario do site) e grava:

    dados/capital-humano.json   (banco completo)
    dados/capital-humano.csv    (mesmo conteudo, para planilha)
    dados/capital-humano.js     (o que o site carrega; funciona em file://)

Nao guarda e-mail nem telefone: o contato fica na pagina oficial (campo "fontes").
Uso:  python _scripts/gerar_banco.py
"""
import csv, html, json, re, sys, unicodedata
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
FONTES = RAIZ / "_fontes"
DADOS = RAIZ / "dados"
COLETA = "2026-11-09"
COLETA_IFMG = "2026-11-17"  # espelhos CNPq dos grupos + SUAP (PRE-site-ciper-capital-humano-ifmg-op)
SUAP_LOTACAO = FONTES / "suap_lotacao_op.csv"   # nome;nome_fonte;categoria  (so servidores lotados no Campus Ouro Preto)
SUAP_PROJETOS = FONTES / "suap_projetos_op.csv"  # nome;papel;projeto;tipo;edital;ano  (so servidores; nunca alunos)

PARTICULAS = {"de", "da", "do", "das", "dos", "e", "del", "von", "van", "di", "du"}
MAI = "A-ZÁÉÍÓÚÂÊÔÃÕÇÀÜ"
NOME_RE = re.compile(
    rf"^[{MAI}][\w'’.\-]*(?:\s+(?:d[aeo]s?|e|del|von|van|di|du|[{MAI}][\w'’.\-]*)){{1,8}}$"
)
NAO_NOME = re.compile(
    r"Lattes|Leia mais|^sobre |^Foto|Laborat|Secret[aá]ri|Departamento|Escola|Instituto|"
    r"Universidade|Campus|Copyright|Admin|OpenScholar|Professor|Docente|Técnic|Tecnic|"
    r"Sala|Contato|Plano de|Linha de|Email|E-mail|Curr[ií]cul|Pessoas|Home|In[ií]cio|"
    r"Corpo|Office|Setor|Herb[aá]rio|Ouro Preto|Minas Gerais|Morro|Bauxita|Buscar|"
    r"Programa|Total|Permanente|Colaborador|Researchgate|Google|Tipo de|Identifica|"
    r"SERVIDORES|PEOPLE|PESSOAL|SOBRE|DECIV|UFOP|REDEMAT|Cargos|Membro|Chefe|Participa",
    re.I,
)
LATTES_RE = re.compile(
    r"https?://lattes\.cnpq\.br/\d{16}|https?://buscatextual\.cnpq\.br/buscatextual/visualizacv\.do\?id=\w+"
)
EMAIL_RE = re.compile(r"[\w.\-]+@[\w\-]+(?:\.[\w\-]+)+")
INLINE_RE = re.compile(r"</?(span|strong|b|em|i|u|font|sup|sub|a)\b[^>]*>")

# Afinidade tematica da UNIDADE com os eixos do CIPER (sugestao a validar com cada pessoa).
AFINIDADE = {
    "DEMIN": ["P4", "P1"], "DEGEO": ["P4", "P5"], "DEAMB": ["P3", "P5"],
    "DECAT": ["P6", "P1"], "DECIV": ["X4", "P5"], "DEPRO": ["X1", "P1"],
    "DEBIO": ["P3", "P5"], "DEMAT": ["E1", "E4"], "REDEMAT": ["P4", "P1"],
    "ProAmb": ["P3", "P5"], "DPIPG": ["E2", "X1"], "Grupos de Pesquisa": ["E2", "P2"],
    "Projetos SUAP": ["E2", "P2"],
    "CIPER": ["E2"],
}


def linhas(arq, inicio=None, fim=None, inline=False):
    """Texto da pagina, uma linha por bloco. inline=True: negrito/links nao quebram a linha."""
    bruto = (FONTES / arq).read_text(encoding="utf-8", errors="ignore")
    x = re.sub(r"<script.*?</script>|<style.*?</style>", "", bruto, flags=re.S)
    if inline:
        x = INLINE_RE.sub("", re.sub(r"\s+", " ", x))
    x = html.unescape(re.sub(r"<[^>]+>", "\n", x)).replace("\xa0", " ")
    L = [re.sub(r"\s+", " ", l).strip() for l in x.split("\n")]
    L = [l for l in L if l]
    if inicio:
        idx = [i for i, l in enumerate(L) if l == inicio]
        trilha = [i for i in idx if i and L[i - 1] == "/"]  # titulo logo apos o "voce esta aqui"
        if idx:
            L = L[(trilha[0] if trilha else idx[-1]) + 1:]
    if fim:
        for i, l in enumerate(L):
            if l.startswith(fim):
                L = L[:i]
                break
    return L, html.unescape(bruto).replace("\xa0", " ")


def e_nome(l):
    return bool(NOME_RE.match(l)) and not NAO_NOME.search(l) and len(l) < 60 and "@" not in l


def titulo(nome):
    out = []
    for i, p in enumerate(nome.split()):
        low = p.lower()
        out.append(low if (i and low in PARTICULAS) else low.capitalize())
    return " ".join(out)


def reg(nome, inst, unidade, setor, categoria, fonte, cargo="", titulacao="", areas="", lattes="", programa=""):
    limpo = re.sub(r"^(Dra?|Prof[aª]?)\.?\s+", "", nome).strip(" *")
    if lattes and not lattes.startswith("http"):
        lattes = "https://lattes.cnpq.br/" + lattes
    areas = areas.strip(" .;")
    if len(areas) < 4:
        areas = ""
    return dict(_raw=nome, _email="", nome=limpo, instituicao=inst, unidade=unidade, setores=[setor],
                categoria=categoria, cargo=cargo, titulacao=titulacao, areas=areas, lattes=lattes,
                programas=[programa] if programa else [], fontes=[fonte])


def anexar(bruto, recs):
    """Lattes e e-mail (este so para fundir duplicatas) no trecho entre um nome e o seguinte."""
    cursor, pos = 0, []
    for r in recs:
        i = bruto.find(r["_raw"], cursor)
        pos.append(i)
        if i >= 0:
            cursor = i + len(r["_raw"])
    for k, r in enumerate(recs):
        if pos[k] < 0:
            continue
        fim = next((p for p in pos[k + 1:] if p > pos[k]), pos[k] + 3000)
        seg = bruto[pos[k]: min(fim, pos[k] + 12000)]
        m = LATTES_RE.search(seg)
        if m and not r["lattes"]:
            r["lattes"] = m.group(0).replace("http://", "https://")
        e = EMAIL_RE.search(re.sub(r"<[^>]+>", " ", seg))
        r["_email"] = e.group(0).lower() if e else ""
    return recs


def _celulas(tr):
    return [re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", c))).replace("\xa0", " ").strip()
            for c in re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)]


def cnpq_grupo(arq):
    """Espelho de grupo do Diretorio do CNPq: situacao, area, linhas, pesquisadores e tecnicos.
    Estudantes e egressos sao ignorados (LGPD). Cada tabela vale so na 1.a ocorrencia (as seguintes sao de egressos)."""
    s = re.sub(r"<script.*?</script>", "", arq.read_text(encoding="utf-8", errors="ignore"), flags=re.S)
    txt = [l.strip() for l in html.unescape(re.sub(r"<[^>]+>", "\n", s)).replace("\xa0", " ").split("\n") if l.strip()]

    def depois(rot):
        return next((txt[i + 1] for i, l in enumerate(txt) if l == rot and i + 1 < len(txt)), "")

    tabelas = {}
    for t in re.findall(r"<table[^>]*>(.*?)</table>", s, re.S):
        ths = [re.sub(r"<[^>]+>", "", h).strip() for h in re.findall(r"<th[^>]*>(.*?)</th>", t, re.S)]
        if ths and ths[0] not in tabelas:
            cel = [_celulas(tr) for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", t, re.S)]
            tabelas[ths[0]] = [c for c in cel if c and c[0] and not c[0].startswith("Nenhum")]
    return dict(id=re.search(r"(\d{16})", arq.name).group(1), situacao=depois("Situação do grupo:"),
                area=depois("Área predominante:"),
                linhas=[c[0] for c in tabelas.get("Nome da linha de pesquisa", [])],
                pesquisadores=[(c[0], c[1] if len(c) > 1 else "") for c in tabelas.get("Pesquisadores", [])],
                tecnicos=[(c[0], c[1] if len(c) > 1 else "") for c in tabelas.get("Técnicos", [])])


def ler_csv(arq):
    if not arq.exists():
        return []
    with arq.open(encoding="utf-8-sig", newline="") as fh:
        return [r for r in csv.DictReader(fh, delimiter=";") if r.get("nome")]


def por_marcador(arq, marcadores, inst, unidade, setor, categoria, fonte, maiusculas=False):
    """Paginas no formato 'Professor:' / nome / 'Lattes:' / url / 'Linha de Pesquisa:' / texto."""
    L, bruto = linhas(arq)
    out, i = [], 0
    while i < len(L):
        if L[i] in marcadores and i + 1 < len(L):
            nome = titulo(L[i + 1]) if maiusculas else L[i + 1]
            lat, area, j = "", "", i + 2
            while j < len(L) and L[j] not in marcadores and not L[j].startswith("Admin"):
                if "lattes.cnpq.br" in L[j]:
                    m = re.search(r"(\d{16})", L[j])
                    lat = m.group(1) if m else ""
                if re.match(r"(Linha de Pesquisa|Laborat[oó]rios?):", L[j]) and j + 1 < len(L):
                    area = L[j + 1]
                j += 1
            r = reg(nome, inst, unidade, setor, categoria, fonte, areas=area, lattes=lat)
            r["_raw"] = L[i + 1]
            out.append(r)
            i = j
        else:
            i += 1
    return anexar(bruto, out)


def por_nome_seguido(arq, inst, unidade, setor, categoria, fonte, inicio=None, fim=None,
                     exige=r"@|Lattes", janela=5, area_re=None):
    """Paginas em que o nome vem numa linha e, logo abaixo, e-mail/Lattes/laboratorio."""
    L, bruto = linhas(arq, inicio, fim)
    idx = [i for i, l in enumerate(L) if e_nome(l)]
    out = []
    for k, i in enumerate(idx):
        prox_i = idx[k + 1] if k + 1 < len(idx) else len(L)
        bloco = L[i + 1: min(i + 1 + janela, prox_i)]
        if not any(re.search(exige, b) for b in bloco):
            continue
        if any("Aposentad" in b for b in L[i + 1: prox_i]):
            continue
        area = next((b for b in bloco if area_re and re.match(area_re, b)), "")
        out.append(reg(L[i], inst, unidade, setor, categoria, fonte, areas=area))
    return anexar(bruto, out)


def coletar():
    R = []
    EM, ICEB = "Escola de Minas", "Instituto de Ciências Exatas e Biológicas (ICEB)"
    D, T = "Docente", "Técnico-administrativo"

    # --- UFOP / DEAMB
    f = "https://deamb.ufop.br/pessoas"
    L, bruto = linhas("p_deamb.html", inline=True)
    secao, P = D, []
    for i, l in enumerate(L):
        if l.startswith("Técnic"):
            secao = T
        if re.match(r"^Dra?\. ", l) or (secao == T and e_nome(l)):
            cargo = next((b for b in L[i + 1:i + 4] if b.startswith(("Professor", "Técnic", "Assistente", "Secret"))), "")
            P.append(reg(l, "UFOP", EM, "DEAMB", secao, f, cargo=cargo))
    R += anexar(bruto, P)

    # --- UFOP / DECAT, DEPRO (formato com marcadores)
    R += por_marcador("p_decat.html", {"Professor:", "Professora:"}, "UFOP", EM, "DECAT", D, "https://decat.ufop.br/docentes")
    R += por_marcador("p_decat_tec.html", {"Técnico:", "Técnica:"}, "UFOP", EM, "DECAT", T, "https://decat.ufop.br/técnicos")
    R += por_marcador("p_depro.html", {"Professor:", "Professora:"}, "UFOP", EM, "DEPRO", D, "https://depro.ufop.br/corpo-docente", maiusculas=True)

    # --- UFOP / DECIV
    R += por_nome_seguido("p_deciv.html", "UFOP", EM, "DECIV", D, "https://sites.ufop.br/deciv/docentes", inicio="Docentes", fim="Contato", janela=4)
    L, bruto = linhas("p_deciv_tec.html", "Técnicos Administrativos", "Contato")
    P = []
    for l in L:
        if " - " in l and "@" not in l:
            nome, lab = l.split(" - ", 1)
            P.append(reg(nome, "UFOP", EM, "DECIV", T, "https://sites.ufop.br/deciv/tecnicos-adm", areas=lab))
    R += P

    # --- UFOP / DEGEO
    R += por_nome_seguido("p_degeo.html", "UFOP", EM, "DEGEO", D, "https://degeo.ufop.br/people/equipe/docentes-degeo", inicio="Docentes", fim="DEPARTAMENTO DE GEOLOGIA")
    R += por_nome_seguido("p_degeo_tec.html", "UFOP", EM, "DEGEO", T, "https://degeo.ufop.br/people/equipe/técnicos", inicio="Técnicos", fim="DEPARTAMENTO DE GEOLOGIA")

    # --- UFOP / DEMIN
    f = "https://sites.ufop.br/demin/corpo-docente"
    L, bruto = linhas("p_demin.html", "Corpo Docente", "UFOP", inline=True)
    cargo, P = "", []
    for i, l in enumerate(L[:-1]):
        if l.startswith("Professores "):
            cargo = "Professor " + l.split(" ", 1)[1].lower().rstrip("s")
        if "@" in L[i + 1] and e_nome(l):
            bio = L[i + 2] if i + 2 < len(L) and len(L[i + 2]) > 60 else ""
            bio = re.split(r"(?<=[.!?])\s", bio)[0][:260]
            P.append(reg(l, "UFOP", EM, "DEMIN", D, f, cargo=cargo, areas=bio))
    R += anexar(bruto, P)
    L, _ = linhas("p_demin_tec.html", "RAMAL", "UFOP")
    for i in range(0, len(L) - 1, 3):
        if re.match(rf"^[{MAI}]", L[i]) and not L[i][0].isdigit():
            R.append(reg(L[i], "UFOP", EM, "DEMIN", T, "https://sites.ufop.br/demin/técnicos-administrativos-em-educação", areas=L[i + 1]))

    # --- UFOP / DEBIO
    lab = r"(Laborat|Setor|Herb|Secret)"
    R += por_nome_seguido("p_debio.html", "UFOP", ICEB, "DEBIO", D, "https://debio.ufop.br/docentes", inicio="Docentes", fim="Departamento de Biodiversidade", exige=lab, janela=2, area_re=lab)
    R += por_nome_seguido("p_debio_tec.html", "UFOP", ICEB, "DEBIO", T, "https://debio.ufop.br/corpo_tecnico", inicio="Corpo Técnico", fim="Departamento de Biodiversidade", exige=lab, janela=2, area_re=lab)

    # --- UFOP / DEMAT
    f = "https://demat.ufop.br/professores"
    L, bruto = linhas("p_demat.html", "Professores", "Participação em Colegiado")
    tit = r"^(Mestr|Doutor|Especialista|Graduad|Bacharel|Licenciad|P[oó]s-Doutor)"
    ini = [i for i in range(len(L) - 1) if e_nome(L[i]) and re.match(tit, L[i + 1])]
    P = []
    for k, i in enumerate(ini):
        fim_i = ini[k + 1] if k + 1 < len(ini) else len(L)
        bloco = L[i + 2: fim_i]
        area = ""
        for j, b in enumerate(bloco):
            if b.startswith("Áreas de interesse") and j + 1 < len(bloco):
                area = " ".join(bloco[j + 1:])
        P.append(reg(L[i], "UFOP", ICEB, "DEMAT", D, f, titulacao=L[i + 1], areas=area[:260]))
    R += anexar(bruto, P)

    # --- UFOP / REDEMAT (pos-graduacao em Engenharia de Materiais)
    f = "https://redemat.ufop.br/docentes-1"
    L, bruto = linhas("p_redemat.html")
    P = []
    for i, l in enumerate(L[:-3]):
        if L[i + 1] in ("Permanente", "Colaborador") and "@" in L[i + 2] and e_nome(l):
            P.append(reg(l, "UFOP", "Pós-graduação (UFOP/UEMG)", "REDEMAT", D, f, cargo="Docente " + L[i + 1].lower(),
                         areas=L[i + 3] if "@" not in L[i + 3] else "", programa="REDEMAT"))
    for r in anexar(bruto, P):
        if not r["_email"].endswith("ufop.edu.br"):  # a REDEMAT e uma rede UFOP/UEMG
            r["instituicao"], r["unidade"] = "Parceiro externo", "REDEMAT (rede UFOP/UEMG)"
        R.append(r)

    # --- UFOP / ProAmb (pos-graduacao em Engenharia Ambiental)
    f = "https://proamb.ufop.br/docentes"
    L, bruto = linhas("p_proamb.html", inline=True)
    P = []
    for i, l in enumerate(L[:-4]):
        if re.match(r"^Dra?\. ", l) and "@" in " ".join(L[i + 1:i + 4]):
            tit_ = L[i + 1] if "@" not in L[i + 1] else ""
            k = next(j for j in range(i + 1, i + 4) if "@" in L[j])
            cred = L[k + 1] if k + 1 < len(L) else ""
            lin = L[k + 2] if k + 2 < len(L) and not re.match(r"^(Dra?\. |-$)", L[k + 2]) else ""
            P.append(reg(l, "UFOP", "Pós-graduação", "ProAmb", D, f,
                         cargo="Docente permanente" if "permanente" in cred.lower() else "Docente colaborador",
                         titulacao=tit_, areas=lin[:300], programa="ProAmb"))
    R += anexar(bruto, P)

    # --- IFMG-OP / Grupos de pesquisa (lideres) e DPIPG
    f = "https://ouropreto.ifmg.edu.br/ouropreto/pesquisa/grupos-de-pesquisa"
    L, _ = linhas("ifmg_grupos.html", "Grupos de Pesquisa", "Voltar para o topo")
    grupos, atual = [], None
    for i, l in enumerate(L):
        m = re.match(r"^(\d+)\)\s*(.+)$", l)
        if m:
            nome_g = m.group(2)
            if i + 1 < len(L) and not L[i + 1].startswith("Líder"):
                nome_g += " " + L[i + 1]
            atual = dict(nome=nome_g, lideres=[], dgp="", instituicao="IFMG", fonte=f)
            grupos.append(atual)
        elif l.startswith("Líder") and atual:
            nomes = re.sub(r"Link na Plataforma.*$", "", l.split(":", 1)[1]).strip()
            atual["lideres"] = [n.strip() for n in re.split(r"\s+e\s+", nomes)]
        elif l.startswith("dgp.cnpq.br") and atual:
            atual["dgp"] = "http://" + l
    for g in grupos:
        for n in g["lideres"][:1]:  # 1.o lider; colider de outra instituicao fica so na lista de grupos
            R.append(reg(n, "IFMG", "Campus Ouro Preto", "Grupos de Pesquisa", "Docente", f,
                         cargo="Líder de grupo de pesquisa (CNPq)", areas=g["nome"]))
    f = "https://ouropreto.ifmg.edu.br/ouropreto/pesquisa/equipe-da-dpipg"
    L, _ = linhas("ifmg_dpipg.html", "Equipe da DPIPG", "Voltar para o topo")
    secao, papel = "", ""
    for n, l in enumerate(L):
        if n and L[n - 1] == "por":  # assinatura de quem publicou a pagina
            continue
        if l.startswith(("Diretoria", "Seção")):
            secao, papel = l, "Direção" if l.startswith("Diretoria") else ""
        elif l.startswith("Chefia"):
            papel = "Chefia"
        elif l.startswith("Técnico"):
            papel = "Técnico-administrativo"
        elif e_nome(l):
            R.append(reg(l, "IFMG", "Campus Ouro Preto", "DPIPG", "Gestão de pesquisa e inovação", f,
                         cargo=(papel + " — " + secao).strip(" —"), areas=secao))

    # --- IFMG-OP / membros dos grupos (espelhos CNPq) e projetos do SUAP, coleta de 17/11/2026.
    # So entra quem o SUAP confirma como servidor lotado no Campus Ouro Preto (externos e estudantes ficam fora).
    lot = {}
    for r in ler_csv(SUAP_LOTACAO):  # vale o nome do SUAP e o da fonte (CNPq pode trazer o nome de solteira)
        lot[chave(r["nome"])] = lot[chave(r.get("nome_fonte") or r["nome"])] = r

    def ifmg(nome, setor, fonte, **kw):
        s = lot.get(chave(nome))
        if not s:
            return None
        r = reg(s.get("nome_fonte") or nome, "IFMG", "Campus Ouro Preto", setor, s["categoria"], fonte, **kw)
        r["coleta"] = COLETA_IFMG
        R.append(r)
        return r

    for g in grupos:
        m = re.search(r"(\d{16})", g["dgp"])
        arq = FONTES / "cnpq" / f"grupo_{m.group(1)}.html" if m else None
        if not arq or not arq.exists():
            continue
        c = cnpq_grupo(arq)
        g.update(area=c["area"], situacao=c["situacao"], linhas=c["linhas"], coleta=COLETA_IFMG)
        # a pagina do campus abrevia o lider ("Diego Oliveira"); o espelho traz o nome completo
        for n in g["lideres"]:
            kn = chave(n).split()
            cheio = next((p for p, _ in c["pesquisadores"]
                          if chave(p).split()[0] == kn[0] and chave(p).split()[-1] == kn[-1]), None)
            if cheio and chave(cheio) != chave(n):
                for r in R:
                    if r["_raw"] == n and r["setores"] == ["Grupos de Pesquisa"]:
                        r["nome"] = cheio
                g["lideres"] = [cheio if x == n else x for x in g["lideres"]]
        lideres = {chave(n) for n in g["lideres"]}
        for nome, tit in c["pesquisadores"] + c["tecnicos"]:
            papel = "Líder" if chave(nome) in lideres else ("Técnico(a)" if (nome, tit) in c["tecnicos"] else "Pesquisador(a)")
            ifmg(nome, "Grupos de Pesquisa", g["dgp"], titulacao=tit,
                 cargo=f"{papel} de grupo de pesquisa (CNPq)", areas=f"{g['nome']} ({c['area']})")
    for p in ler_csv(SUAP_PROJETOS):
        tipo = p.get("tipo") or "Pesquisa"
        m = re.search(r"(\d+)\s*/\s*(\d{4})", p["edital"])  # rotulo curto: o cartao imprime a fonte sem quebra
        ifmg(p["nome"], "Projetos SUAP", f"SUAP IFMG — Edital {int(m.group(1))}/{m.group(2)}" if m else "SUAP IFMG",
             cargo=f"{p['papel']} de projeto de {tipo.lower()} (SUAP)",
             areas=f"Projeto de {tipo.lower()} ({p['ano']}): {p['projeto']}")

    # --- Organizacao tecnica do CIPER (Dossie Executivo, fev/2026; nomes completos nos creditos do video)
    f = "Dossiê Executivo do CIPER (fev. 2026)"
    R.append(reg("Ernani Carlos de Araujo", "UFOP", "Escola de Minas", "CIPER", "Docente", f, cargo="Organização técnica do CIPER"))
    R.append(reg("Julio Cesar Silva Azevedo", "IFMG", "Campus Ouro Preto", "CIPER", "Docente", f, cargo="Organização técnica do CIPER"))
    return R, grupos


def chave(nome):
    s = unicodedata.normalize("NFD", nome.lower())
    return re.sub(r"[^a-z ]", "", "".join(c for c in s if unicodedata.category(c) != "Mn")).strip()


def fundir(R):
    """Uma pessoa = um registro. Junta por nome; ou por e-mail, se 1.o e ultimo nomes coincidem."""
    banco, por_email = {}, {}
    for r in R:
        if len(r["nome"].split()) < 2:
            continue
        k = chave(r["nome"])
        b = banco.get(k)
        if b is None and r["_email"] and r["_email"] in por_email:
            c = por_email[r["_email"]]
            kc, kr = chave(c["nome"]).split(), k.split()
            if kc[0] == kr[0] and kc[-1] == kr[-1]:
                b = c
                if len(r["nome"]) > len(b["nome"]):
                    b["nome"] = r["nome"]
        if b is None:
            banco[k] = r
            if r["_email"]:
                por_email.setdefault(r["_email"], r)
            continue
        for campo in ("setores", "programas", "fontes"):
            for v in r[campo]:
                if v not in b[campo]:
                    b[campo].append(v)
        for campo in ("cargo", "titulacao", "lattes"):
            b[campo] = b[campo] or r[campo]
        if r.get("coleta", "") > b.get("coleta", ""):
            b["coleta"] = r["coleta"]
        if r["areas"] and r["areas"] not in b["areas"]:
            if b["instituicao"] == "IFMG":  # "Grupo X" + "Grupo X (area)" -> fica so a forma mais completa
                b["areas"] = "; ".join([x for x in b["areas"].split("; ") if x and x not in r["areas"]] + [r["areas"]])
            else:
                b["areas"] = (b["areas"] + "; " + r["areas"]).strip("; ")
        if r["categoria"] == "Docente":
            b["categoria"] = "Docente"
    out = list(banco.values())
    rep = {u for u, n in Counter(b["lattes"] for b in out if b["lattes"]).items() if n > 1}
    for b in out:
        if b["lattes"] in rep:  # mesmo link em duas pessoas = associacao duvidosa; melhor vazio
            b["lattes"] = ""
        b.pop("_raw", None)
        b.pop("_email", None)
    return out


def adesoes():
    """Cadastros recebidos pelo formulario (dados/adesoes.csv) - autodeclaracao do Dossie 4.2."""
    arq = DADOS / "adesoes.csv"
    if not arq.exists():
        return {}
    out = {}
    with arq.open(encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh, delimiter=";"):
            if row.get("nome"):
                out[chave(row["nome"])] = row
    return out


COMPLETO = FONTES / "completo"
# Pesquisadores colaboradores de outras instituicoes que aparecem no banco publico (Regimento v2, art. 9o).
COLABORADORES = {"ernani carlos de araujo": "Professor da UFOP, pesquisador colaborador"}
COLS = ["id", "nome", "instituicao", "unidade", "setores", "categoria", "cargo", "titulacao", "areas",
        "lattes", "programas", "afinidade_unidade", "eixos_declarados", "orienta_ic", "adesao", "fontes", "coleta"]


def escrever(pasta, banco, grupos):
    saida = dict(gerado_em=max(b["coleta"] for b in banco), total=len(banco), pessoas=banco, grupos=grupos)
    pasta.mkdir(parents=True, exist_ok=True)
    (pasta / "capital-humano.json").write_text(json.dumps(saida, ensure_ascii=False, indent=1), encoding="utf-8")
    (pasta / "capital-humano.js").write_text("window.CIPER_BANCO = " + json.dumps(saida, ensure_ascii=False) + ";\n", encoding="utf-8")
    with (pasta / "capital-humano.csv").open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.writer(fh, delimiter=";")
        w.writerow(COLS)
        for b in banco:
            w.writerow([" | ".join(b[c]) if isinstance(b[c], list) else b[c] for c in COLS])


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    R, grupos = coletar()
    banco = fundir(R)
    ad = adesoes()
    for b in banco:
        eixos = []
        for s in b["setores"]:
            for e in AFINIDADE.get(s, []):
                if e not in eixos:
                    eixos.append(e)
        b["afinidade_unidade"] = eixos
        a = ad.pop(chave(b["nome"]), None)
        b["eixos_declarados"] = [e for e in (a or {}).get("eixos", "").replace(",", " ").split() if e]
        b["orienta_ic"] = (a or {}).get("orienta_ic", "")
        b["adesao"] = "Adesão registrada" if a else "A consultar"
        if a:
            for campo in ("lattes", "areas"):
                if a.get(campo):
                    b[campo] = a[campo]
        b["coleta"] = b.get("coleta") or COLETA
        if b["instituicao"] == "IFMG" and len(b["areas"]) > 600:  # muitos projetos: corta no ultimo item inteiro
            b["areas"] = b["areas"][:600].rsplit("; ", 1)[0] + " …"
    for a in ad.values():  # quem se cadastrou e nao estava nas fontes publicas
        banco.append(dict(nome=a["nome"], instituicao=a.get("instituicao", ""), unidade=a.get("unidade", ""),
                          setores=[a.get("setor", "")], categoria=a.get("categoria", ""), cargo=a.get("cargo", ""),
                          titulacao=a.get("titulacao", ""), areas=a.get("areas", ""), lattes=a.get("lattes", ""),
                          programas=[], fontes=["Formulário de adesão do CIPER"], afinidade_unidade=[],
                          eixos_declarados=a.get("eixos", "").replace(",", " ").split(),
                          orienta_ic=a.get("orienta_ic", ""), adesao="Adesão registrada", coleta=COLETA))
    banco.sort(key=lambda b: chave(b["nome"]))
    for i, b in enumerate(banco, 1):
        b["id"] = f"CH-{i:04d}"

    # Banco COMPLETO (todas as instituicoes): fica em _fontes/completo/, fora do git e do site,
    # para a etapa dos convenios (PRE-site-ciper-so-ifmg-ocultar-parcerias-2026-11-20).
    escrever(COMPLETO, banco, grupos)
    # Banco PUBLICO: ate o CONSUP o CIPER e so do IFMG; entram o IFMG e os pesquisadores colaboradores.
    publico = []
    for b in banco:
        if b["instituicao"] == "IFMG":
            publico.append(b)
        elif chave(b["nome"]) in COLABORADORES:
            publico.append(dict(b, instituicao="Colaborador", unidade=COLABORADORES[chave(b["nome"])]))
    escrever(DADOS, publico, grupos)

    print("TOTAL (completo)", len(banco), "| publico", len(publico))
    print("publico por instituicao", dict(Counter(b["instituicao"] for b in publico)))
    print("por instituicao", dict(Counter(b["instituicao"] for b in banco)))
    print("por categoria", dict(Counter(b["categoria"] for b in banco)))
    print("por setor", dict(Counter(s for b in banco for s in b["setores"])))
    print("com Lattes", sum(1 for b in banco if b["lattes"]), "| com area", sum(1 for b in banco if b["areas"]))
    print("grupos IFMG", len(grupos))


if __name__ == "__main__":
    main()
