"""
Main FastAPI application for Spot It Bot It game.

Handles HTTP routes and WebSocket connections for two-player online gameplay.
"""

import asyncio
import json
import random
import string
from typing import Dict, Set, Optional
from datetime import datetime, timedelta

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from game_logic import SpotItGame, load_symbols

app = FastAPI(title="Spot It Bot It")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Game state management
class GameRoom:
    """Represents a game room with players and game state."""
    
    def __init__(self, room_code: str):
        self.room_code = room_code
        self.players: Dict[str, WebSocket] = {}  # player_id -> websocket
        self.player_names: Dict[str, str] = {}  # player_id -> player_name
        self.scores: Dict[str, int] = {}  # player_id -> score
        self.current_cards: Dict[str, list] = {}  # player_id -> [card1, card2]
        self.current_match: Optional[str] = None  # The matching symbol
        self.game_started = False
        self.round_timer: Optional[datetime] = None
        self.round_duration = 15  # seconds
        self.game = None
        self.winner: Optional[str] = None  # player_id who found the match
        self.solo_mode = False  # Single player mode
        
    def add_player(self, player_id: str, websocket: WebSocket, player_name: str, solo_mode: bool = False):
        """Add a player to the room."""
        if not solo_mode and len(self.players) >= 2:
            raise ValueError("Room is full (max 2 players)")
        self.players[player_id] = websocket
        self.player_names[player_id] = player_name
        self.scores[player_id] = 0
        self.solo_mode = solo_mode
    
    def remove_player(self, player_id: str):
        """Remove a player from the room."""
        self.players.pop(player_id, None)
        self.player_names.pop(player_id, None)
        self.scores.pop(player_id, None)
        self.current_cards.pop(player_id, None)
    
    def is_full(self) -> bool:
        """Check if room has 2 players (or ready for solo mode)."""
        if self.solo_mode:
            return len(self.players) >= 1
        return len(self.players) == 2
    
    def start_game(self):
        """Initialize the game with symbols."""
        symbols = load_symbols()
        self.game = SpotItGame(symbols, symbols_per_card=8)
        self.game_started = True
    
    def start_round(self):
        """Start a new round with two cards."""
        if not self.game:
            self.start_game()
        
        card1, card2 = self.game.get_two_cards()
        self.current_match = self.game.find_match(card1, card2)
        
        # Assign cards to players (each sees both cards)
        player_ids = list(self.players.keys())
        if len(player_ids) == 2:
            # Shuffle cards so players see different arrangements
            self.current_cards[player_ids[0]] = [card1.copy(), card2.copy()]
            self.current_cards[player_ids[1]] = [card2.copy(), card1.copy()]
        else:
            # Single player (for testing)
            self.current_cards[player_ids[0]] = [card1.copy(), card2.copy()]
        
        self.round_timer = datetime.now() + timedelta(seconds=self.round_duration)
        self.winner = None
    
    def check_match(self, player_id: str, guess: str) -> bool:
        """Check if player's guess matches the current round's match."""
        if not self.current_match:
            return False
        
        # Normalize guess (case-insensitive, strip whitespace)
        normalized_guess = guess.strip().lower()
        normalized_match = self.current_match.strip().lower()
        
        if normalized_guess == normalized_match:
            if not self.winner:  # First to find it wins
                self.winner = player_id
                self.scores[player_id] = self.scores.get(player_id, 0) + 1
                return True
        return False
    
    def is_round_over(self) -> bool:
        """Check if round timer has expired."""
        if not self.round_timer:
            return False
        return datetime.now() >= self.round_timer
    
    def get_state(self) -> dict:
        """Get current game state."""
        return {
            "room_code": self.room_code,
            "players": {pid: self.player_names[pid] for pid in self.players.keys()},
            "scores": self.scores.copy(),
            "game_started": self.game_started,
            "current_cards": self.current_cards.copy(),
            "round_timer": self.round_timer.isoformat() if self.round_timer else None,
            "round_duration": self.round_duration,
            "winner": self.winner,
            "is_full": self.is_full(),
            "solo_mode": self.solo_mode
        }


# Global room management
rooms: Dict[str, GameRoom] = {}


def generate_room_code() -> str:
    """Generate a random 6-character room code."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))


@app.get("/")
async def home():
    """Serve the main game page."""
    return FileResponse("templates/index.html")


@app.get("/api/rooms/{room_code}/status")
async def get_room_status(room_code: str):
    """Get room status (for checking if room exists)."""
    room = rooms.get(room_code.upper())
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return {
        "exists": True,
        "is_full": room.is_full(),
        "player_count": len(room.players)
    }


@app.post("/api/rooms/create")
async def create_room(solo: bool = Query(False)):
    """Create a new game room."""
    room_code = generate_room_code()
    while room_code in rooms:
        room_code = generate_room_code()
    
    room = GameRoom(room_code)
    if solo:
        room.solo_mode = True
    rooms[room_code] = room
    return {"room_code": room_code, "solo_mode": solo}


@app.websocket("/ws/{room_code}")
async def websocket_endpoint(websocket: WebSocket, room_code: str):
    """Handle WebSocket connections for game rooms."""
    await websocket.accept()
    
    room_code = room_code.upper()
    room = rooms.get(room_code)
    
    if not room:
        await websocket.send_json({"type": "error", "message": "Room not found"})
        await websocket.close()
        return
    
    # Generate player ID
    player_id = f"player_{len(room.players) + 1}"
    player_name = "Solo Player" if room.solo_mode else f"Player {len(room.players) + 1}"
    
    try:
        # Add player to room
        room.add_player(player_id, websocket, player_name, solo_mode=room.solo_mode)
        
        # Notify player of connection
        await websocket.send_json({
            "type": "connected",
            "player_id": player_id,
            "player_name": player_name,
            "room_code": room_code
        })
        
        # Broadcast to other players
        await broadcast_to_room(room, {
            "type": "player_joined",
            "player_id": player_id,
            "player_name": player_name,
            "state": room.get_state()
        }, exclude_player=player_id)
        
        # Send current state to new player
        await websocket.send_json({
            "type": "state_update",
            "state": room.get_state()
        })
        
        # If room is ready (full for multiplayer, or solo mode)
        if room.is_full():
            if room.solo_mode:
                await websocket.send_json({
                    "type": "room_ready",
                    "message": "Ready to play solo! Click Start Game."
                })
            else:
                await broadcast_to_room(room, {
                    "type": "room_full",
                    "message": "Both players connected! Ready to start."
                })
        
        # Main message loop
        while True:
            data = await websocket.receive_json()
            message_type = data.get("type")
            
            if message_type == "start_game":
                if room.is_full() and not room.game_started:
                    room.start_game()
                    room.start_round()
                    await broadcast_to_room(room, {
                        "type": "game_started",
                        "state": room.get_state()
                    })
            
            elif message_type == "guess":
                guess = data.get("guess", "").strip()
                if guess and room.current_match:
                    is_correct = room.check_match(player_id, guess)
                    if is_correct:
                        # Player found the match!
                        if room.solo_mode:
                            # Solo mode: just notify the player
                            await websocket.send_json({
                                "type": "match_found",
                                "player_id": player_id,
                                "player_name": player_name,
                                "match": room.current_match,
                                "state": room.get_state(),
                                "solo_mode": True
                            })
                        else:
                            # Multiplayer: broadcast to all
                            await broadcast_to_room(room, {
                                "type": "match_found",
                                "player_id": player_id,
                                "player_name": player_name,
                                "match": room.current_match,
                                "state": room.get_state()
                            })
                        
                        # Wait a bit, then start next round
                        await asyncio.sleep(3)
                        room.start_round()
                        if room.solo_mode:
                            await websocket.send_json({
                                "type": "new_round",
                                "state": room.get_state()
                            })
                        else:
                            await broadcast_to_room(room, {
                                "type": "new_round",
                                "state": room.get_state()
                            })
                    else:
                        # Wrong guess
                        await websocket.send_json({
                            "type": "wrong_guess",
                            "message": "That's not the match! Keep looking."
                        })
            
            elif message_type == "next_round":
                if room.game_started:
                    room.start_round()
                    await broadcast_to_room(room, {
                        "type": "new_round",
                        "state": room.get_state()
                    })
            
            elif message_type == "ping":
                await websocket.send_json({"type": "pong"})
    
    except WebSocketDisconnect:
        room.remove_player(player_id)
        await broadcast_to_room(room, {
            "type": "player_left",
            "player_id": player_id,
            "state": room.get_state()
        })
        
        # Clean up empty rooms after 5 minutes
        if len(room.players) == 0:
            await asyncio.sleep(300)  # 5 minutes
            if len(room.players) == 0:
                rooms.pop(room_code, None)


async def broadcast_to_room(room: GameRoom, message: dict, exclude_player: Optional[str] = None):
    """Broadcast a message to all players in a room."""
    disconnected = []
    for player_id, ws in room.players.items():
        if player_id != exclude_player:
            try:
                await ws.send_json(message)
            except:
                disconnected.append(player_id)
    
    # Remove disconnected players
    for player_id in disconnected:
        room.remove_player(player_id)


# Background task to check round timers
async def check_round_timers():
    """Periodically check if rounds have expired."""
    while True:
        await asyncio.sleep(1)
        for room_code, room in list(rooms.items()):
            if room.game_started and room.round_timer and room.is_round_over() and not room.winner:
                # Round expired, no winner
                room.start_round()
                await broadcast_to_room(room, {
                    "type": "round_expired",
                    "message": "Time's up! Starting new round.",
                    "state": room.get_state()
                })


@app.on_event("startup")
async def startup_event():
    """Start background tasks on server startup."""
    asyncio.create_task(check_round_timers())


if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

