# Network Chess Game - Python Client

## File Structure

```
ui/
├── network_client.py    - TCP Socket client (ChessClient class)
├── chess_board.py       - Chess board logic and rendering
├── gui_main.py          - Main GUI application
├── gui_handlers.py      - GUI event handlers
├── gui_callbacks.py     - Network callbacks
└── main.py              - Entry point
```

## Running the Application

```bash
cd ui
python main.py
```

## Module Descriptions

### network_client.py
- TCP socket connection management
- JSON message send/receive
- Game actions (login, register, move, challenge, etc.)

### chess_board.py
- Chess board state management
- Board rendering on Tkinter canvas
- Move validation and piece management

### gui_main.py
- Main GUI window setup
- UI component initialization
- Event binding

### gui_handlers.py
- Button click handlers
- User input processing
- UI state management

### gui_callbacks.py
- Network message handlers
- Server response processing
- UI updates from server events

## Benefits of Modular Structure

1. **Easier Debugging** - Each module has specific responsibility
2. **Maintainability** - Changes in one module don't affect others
3. **Reusability** - Can reuse network_client.py in other projects
4. **Testability** - Each module can be tested independently
5. **Collaboration** - Multiple developers can work on different modules
