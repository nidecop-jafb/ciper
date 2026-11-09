// CIPER — comportamento da página inicial (menu, galeria, vídeo, resumo do banco)
(function () {
  var botao = document.getElementById('abre-menu'), menu = document.getElementById('menu');
  if (botao) {
    botao.addEventListener('click', function () {
      var aberto = menu.classList.toggle('aberto');
      botao.setAttribute('aria-expanded', aberto);
    });
    menu.addEventListener('click', function (e) { if (e.target.tagName === 'A') menu.classList.remove('aberto'); });
  }

  // Galeria: clique amplia; clique ou Esc fecha
  var luz = document.getElementById('luz');
  if (luz) {
    document.querySelectorAll('#galeria figure').forEach(function (f) {
      f.addEventListener('click', function () {
        luz.querySelector('img').src = f.querySelector('img').src;
        luz.querySelector('img').alt = f.querySelector('img').alt;
        luz.querySelector('p').textContent = f.querySelector('figcaption').textContent;
        luz.classList.add('on');
      });
    });
    luz.addEventListener('click', function () { luz.classList.remove('on'); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') luz.classList.remove('on'); });
  }

  // Vídeo: troca de idioma
  var filme = document.getElementById('filme');
  document.querySelectorAll('.abas button').forEach(function (b) {
    b.addEventListener('click', function () {
      document.querySelectorAll('.abas button').forEach(function (x) { x.classList.remove('on'); });
      b.classList.add('on');
      filme.pause(); filme.src = b.dataset.src; filme.load();
    });
  });

  // Resumo do banco de capital humano
  var alvo = document.getElementById('resumo-banco'), B = window.CIPER_BANCO;
  if (alvo && B) {
    var p = B.pessoas, conta = function (f) { return p.filter(f).length; };
    var setores = {}; p.forEach(function (x) { x.setores.forEach(function (s) { setores[s] = 1; }); });
    var itens = [
      [p.length, 'pessoas mapeadas'],
      [conta(function (x) { return x.categoria === 'Docente'; }), 'docentes e pesquisadores'],
      [conta(function (x) { return x.categoria !== 'Docente'; }), 'técnicos e gestores'],
      [Object.keys(setores).length, 'unidades e programas'],
      [conta(function (x) { return x.lattes; }), 'com Currículo Lattes vinculado'],
      [B.grupos.length, 'grupos de pesquisa do IFMG-OP']
    ];
    alvo.innerHTML = itens.map(function (i) { return '<div class="num"><b>' + i[0] + '</b><span>' + i[1] + '</span></div>'; }).join('');
  }
})();
