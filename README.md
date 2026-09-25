# Na sua cara, coroa

## Guia para o frontend

Este projeto é um jogo de cara ou coroa para dois jogadores. O backend atual é um servidor WebSocket Python assíncrono; ele não expõe uma API REST. O frontend deve usar a API nativa `WebSocket` do navegador e manter uma conexão persistente com o servidor.

## Arquitetura

```text
Frontend
	 │
	 │ WebSocket
	 ▼
Python WebSocket Server
	 │
	 ├── Host
	 ├── ClientSession
	 ├── Room
	 └── Game
```

- **`Host`** (`backend/src/projeto_cara_coroa/server/host.py`) recebe conexões WebSocket, valida cada mensagem JSON com Pydantic, despacha os comandos e mantém os dicionários de salas e sessões.
- **`ClientSession`** (`backend/src/projeto_cara_coroa/client/session.py`) representa um jogador conectado e guarda a conexão WebSocket desse jogador, além do `room_id` atual.
- **`Room`** (`backend/src/projeto_cara_coroa/server/room.py`) representa uma partida entre dois jogadores. O criador da sala é o `host`/player 1; quem entra depois é o `guest`/player 2. A sala inicia partidas, aguarda decisões de rematch e pode iniciar novas partidas.
- **`Game`** (`backend/src/projeto_cara_coroa/server/game.py`) aguarda a escolha dos dois jogadores, sorteia o resultado (`heads` ou `tails`), atualiza `host_score` e `guest_score`, e informa se haverá outra rodada ou se a partida terminou.

O ponto de entrada é `backend/src/projeto_cara_coroa/main.py`. O servidor usa `asyncio` e a biblioteca `websockets`.

## Conexão

- Porta do backend: `8000`
- Endpoint local: `ws://localhost:8000`
- Docker publica a porta com `8000:8000` no serviço `server` de `docker-compose.yml`.

Exemplo de conexão no navegador:

```js
const socket = new WebSocket("ws://localhost:8000");

socket.addEventListener("open", () => {
	// A conexão está pronta para enviar comandos.
});

socket.addEventListener("message", (event) => {
	const response = JSON.parse(event.data);
	// Atualize a interface usando response.status e response.message.
});

socket.addEventListener("close", () => {
	// Mostre o estado desconectado e permita reconectar quando apropriado.
});
```

O fluxo esperado é: conectar → enviar mensagens JSON → receber mensagens assíncronas → atualizar a interface → fechar ou reconectar quando necessário. O servidor não envia uma mensagem inicial de boas-vindas: o frontend deve iniciar o fluxo enviando `create_room` ou `join_room`.

## Formato das mensagens

Cada mensagem enviada pelo frontend precisa ter um campo `type`. O backend valida o formato antes de processá-la.

### Criar uma sala

```json
{ "type": "create_room" }
```

Resposta de sucesso:

```json
{ "status": "ok", "message": { "room_id": "A1B2C3" } }
```

O `room_id` é um código aleatório de seis caracteres alfanuméricos, convertido para maiúsculas. O jogador que cria a sala torna-se o `host` (player 1).

### Entrar em uma sala

```json
{ "type": "join_room", "room_id": "A1B2C3" }
```

Resposta de sucesso:

```json
{ "status": "ok", "message": { "room_id": "A1B2C3" } }
```

O backend normaliza o código recebido para maiúsculas. Uma sala aceita somente um `guest`; se já houver dois jogadores, a resposta é um erro. Quando o segundo jogador entra, a partida é iniciada automaticamente.

### Escolher cara ou coroa

```json
{ "type": "coin_choice", "choice": "heads" }
```

Os únicos valores válidos para `choice` são `heads` e `tails`.

O servidor só responde a esse comando depois que os dois jogadores enviarem suas escolhas. A resposta tem este formato:

```json
{
	"status": "ok",
	"message": {
		"status": "next_round",
		"host_score": 1,
		"guest_score": 0,
		"result": "heads"
	}
}
```

Os campos de `message` são:

- `status`: `next_round` enquanto a partida continua ou `game_finish` quando há um vencedor.
- `host_score`: pontuação acumulada do player 1.
- `guest_score`: pontuação acumulada do player 2.
- `result`: resultado sorteado, `heads` ou `tails`.

O frontend deve associar `host_score` ao criador da sala e `guest_score` ao jogador que entrou nela. A regra implementada encerra a partida quando um jogador alcança pelo menos 5 pontos e a diferença entre as pontuações é de pelo menos 2.

### Solicitar rematch

Depois de receber `status: "game_finish"`, cada jogador deve enviar sua decisão:

```json
{ "type": "rematch", "accept": true }
```

`accept` é booleano. O backend aguarda as duas respostas. Somente depois disso cada solicitação pendente recebe uma resposta:

```json
{ "status": "ok", "message": { "result": "accepted" } }
```

ou:

```json
{ "status": "ok", "message": { "result": "declined" } }
```

Se os dois aceitarem, uma nova partida começa na mesma sala e as pontuações são reiniciadas. Se qualquer um recusar, o backend remove os jogadores da sala, mas o código atual não fecha explicitamente as conexões WebSocket; confirme com o responsável pelo backend se o comportamento esperado da interface é fechar também a conexão ou permitir uma nova ação nela.

## Respostas e erros

As respostas normais usam sempre o envelope:

```json
{ "status": "ok" | "error", "message": "..." }
```

Em sucesso, `message` pode ser um objeto com dados (`room_id`, resultado do jogo ou rematch). Em erros de negócio, atualmente é uma string. Exemplos observados no código:

```json
{ "status": "error", "message": "Room A1B2C3 does not exist." }
```

```json
{ "status": "error", "message": "Room A1B2C3 is already full." }
```

Também há erros para tentar criar ou entrar em outra sala enquanto a sessão já está em uma sala, escolher antes de a partida começar (`Game has not started yet`) ou solicitar rematch enquanto o jogo ainda está em execução (`Game is still running`).

Mensagens que não obedecem aos schemas de `backend/src/projeto_cara_coroa/protocols.py` são rejeitadas pelo Pydantic. O código prevê retornar `status: "error"` com uma lista de erros de validação, mas atualmente o caminho usado para enviar esse erro chama `_send_message`, método que não está definido em `Host`. Portanto, o frontend deve enviar exatamente os tipos e campos documentados; o formato final de erros de validação ainda precisa ser confirmado ou corrigido no backend.

## Fluxo recomendado da interface

1. Abra uma única conexão WebSocket e mantenha-a associada ao estado da sessão.
2. Para hospedar, envie `create_room` e mostre o `room_id` retornado.
3. Para entrar, envie `join_room` com o código informado pelo usuário.
4. Depois de a sala estar completa, habilite a escolha de `heads` ou `tails`.
5. Desabilite o envio de uma nova escolha até receber o resultado da rodada. A resposta pode demorar porque depende da escolha do outro jogador.
6. Atualize placar e resultado usando `host_score`, `guest_score` e `result`. Em `game_finish`, mostre a opção de rematch.
7. Envie `rematch` uma vez por jogador e aguarde a resposta assíncrona.
8. Trate respostas com `status: "error"`, o evento `close` e o evento `error` do objeto WebSocket como estados de interface distintos, com possibilidade de reconexão conforme a regra do produto.

Não há autenticação, identificação pública de jogador, endpoint HTTP, mensagens de presença ou broadcast de estado independente no protocolo atual. Se o frontend precisar desses recursos, eles devem ser combinados com o responsável pelo backend antes de criar um novo contrato.

## Executar localmente

Na raiz do projeto:

```bash
docker compose up --build
```

O servidor ficará disponível em `ws://localhost:8000`. O serviço é definido em `docker-compose.yml` e é construído a partir de `backend/Dockerfile`.

Os módulos de protocolo e schema estão atualmente em arquivos únicos, `backend/src/projeto_cara_coroa/protocols.py` e `backend/src/projeto_cara_coroa/schemas.py`; não existem diretórios `protocols/` ou `schemas/` no backend atual.

## Frontend

O frontend está em `frontend/` e usa a API nativa `WebSocket` do navegador para se conectar ao servidor em `ws://localhost:8000`.

Depois de executar:

```bash
docker compose up --build
```

abra `frontend/index.html` no navegador.
