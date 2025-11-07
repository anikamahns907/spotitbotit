/**
 * Spot It Bot It - Client-side game logic
 * Handles WebSocket communication and UI updates
 */

class SpotItGame {
    constructor() {
        this.ws = null;
        this.roomCode = null;
        this.playerId = null;
        this.playerName = null;
        this.gameState = null;
        this.timerInterval = null;
        this.soloMode = false;
        
        this.initializeEventListeners();
    }
    
    initializeEventListeners() {
        // Room creation/joining
        document.getElementById('play-solo-btn').addEventListener('click', () => this.playSolo());
        document.getElementById('create-room-btn').addEventListener('click', () => this.createRoom());
        document.getElementById('join-room-btn').addEventListener('click', () => this.joinRoom());
        document.getElementById('room-code-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.joinRoom();
        });
        
        // Game controls
        document.getElementById('start-game-btn').addEventListener('click', () => this.startGame());
        document.getElementById('submit-guess-btn').addEventListener('click', () => this.submitGuess());
        document.getElementById('guess-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.submitGuess();
        });
        
        // Symbol click handlers (will be added dynamically)
    }
    
    async playSolo() {
        try {
            const response = await fetch('/api/rooms/create?solo=true', { method: 'POST' });
            const data = await response.json();
            this.roomCode = data.room_code;
            this.soloMode = true;
            this.connectWebSocket();
        } catch (error) {
            console.error('Error starting solo game:', error);
            this.showMessage('Error starting solo game. Please try again.', 'error');
        }
    }
    
    async createRoom() {
        try {
            const response = await fetch('/api/rooms/create', { method: 'POST' });
            const data = await response.json();
            this.roomCode = data.room_code;
            this.soloMode = false;
            this.connectWebSocket();
        } catch (error) {
            console.error('Error creating room:', error);
            this.showMessage('Error creating room. Please try again.', 'error');
        }
    }
    
    async joinRoom() {
        const roomCodeInput = document.getElementById('room-code-input');
        const roomCode = roomCodeInput.value.trim().toUpperCase();
        
        if (!roomCode || roomCode.length !== 6) {
            this.showMessage('Please enter a valid 6-character room code.', 'error');
            return;
        }
        
        try {
            const response = await fetch(`/api/rooms/${roomCode}/status`);
            const data = await response.json();
            
            if (data.exists) {
                this.roomCode = roomCode;
                this.connectWebSocket();
            } else {
                this.showMessage('Room not found. Please check the room code.', 'error');
            }
        } catch (error) {
            this.showMessage('Room not found. Please check the room code.', 'error');
        }
    }
    
    connectWebSocket() {
        if (!this.roomCode) return;
        
        // Automatically use wss:// for HTTPS, ws:// for HTTP
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/${this.roomCode}`;
        
        console.log('Connecting to:', wsUrl);
        this.ws = new WebSocket(wsUrl);
        
        this.ws.onopen = () => {
            console.log('WebSocket connected');
        };
        
        this.ws.onmessage = (event) => {
            const message = JSON.parse(event.data);
            this.handleMessage(message);
        };
        
        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.showMessage('Connection error. Please try again.', 'error');
        };
        
        this.ws.onclose = () => {
            console.log('WebSocket disconnected');
            this.showMessage('Connection lost. Please refresh the page.', 'error');
        };
    }
    
    handleMessage(message) {
        console.log('Received message:', message);
        
        switch (message.type) {
            case 'connected':
                this.playerId = message.player_id;
                this.playerName = message.player_name;
                this.roomCode = message.room_code;
                this.updateRoomInfo();
                break;
                
            case 'player_joined':
            case 'state_update':
                this.gameState = message.state;
                this.updateUI();
                break;
                
            case 'room_full':
                this.showMessage(message.message, 'info');
                break;
                
            case 'room_ready':
                this.showMessage(message.message, 'info');
                break;
                
            case 'game_started':
                this.gameState = message.state;
                this.showGameScreen();
                this.updateCards();
                this.startTimer();
                break;
                
            case 'new_round':
                this.gameState = message.state;
                this.updateCards();
                this.clearMessage();
                this.startTimer();
                break;
                
            case 'match_found':
                this.gameState = message.state;
                const winnerName = message.player_name;
                const match = message.match;
                if (message.solo_mode) {
                    this.showMessage(`🎉 You found it! "${match}" - Great job! Score: ${this.gameState.scores[this.playerId] || 0}`, 'success');
                    this.playSound('win');
                } else if (this.playerId === message.player_id) {
                    this.showMessage(`🎉 You found it! "${match}" - You win this round!`, 'success');
                    this.playSound('win');
                } else {
                    this.showMessage(`😔 ${winnerName} found "${match}" first!`, 'error');
                }
                this.updateScores();
                break;
                
            case 'wrong_guess':
                this.showMessage(message.message, 'error');
                break;
                
            case 'round_expired':
                this.showMessage(message.message, 'info');
                this.gameState = message.state;
                this.updateCards();
                this.startTimer();
                break;
                
            case 'player_left':
                this.gameState = message.state;
                this.updateUI();
                this.showMessage('A player left the game.', 'info');
                break;
        }
    }
    
    updateRoomInfo() {
        document.getElementById('display-room-code').textContent = this.roomCode;
        document.getElementById('room-info').classList.remove('hidden');
        
        if (this.gameState) {
            this.updateUI();
        }
    }
    
    updateUI() {
        if (!this.gameState) return;
        
        // Update player count
        const playerCount = Object.keys(this.gameState.players || {}).length;
        document.getElementById('player-count').textContent = 
            `${playerCount}/2 players connected`;
        
        // Update scores
        if (this.gameState.scores) {
            const playerIds = Object.keys(this.gameState.players || {});
            if (playerIds.length >= 1) {
                const pid1 = playerIds[0];
                document.getElementById('player1-name').textContent = this.gameState.players[pid1];
                document.getElementById('player1-score').textContent = this.gameState.scores[pid1] || 0;
            }
            if (playerIds.length >= 2) {
                const pid2 = playerIds[1];
                document.getElementById('player2-name').textContent = this.gameState.players[pid2];
                document.getElementById('player2-score').textContent = this.gameState.scores[pid2] || 0;
            }
        }
        
        // Show/hide start button
        const startBtn = document.getElementById('start-game-btn');
        if (this.gameState.is_full && !this.gameState.game_started) {
            startBtn.style.display = 'block';
        } else {
            startBtn.style.display = 'none';
        }
        
        // Update solo mode indicator
        if (this.gameState.solo_mode) {
            this.soloMode = true;
            document.getElementById('solo-mode-indicator').classList.remove('hidden');
        }
    }
    
    showGameScreen() {
        document.getElementById('room-screen').classList.remove('active');
        document.getElementById('game-screen').classList.add('active');
        document.getElementById('current-room-code').textContent = this.roomCode;
        document.getElementById('game-content').classList.remove('hidden');
        
        // Show solo mode indicator if in solo mode
        if (this.soloMode || (this.gameState && this.gameState.solo_mode)) {
            document.getElementById('solo-mode-indicator').classList.remove('hidden');
        }
    }
    
    startGame() {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({ type: 'start_game' }));
        }
    }
    
    updateCards() {
        if (!this.gameState || !this.gameState.current_cards) return;
        
        const myCards = this.gameState.current_cards[this.playerId];
        if (!myCards || myCards.length < 2) return;
        
        // Update card 1
        const symbols1 = document.getElementById('symbols1');
        symbols1.innerHTML = '';
        myCards[0].forEach(symbol => {
            const symbolEl = this.createSymbolElement(symbol);
            symbols1.appendChild(symbolEl);
        });
        
        // Update card 2
        const symbols2 = document.getElementById('symbols2');
        symbols2.innerHTML = '';
        myCards[1].forEach(symbol => {
            const symbolEl = this.createSymbolElement(symbol);
            symbols2.appendChild(symbolEl);
        });
        
        // Clear guess input
        document.getElementById('guess-input').value = '';
        document.getElementById('guess-input').focus();
    }
    
    createSymbolElement(symbol) {
        const div = document.createElement('div');
        div.className = 'symbol';
        div.textContent = symbol;
        div.addEventListener('click', () => {
            document.getElementById('guess-input').value = symbol;
            this.submitGuess();
        });
        return div;
    }
    
    submitGuess() {
        const guessInput = document.getElementById('guess-input');
        const guess = guessInput.value.trim();
        
        if (!guess) {
            this.showMessage('Please enter a guess!', 'error');
            return;
        }
        
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({
                type: 'guess',
                guess: guess
            }));
        }
    }
    
    startTimer() {
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
        }
        
        if (!this.gameState || !this.gameState.round_timer) return;
        
        const updateTimer = () => {
            const timerEl = document.getElementById('timer');
            if (!this.gameState || !this.gameState.round_timer) return;
            
            const endTime = new Date(this.gameState.round_timer);
            const now = new Date();
            const remaining = Math.max(0, Math.ceil((endTime - now) / 1000));
            
            timerEl.textContent = remaining;
            
            if (remaining === 0) {
                clearInterval(this.timerInterval);
            }
        };
        
        updateTimer();
        this.timerInterval = setInterval(updateTimer, 1000);
    }
    
    updateScores() {
        if (!this.gameState) return;
        
        const playerIds = Object.keys(this.gameState.players || {});
        if (playerIds.length >= 1) {
            const pid1 = playerIds[0];
            document.getElementById('player1-score').textContent = this.gameState.scores[pid1] || 0;
        }
        if (playerIds.length >= 2) {
            const pid2 = playerIds[1];
            document.getElementById('player2-score').textContent = this.gameState.scores[pid2] || 0;
        }
    }
    
    showMessage(text, type = 'info') {
        const messageEl = document.getElementById('game-message');
        messageEl.textContent = text;
        messageEl.className = `game-message ${type}`;
        
        // Auto-hide after 5 seconds for info messages
        if (type === 'info') {
            setTimeout(() => this.clearMessage(), 5000);
        }
    }
    
    clearMessage() {
        const messageEl = document.getElementById('game-message');
        messageEl.textContent = '';
        messageEl.className = 'game-message';
    }
    
    playSound(type) {
        // Laugh track sound effect using Web Audio API
        // Creates a cheerful "laugh" sound when someone wins
        if (type === 'win') {
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            
            // Create a sequence of notes for a "laugh" effect
            const notes = [523.25, 659.25, 783.99, 987.77]; // C5, E5, G5, B5
            let currentTime = audioContext.currentTime;
            
            notes.forEach((freq, index) => {
                const oscillator = audioContext.createOscillator();
                const gainNode = audioContext.createGain();
                
                oscillator.connect(gainNode);
                gainNode.connect(audioContext.destination);
                
                oscillator.frequency.value = freq;
                oscillator.type = 'sine';
                
                const noteDuration = 0.15;
                gainNode.gain.setValueAtTime(0, currentTime);
                gainNode.gain.linearRampToValueAtTime(0.2, currentTime + 0.01);
                gainNode.gain.exponentialRampToValueAtTime(0.01, currentTime + noteDuration);
                
                oscillator.start(currentTime);
                oscillator.stop(currentTime + noteDuration);
                
                currentTime += noteDuration * 0.8; // Overlap notes slightly
            });
        }
    }
}

// Initialize game when page loads
document.addEventListener('DOMContentLoaded', () => {
    window.game = new SpotItGame();
});

