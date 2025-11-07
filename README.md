# Spot It Bot It - Online Two-Player Game

A two-player online version of the classic "Spot It" game with funny custom objects!

## Features

- 🎮 Two-player online gameplay over the internet
- 🎯 Real-time WebSocket communication
- 😂 Custom funny objects instead of original symbols
- ⏱️ Round timer (optional)
- 🔊 Sound effects (optional)
- 🎨 Simple, clean web interface

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
python main.py
```

The server will start on `http://0.0.0.0:8000` (accessible from any computer on your network).

3. Open your browser to:
   - Local: `http://localhost:8000`
   - From another computer: `http://YOUR_IP_ADDRESS:8000` (replace with your server's IP)

4. **How to Play:**
   - **Player 1:** Click "Create Room" and share the room code with your friend
   - **Player 2:** Enter the room code and click "Join Room"
   - Once both players are connected, click "Start Game"
   - Find the matching object between the two cards!
   - Type or click the matching object name to score a point
   - First player to find the match wins the round

## Customization

- Edit `funny_objects.txt` to change the list of objects
- Modify `game_logic.py` to adjust game rules
- Update `static/style.css` and `templates/index.html` for UI changes

## How It Works

The game uses a mathematical structure to ensure every pair of cards shares exactly one matching symbol. Each card displays 8 randomly chosen objects, and players race to find the match between their cards.

### Game Features

- **Real-time WebSocket Communication:** Players see updates instantly
- **15-Second Round Timer:** Each round has a time limit
- **Sound Effects:** Cheerful "laugh track" sound when someone wins
- **Live Score Tracking:** Scores update in real-time for both players
- **Click or Type:** You can click on symbols or type the match name

### Technical Details

- **Backend:** FastAPI with WebSocket support
- **Frontend:** HTML, CSS, and vanilla JavaScript
- **Card Generation:** Mathematical algorithm ensures every pair shares exactly one symbol
- **Room System:** 6-character room codes for easy joining

### Customization Tips

- **Change Objects:** Edit `funny_objects.txt` - one object per line
- **Adjust Timer:** Modify `round_duration` in `main.py` (GameRoom class)
- **Sound Effects:** Replace the Web Audio API code in `static/game.js` with actual sound files
- **Styling:** Customize colors and layout in `static/style.css`

