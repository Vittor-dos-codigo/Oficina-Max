"""Loja de peças - programa de vendas.

Mantidos exatamente os itens e valores originais do estoque.
Para rodar: python3 projetin.py
"""

import unicodedata


# ---------------------------------------------------------------------------
# Dados - os mesmos do código original (itens, quantidades e preços)
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
# Utilitários de texto e entrada
# ---------------------------------------------------------------------------
def normalizar(texto):
    """Minúsculas, sem espaços extras e sem acentos, para comparar entradas.

    Assim 'Câmara de Ar', 'camara de ar' e 'CAMARA DE AR' são o mesmo produto,
    e 'João' é encontrado mesmo digitado como 'joao'.
    """
    texto = texto.strip().lower()
    texto = unicodedata.normalize('NFD', texto)
    return ''.join(letra for letra in texto if unicodedata.category(letra) != 'Mn')


def nome_valido(nome):
    """Aceita letras (com acento), espaços, hífen e apóstrofo."""
    nome = nome.strip()
    return bool(nome) and all(
        letra.isalpha() or letra in " -'" for letra in nome
    )


def perguntar_sim_nao(pergunta):
    """Pergunta até receber 'sim' ou 'não' e devolve True/False."""
    while True:
        resposta = normalizar(input(pergunta))
        if resposta in ('sim', 's'):
            return True
        if resposta in ('nao', 'n'):
            return False
        print("Por favor, responda com 'sim' ou 'não'.")


def buscar_cliente(nome):
    for cliente in clientes:
        if normalizar(cliente['nome']) == normalizar(nome):
            return cliente
    return None


def mostrar_catalogo():
    print('\n--- Produtos em estoque ---')
    for produto, quantidade in estoque.items():
        print(f"- {produto}: R$ {valores[produto]:.2f} "
              f"({quantidade} em estoque)")
    print('---------------------------')


# ---------------------------------------------------------------------------
# Etapas da compra
# ---------------------------------------------------------------------------
def identificar_cliente():
    while True:
        nome = input('Olá, seja bem-vindo! Qual é o seu nome? ').strip()
        if nome_valido(nome):
            break
        print('Por favor, insira um nome válido.')

    print(f'Olá {nome}, seja bem-vindo!')
    cliente = buscar_cliente(nome)

    if cliente is None:
        print('Você não está cadastrado em nosso sistema.')
        if perguntar_sim_nao('Deseja se cadastrar? (sim/não): '):
            clientes.append({'nome': nome})
            print(f'Cadastro realizado com sucesso! Bem-vindo, {nome}!')
        else:
            print('Ok, prosseguiremos sem cadastro.')
    return nome


def escolher_produto():
    """Mostra o catálogo e devolve o produto escolhido, ou None para sair."""
    while True:
        mostrar_catalogo()
        compra = input(
            'O que você deseja comprar? '
            '(ou digite "sair" para encerrar): '
        ).strip()
        if normalizar(compra) == 'sair':
            return None
        for produto in estoque:
            if normalizar(produto) == normalizar(compra):
                return produto
        print('Desculpe, não temos esse produto em estoque.')
        if not perguntar_sim_nao('Deseja tentar outro produto? (sim/não): '):
            return None


def ler_quantidade(produto, ja_no_carrinho):
    """Lê a quantidade, sem quebrar com letras e respeitando o estoque."""
    disponivel = estoque[produto] - ja_no_carrinho
    while True:
        try:
            quantidade = int(input(
                f'Qual a quantidade? (disponível: {disponivel}): '
            ))
        except ValueError:
            print('Por favor, digite um número inteiro.')
            continue
        if quantidade <= 0:
            print('A quantidade precisa ser maior que zero.')
        elif quantidade > disponivel:
            print('Desculpe, não temos essa quantidade em estoque.')
        else:
            return quantidade


def escolher_pagamento():
    """Lê a forma de pagamento."""
    print('\nFormas de pagamento:', ', '.join(formas_de_pagamento))
    while True:
        pagamento = input('Qual a forma de pagamento? ').strip()
        forma = next(
            (forma for forma in formas_de_pagamento
             if normalizar(forma) == normalizar(pagamento)),
            None,
        )
        if forma is None:
            print('Por favor, insira uma forma de pagamento válida.')
            continue
        return forma


def finalizar_compra(nome, carrinho):
    """Calcula o total, aplica o desconto, dá baixa no estoque e imprime
    o resumo da compra. O desconto e a baixa no estoque agora acontecem
    para qualquer forma de pagamento, não só para pix/dinheiro."""
    subtotal = sum(item['preço_total'] for item in carrinho)
    desconto = 0.0
    total = subtotal

    pagamento = escolher_pagamento()
    if pagamento in ('pix', 'dinheiro') and subtotal >= 300:
        desconto = round(subtotal * 0.05, 2)
        total = round(subtotal - desconto, 2)

    for item in carrinho:
        estoque[item['produto']] -= item['quantidade']

    print('\n========== Resumo da compra ==========')
    print(f'Cliente: {nome}')
    for item in carrinho:
        print(f"- {item['produto']}: {item['quantidade']} x "
              f"R$ {item['preço_unitário']:.2f} = "
              f"R$ {item['preço_total']:.2f}")
    print(f'Subtotal: R$ {subtotal:.2f}')
    if desconto:
        print(f'Desconto (5% no {pagamento}): -R$ {desconto:.2f}')
    print(f'Total: R$ {total:.2f}')
    print(f'Pagamento: {pagamento}')
    print('======================================')
    print('Obrigado por sua compra!')


def main():
    nome = identificar_cliente()
    carrinho = []

    while True:
        produto = escolher_produto()
        if produto is None:
            break

        ja_no_carrinho = sum(
            item['quantidade'] for item in carrinho
            if item['produto'] == produto
        )
        if estoque[produto] - ja_no_carrinho <= 0:
            print('Desculpe, esse produto esgotou.')
            continue

        quantidade = ler_quantidade(produto, ja_no_carrinho)
        carrinho.append({
            'produto': produto,
            'quantidade': quantidade,
            'preço_unitário': valores[produto],
            'preço_total': round(valores[produto] * quantidade, 2),
        })
        print(f'{quantidade} x {produto} adicionado(s) ao carrinho.')

        if not perguntar_sim_nao(
                'Deseja comprar mais algum produto? (sim/não): '):
            break

    if not carrinho:
        print('Ok, obrigado por visitar nossa loja!')
        return

    finalizar_compra(nome, carrinho)


if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print('\nCompra encerrada. Obrigado por visitar nossa loja!')
