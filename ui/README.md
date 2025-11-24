# Chess Game UI

Web-based chess interface for Network Chess Game.

## Features

✅ **Interactive Chess Board**
- 8x8 grid with light/dark squares
- Unicode chess pieces (♔♕♖♗♘♙)
- Click to select and move pieces
- Visual highlights for selected squares

✅ **User Interface**
- Login/Register system
- Player information display
- Online players list
- Move history tracker
- Game log/chat

✅ **Game Controls**
- Resign game
- Offer draw
- Start new game
- View match history

✅ **Responsive Design**
- Works on desktop and tablet
- Mobile-friendly layout
- Beautiful gradient background

## How to Run

### Option 1: Simple HTTP Server (Python)

```bash
cd ui
python -m http.server 8000
```

Then open: `http://localhost:8000`

### Option 2: Live Server (VS Code Extension)

1. Install "Live Server" extension
2. Right-click `index.html`
3. Select "Open with Live Server"

### Option 3: Direct File

Just open `index.html` in your browser (drag and drop)

## File Structure

```
ui/
├── index.html      # Main HTML structure
├── styles.css      # CSS styling and layout
├── chess.js        # Chess board logic and FEN parser
└── app.js          # Application logic and server communication
```

## Server Connection

**Important:** The current implementation uses mock/simulated server responses for testing the UI.

To connect to real C++ server, you need to:

1. **Add HTTP/WebSocket support to server** OR
2. **Create a bridge service** (Node.js/Python) that:
   - Connects to C++ TCP server
   - Exposes WebSocket/HTTP API for browser

### Example Bridge (Node.js)

```javascript
const net = require('net');
const WebSocket = require('ws');

const wss = new WebSocket.Server({ port: 8080 });
const tcpClient = net.connect(5001, '127.0.0.1');

wss.on('connection', (ws) => {
    ws.on('message', (data) => {
        tcpClient.write(data + '\n');
    });
    
    tcpClient.on('data', (data) => {
        ws.send(data.toString());
    });
});
```

## Usage

1. **Start the server** (C++ game logic server on port 5001)
2. **Open UI** in browser
3. **Register/Login** with username and password
4. **Challenge player** from online list
5. **Play chess!** Click pieces to move

## Screenshots

### Main Game Screen
- Left panel: Login and player list
- Center: Interactive chess board
- Right panel: Move history and game log

### Features Demo
- Drag and drop pieces
- Real-time move validation
- Beautiful animations and transitions

## Technologies Used

- **HTML5** - Structure
- **CSS3** - Styling and animations
- **Vanilla JavaScript** - Game logic (no frameworks!)
- **Unicode Characters** - Chess pieces (no images needed!)

## Future Improvements

- [ ] WebSocket real-time communication
- [ ] Timer/clock for timed games
- [ ] Sound effects for moves
- [ ] Captured pieces display
- [ ] Game replay feature
- [ ] Rating chart/statistics
- [ ] Multiple board themes

## Browser Compatibility

✅ Chrome/Edge (recommended)
✅ Firefox
✅ Safari
⚠️ IE11 (not supported)

## License

Part of Network Chess Game project
