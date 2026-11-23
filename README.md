# Oficina-Max — Loja de Peças

Loja de peças de moto com duas versões do mesmo programa: uma de terminal
e uma web, com frontend em HTML/CSS e backend em Python.

Projeto pessoal de estudo, criado com auxílio de IA (Muse) para praticar
o uso de IA no desenvolvimento: do programa de terminal ao site, incluindo
correções, testes e organização do projeto.

## O que a loja faz

- Mostra o catálogo com preço e estoque de 7 peças.
- Permite montar um carrinho com vários produtos.
- Calcula o total e aplica 5% de desconto para pix ou dinheiro em compras
  a partir de R$ 300,00.
- Dá baixa no estoque só depois que a compra é validada.
- Clientes João e Pedro já cadastrados (só o nome); novos clientes podem
  se cadastrar na hora.

## Versão web

```bash
python3 app.py
```

Depois abra http://localhost:8000 no navegador. Para parar, `Ctrl+C`.

## Versão de terminal

```bash
python3 projetin.py
```

## Arquivos

- `app.py` — servidor Python (só biblioteca padrão) e regras da loja.
  Serve a página e a API em JSON.
- `index.html` — estrutura da página: cliente, catálogo, carrinho,
  pagamento e recibo.
- `style.css` — visual da loja.
- `app.js` — lógica do navegador: carrega o catálogo, monta o carrinho,
  calcula o total e chama a API.
- `projetin.py` — versão de terminal, com as mesmas regras e dados.
- `MEMORY.md` — memória do projeto: dados, regras, decisões e testes.

## Regras

- 7 produtos, estoque inicial de 30 unidades cada; preços fixos
  (câmara de ar R$ 60,00; pneu dianteiro R$ 380,00; lona de freio
  R$ 35,00; pastilha de freio R$ 35,00; filtro de ar R$ 60,00;
  kit transmissão R$ 150,00; óleo de motor R$ 35,00).
- Pagamento: pix, cartão de crédito, cartão de débito e dinheiro.
  Não existe fiado.
- Quantidade maior que o estoque é recusada.
- Sem banco de dados: tudo fica em memória e volta ao original quando
  o servidor é reiniciado.
