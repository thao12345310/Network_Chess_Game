// chess.js - Chess board representation and piece logic

// Unicode chess pieces
const PIECES = {
    'K': '♔', 'Q': '♕', 'R': '♖', 'B': '♗', 'N': '♘', 'P': '♙',  // White
    'k': '♚', 'q': '♛', 'r': '♜', 'b': '♝', 'n': '♞', 'p': '♟'   // Black
};

// Initial chess board in FEN notation
const INITIAL_FEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1';

class ChessBoard {
    constructor() {
        this.board = [];
        this.selectedSquare = null;
        this.currentTurn = 'w'; // 'w' or 'b'
        this.fen = INITIAL_FEN;
        this.initBoard();
    }

    initBoard() {
        // Initialize empty 8x8 board
        this.board = Array(8).fill(null).map(() => Array(8).fill(null));
        this.parseFEN(this.fen);
    }

    parseFEN(fen) {
        const parts = fen.split(' ');
        const position = parts[0];
        this.currentTurn = parts[1];

        const ranks = position.split('/');
        for (let rank = 0; rank < 8; rank++) {
            let file = 0;
            for (let char of ranks[rank]) {
                if (isNaN(char)) {
                    // It's a piece
                    this.board[rank][file] = char;
                    file++;
                } else {
                    // It's a number of empty squares
                    file += parseInt(char);
                }
            }
        }
    }

    getPiece(row, col) {
        if (row < 0 || row > 7 || col < 0 || col > 7) return null;
        return this.board[row][col];
    }

    setPiece(row, col, piece) {
        if (row < 0 || row > 7 || col < 0 || col > 7) return;
        this.board[row][col] = piece;
    }

    movePiece(fromRow, fromCol, toRow, toCol) {
        const piece = this.getPiece(fromRow, fromCol);
        if (!piece) return false;

        this.setPiece(toRow, toCol, piece);
        this.setPiece(fromRow, fromCol, null);
        this.currentTurn = this.currentTurn === 'w' ? 'b' : 'w';
        return true;
    }

    isValidPiece(row, col) {
        const piece = this.getPiece(row, col);
        if (!piece) return false;

        // Check if piece color matches current turn
        const isWhite = piece === piece.toUpperCase();
        return (isWhite && this.currentTurn === 'w') || (!isWhite && this.currentTurn === 'b');
    }

    boardToFEN() {
        let fen = '';
        for (let rank = 0; rank < 8; rank++) {
            let empty = 0;
            for (let file = 0; file < 8; file++) {
                const piece = this.board[rank][file];
                if (piece) {
                    if (empty > 0) {
                        fen += empty;
                        empty = 0;
                    }
                    fen += piece;
                } else {
                    empty++;
                }
            }
            if (empty > 0) fen += empty;
            if (rank < 7) fen += '/';
        }
        fen += ` ${this.currentTurn} KQkq - 0 1`;
        return fen;
    }

    positionToNotation(row, col) {
        const files = 'abcdefgh';
        const ranks = '87654321';
        return files[col] + ranks[row];
    }

    notationToPosition(notation) {
        const files = 'abcdefgh';
        const ranks = '87654321';
        const col = files.indexOf(notation[0]);
        const row = ranks.indexOf(notation[1]);
        return { row, col };
    }
}

// Export for use in app.js
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { ChessBoard, PIECES };
}
