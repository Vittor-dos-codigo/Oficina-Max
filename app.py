"""Loja de Peças - backend em Python (só biblioteca padrão).

Sem banco de dados e sem dependências para instalar: tudo fica em memória
e é resetado quando o servidor é reiniciado. É um projeto de teste.

Para rodar:
    python3 app.py

Depois abra no navegador:
    http://localhost:8000

Endpoints:
    GET  /                -> página da loja (index.html)
    GET  /style.css       -> estilos
    GET  /app.js          -> lógica do frontend
    GET  /api/catalogo    -> produtos, preços e estoque atual
    POST /api/cliente     -> {"nome": "..."} procura o cliente cadastrado
    POST /api/cadastrar   -> {"nome": "..."} cadastra o cliente
    POST /api/finalizar   -> finaliza a compra e dá baixa no estoque
"""

import json
import unicodedata
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
PORTA = 8000

# ---------------------------------------------------------------------------
# Dados - os mesmos do projetin.py original (itens, quantidades e preços)
# ---------------------------------------------------------------------------
estoque = {
    'camara de ar': 30,
    'pneu dianteiro': 30,
    'lona de freio': 30,
    'pastilha de freio': 30,
    'filtro de ar': 30,
    'kit transmissão': 30,
    'oleo de motor': 30,
}

valores = {
    'camara de ar': 60.00,
    'pneu dianteiro': 380.00,
    'lona de freio': 35.00,
    'pastilha de freio': 35.00,
    'filtro de ar': 60.00,
    'kit transmissão': 150.00,
    'oleo de motor': 35.00,
}

clientes = [
    {'nome': 'João'},
    {'nome': 'Pedro'},
]

formas_de_pagamento = [
    'pix',
    'cartão de crédito',
    'cartão de débito',
    'dinheiro',
]


# ---------------------------------------------------------------------------
# Utilitários
# ---------------------------------------------------------------------------
def normalizar(texto):
    """Minúsculas, sem espaços extras e sem acentos, para comparar entradas."""
    texto = str(texto or '').strip().lower()
    texto = unicodedata.normalize('NFD', texto)
    return ''.join(letra for letra in texto if unicodedata.category(letra) != 'Mn')


def nome_valido(nome):
    nome = str(nome or '').strip()
    return bool(nome) and all(
        letra.isalpha() or letra in " -'" for letra in nome
    )


def buscar_cliente(nome):
    for cliente in clientes:
        if normalizar(cliente['nome']) == normalizar(nome):
            return cliente
    return None


def catalogo():
    return [
        {'produto': produto, 'preço': valores[produto], 'estoque': estoque[produto]}
        for produto in estoque
    ]


def erro(mensagem, codigo=400):
    return codigo, {'ok': False, 'erro': mensagem}


# ---------------------------------------------------------------------------
# Regras da compra (as mesmas do programa de terminal)
# ---------------------------------------------------------------------------
def finalizar_compra(dados):
    nome = str(dados.get('nome') or '').strip()
    if not nome_valido(nome):
        return erro('Informe um nome válido para finalizar a compra.')

    carrinho = dados.get('carrinho') or []
    if not isinstance(carrinho, list) or not carrinho:
        return erro('Seu carrinho está vazio.')

    pagamento = str(dados.get('pagamento') or '').strip()
    forma = next(
        (forma for forma in formas_de_pagamento
         if normalizar(forma) == normalizar(pagamento)),
        None,
    )
    if forma is None:
        return erro('Escolha uma forma de pagamento válida.')

    # Valida cada item e soma as quantidades por produto.
    quantidades = {}
    for item in carrinho:
        produto = next(
            (p for p in estoque if normalizar(p) == normalizar(item.get('produto', ''))),
            None,
        )
        if produto is None:
            return erro(f"Produto não encontrado: {item.get('produto')!r}.")
        try:
            quantidade = int(item.get('quantidade'))
        except (TypeError, ValueError):
            return erro(f'Quantidade inválida para {produto}.')
        if quantidade <= 0:
            return erro(f'A quantidade de {produto} precisa ser maior que zero.')
        quantidades[produto] = quantidades.get(produto, 0) + quantidade

    for produto, quantidade in quantidades.items():
        if quantidade > estoque[produto]:
            return erro(
                f'Só temos {estoque[produto]} unidade(s) de {produto} em estoque.'
            )

    itens = []
    subtotal = 0.0
    for produto, quantidade in quantidades.items():
        preco_total = round(valores[produto] * quantidade, 2)
        subtotal += preco_total
        itens.append({
            'produto': produto,
            'quantidade': quantidade,
            'preço_unitário': valores[produto],
            'preço_total': preco_total,
        })
    subtotal = round(subtotal, 2)

    desconto = 0.0
    if forma in ('pix', 'dinheiro') and subtotal >= 300:
        desconto = round(subtotal * 0.05, 2)
    total = round(subtotal - desconto, 2)

    # Só dá baixa no estoque depois que tudo foi validado.
    for produto, quantidade in quantidades.items():
        estoque[produto] -= quantidade

    return 200, {
        'ok': True,
        'cliente': nome,
        'itens': itens,
        'subtotal': subtotal,
        'desconto': desconto,
        'total': total,
        'pagamento': forma,
        'catalogo': catalogo(),
    }


def cadastrar_cliente(dados):
    nome = str(dados.get('nome') or '').strip()
    if not nome_valido(nome):
        return erro('Informe um nome válido para se cadastrar.')
    cliente = buscar_cliente(nome)
    if cliente is not None:
        return 200, {'ok': True, 'cliente': cliente, 'novo': False}
    cliente = {'nome': nome}
    clientes.append(cliente)
    return 200, {'ok': True, 'cliente': cliente, 'novo': True}


# ---------------------------------------------------------------------------
# Servidor HTTP
# ---------------------------------------------------------------------------
TIPOS = {
    '.html': 'text/html; charset=utf-8',
    '.css': 'text/css; charset=utf-8',
    '.js': 'text/javascript; charset=utf-8',
}


class LojaHandler(BaseHTTPRequestHandler):
    def log_message(self, *args):  # silencia o log de cada requisição
        pass

    def _enviar_json(self, codigo, dados):
        corpo = json.dumps(dados, ensure_ascii=False).encode('utf-8')
        self.send_response(codigo)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(corpo)))
        self.end_headers()
        self.wfile.write(corpo)

    def _enviar_arquivo(self, nome):
        caminho = BASE_DIR / nome
        if not caminho.is_file():
            self.send_error(404, 'Arquivo não encontrado')
            return
        corpo = caminho.read_bytes()
        self.send_response(200)
        self.send_header('Content-Type', TIPOS.get(caminho.suffix, 'application/octet-stream'))
        self.send_header('Content-Length', str(len(corpo)))
        self.end_headers()
        self.wfile.write(corpo)

    def _ler_json(self):
        tamanho = int(self.headers.get('Content-Length') or 0)
        if not tamanho:
            return {}
        return json.loads(self.rfile.read(tamanho).decode('utf-8') or '{}')

    def do_GET(self):
        if self.path in ('/', '/index.html'):
            self._enviar_arquivo('index.html')
        elif self.path == '/style.css':
            self._enviar_arquivo('style.css')
        elif self.path == '/app.js':
            self._enviar_arquivo('app.js')
        elif self.path == '/api/catalogo':
            self._enviar_json(200, {'ok': True, 'catalogo': catalogo()})
        else:
            self.send_error(404, 'Página não encontrada')

    def do_POST(self):
        try:
            dados = self._ler_json()
        except (ValueError, UnicodeDecodeError):
            self._enviar_json(*erro('Envie os dados em formato JSON válido.'))
            return

        if self.path == '/api/cliente':
            cliente = buscar_cliente(dados.get('nome', ''))
            self._enviar_json(200, {'ok': True, 'cliente': cliente})
        elif self.path == '/api/cadastrar':
            self._enviar_json(*cadastrar_cliente(dados))
        elif self.path == '/api/finalizar':
            self._enviar_json(*finalizar_compra(dados))
        else:
            self.send_error(404, 'Página não encontrada')


if __name__ == '__main__':
    servidor = ThreadingHTTPServer(('127.0.0.1', PORTA), LojaHandler)
    print(f'Loja de Peças rodando em http://localhost:{PORTA}')
    print('Pressione Ctrl+C para parar.')
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print('\nServidor parado.')
