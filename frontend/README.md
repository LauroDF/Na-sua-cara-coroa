# Frontend — Na sua cara, coroa

Frontend do jogo de cara ou coroa. A interface usa a API nativa `WebSocket` do navegador e conversa diretamente com o servidor Python.

## Estrutura

- `index.html` — estrutura das telas e componentes da interface.
- `style.css` — estilos e responsividade.
- `app.js` — conexão WebSocket, estado da interface e protocolo do jogo.

## Executar

1. Suba o backend na raiz do projeto:

```bash
docker compose up --build
```

2. Com o servidor disponível em `ws://localhost:8000`, abra `frontend/index.html` no navegador.

O frontend não usa API REST nem biblioteca WebSocket externa.

## Fluxo

- Criar sala: `{"type":"create_room"}`
- Entrar: `{"type":"join_room","room_id":"..."}` 
- Escolher: `{"type":"coin_choice","choice":"heads"|"tails"}`
- Rematch: `{"type":"rematch","accept":true|false}`

O Player 1 é o criador da sala e usa `host_score`; o Player 2 usa `guest_score`.
