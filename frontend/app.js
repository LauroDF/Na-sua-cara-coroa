const WS_URL = "ws://localhost:8000";

let socket = null;
let role = null; // "host" | "guest"
let roomId = null;
let hasChosen = false;
let reconnectTimer = null;
let toastTimer = null;

const $ = (id) => document.getElementById(id);

const screens = {
    home: $("homeScreen"),
    waiting: $("waitingScreen"),
    game: $("gameScreen"),
    finish: $("finishScreen"),
};

function showScreen(name) {
    Object.values(screens).forEach((screen) => screen.classList.remove("active"));
    screens[name].classList.add("active");
}

function setConnectionStatus(online) {
    const badge = $("connectionBadge");
    badge.classList.toggle("online", online);
    badge.classList.toggle("offline", !online);
    $("connectionText").textContent = online ? "Conectado" : "Desconectado";
}

function showToast(message, type = "normal") {
    const toast = $("toast");
    toast.textContent = message;
    toast.className = `toast show ${type === "error" ? "error" : ""}`;

    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => {
        toast.classList.remove("show");
    }, 3800);
}

function setGameStatus(message) {
    $("gameStatus").textContent = message;
}

function connect() {
    if (socket && (
        socket.readyState === WebSocket.OPEN ||
        socket.readyState === WebSocket.CONNECTING
    )) {
        return;
    }

    clearTimeout(reconnectTimer);

    try {
        socket = new WebSocket(WS_URL);
    } catch (error) {
        showToast("Não foi possível criar a conexão com o servidor.", "error");
        setConnectionStatus(false);
        return;
    }

    socket.addEventListener("open", () => {
        setConnectionStatus(true);
    });

    socket.addEventListener("message", (event) => {
        try {
            const response = JSON.parse(event.data);
            handleResponse(response);
        } catch (error) {
            showToast("O servidor enviou uma resposta inválida.", "error");
        }
    });

    socket.addEventListener("error", () => {
        setConnectionStatus(false);
        showToast("Erro na conexão com o servidor.", "error");
    });

    socket.addEventListener("close", () => {
        setConnectionStatus(false);

        if (roomId !== null) {
            showToast("Conexão encerrada. Verifique se o servidor está ativo.", "error");
        }

        socket = null;
    });
}

function send(message) {
    if (!socket || socket.readyState !== WebSocket.OPEN) {
        showToast("Conecte-se ao servidor antes de continuar.", "error");
        connect();
        return false;
    }

    socket.send(JSON.stringify(message));
    return true;
}

function handleResponse(response) {
    if (!response || !response.status) {
        showToast("Resposta desconhecida do servidor.", "error");
        return;
    }

    if (response.status === "error") {
        handleServerError(response.message);
        return;
    }

    handleSuccess(response.message);
}

function handleSuccess(message) {
    if (!message || typeof message !== "object") {
        return;
    }

    if (message.status === "room_ready") {
        roomId = message.room_id || roomId;

        $("roomCode").textContent = roomId;
        $("gameRoomCode").textContent = roomId;

        resetScores();
        hasChosen = false;
        clearChoiceSelection();

        showScreen("game");
        setGameStatus("O Player 2 entrou. Escolha cara ou coroa.");
        setChoiceButtonsEnabled(true);

        return;
    }

    if (message.room_id) {
        roomId = message.room_id;
        $("roomCode").textContent = roomId;
        $("gameRoomCode").textContent = roomId;
    }

    if (message.status === "next_round" || message.status === "game_finish") {
        handleRoundResult(message);
        return;
    }

    if (message.result === "accepted") {
        startRematch();
        return;
    }

    if (message.result === "declined") {
        finishConnection();
        showToast("A partida foi encerrada.");
    }
}

function handleServerError(message) {
    if (Array.isArray(message)) {
        showToast("A mensagem enviada não é válida para o servidor.", "error");
        return;
    }

    showToast(String(message || "O servidor recusou a operação."), "error");

    if (String(message).includes("Game has not started yet")) {
        hasChosen = false;
        setChoiceButtonsEnabled(true);
        setGameStatus("A partida ainda não começou. Aguarde o segundo jogador.");
        return;
    }

    if (String(message).includes("Room") && String(message).includes("does not exist")) {
        $("roomInput").focus();
    }
}

function handleRoundResult(result) {
    const hostScore = Number(result.host_score) || 0;
    const guestScore = Number(result.guest_score) || 0;

    $("hostScore").textContent = hostScore;
    $("guestScore").textContent = guestScore;
    $("finalHostScore").textContent = hostScore;
    $("finalGuestScore").textContent = guestScore;
    updatePlayerEffects(result);

    revealResult(result.result);

    hasChosen = false;
    clearChoiceSelection();

    if (result.status === "game_finish") {
        showFinishScreen(hostScore, guestScore);
        return;
    }

    showScreen("game");
    setGameStatus("Escolha cara ou coroa para a próxima rodada.");
    setChoiceButtonsEnabled(true);
    $("waitingChoice").classList.add("hidden");
}

function updatePlayerEffects(result) {
    const hostEffect = $("hostEffect");
    const guestEffect = $("guestEffect");

    hostEffect.className = "player-effect hidden";
    guestEffect.className = "player-effect hidden";

    hostEffect.textContent = "";
    guestEffect.textContent = "";

    const hostStreak = Number(result.host_streak) || 0;
    const guestStreak = Number(result.guest_streak) || 0;

    const hostBonus = Number(result.host_bonus) || 1;
    const guestBonus = Number(result.guest_bonus) || 1;

    if (hostStreak >= 3) {
        hostEffect.classList.remove("hidden");
        hostEffect.classList.add("streak");
        hostEffect.innerHTML =
            `🔥 STREAK X${hostStreak}<br>NEXT HIT: +${hostBonus}`;
    }

    if (guestStreak >= 3) {
        guestEffect.classList.remove("hidden");
        guestEffect.classList.add("streak");
        guestEffect.innerHTML =
            `🔥 STREAK X${guestStreak}<br>NEXT HIT: +${guestBonus}`;
    }

    if (result.luck_player === "host") {
        hostEffect.classList.remove("hidden");
        hostEffect.classList.add("lucky");

        if (hostStreak >= 3) {
            hostEffect.classList.add("streak");
            hostEffect.innerHTML += "<br>🍀 LUCKY";
        } else {
            hostEffect.innerHTML = "🍀 LUCKY<br>CHANCE EXTRA";
        }
    }

    if (result.luck_player === "guest") {
        guestEffect.classList.remove("hidden");
        guestEffect.classList.add("lucky");

        if (guestStreak >= 3) {
            guestEffect.classList.add("streak");
            guestEffect.innerHTML += "<br>🍀 LUCKY";
        } else {
            guestEffect.innerHTML = "🍀 LUCKY<br>CHANCE EXTRA";
        }
    }
}

function revealResult(result) {
    const isHeads = result === "heads";
    const label = isHeads ? "CARA" : "COROA";

    $("resultCoinText").textContent = isHeads ? ":D" : "W";
    $("resultText").textContent = `Deu ${label}.`;

    $("resultCoin").classList.remove("reveal");
    void $("resultCoin").offsetWidth;
    $("resultCoin").classList.add("reveal");
}

function showFinishScreen(hostScore, guestScore) {
    const playerWon =
        (role === "host" && hostScore > guestScore) ||
        (role === "guest" && guestScore > hostScore);

    $("winnerTitle").textContent = playerWon ? "Você venceu!" : "Você perdeu!";
    $("winnerDescription").textContent =
        playerWon
            ? "Você alcançou a pontuação necessária para vencer a partida."
            : "O outro jogador alcançou a pontuação necessária para vencer.";

    $("rematchStatus").textContent = "Quer jogar novamente?";
    $("acceptRematchButton").disabled = false;
    $("declineRematchButton").disabled = false;
    $("acceptRematchButton").classList.remove("hidden");
    $("declineRematchButton").classList.remove("hidden");
    $("newConnectionButton").classList.add("hidden");

    showScreen("finish");
}

function startRematch() {
    resetScores();
    hasChosen = false;
    clearChoiceSelection();

    $("rematchStatus").textContent = "O rematch foi aceito. Nova partida iniciada.";
    setChoiceButtonsEnabled(true);
    $("waitingChoice").classList.add("hidden");

    showScreen("game");
    setGameStatus("Escolha cara ou coroa.");
}

function resetScores() {
    $("hostScore").textContent = "0";
    $("guestScore").textContent = "0";
    $("finalHostScore").textContent = "0";
    $("finalGuestScore").textContent = "0";
    $("resultCoinText").textContent = "?";
    $("resultText").textContent = "Aguardando resultado";

    $("hostEffect").className = "player-effect hidden";
    $("guestEffect").className = "player-effect hidden";

    $("hostEffect").textContent = "";
    $("guestEffect").textContent = "";
}

function setChoiceButtonsEnabled(enabled) {
    document.querySelectorAll(".choice-button").forEach((button) => {
        button.disabled = !enabled;
    });

    $("waitingChoice").classList.toggle("hidden", enabled);
}

function clearChoiceSelection() {
    document.querySelectorAll(".choice-button").forEach((button) => {
        button.classList.remove("selected");
    });
}

function selectChoice(button) {
    if (hasChosen) {
        return;
    }

    const choice = button.dataset.choice;
    const sent = send({
        type: "coin_choice",
        choice,
    });

    if (!sent) {
        return;
    }

    hasChosen = true;
    clearChoiceSelection();
    button.classList.add("selected");
    setChoiceButtonsEnabled(false);
    setGameStatus("Escolha enviada. Aguardando o outro jogador...");
}

function createRoom() {
    if (!send({ type: "create_room" })) {
        return;
    }

    role = "host";
    showScreen("waiting");
    $("copyFeedback").textContent = "";
}

function joinRoom() {
    const input = $("roomInput");
    const code = input.value.trim().toUpperCase();

    if (code.length !== 6) {
        showToast("Digite um código de sala com 6 caracteres.", "error");
        input.focus();
        return;
    }

    if (!send({
        type: "join_room",
        room_id: code,
    })) {
        return;
    }

    role = "guest";
    roomId = code;
    $("gameRoomCode").textContent = code;
    resetScores();
    showScreen("game");
    setGameStatus("Você entrou na sala. Escolha cara ou coroa.");
    setChoiceButtonsEnabled(true);
}

function requestRematch(accept) {
    $("acceptRematchButton").disabled = true;
    $("declineRematchButton").disabled = true;
    $("rematchStatus").textContent =
        accept
            ? "Você aceitou. Aguardando o outro jogador..."
            : "Você recusou. Encerrando partida...";

    send({
        type: "rematch",
        accept,
    });
}

function finishConnection() {
    roomId = null;
    role = null;
    hasChosen = false;

    if (socket) {
        socket.close();
    }

    resetScores();
    showScreen("home");
    setChoiceButtonsEnabled(true);
}

async function copyRoomCode() {
    if (!roomId) {
        return;
    }

    try {
        await navigator.clipboard.writeText(roomId);
        $("copyFeedback").textContent = "Código copiado!";
    } catch {
        $("copyFeedback").textContent = `Copie manualmente: ${roomId}`;
    }

    setTimeout(() => {
        $("copyFeedback").textContent = "";
    }, 2500);
}

$("createRoomButton").addEventListener("click", createRoom);
$("joinRoomButton").addEventListener("click", joinRoom);

$("roomInput").addEventListener("input", (event) => {
    event.target.value = event.target.value
        .replace(/[^a-zA-Z0-9]/g, "")
        .toUpperCase();
});

$("roomInput").addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
        joinRoom();
    }
});

$("roomCodeButton").addEventListener("click", copyRoomCode);
$("cancelRoomButton").addEventListener("click", finishConnection);

document.querySelectorAll(".choice-button").forEach((button) => {
    button.addEventListener("click", () => selectChoice(button));
});

$("acceptRematchButton").addEventListener("click", () => requestRematch(true));
$("declineRematchButton").addEventListener("click", () => requestRematch(false));

$("newConnectionButton").addEventListener("click", finishConnection);

window.addEventListener("beforeunload", () => {
    if (socket) {
        socket.close();
    }
});

connect();
