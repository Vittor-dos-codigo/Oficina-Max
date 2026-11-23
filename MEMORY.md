# MEMORY.md — Loja de Peças

Memória do projeto, para retomar o trabalho em tarefas futuras sem precisar
redescobrir as decisões já tomadas. Atualizado em 23/11/2026.

> **Combinado:** antes de criar um novo projeto, o usuário edita este
> `MEMORY.md` primeiro — e eu devo lembrá-lo disso quando ele mencionar
> um projeto novo.

## O que é

Projeto pessoal de teste: uma loja de peças de moto com um programa de
terminal (`projetin.py`, na raiz do repositório) e uma versão web (nesta
mesma pasta), com frontend em HTML/CSS e backend em Python. Não tem banco
de dados e não tem
nada para instalar.

## Como rodar

```bash
python3 app.py
```

Depois abra http://localhost:8000 no navegador. Para parar, `Ctrl+C`.
Versão de terminal: `python3 projetin.py`.

## Arquivos

- `app.py` — servidor Python (só biblioteca padrão) e todas as regras da
  loja. Serve a página e a API em JSON.
- `index.html` — estrutura da página: cliente, catálogo, carrinho,
  pagamento e recibo.
- `style.css` — visual da loja.
- `app.js` — lógica do navegador: carrega o catálogo, monta o carrinho,
  calcula o total e chama a API.
- `README.md` — como rodar e como a integração funciona.
- `MEMORY.md` — este arquivo.
- `projetin.py` — versão de terminal, com as mesmas regras e dados.

## Dados atuais (não mudar sem pedir)

Produtos, preços e estoque inicial. Os preços são os do programa original;
o estoque foi aumentado para 30 em todas as peças em 23/11/2026.

| Produto | Preço | Estoque inicial |
| --- | --- | --- |
| camara de ar | R$ 60,00 | 30 |
| pneu dianteiro | R$ 380,00 | 30 |
| lona de freio | R$ 35,00 | 30 |
| pastilha de freio | R$ 35,00 | 30 |
| filtro de ar | R$ 60,00 | 30 |
| kit transmissão | R$ 150,00 | 30 |
| oleo de motor | R$ 35,00 | 30 |

Clientes cadastrados (só o nome, sem nenhum outro campo):

- João
- Pedro

## Regras da loja

- Formas de pagamento: pix, cartão de crédito, cartão de débito e dinheiro.
  Não existe fiado.
- Desconto de 5% para pix ou dinheiro em compras a partir de R$ 300,00
  (subtotal). Abaixo disso, sem desconto.
- O cliente pode comprar vários produtos; o total soma todos os itens.
- Quantidade precisa ser um número inteiro maior que zero e menor ou igual
  ao estoque disponível (descontando o que já está no carrinho).
- A baixa no estoque só acontece depois que a compra inteira foi validada.
- Nomes e produtos aceitam maiúsculas e acentos: "Câmara de Ar", "João"
  digitado como "Joao" e "Pix" funcionam.
- O site mostra o catálogo com preço e estoque; o Python é quem valida a
  compra de verdade, o navegador só calcula uma prévia do total.

## API (backend Python)

- `GET /` — página da loja.
- `GET /api/catalogo` — produtos, preços e estoque atual.
- `POST /api/cliente` — `{"nome": "..."}` procura o cliente cadastrado.
- `POST /api/cadastrar` — `{"nome": "..."}` cadastra o cliente.
- `POST /api/finalizar` — `{"nome", "pagamento", "carrinho": [{"produto",
  "quantidade"}]}` valida, aplica o desconto, dá baixa no estoque e
  devolve o recibo com subtotal, desconto e total.

## Decisões já tomadas (histórico)

- 23/11/2026 — programa de terminal corrigido: o carrinho passou a aceitar
  vários produtos, a compra passou a ser finalizada para qualquer forma de
  pagamento (antes só acontecia com pix/dinheiro acima de R$ 300,00) e a
  quantidade inválida passou a ser pedida de novo em vez de quebrar o
  programa. Cadastro novo entrava como bloqueado e foi mudado para ativo.
- 23/11/2026 — frontend criado, com Python usando só a biblioteca padrão,
  sem banco de dados e sem dependências.
- 23/11/2026 — removida da tela a situação do cliente ("Situação: ativo")
  e a linha "Já cadastrados para testar: João (bloqueado) e Pedro (ativo)".
  A recusa do fiado ficou genérica.
- 23/11/2026 — desconto mudado de 10% para 5% (primeiro só no site,
  depois também no terminal).
- 23/11/2026 — opção de comprar fiado removida do site e do terminal.
- 23/11/2026 — estoque de todas as peças aumentado para 30.
- 23/11/2026 — campo "situação" do cliente removido por completo dos dois
  programas, porque sem o fiado ele não tinha mais utilidade. Clientes
  agora têm só o nome.

## Testes já verificados

- Pedro compra 1 pneu dianteiro no pix: subtotal R$ 380,00, desconto
  R$ 19,00, total R$ 361,00. Estoque do pneu cai de 30 para 29.
- Compra de 25 óleos de motor no dinheiro no site: subtotal R$ 875,00,
  desconto R$ 43,75, total R$ 831,25.
- Cliente nova (Maria) se cadastra e compra câmara de ar + filtro de ar
  no cartão: total R$ 120,00, sem desconto.
- Quantidade maior que o estoque e forma de pagamento inválida (incluindo
  fiado) são recusadas com mensagem de erro.
- Cadastro e consulta de cliente devolvem só `{"nome": "..."}`.

## Limitações conhecidas

- Tudo fica em memória: ao reiniciar o servidor, o estoque e os clientes
  cadastrados durante a sessão voltam ao original.
- Não há login, senha ou controle de acesso; qualquer pessoa com o nome
  compra como aquele cliente.
- Os dados não são salvos em arquivo nem em banco de dados.

## Ideias para o futuro (não decididas)

- Salvar estoque e clientes em um arquivo, para não resetar ao reiniciar.
- Adicionar fotos e descrições aos produtos.
- Permitir cadastrar novos produtos pela página.
- Histórico de vendas do dia.
