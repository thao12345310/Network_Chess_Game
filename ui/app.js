// app.js - Main application logic and server communication

class ChessApp {
    constructor() {
        this.chess = new ChessBoard();
        this.socket = null;
        this.sessionToken = null;
        this.gameId = null;
        this.username = null;
        this.selectedSquare = null;
        this.moves = [];

        this.initUI();
        this.attachEventListeners();
    }

    initUI() {
        this.renderBoard();
        this.updateConnectionStatus(false);
    }

    renderBoard() {
        const boardElement = document.getElementById('chess-board');
        boardElement.innerHTML = '';

        for (let row = 0; row < 8; row++) {
            for (let col = 0; col < 8; col++) {
                const square = document.createElement('div');
                square.className = 'square';
                square.className += (row + col) % 2 === 0 ? ' light' : ' dark';
                square.dataset.row = row;
                square.dataset.col = col;

                const piece = this.chess.getPiece(row, col);
                if (piece) {
                    square.textContent = PIECES[piece];
                }

                square.addEventListener('click', () => this.handleSquareClick(row, col));
                boardElement.appendChild(square);
            }
        }
    }

    handleSquareClick(row, col) {
        const square = document.querySelector(`[data-row="${row}"][data-col="${col}"]`);

        if (this.selectedSquare) {
            // Try to move
            const fromRow = this.selectedSquare.row;
            const fromCol = this.selectedSquare.col;

            this.clearHighlights();
            this.sendMove(fromRow, fromCol, row, col);
            this.selectedSquare = null;
        } else {
            // Select piece
            if (this.chess.isValidPiece(row, col)) {
                this.clearHighlights();
                this.selectedSquare = { row, col };
                square.classList.add('selected');
            }
        }
    }

    clearHighlights() {
        document.querySelectorAll('.square').forEach(sq => {
            sq.classList.remove('selected', 'highlight', 'valid-move');
        });
    }

    // Server Communication
    connectToServer() {
        const serverURL = 'ws://127.0.0.1:5001';

        try {
            // Note: Your C++ server uses TCP, not WebSocket
            // For web UI, we'll need to add WebSocket support to server
            // or use HTTP polling
            this.logMessage('Connecting to server...', 'info');

            // For now, simulate connection
            setTimeout(() => {
                this.updateConnectionStatus(true);
                this.logMessage('Connected to server!', 'success');
            }, 500);

        } catch (error) {
            this.logMessage('Connection failed: ' + error.message, 'error');
            this.updateConnectionStatus(false);
        }
    }

    login() {
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;

        if (!username || !password) {
            this.logMessage('Please enter username and password', 'error');
            return;
        }

        // Send login request
        this.sendToServer({
            type: 'LOGIN',
            username: username,
            password: password,
            timestamp: Date.now()
        });

        this.username = username;
    }

    register() {
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;

        if (!username || !password) {
            this.logMessage('Please enter username and password', 'error');
            return;
        }

        this.sendToServer({
            type: 'REGISTER',
            username: username,
            password: password,
            email: username + '@chess.local',
            timestamp: Date.now()
        });
    }

    logout() {
        this.sendToServer({
            type: 'LOGOUT',
            session_token: this.sessionToken
        });

        this.sessionToken = null;
        this.username = null;
        this.showLoginSection();
    }

    sendMove(fromRow, fromCol, toRow, toCol) {
        const from = this.chess.positionToNotation(fromRow, fromCol);
        const to = this.chess.positionToNotation(toRow, toCol);

        this.sendToServer({
            type: 'MOVE',
            game_id: this.gameId,
            from: from,
            to: to,
            session_token: this.sessionToken,
            timestamp: Date.now()
        });

        // Optimistically update UI
        if (this.chess.movePiece(fromRow, fromCol, toRow, toCol)) {
            this.renderBoard();
            this.addMoveToHistory(from, to);
        }
    }

    sendToServer(message) {
        // For TCP server, we need a different approach
        // This is a placeholder - you'll need to implement HTTP API or WebSocket
        console.log('Sending to server:', message);
        this.logMessage(`Sent: ${message.type}`, 'info');

        // Simulate server responses for testing UI
        this.simulateServerResponse(message);
    }

    simulateServerResponse(request) {
        setTimeout(() => {
            switch (request.type) {
                case 'LOGIN':
                    this.handleLoginResponse({
                        type: 'LOGIN_SUCCESS',
                        username: request.username,
                        session_token: 'mock-token-' + Date.now(),
                        elo: 1200
                    });
                    break;
                case 'REGISTER':
                    this.handleLoginResponse({
                        type: 'REGISTER_SUCCESS',
                        username: request.username,
                        session_token: 'mock-token-' + Date.now()
                    });
                    break;
            }
        }, 300);
    }

    handleLoginResponse(response) {
        if (response.type === 'LOGIN_SUCCESS' || response.type === 'REGISTER_SUCCESS') {
            this.sessionToken = response.session_token;
            this.username = response.username;
            this.showPlayerInfo();
            this.logMessage(`Welcome, ${this.username}!`, 'success');

            document.getElementById('player-username').textContent = this.username;
            if (response.elo) {
                document.getElementById('player-elo').textContent = response.elo;
            }
        } else {
            this.logMessage('Login failed: ' + (response.message || 'Unknown error'), 'error');
        }
    }

    // UI Updates
    updateConnectionStatus(connected) {
        const statusElement = document.getElementById('connection-status');
        if (connected) {
            statusElement.textContent = 'Connected';
            statusElement.className = 'status connected';
        } else {
            statusElement.textContent = 'Disconnected';
            statusElement.className = 'status disconnected';
        }
    }

    showLoginSection() {
        document.getElementById('login-section').classList.remove('hidden');
        document.getElementById('player-info').classList.add('hidden');
        document.getElementById('online-players').classList.add('hidden');
    }

    showPlayerInfo() {
        document.getElementById('login-section').classList.add('hidden');
        document.getElementById('player-info').classList.remove('hidden');
        document.getElementById('online-players').classList.remove('hidden');
    }

    addMoveToHistory(from, to) {
        const moveHistory = document.getElementById('move-history');
        const moveNumber = Math.floor(this.moves.length / 2) + 1;
        const isWhite = this.moves.length % 2 === 0;

        this.moves.push({ from, to });

        if (isWhite) {
            const entry = document.createElement('div');
            entry.className = 'move-entry';
            entry.innerHTML = `<span class="move-number">${moveNumber}.</span> ${from}→${to}`;
            moveHistory.appendChild(entry);
        } else {
            const lastEntry = moveHistory.lastElementChild;
            lastEntry.innerHTML += ` ${from}→${to}`;
        }

        moveHistory.scrollTop = moveHistory.scrollHeight;
    }

    logMessage(message, type = 'info') {
        const logElement = document.getElementById('game-log');
        const entry = document.createElement('p');
        entry.className = `log-entry ${type}`;
        entry.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
        logElement.appendChild(entry);
        logElement.scrollTop = logElement.scrollHeight;
    }

    // Event Listeners
    attachEventListeners() {
        // Login/Register
        document.getElementById('login-btn').addEventListener('click', () => this.login());
        document.getElementById('register-btn').addEventListener('click', () => this.register());
        document.getElementById('logout-btn').addEventListener('click', () => this.logout());

        // Game Controls
        document.getElementById('resign-btn').addEventListener('click', () => this.resign());
        document.getElementById('draw-btn').addEventListener('click', () => this.offerDraw());
        document.getElementById('new-game-btn').addEventListener('click', () => this.newGame());

        // Players
        document.getElementById('refresh-players-btn').addEventListener('click', () => this.refreshPlayers());

        // Enter key for login
        document.getElementById('password').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.login();
        });

        // Connect on load
        this.connectToServer();
    }

    resign() {
        if (confirm('Are you sure you want to resign?')) {
            this.sendToServer({
                type: 'RESIGN',
                game_id: this.gameId,
                session_token: this.sessionToken
            });
            this.logMessage('You resigned.', 'error');
        }
    }

    offerDraw() {
        this.sendToServer({
            type: 'OFFER_DRAW',
            game_id: this.gameId,
            session_token: this.sessionToken
        });
        this.logMessage('Draw offer sent.', 'info');
    }

    newGame() {
        this.chess = new ChessBoard();
        this.selectedSquare = null;
        this.moves = [];
        this.renderBoard();

        const moveHistory = document.getElementById('move-history');
        moveHistory.innerHTML = '<p class="text-muted">No moves yet</p>';

        this.logMessage('New game started!', 'success');
    }

    refreshPlayers() {
        this.sendToServer({
            type: 'GET_PLAYER_LIST',
            session_token: this.sessionToken
        });
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.chessApp = new ChessApp();
});
