# 🪙 Na sua cara, coroa

Aplicação multiplayer de **cara ou coroa** desenvolvida para a disciplina de **Computação Distribuída**, utilizando **WebSocket** para comunicação em tempo real entre jogadores.

O projeto é composto por um **servidor assíncrono em Python** responsável pelo estado global e pelas regras da partida, e um **cliente em JavaScript** responsável pela interface e interação com os jogadores.

> Projeto acadêmico — Ciência da Computação
> Disciplina: Computação Distribuída
> Professor: Hiago Oliveira
> Data de apresentação: 25/09/2026

---

## 🎯 Sobre o projeto

**Na sua cara, coroa** é um jogo multiplayer para dois jogadores no qual cada participante escolhe entre **cara** e **coroa** a cada rodada.

A aplicação utiliza WebSocket para manter uma conexão persistente entre cada cliente e o servidor, permitindo que os jogadores participem da mesma partida em tempo real.

O servidor é responsável por:

* Gerenciar as conexões dos jogadores;
* Criar e administrar salas;
* Controlar os jogadores de cada sala;
* Receber as escolhas de cara ou coroa;
* Sortear o resultado da moeda;
* Controlar a pontuação;
* Controlar as sequências de vitórias;
* Aplicar as mecânicas de recuperação;
* Determinar o vencedor;
* Gerenciar o sistema de revanche.

O frontend é responsável por:

* Apresentar a interface do jogo;
* Criar e entrar em salas;
* Exibir o código da sala;
* Permitir a escolha entre cara e coroa;
* Exibir placar e resultados;
* Informar o estado da conexão;
* Exibir as mecânicas especiais da partida;
* Permitir aceitar ou recusar uma revanche.

---

# 🏗️ Arquitetura

A aplicação possui uma separação clara entre **Cliente** e **Servidor**.

```text
┌──────────────────────┐
│      PLAYER 1        │
│   JavaScript/Web     │
└──────────┬───────────┘
           │
           │ WebSocket
           │
           ▼
┌──────────────────────┐
│                      │
│   PYTHON SERVER      │
│                      │
│  ┌────────────────┐  │
│  │     Host       │  │
│  ├────────────────┤  │
│  │     Room       │  │
│  ├────────────────┤  │
│  │     Game       │  │
│  └────────────────┘  │
│                      │
└──────────┬───────────┘
           │
           │ WebSocket
           │
           ▼
┌──────────────────────┐
│      PLAYER 2        │
│   JavaScript/Web     │
└──────────────────────┘
```

### Servidor

O servidor mantém o **estado global da aplicação** e concentra as regras do jogo.

Principais componentes:

* `Host` — gerencia conexões, salas e mensagens;
* `Room` — representa uma sala com dois jogadores;
* `Game` — controla a partida, escolhas, pontuação e resultado;
* `ClientSession` — representa a conexão de um jogador;
* `schemas` — estruturas utilizadas para comunicação e validação dos dados.

### Cliente

O frontend utiliza JavaScript nativo e a API `WebSocket` disponível no navegador.

Principais arquivos:

```text
frontend/
├── index.html
├── style.css
├── app.js
└── README.md
```

* `index.html` — estrutura da interface;
* `style.css` — estilos e animações;
* `app.js` — conexão WebSocket, interação e atualização da interface;
* `README.md` — informações específicas sobre o frontend.

---

# 🔌 Comunicação via WebSocket

O servidor utiliza a seguinte conexão:

```text
ws://localhost:8000
```

Não existe uma API REST para as operações do jogo. A comunicação entre cliente e servidor é realizada por mensagens JSON através do WebSocket.

### Ciclo de vida

A conexão segue, de forma simplificada:

```text
Cliente
   │
   │  Handshake WebSocket
   ▼
Servidor
   │
   │  Conexão persistente
   │◄────────────────────►│
   │    Mensagens JSON    │
   │◄────────────────────►│
   │
   │  Encerramento
   ▼
Desconectado
```

A conexão permanece aberta durante a utilização da partida, permitindo que mensagens sejam enviadas entre cliente e servidor sem a necessidade de estabelecer uma nova conexão para cada ação.

---

# 🏠 Salas

Cada partida acontece dentro de uma sala com **dois jogadores**.

O primeiro jogador cria a sala e se torna o **Player 1**.

O segundo jogador utiliza o código da sala para entrar e se torna o **Player 2**.

Exemplo:

```text
Player 1
   │
   │ create_room
   ▼
Servidor
   │
   └──► Sala: A1B2C3
              │
              │ join_room
              ▼
           Player 2
```

Quando o segundo jogador entra, o servidor envia uma notificação `room_ready` ao primeiro jogador para que ambos possam iniciar a partida.

---

# 📡 Protocolo de mensagens

As mensagens são enviadas em formato JSON.

## Criar sala

Cliente:

```json
{
  "type": "create_room"
}
```

O servidor cria uma nova sala e retorna o código correspondente.

---

## Entrar em uma sala

Cliente:

```json
{
  "type": "join_room",
  "room_id": "A1B2C3"
}
```

---

## Escolher cara ou coroa

Cara:

```json
{
  "type": "coin_choice",
  "choice": "heads"
}
```

Coroa:

```json
{
  "type": "coin_choice",
  "choice": "tails"
}
```

O resultado da rodada é enviado somente depois que os dois jogadores realizam suas escolhas.

---

## Revanche

Aceitar:

```json
{
  "type": "rematch",
  "accept": true
}
```

Recusar:

```json
{
  "type": "rematch",
  "accept": false
}
```

A revanche somente é iniciada quando os dois jogadores respondem.

---

# 🕹️ Regras do jogo

A cada rodada:

1. Os dois jogadores escolhem entre cara e coroa.
2. O servidor determina o resultado da moeda.
3. O jogador que escolheu o lado sorteado recebe pontos.
4. O placar é atualizado.
5. O servidor verifica as condições da partida.
6. Uma nova rodada é iniciada caso a partida ainda não tenha terminado.

A moeda utiliza uma escolha aleatória entre:

```text
heads
tails
```

---

# 🔥 Sistema de sequência

O jogo possui uma mecânica de **sequência de acertos**.

Quando um jogador mantém uma sequência de vitórias, seus acertos podem valer mais pontos.

A progressão atual é:

```text
1º acerto consecutivo → +1 ponto
2º acerto consecutivo → +1 ponto
3º acerto consecutivo → +1 ponto
4º acerto consecutivo → +2 pontos
5º acerto consecutivo → +3 pontos
6º acerto consecutivo → +4 pontos
...
```

Quando o jogador erra, sua sequência é reiniciada.

A interface exibe visualmente o efeito:

```text
🔥 STREAK X4
NEXT HIT: +2
```

---

# 🍀 Sistema de recuperação

Para evitar que uma grande vantagem de pontuação torne a partida pouco competitiva, existe uma mecânica de recuperação.

Quando um jogador está **10 ou mais pontos atrás**, ele recebe uma vantagem probabilística sobre a escolha realizada.

Essa vantagem aumenta quando a diferença é ainda maior.

Os valores exatos da probabilidade são controlados exclusivamente pelo servidor e **não são exibidos aos jogadores**.

Na interface, o jogador recebe apenas a indicação:

```text
🍀 LUCKY
CHANCE EXTRA
```

A mecânica não garante o resultado da rodada; ela apenas modifica a probabilidade utilizada pelo servidor.

---

# 🏆 Condição de vitória

A partida utiliza como pontuação final:

```text
20 pontos
```

Para vencer, o jogador precisa:

* alcançar pelo menos 20 pontos;
* possuir uma vantagem mínima de 2 pontos sobre o adversário.

Exemplos:

```text
20 × 18 → vitória
21 × 19 → vitória
20 × 19 → continua
```

---

# 🔄 Sistema de revanche

Após o encerramento da partida, os jogadores podem solicitar uma revanche.

Cada jogador pode:

```text
ACEITAR
```

ou

```text
RECUSAR
```

A nova partida somente começa quando os dois jogadores aceitam.

Caso algum jogador recuse, a sessão da sala é encerrada.

---

# 📁 Estrutura do projeto

```text
Na-sua-cara-coroa/
│
├── backend/
│   ├── src/
│   │   └── projeto_cara_coroa/
│   │       ├── client/
│   │       ├── server/
│   │       ├── protocols.py
│   │       └── schemas.py
│   │
│   └── ...
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   ├── app.js
│   └── README.md
│
├── docker-compose.yml
│
└── README.md
```

---

# 🚀 Como executar

## Pré-requisitos

É necessário possuir:

* [Docker](https://www.docker.com/)
* [Git](https://git-scm.com/)
* Navegador web moderno;
* Uma ferramenta para servir o frontend localmente, como o **Live Server** do VS Code.

---

## 1. Clonar o repositório

```bash
git clone https://github.com/LauroDF/Na-sua-cara-coroa.git
```

Entrar na pasta:

```bash
cd Na-sua-cara-coroa
```

---

## 2. Iniciar o servidor

Na raiz do projeto:

```bash
docker compose up --build
```

O backend ficará disponível em:

```text
ws://localhost:8000
```

---

## 3. Iniciar o frontend

Abra a pasta `frontend` no VS Code.

Utilizando o **Live Server**, abra:

```text
frontend/index.html
```

O navegador exibirá a interface do jogo.

---

# 👥 Como testar uma partida

Como o jogo possui dois jogadores, podem ser utilizadas duas abas ou janelas do navegador.

### Player 1

1. Abra o jogo.
2. Clique em **Criar sala**.
3. Copie o código da sala.

### Player 2

1. Abra o jogo em outra aba/janela.
2. Informe o código recebido.
3. Entre na sala.

### Partida

Depois que os dois jogadores estiverem conectados:

1. Player 1 escolhe cara ou coroa.
2. Player 2 escolhe cara ou coroa.
3. O servidor aguarda as duas escolhas.
4. A moeda é definida.
5. O placar é atualizado.
6. Uma nova rodada começa.

A partida continua até que um jogador atinja a condição de vitória.

---

# 🧪 Cenários para demonstração

Durante a apresentação, podem ser demonstrados:

* Criação de uma sala;
* Entrada de um segundo jogador;
* Comunicação em tempo real via WebSocket;
* Escolha simultânea de cara ou coroa;
* Atualização do placar;
* Sequência de vitórias;
* Bônus de pontuação;
* Mecânica de recuperação;
* Finalização da partida;
* Solicitação de revanche;
* Aceitação ou recusa da revanche;
* Tratamento de salas inválidas ou cheias;
* Encerramento da conexão.

---

# 🛠️ Tecnologias utilizadas

### Backend

* Python
* `asyncio`
* WebSocket
* Pydantic
* Docker

### Frontend

* HTML5
* CSS3
* JavaScript
* WebSocket API

### Controle de versão

* Git
* GitHub

---

# 🎓 Objetivo acadêmico

O projeto foi desenvolvido para demonstrar conceitos de **Computação Distribuída**, especialmente a comunicação em tempo real utilizando WebSocket.

A aplicação permite observar na prática conceitos como:

* Comunicação cliente-servidor;
* Conexões persistentes;
* Handshake WebSocket;
* Troca de mensagens;
* Gerenciamento de sessões;
* Gerenciamento de estado distribuído entre clientes;
* Concorrência assíncrona;
* Sincronização entre jogadores;
* Encerramento de conexões.

A proposta segue os requisitos da atividade da disciplina, que estabelece a utilização de **WebSocket com Python no servidor e JavaScript no cliente**, além da separação entre responsabilidades do servidor e do cliente.

---

# 👨‍💻 Projeto

**Na sua cara, coroa**

Desenvolvido como trabalho acadêmico da disciplina de **Computação Distribuída — Ciência da Computação**.
