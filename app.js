/* Loja de Peças - lógica do frontend.
   Fala com o backend Python (app.py) pelos endpoints /api/*. */

const $ = (id) => document.getElementById(id);
const BRL = (valor) =>
  valor.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });

let catalogo = [];
let carrinho = {}; // produto -> quantidade
let cliente = null; // { nome } ou null
let nomeDigitado = '';

async function carregarCatalogo() {
  const resposta = await fetch('/api/catalogo');
  const dados = await resposta.json();
  catalogo = dados.catalogo;
  renderizarCatalogo();
  renderizarCarrinho();
}

function renderizarCatalogo() {
  const grade = $('grade-produtos');
  grade.innerHTML = '';
  for (const item of catalogo) {
    const esgotado = item.estoque <= 0;
    const card = document.createElement('article');
    card.className = 'produto';
    card.innerHTML = `
      <h3>${item.produto}</h3>
      <p class="preco">${BRL(item.preço)}</p>
      <p class="estoque ${esgotado ? 'esgotado' : ''}">
        ${esgotado ? 'Esgotado' : `${item.estoque} em estoque`}
      </p>
      <div class="adicionar">
        <input type="number" min="1" max="${item.estoque}" value="1"
               aria-label="Quantidade de ${item.produto}" ${esgotado ? 'disabled' : ''}>
        <button type="button" ${esgotado ? 'disabled' : ''}>Adicionar</button>
      </div>`;
    const [input, botao] = [card.querySelector('input'), card.querySelector('button')];
    botao.addEventListener('click', () => {
      const quantidade = parseInt(input.value, 10);
      if (!quantidade || quantidade <= 0) {
        alert('Informe uma quantidade maior que zero.');
        return;
      }
      const jaNoCarrinho = carrinho[item.produto] || 0;
      if (quantidade + jaNoCarrinho > item.estoque) {
        alert(`Só temos ${item.estoque} unidade(s) de ${item.produto} em estoque.`);
        return;
      }
      carrinho[item.produto] = jaNoCarrinho + quantidade;
      renderizarCarrinho();
    });
    grade.appendChild(card);
  }
}

function totais() {
  let subtotal = 0;
  for (const [produto, quantidade] of Object.entries(carrinho)) {
    const item = catalogo.find((p) => p.produto === produto);
    if (item) subtotal += item.preço * quantidade;
  }
  const pagamento = document.querySelector('input[name="pagamento"]:checked')?.value;
  const desconto =
    pagamento && ['pix', 'dinheiro'].includes(pagamento) && subtotal >= 300
      ? subtotal * 0.05
      : 0;
  return { subtotal, desconto, total: subtotal - desconto };
}

function renderizarCarrinho() {
  const lista = $('itens-carrinho');
  lista.innerHTML = '';
  const produtos = Object.keys(carrinho);
  if (!produtos.length) {
    lista.innerHTML = '<li class="vazio">Seu carrinho está vazio.</li>';
  }
  for (const produto of produtos) {
    const item = catalogo.find((p) => p.produto === produto);
    const li = document.createElement('li');
    li.innerHTML = `<span>${carrinho[produto]} x ${produto}</span>
      <span>${BRL((item?.preço || 0) * carrinho[produto])}</span>`;
    const remover = document.createElement('button');
    remover.type = 'button';
    remover.textContent = 'Remover';
    remover.addEventListener('click', () => {
      delete carrinho[produto];
      renderizarCarrinho();
    });
    li.appendChild(remover);
    lista.appendChild(li);
  }

  const { subtotal, desconto, total } = totais();
  $('subtotal').textContent = BRL(subtotal);
  $('desconto').textContent = `- ${BRL(desconto)}`;
  $('linha-desconto').classList.toggle('escondido', desconto <= 0);
  $('total').textContent = BRL(total);
  $('botao-finalizar').disabled = !produtos.length || !nomeDigitado.trim();
}

async function entrar() {
  nomeDigitado = $('nome').value.trim();
  const msg = $('mensagem-cliente');
  if (!nomeDigitado) { msg.textContent = 'Digite seu nome para continuar.'; return; }
  const resposta = await fetch('/api/cliente', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ nome: nomeDigitado }),
  });
  const dados = await resposta.json();
  cliente = dados.cliente;
  if (cliente) {
    msg.textContent = `Olá, ${cliente.nome}!`;
    $('botao-cadastrar').classList.add('escondido');
  } else {
    msg.textContent = 'Você não está cadastrado em nosso sistema.';
    $('botao-cadastrar').classList.remove('escondido');
  }
  renderizarCarrinho();
}

async function cadastrar() {
  const resposta = await fetch('/api/cadastrar', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ nome: nomeDigitado }),
  });
  const dados = await resposta.json();
  if (!dados.ok) { $('mensagem-cliente').textContent = dados.erro; return; }
  cliente = dados.cliente;
  $('mensagem-cliente').textContent =
    `Cadastro realizado com sucesso! Bem-vindo(a), ${cliente.nome}!`;
  $('botao-cadastrar').classList.add('escondido');
  renderizarCarrinho();
}

async function finalizar() {
  $('mensagem-erro').textContent = '';
  const pagamento = document.querySelector('input[name="pagamento"]:checked')?.value;
  if (!pagamento) {
    $('mensagem-erro').textContent = 'Escolha uma forma de pagamento.';
    return;
  }
  const resposta = await fetch('/api/finalizar', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      nome: nomeDigitado,
      pagamento,
      carrinho: Object.entries(carrinho).map(([produto, quantidade]) => ({ produto, quantidade })),
    }),
  });
  const dados = await resposta.json();
  if (!dados.ok) { $('mensagem-erro').textContent = dados.erro; return; }

  // Recibo
  $('recibo-cliente').textContent = `Cliente: ${dados.cliente}`;
  $('recibo-itens').innerHTML = dados.itens
    .map((i) => `<li><span>${i.quantidade} x ${i.produto}</span><span>${BRL(i.preço_total)}</span></li>`)
    .join('');
  $('recibo-subtotal').textContent = BRL(dados.subtotal);
  $('recibo-desconto').textContent = `- ${BRL(dados.desconto)}`;
  $('recibo-linha-desconto').classList.toggle('escondido', dados.desconto <= 0);
  $('recibo-total').textContent = BRL(dados.total);
  $('recibo-pagamento').textContent = dados.pagamento;
  $('recibo').classList.remove('escondido');
  $('recibo').scrollIntoView({ behavior: 'smooth' });

  // Atualiza estoque na tela e limpa o carrinho.
  catalogo = dados.catalogo;
  carrinho = {};
  renderizarCatalogo();
  renderizarCarrinho();
}

$('botao-entrar').addEventListener('click', entrar);
$('nome').addEventListener('change', entrar);
$('botao-cadastrar').addEventListener('click', cadastrar);
$('botao-finalizar').addEventListener('click', finalizar);
$('botao-nova-compra').addEventListener('click', () => {
  $('recibo').classList.add('escondido');
  window.scrollTo({ top: 0, behavior: 'smooth' });
});
document.querySelectorAll('input[name="pagamento"]').forEach((radio) =>
  radio.addEventListener('change', renderizarCarrinho));

carregarCatalogo();
