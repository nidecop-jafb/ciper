// CIPER — Banco de Capital Humano: busca, filtros, paginação, exportação e ficha de adesão
(function () {
  var B = window.CIPER_BANCO || { pessoas: [], grupos: [] };
  var P = B.pessoas, POR_PAGINA = 25, pagina = 1, filtrados = P;
  var $ = function (id) { return document.getElementById(id); };
  var EIXOS = {
    P1: 'Tecnologias limpas e bioinovação (patentes e investimentos)',
    P2: 'Excelência científica e parcerias internacionais',
    P3: 'Bioeconomia, economia circular e biocombustíveis',
    P4: 'Valorização de minerais críticos (nióbio, lítio e terras raras)',
    P5: 'Potenciais hídricos e hidrogênio verde (H2V)',
    P6: 'Energias solar/eólica e transmissão disruptiva (sem fio)',
    P7: 'Comunicação interatômica e pesquisa de fronteira',
    E1: 'Capacitação técnica e científica (talentos STEM)',
    E2: 'Integração acadêmica UFOP/IFMG/FG',
    E3: 'Espaços de experimentação e laboratórios interativos',
    E4: 'Capacitação de professores e alunos da Educação Básica',
    X1: 'Diversificação econômica e incubação de startups',
    X2: 'Turismo científico internacional e planetário',
    X3: 'Democratização do conhecimento (museu interativo)',
    X4: 'Sustentabilidade e acessibilidade arquitetônica (LEED)'
  };
  var esc = function (s) { return String(s || '').replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); };
  var limpa = function (s) { return String(s || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, ''); };
  var eixosDe = function (p) { return p.eixos_declarados.length ? p.eixos_declarados : p.afinidade_unidade; };
  var conta = function (lista, chave) {
    var c = {};
    lista.forEach(function (p) { [].concat(chave(p)).forEach(function (k) { if (k) c[k] = (c[k] || 0) + 1; }); });
    return Object.keys(c).map(function (k) { return [k, c[k]]; }).sort(function (a, b) { return b[1] - a[1]; });
  };
  P.forEach(function (p) { p._busca = limpa([p.nome, p.areas, p.cargo, p.titulacao, p.unidade, p.setores.join(' '), p.instituicao].join(' ')); });

  // contadores do topo
  $('contadores').innerHTML = [
    [P.length, 'pessoas mapeadas'],
    [P.filter(function (p) { return p.categoria === 'Docente'; }).length, 'docentes e pesquisadores'],
    [P.filter(function (p) { return p.categoria !== 'Docente'; }).length, 'técnicos e gestores'],
    [conta(P, function (p) { return p.setores; }).length, 'unidades e programas'],
    [P.filter(function (p) { return p.lattes; }).length, 'com Currículo Lattes'],
    [P.filter(function (p) { return p.adesao === 'Adesão registrada'; }).length, 'adesões registradas']
  ].map(function (i) { return '<div class="num"><b>' + i[0] + '</b><span>' + i[1] + '</span></div>'; }).join('');

  // opções dos filtros
  function opcoes(sel, pares) { pares.forEach(function (o) { var e = document.createElement('option'); e.value = o[0]; e.textContent = o[1]; sel.appendChild(e); }); }
  opcoes($('f-inst'), conta(P, function (p) { return p.instituicao; }).map(function (x) { return [x[0], x[0] + ' (' + x[1] + ')']; }));
  opcoes($('f-setor'), conta(P, function (p) { return p.setores; }).sort(function (a, b) { return a[0].localeCompare(b[0]); }).map(function (x) { return [x[0], x[0] + ' (' + x[1] + ')']; }));
  opcoes($('f-cat'), conta(P, function (p) { return p.categoria; }).map(function (x) { return [x[0], x[0] + ' (' + x[1] + ')']; }));
  opcoes($('f-eixo'), Object.keys(EIXOS).map(function (k) { return [k, k + ' · ' + EIXOS[k]]; }));

  function cartao(p) {
    var ex = eixosDe(p).map(function (e) { return '<span class="chip ' + e[0] + '" title="' + esc(EIXOS[e]) + (p.eixos_declarados.length ? '' : ' — afinidade da unidade') + '">' + e + '</span>'; }).join('');
    var fonte = p.fontes.filter(function (f) { return /^https?:/.test(f); })[0];
    return '<article class="pessoa">' +
      '<div><h3>' + esc(p.nome) + '</h3>' +
      '<div class="meta"><span class="chip ' + esc(p.instituicao) + '">' + esc(p.instituicao) + '</span>' + esc(p.setores.join(' · ')) + ' — ' + esc(p.unidade) + '</div>' +
      '<div class="meta">' + esc([p.categoria, p.cargo].filter(Boolean).join(' · ')) + '</div></div>' +
      '<div class="area">' + (p.titulacao ? '<div class="meta">' + esc(p.titulacao) + '</div>' : '') + esc(p.areas) + '<div style="margin-top:6px">' + ex + '</div></div>' +
      '<div class="links"><span class="chip ' + (p.adesao === 'Adesão registrada' ? 'ok' : 'pend') + '">' + esc(p.adesao) + '</span>' +
      (p.lattes ? '<a href="' + esc(p.lattes) + '" target="_blank" rel="noopener">Currículo Lattes ↗</a>' : '') +
      (fonte ? '<a href="' + esc(fonte) + '" target="_blank" rel="noopener">Página oficial ↗</a>' : '<span class="meta">' + esc(p.fontes[0]) + '</span>') +
      '<span class="meta">' + esc(p.id) + '</span></div></article>';
  }

  function aplicar() {
    var q = limpa($('q').value).split(/\s+/).filter(Boolean);
    var inst = $('f-inst').value, setor = $('f-setor').value, cat = $('f-cat').value, eixo = $('f-eixo').value;
    filtrados = P.filter(function (p) {
      return q.every(function (t) { return p._busca.indexOf(t) >= 0; }) &&
        (!inst || p.instituicao === inst) && (!setor || p.setores.indexOf(setor) >= 0) &&
        (!cat || p.categoria === cat) && (!eixo || eixosDe(p).indexOf(eixo) >= 0) &&
        (!$('f-lattes').checked || p.lattes) && (!$('f-adesao').checked || p.adesao === 'Adesão registrada');
    });
    pagina = 1; desenhar();
  }

  function desenhar() {
    var n = filtrados.length, paginas = Math.max(1, Math.ceil(n / POR_PAGINA));
    pagina = Math.min(pagina, paginas);
    var fatia = filtrados.slice((pagina - 1) * POR_PAGINA, pagina * POR_PAGINA);
    $('lista').innerHTML = n ? fatia.map(cartao).join('') : '<div class="vazio">Nenhuma pessoa encontrada com esses filtros.</div>';
    $('total').textContent = n + (n === 1 ? ' pessoa' : ' pessoas');
    $('pagina').textContent = 'Página ' + pagina + ' de ' + paginas;
    $('ant').disabled = pagina <= 1; $('prox').disabled = pagina >= paginas;
  }

  ['q', 'f-inst', 'f-setor', 'f-cat', 'f-eixo', 'f-lattes', 'f-adesao'].forEach(function (id) { $(id).addEventListener('input', aplicar); });
  $('ant').addEventListener('click', function () { pagina--; desenhar(); $('banco').scrollIntoView(); });
  $('prox').addEventListener('click', function () { pagina++; desenhar(); $('banco').scrollIntoView(); });
  $('limpar').addEventListener('click', function () {
    ['q', 'f-inst', 'f-setor', 'f-cat', 'f-eixo'].forEach(function (id) { $(id).value = ''; });
    $('f-lattes').checked = $('f-adesao').checked = false; aplicar();
  });

  function baixar(nome, texto) {
    var a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob(['﻿' + texto], { type: 'text/csv;charset=utf-8' }));
    a.download = nome; document.body.appendChild(a); a.click(); a.remove();
  }
  var celula = function (v) { return '"' + String(Array.isArray(v) ? v.join(' | ') : (v || '')).replace(/"/g, '""') + '"'; };
  $('exportar').addEventListener('click', function () {
    var cols = ['id', 'nome', 'instituicao', 'unidade', 'setores', 'categoria', 'cargo', 'titulacao', 'areas', 'lattes', 'afinidade_unidade', 'eixos_declarados', 'adesao', 'fontes'];
    baixar('ciper-capital-humano-selecao.csv', [cols.join(';')].concat(filtrados.map(function (p) { return cols.map(function (c) { return celula(p[c]); }).join(';'); })).join('\r\n'));
  });

  // panorama
  function barras(alvo, dados, rotulo) {
    var max = dados.length ? dados[0][1] : 1;
    $(alvo).innerHTML = dados.map(function (d) {
      return '<div class="barra"><span title="' + esc(rotulo ? rotulo(d[0]) : d[0]) + '">' + esc(d[0]) + '</span><i style="width:' + Math.max(3, 100 * d[1] / max) + '%"></i><span>' + d[1] + '</span></div>';
    }).join('');
  }
  barras('b-setor', conta(P, function (p) { return p.setores; }));
  barras('b-eixo', conta(P, eixosDe), function (k) { return EIXOS[k]; });

  // grupos de pesquisa
  $('lista-grupos').innerHTML = B.grupos.map(function (g) {
    return '<div class="cartao"><h3 style="font-size:1.05rem">' + esc(g.nome) + '</h3><p class="meta" style="font-size:.9rem">Liderança: ' + esc(g.lideres.join(' e ')) + '</p>' +
      (g.dgp ? '<p><a href="' + esc(g.dgp) + '" target="_blank" rel="noopener">Espelho no Diretório do CNPq ↗</a></p>' : '') + '</div>';
  }).join('');

  // ficha de adesão (Dossiê Executivo, item 4.2)
  $('a-eixos').innerHTML = Object.keys(EIXOS).map(function (k) {
    return '<label><input type="checkbox" value="' + k + '"> <span><strong>' + k + '</strong> — ' + esc(EIXOS[k]) + '</span></label>';
  }).join('');
  $('nomes').innerHTML = P.map(function (p) { return '<option value="' + esc(p.nome) + '">'; }).join('');
  $('a-nome').addEventListener('change', function () {
    var p = P.filter(function (x) { return x.nome === $('a-nome').value; })[0];
    if (!p) return;
    if (['UFOP', 'IFMG'].indexOf(p.instituicao) >= 0) $('a-inst').value = p.instituicao;
    $('a-setor').value = p.setores.join(' / ');
    if (p.lattes) $('a-lattes').value = p.lattes;
    if (p.areas && !$('a-areas').value) $('a-areas').value = p.areas;
  });
  $('ficha').addEventListener('submit', function (e) {
    e.preventDefault();
    var eixos = [].slice.call(document.querySelectorAll('#a-eixos input:checked')).map(function (c) { return c.value; });
    var cols = ['nome', 'citacao', 'lattes', 'areas', 'instituicao', 'unidade', 'setor', 'categoria', 'cargo', 'titulacao', 'eixos', 'orienta_ic', 'ciente', 'data'];
    var v = {
      nome: $('a-nome').value.trim(), citacao: $('a-cit').value.trim(), lattes: $('a-lattes').value.trim(), areas: $('a-areas').value.trim(),
      instituicao: $('a-inst').value, unidade: '', setor: $('a-setor').value.trim(), categoria: $('a-cat').value, cargo: '', titulacao: '',
      eixos: eixos.join(' '), orienta_ic: $('a-ic').value, ciente: 'Sim', data: new Date().toISOString().slice(0, 10)
    };
    baixar('adesao-ciper-' + limpa(v.nome).replace(/[^a-z]+/g, '-') + '.csv', cols.join(';') + '\r\n' + cols.map(function (c) { return celula(v[c]); }).join(';'));
    $('a-ok').style.display = 'block';
  });

  // menu no celular
  var botao = $('abre-menu'), menu = $('menu');
  botao.addEventListener('click', function () { botao.setAttribute('aria-expanded', menu.classList.toggle('aberto')); });
  menu.addEventListener('click', function (e) { if (e.target.tagName === 'A') menu.classList.remove('aberto'); });

  aplicar();
})();
