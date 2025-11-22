/**
 * Tetris Therapist - Main Game JavaScript
 * Handles canvas rendering, game controls, and API communication
 */

// Game state
let gameState = null;
let gameCanvas, gameCtx;
let nextCanvas, nextCtx;
let heldCanvas, heldCtx;
let gameLoop = null;
let dropTimer = 0;
let lastDropTime = 0;
let therapistRoastTimer = 0;
let therapistRoastInterval = 0;
let gameStarted = false;

// Piece colors (matching backend)
const PIECE_COLORS = {
    'I': '#00f0f0',
    'O': '#f0f000',
    'T': '#a000f0',
    'S': '#00f000',
    'Z': '#f00000',
    'J': '#0000f0',
    'L': '#f0a000',
};

// Tetromino shapes (matching backend)
const TETROMINOES = {
    'I': [
        [[0, 0, 0, 0], [1, 1, 1, 1], [0, 0, 0, 0], [0, 0, 0, 0]],
        [[0, 0, 1, 0], [0, 0, 1, 0], [0, 0, 1, 0], [0, 0, 1, 0]],
        [[0, 0, 0, 0], [0, 0, 0, 0], [1, 1, 1, 1], [0, 0, 0, 0]],
        [[0, 1, 0, 0], [0, 1, 0, 0], [0, 1, 0, 0], [0, 1, 0, 0]]
    ],
    'O': [
        [[1, 1], [1, 1]]
    ],
    'T': [
        [[0, 1, 0], [1, 1, 1], [0, 0, 0]],
        [[0, 1, 0], [0, 1, 1], [0, 1, 0]],
        [[0, 0, 0], [1, 1, 1], [0, 1, 0]],
        [[0, 1, 0], [1, 1, 0], [0, 1, 0]]
    ],
    'S': [
        [[0, 1, 1], [1, 1, 0], [0, 0, 0]],
        [[0, 1, 0], [0, 1, 1], [0, 0, 1]]
    ],
    'Z': [
        [[1, 1, 0], [0, 1, 1], [0, 0, 0]],
        [[0, 0, 1], [0, 1, 1], [0, 1, 0]]
    ],
    'J': [
        [[1, 0, 0], [1, 1, 1], [0, 0, 0]],
        [[0, 1, 1], [0, 1, 0], [0, 1, 0]],
        [[0, 0, 0], [1, 1, 1], [0, 0, 1]],
        [[0, 1, 0], [0, 1, 0], [1, 1, 0]]
    ],
    'L': [
        [[0, 0, 1], [1, 1, 1], [0, 0, 0]],
        [[0, 1, 0], [0, 1, 0], [0, 1, 1]],
        [[0, 0, 0], [1, 1, 1], [1, 0, 0]],
        [[1, 1, 0], [0, 1, 0], [0, 1, 0]]
    ]
};

const BOARD_WIDTH = 10;
const BOARD_HEIGHT = 20;
const CELL_SIZE = 30;

// Initialize game
document.addEventListener('DOMContentLoaded', () => {
    gameCanvas = document.getElementById('game-canvas');
    gameCtx = gameCanvas.getContext('2d');
    nextCanvas = document.getElementById('next-canvas');
    nextCtx = nextCanvas.getContext('2d');
    heldCanvas = document.getElementById('held-canvas');
    heldCtx = heldCanvas.getContext('2d');
    
    setupEventListeners();
    startNewGame();
});

function setupEventListeners() {
    // Keyboard controls
    document.addEventListener('keydown', handleKeyPress);
    
    // Restart/Resume button
    document.getElementById('restart-btn').addEventListener('click', () => {
        if (gameState && gameState.paused) {
            togglePause();
        } else {
            startNewGame();
        }
    });
    
    // Pause menu restart button
    const pauseRestartBtn = document.getElementById('pause-restart-btn');
    if (pauseRestartBtn) {
        pauseRestartBtn.addEventListener('click', () => {
            startNewGame();
        });
    }
}

function handleKeyPress(e) {
    if (!gameStarted || !gameState || gameState.game_over) return;
    
    switch(e.key.toLowerCase()) {
        case 'p':
        case 'escape':
            e.preventDefault();
            togglePause();
            break;
        case 'a':
        case 'arrowleft':
            e.preventDefault();
            if (!gameState.paused) movePiece('left');
            break;
        case 'd':
        case 'arrowright':
            e.preventDefault();
            if (!gameState.paused) movePiece('right');
            break;
        case 's':
        case 'arrowdown':
            e.preventDefault();
            if (!gameState.paused) movePiece('down');
            break;
        case 'w':
        case 'arrowup':
            e.preventDefault();
            if (!gameState.paused) rotatePiece();
            break;
        case ' ':
            e.preventDefault();
            if (!gameState.paused) hardDrop();
            break;
        case 'c':
            e.preventDefault();
            if (!gameState.paused) holdPiece();
            break;
    }
}

async function togglePause() {
    if (!gameState || gameState.game_over) return;
    
    try {
        const response = await fetch('/api/pause/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCsrfToken(),
                'Content-Type': 'application/json',
            },
        });
        
        const data = await response.json();
        if (data.success) {
            gameState = data.game_state;
            updatePauseDisplay();
        }
    } catch (error) {
        console.error('Error toggling pause:', error);
    }
}

function updatePauseDisplay() {
    const overlay = document.getElementById('game-over-overlay');
    const restartBtn = document.getElementById('restart-btn');
    const pauseRestartBtn = document.getElementById('pause-restart-btn');
    if (!overlay) return;
    
    if (gameState && gameState.paused) {
        overlay.classList.remove('hidden');
        overlay.querySelector('h2').textContent = 'PAUSED';
        overlay.querySelector('#final-score').textContent = '';
        overlay.querySelector('#therapy-report').textContent = 'Press P or ESC to resume';
        
        // Show both Resume and Restart buttons
        if (restartBtn) {
            restartBtn.textContent = 'Resume';
            restartBtn.style.display = 'inline-block';
        }
        if (pauseRestartBtn) {
            pauseRestartBtn.style.display = 'inline-block';
        }
    } else if (gameState && !gameState.game_over) {
        overlay.classList.add('hidden');
        // Hide pause restart button when not paused
        if (pauseRestartBtn) {
            pauseRestartBtn.style.display = 'none';
        }
    }
}

// API calls
async function startNewGame() {
    try {
        const response = await fetch('/api/start/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCsrfToken(),
                'Content-Type': 'application/json',
            },
        });
        
        const data = await response.json();
        if (data.success) {
            gameState = data.game_state;
            gameStarted = true;
            lastDropTime = Date.now();
            therapistRoastTimer = Date.now();
            // Therapist talks every 10 seconds
            therapistRoastInterval = 10000;
            
            // Hide game over overlay
            document.getElementById('game-over-overlay').classList.add('hidden');
            
            // Start game loop
            if (gameLoop) {
                cancelAnimationFrame(gameLoop);
            }
            gameLoop = requestAnimationFrame(updateGame);
        }
    } catch (error) {
        console.error('Error starting game:', error);
    }
}

async function movePiece(direction) {
    if (!gameState || gameState.game_over) return;
    
    try {
        const endpoint = direction === 'left' ? '/api/move/left/' :
                        direction === 'right' ? '/api/move/right/' :
                        '/api/move/down/';
        
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCsrfToken(),
                'Content-Type': 'application/json',
            },
        });
        
        const data = await response.json();
        if (data.success) {
            gameState = data.game_state;
            // Immediately render to show movement
            render();
            checkForRoast(data);
            // Track action and request contextual roast
            trackAction(direction === 'left' ? 'move_left' : direction === 'right' ? 'move_right' : 'move_down');
            requestRoastAfterAction(direction === 'left' ? 'move_left' : direction === 'right' ? 'move_right' : 'move_down');
            
            if (data.landed) {
                lastDropTime = Date.now();
            }
            
            if (gameState.game_over) {
                handleGameOver();
            }
        }
    } catch (error) {
        console.error('Error moving piece:', error);
    }
}

async function rotatePiece() {
    if (!gameState || gameState.game_over || gameState.paused) return;
    
    // Optimistic update: show rotation immediately before API call
    const newRotation = (gameState.current_rotation + 1) % TETROMINOES[gameState.current_piece].length;
    const oldRotation = gameState.current_rotation;
    gameState.current_rotation = newRotation;
    
    // Render immediately to show the rotation
    render();
    
    try {
        const response = await fetch('/api/rotate/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCsrfToken(),
                'Content-Type': 'application/json',
            },
        });
        
        const data = await response.json();
        if (data.success) {
            // Update with server state (may have wall kicks)
            gameState = data.game_state;
            // Render again with final position
            render();
            checkForRoast(data);
            // Track action and request contextual roast
            trackAction('rotate');
            requestRoastAfterAction('rotate');
            
            if (gameState.game_over) {
                handleGameOver();
            }
        } else {
            // Rotation failed, revert to old rotation
            gameState.current_rotation = oldRotation;
            render();
        }
    } catch (error) {
        console.error('Error rotating piece:', error);
        // On error, revert to old rotation
        gameState.current_rotation = oldRotation;
        render();
    }
}

async function hardDrop() {
    if (!gameState || gameState.game_over || gameState.paused) return;
    
    try {
        const response = await fetch('/api/hard-drop/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCsrfToken(),
                'Content-Type': 'application/json',
            },
        });
        
        const data = await response.json();
        if (data.success) {
            gameState = data.game_state;
            // Immediately render to show hard drop
            render();
            checkForRoast(data);
            // Track action and request contextual roast
            trackAction('hard_drop');
            requestRoastAfterAction('hard_drop');
            lastDropTime = Date.now();
            
            if (gameState.game_over) {
                handleGameOver();
            }
        }
    } catch (error) {
        console.error('Error hard dropping:', error);
    }
}

async function holdPiece() {
    if (!gameState || gameState.game_over || gameState.paused) return;
    
    try {
        const response = await fetch('/api/hold/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCsrfToken(),
                'Content-Type': 'application/json',
            },
        });
        
        const data = await response.json();
        if (data.success) {
            gameState = data.game_state;
            // Immediately render to show hold
            render();
            checkForRoast(data);
            // Track action and request contextual roast
            trackAction('hold');
            requestRoastAfterAction('hold');
            
            if (gameState.game_over) {
                handleGameOver();
            }
        }
    } catch (error) {
        console.error('Error holding piece:', error);
    }
}

// Track last roast time to prevent too frequent roasts
let lastRoastTime = 0;
const MIN_ROAST_INTERVAL = 10000; // Minimum 10 seconds between roasts (prevents spam)

function checkForRoast(data) {
    if (data.roast) {
        showTherapistPopup(data.roast);
    }
}

// Request roast after an action (with 10 second throttling)
function requestRoastAfterAction(actionType = null) {
    const now = Date.now();
    // Only request if enough time has passed since last roast (10 seconds)
    if (now - lastRoastTime > MIN_ROAST_INTERVAL) {
        lastRoastTime = now;
        requestTherapistRoast(actionType);
    }
}

// Game loop
function updateGame() {
    if (!gameState || gameState.game_over) {
        if (gameLoop) {
            cancelAnimationFrame(gameLoop);
        }
        return;
    }
    
    const now = Date.now();
    
    // Auto-drop based on level
    const dropInterval = Math.max(50, 1000 - (gameState.level - 1) * 50);
    
    if (now - lastDropTime > dropInterval) {
        movePiece('down');
        lastDropTime = now;
    }
    
    // Timer-based roast - triggers every 10 seconds (no specific action context)
    if (now - therapistRoastTimer > therapistRoastInterval) {
        // Update last roast time to sync with timer
        lastRoastTime = now;
        requestTherapistRoast(null); // No specific action, general observation
        therapistRoastTimer = now;
        // Reset interval to 10 seconds
        therapistRoastInterval = 10000;
    }
    
    render();
    gameLoop = requestAnimationFrame(updateGame);
}

// Rendering
function render() {
    if (!gameState) return;
    
    // Clear canvases with therapy office theme colors (warm cream)
    gameCtx.fillStyle = '#faf8f3';
    gameCtx.fillRect(0, 0, gameCanvas.width, gameCanvas.height);
    
    nextCtx.fillStyle = '#faf8f3';
    nextCtx.fillRect(0, 0, nextCanvas.width, nextCanvas.height);
    
    heldCtx.fillStyle = '#faf8f3';
    heldCtx.fillRect(0, 0, heldCanvas.width, heldCanvas.height);
    
    // Draw board
    drawBoard();
    
    // Draw current piece
    if (gameState.current_piece) {
        drawPiece(
            gameCtx,
            gameState.current_piece,
            gameState.current_rotation,
            gameState.current_x,
            gameState.current_y,
            true
        );
    }
    
    // Draw next piece
    if (gameState.next_piece_type) {
        drawNextPiece();
    }
    
    // Draw held piece
    if (gameState.held_piece) {
        drawHeldPiece();
    }
    
    // Update stats
    updateStats();
}

function drawBoard() {
    const board = gameState.board;
    
    for (let y = 0; y < BOARD_HEIGHT; y++) {
        for (let x = 0; x < BOARD_WIDTH; x++) {
            if (board[y][x] !== 0) {
                drawCell(gameCtx, x, y, board[y][x]);
            } else {
                // Draw subtle grid with therapy office colors
                gameCtx.strokeStyle = 'rgba(139, 115, 85, 0.12)';
                gameCtx.lineWidth = 0.5;
                gameCtx.strokeRect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE);
            }
        }
    }
}

function drawPiece(ctx, pieceType, rotation, x, y, showGhost = false) {
    const shape = TETROMINOES[pieceType][rotation % TETROMINOES[pieceType].length];
    const color = PIECE_COLORS[pieceType];
    
    // Draw ghost piece (drop preview)
    if (showGhost) {
        let ghostY = y;
        while (isValidPosition(pieceType, rotation, x, ghostY + 1)) {
            ghostY++;
        }
        if (ghostY > y) {
            drawPieceShape(ctx, shape, x, ghostY, color, 0.3);
        }
    }
    
    // Draw actual piece
    drawPieceShape(ctx, shape, x, y, color, 1.0);
}

function drawPieceShape(ctx, shape, x, y, color, alpha) {
    ctx.globalAlpha = alpha;
    
    for (let row = 0; row < shape.length; row++) {
        for (let col = 0; col < shape[row].length; col++) {
            if (shape[row][col]) {
                const cellX = (x + col) * CELL_SIZE;
                const cellY = (y + row) * CELL_SIZE;
                
                // Draw cell with rounded corners effect
                ctx.fillStyle = color;
                ctx.fillRect(cellX + 2, cellY + 2, CELL_SIZE - 4, CELL_SIZE - 4);
                
                // Draw softer border
                ctx.strokeStyle = color;
                ctx.lineWidth = 1.5;
                ctx.strokeRect(cellX + 2, cellY + 2, CELL_SIZE - 4, CELL_SIZE - 4);
                
                // Add subtle highlight
                ctx.fillStyle = 'rgba(255, 255, 255, 0.2)';
                ctx.fillRect(cellX + 2, cellY + 2, CELL_SIZE - 4, (CELL_SIZE - 4) / 3);
            }
        }
    }
    
    ctx.globalAlpha = 1.0;
}

function drawNextPiece() {
    const pieceType = gameState.next_piece_type;
    const shape = TETROMINOES[pieceType][0];
    const color = PIECE_COLORS[pieceType];
    const size = pieceType === 'I' || pieceType === 'O' ? 30 : 25;
    const offsetX = (nextCanvas.width - shape[0].length * size) / 2;
    const offsetY = (nextCanvas.height - shape.length * size) / 2;
    
    nextCtx.fillStyle = color;
    
    for (let row = 0; row < shape.length; row++) {
        for (let col = 0; col < shape[row].length; col++) {
            if (shape[row][col]) {
                const x = offsetX + col * size;
                const y = offsetY + row * size;
                nextCtx.fillRect(x + 1, y + 1, size - 2, size - 2);
                nextCtx.strokeStyle = color;
                nextCtx.lineWidth = 2;
                nextCtx.strokeRect(x + 1, y + 1, size - 2, size - 2);
            }
        }
    }
}

function drawHeldPiece() {
    const pieceType = gameState.held_piece;
    const shape = TETROMINOES[pieceType][0];
    const color = PIECE_COLORS[pieceType];
    const size = pieceType === 'I' || pieceType === 'O' ? 20 : 18;
    const offsetX = (heldCanvas.width - shape[0].length * size) / 2;
    const offsetY = (heldCanvas.height - shape.length * size) / 2;
    
    heldCtx.fillStyle = color;
    
    for (let row = 0; row < shape.length; row++) {
        for (let col = 0; col < shape[row].length; col++) {
            if (shape[row][col]) {
                const x = offsetX + col * size;
                const y = offsetY + row * size;
                heldCtx.fillRect(x + 1, y + 1, size - 2, size - 2);
                heldCtx.strokeStyle = color;
                heldCtx.lineWidth = 2;
                heldCtx.strokeRect(x + 1, y + 1, size - 2, size - 2);
            }
        }
    }
}

function drawCell(ctx, x, y, color) {
    const cellX = x * CELL_SIZE;
    const cellY = y * CELL_SIZE;
    
    // Draw cell with softer styling
    ctx.fillStyle = color;
    ctx.fillRect(cellX + 2, cellY + 2, CELL_SIZE - 4, CELL_SIZE - 4);
    
    ctx.strokeStyle = color;
    ctx.lineWidth = 1.5;
    ctx.strokeRect(cellX + 2, cellY + 2, CELL_SIZE - 4, CELL_SIZE - 4);
    
    // Add subtle highlight
    ctx.fillStyle = 'rgba(255, 255, 255, 0.15)';
    ctx.fillRect(cellX + 2, cellY + 2, CELL_SIZE - 4, (CELL_SIZE - 4) / 3);
}

function isValidPosition(pieceType, rotation, x, y) {
    // Simplified check - full validation is done server-side
    const shape = TETROMINOES[pieceType][rotation % TETROMINOES[pieceType].length];
    
    for (let row = 0; row < shape.length; row++) {
        for (let col = 0; col < shape[row].length; col++) {
            if (shape[row][col]) {
                const boardX = x + col;
                const boardY = y + row;
                
                if (boardX < 0 || boardX >= BOARD_WIDTH || boardY >= BOARD_HEIGHT) {
                    return false;
                }
                if (boardY >= 0 && gameState.board[boardY][boardX] !== 0) {
                    return false;
                }
            }
        }
    }
    return true;
}

function updateStats() {
    document.getElementById('score').textContent = gameState.score.toLocaleString();
    document.getElementById('lines').textContent = gameState.lines_cleared;
    document.getElementById('level').textContent = gameState.level;
}

// Track recent actions for contextual roasts
let recentActions = [];
const MAX_RECENT_ACTIONS = 10;

async function requestTherapistRoast(actionType = null) {
    try {
        // Prepare context for contextual roasts
        const requestBody = {
            action_type: actionType,
            recent_stats: {
                recent_moves: recentActions.filter(a => a === 'move_left' || a === 'move_right').length,
                recent_rotations: recentActions.filter(a => a === 'rotate').length,
                recent_drops: recentActions.filter(a => a === 'hard_drop' || a === 'move_down').length,
            }
        };
        
        const response = await fetch('/api/therapist/roast/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCsrfToken(),
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestBody),
        });
        
        const data = await response.json();
        if (data.roast) {
            showTherapistPopup(data.roast);
        }
    } catch (error) {
        console.error('Error getting roast:', error);
    }
}

// Track action for contextual roasts
function trackAction(actionType) {
    recentActions.push(actionType);
    if (recentActions.length > MAX_RECENT_ACTIONS) {
        recentActions.shift(); // Remove oldest
    }
}

function showTherapistPopup(roast) {
    // Show speech bubble next to icon instead of full popup
    const speechBubble = document.getElementById('therapist-speech-bubble');
    const speechText = document.getElementById('speech-bubble-text');
    const iconWrapper = document.getElementById('therapist-icon-wrapper');
    
    if (speechBubble && speechText && iconWrapper) {
        speechText.textContent = roast;
        speechBubble.classList.remove('hidden');
        
        // Remove any previous animation classes
        iconWrapper.classList.remove('talking', 'angry', 'laughing');
        
        // Add laughing animation (happy therapist laughing at his roasts)
        iconWrapper.classList.add('laughing');
        
        // Hide speech bubble after speech ends (estimate based on text length)
        const speechDuration = Math.max(3000, roast.length * 80); // ~80ms per character, min 3 seconds
        
        // Stop laughing animation when speech ends
        setTimeout(() => {
            if (iconWrapper) {
                iconWrapper.classList.remove('laughing', 'talking', 'angry');
            }
        }, speechDuration);
        
        // Auto-hide speech bubble after speech + 2 seconds
        setTimeout(() => {
            if (speechBubble) {
                speechBubble.classList.add('hidden');
            }
        }, speechDuration + 2000);
    } else {
        // Fallback to old popup if elements don't exist
        const popup = document.getElementById('therapist-popup');
        const message = document.getElementById('therapist-message');
        
        if (popup && message) {
            message.textContent = roast;
            popup.classList.remove('hidden');
        }
    }
    
    // Speak the roast using Web Speech API
    speakTherapistMessage(roast);
}

// Store available voices
let availableVoices = [];

// Human-like TTS Configuration
// Choose one: ElevenLabs (best quality) or Google Cloud TTS (free tier)

// Option 1: ElevenLabs (Very human-like, free tier: 10,000 chars/month)
// Get free API key: https://elevenlabs.io
let ELEVENLABS_API_KEY = '';
let GOOGLE_TTS_API_KEY = '';

// Function to load API keys from window (called after page loads)
function loadTTSApiKeys() {
    if (typeof window !== 'undefined') {
        if (window.ELEVENLABS_API_KEY) {
            ELEVENLABS_API_KEY = window.ELEVENLABS_API_KEY;
            console.log('✅ ElevenLabs API key loaded:', ELEVENLABS_API_KEY.substring(0, 10) + '...');
        }
        if (window.GOOGLE_TTS_API_KEY) {
            GOOGLE_TTS_API_KEY = window.GOOGLE_TTS_API_KEY;
            console.log('✅ Google TTS API key loaded');
        }
    }
}

// Load keys when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', loadTTSApiKeys);
} else {
    loadTTSApiKeys();
}

// Also try loading after a short delay (in case script loads before window vars are set)
setTimeout(loadTTSApiKeys, 100);

// ElevenLabs Voice IDs - British Male Voices
// pNInz6obpgDQGcFmaJgB - Adam (British male - deep)
// VR6AewLTigWG4xSOukaG - Arnold (British male)
// TxGEqnHWrfWFTfGW9XjX - Josh (British male)
// Use Arnold for a deeper, more therapist-like voice
const ELEVENLABS_VOICE_ID = 'VR6AewLTigWG4xSOukaG'; // Arnold - Deep British male voice (therapist-like)

// Option 2: Google Cloud TTS (Very human-like, free tier: 0-4 million chars/month)
const GOOGLE_TTS_VOICE = 'en-GB-Neural2-D'; // Deep British male (very human-like)

// Check which service to use (priority: ElevenLabs > Google TTS > Browser TTS)
function shouldUseElevenLabs() {
    // Reload keys each time to ensure we have the latest
    loadTTSApiKeys();
    const hasKey = ELEVENLABS_API_KEY && ELEVENLABS_API_KEY.length > 0 && ELEVENLABS_API_KEY !== 'YOUR_API_KEY_HERE';
    if (hasKey) {
        console.log('✅ ElevenLabs is available');
    } else {
        console.log('❌ ElevenLabs API key not found');
    }
    return hasKey;
}

function shouldUseGoogleTTS() {
    loadTTSApiKeys();
    return GOOGLE_TTS_API_KEY && GOOGLE_TTS_API_KEY.length > 0 && GOOGLE_TTS_API_KEY !== 'YOUR_API_KEY_HERE';
}

function loadVoices() {
    availableVoices = window.speechSynthesis.getVoices();
}

// Initialize voices
if ('speechSynthesis' in window) {
    loadVoices();
    // Some browsers load voices asynchronously
    if (window.speechSynthesis.onvoiceschanged !== undefined) {
        window.speechSynthesis.onvoiceschanged = loadVoices;
    }
}

// ElevenLabs TTS function (Very human-like)
async function speakWithElevenLabs(text) {
    // Ensure we have the latest API key
    loadTTSApiKeys();
    
    if (!ELEVENLABS_API_KEY || ELEVENLABS_API_KEY.length === 0) {
        console.error('❌ ElevenLabs API key is empty');
        console.error('❌ Check game.html - API key should be set before tetris.js loads');
        return false;
    }
    
    console.log('🔑 Using ElevenLabs API key:', ELEVENLABS_API_KEY.substring(0, 15) + '...');
    console.log('🎙️ Using voice ID:', ELEVENLABS_VOICE_ID, '(Arnold - British male)');
    
    try {
        const cleanText = text.replace(/[{}]/g, '').replace(/\s+/g, ' ').trim();
        console.log('🎤 Speaking with ElevenLabs:', cleanText.substring(0, 50) + '...');
        
        const response = await fetch(`https://api.elevenlabs.io/v1/text-to-speech/${ELEVENLABS_VOICE_ID}`, {
            method: 'POST',
            headers: {
                'Accept': 'audio/mpeg',
                'Content-Type': 'application/json',
                'xi-api-key': ELEVENLABS_API_KEY
            },
            body: JSON.stringify({
                text: cleanText,
                model_id: 'eleven_turbo_v2_5', // Newer model that works with free tier (replaces deprecated eleven_monolingual_v1)
                voice_settings: {
                    stability: 0.5,
                    similarity_boost: 0.75,
                    style: 0.0,
                    use_speaker_boost: true
                }
            })
        });
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('❌ ElevenLabs API error:', response.status, errorText);
            console.error('❌ This might mean:');
            console.error('   1. API key is invalid');
            console.error('   2. Voice ID is wrong');
            console.error('   3. API quota exceeded');
            throw new Error(`ElevenLabs API error: ${response.status} - ${errorText}`);
        }
        
        const audioBlob = await response.blob();
        const audioUrl = URL.createObjectURL(audioBlob);
        const audio = new Audio(audioUrl);
        
        console.log('🔊 Playing ElevenLabs audio (Arnold - British male voice)...');
        
        await new Promise((resolve, reject) => {
            audio.onended = () => {
                console.log('✅ ElevenLabs audio finished');
                resolve();
            };
            audio.onerror = (e) => {
                console.error('❌ Audio playback error:', e);
                reject(e);
            };
            audio.play().catch(reject);
        });
        
        URL.revokeObjectURL(audioUrl);
        return true;
    } catch (error) {
        console.error('❌ ElevenLabs TTS error:', error);
        console.error('❌ Falling back to browser TTS (which may sound female/French)');
        return false;
    }
}

// Google Cloud TTS function (Very human-like, free tier)
async function speakWithGoogleTTS(text) {
    if (!shouldUseGoogleTTS()) {
        return false;
    }
    
    try {
        const cleanText = text.replace(/[{}]/g, '').replace(/\s+/g, ' ').trim();
        
        // Google Cloud TTS API endpoint
        const response = await fetch(`https://texttospeech.googleapis.com/v1/text:synthesize?key=${GOOGLE_TTS_API_KEY}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                input: { text: cleanText },
                voice: {
                    languageCode: 'en-GB',
                    name: GOOGLE_TTS_VOICE,
                    ssmlGender: 'MALE'
                },
                audioConfig: {
                    audioEncoding: 'MP3',
                    speakingRate: 0.9,
                    pitch: -2.0, // Deeper voice
                    volumeGainDb: 0.0
                }
            })
        });
        
        if (!response.ok) {
            throw new Error(`Google TTS API error: ${response.status}`);
        }
        
        const data = await response.json();
        const audioData = data.audioContent;
        
        // Decode base64 audio
        const audioBlob = new Blob([
            Uint8Array.from(atob(audioData), c => c.charCodeAt(0))
        ], { type: 'audio/mp3' });
        
        const audioUrl = URL.createObjectURL(audioBlob);
        const audio = new Audio(audioUrl);
        
        await new Promise((resolve, reject) => {
            audio.onended = resolve;
            audio.onerror = reject;
            audio.play();
        });
        
        URL.revokeObjectURL(audioUrl);
        return true;
    } catch (error) {
        console.error('Google TTS error:', error);
        return false;
    }
}

async function speakTherapistMessage(text) {
    if (!text || text.trim().length === 0) {
        console.error('❌ No text provided to speakTherapistMessage');
        return;
    }
    
    console.log('🎤 speakTherapistMessage called with text:', text.substring(0, 50));
    
    // Add a natural laugh at the end of the roast (use "ha ha" instead of "*laughs*" for better TTS)
    const textWithLaugh = text.trim() + ' ha ha ha';
    
    // Ensure API keys are loaded (reload each time to catch late-set keys)
    loadTTSApiKeys();
    console.log('🔑 API Key Status - ElevenLabs:', ELEVENLABS_API_KEY ? 'SET (' + ELEVENLABS_API_KEY.substring(0, 10) + '...)' : 'NOT SET');
    
    // Priority 1: Try ElevenLabs (most human-like)
    if (shouldUseElevenLabs()) {
        console.log('🔄 Attempting ElevenLabs TTS...');
        try {
            const success = await speakWithElevenLabs(textWithLaugh);
            if (success) {
                console.log('✅ Successfully spoke using ElevenLabs TTS (very human-like voice)');
                return;
            }
        } catch (error) {
            console.error('❌ ElevenLabs TTS error:', error);
        }
        console.log('⚠️ ElevenLabs failed, trying Google TTS...');
    } else {
        console.log('❌ ElevenLabs not available - API key:', ELEVENLABS_API_KEY ? 'exists but invalid' : 'not found');
    }
    
    // Priority 2: Try Google Cloud TTS (very human-like, free tier)
    if (shouldUseGoogleTTS()) {
        console.log('🔄 Attempting Google Cloud TTS...');
        try {
            const success = await speakWithGoogleTTS(textWithLaugh);
            if (success) {
                console.log('✅ Successfully spoke using Google Cloud TTS (human-like voice)');
                return;
            }
        } catch (error) {
            console.error('❌ Google TTS error:', error);
        }
        console.log('⚠️ Google TTS failed, falling back to browser TTS');
    }
    
    // Priority 3: Fallback to browser TTS (sounds AI/robotic)
    console.warn('⚠️ Using browser TTS (sounds AI-like). For human voice, set up ElevenLabs or Google TTS API key.');
    console.log('Current API keys - ElevenLabs:', ELEVENLABS_API_KEY ? 'SET' : 'NOT SET', 'Google:', GOOGLE_TTS_API_KEY ? 'SET' : 'NOT SET');
    
    // Fallback to browser SpeechSynthesis
    // Check if browser supports speech synthesis
    if ('speechSynthesis' in window) {
        console.log('🔄 Using browser SpeechSynthesis as fallback...');
        // Cancel any ongoing speech
        window.speechSynthesis.cancel();
        
        // Wait a moment to ensure cancellation is complete
        setTimeout(() => {
            // Reload voices to ensure we have the latest
            loadVoices();
            
            // Clean up text to reduce stuttering - better text processing
            // Add laugh at the end (use "ha ha" for better TTS compatibility)
            const textWithLaugh = text.trim() + ' ha ha ha';
            let cleanText = textWithLaugh
                .replace(/[{}]/g, '') // Remove braces
                .replace(/\s+/g, ' ') // Normalize whitespace
                .replace(/([.!?])\s*([A-Z])/g, '$1 $2') // Ensure proper spacing after punctuation
                .replace(/(\d+)\s*([a-zA-Z])/g, '$1 $2') // Add space between numbers and letters
                .replace(/([a-zA-Z])\s*(\d+)/g, '$1 $2') // Add space between letters and numbers
                .replace(/%/g, ' percent') // Replace % with "percent"
                .replace(/x/g, ' times') // Replace "x" with "times" in context like "2x"
                .trim();
            
            // Create a new speech utterance with cleaned text
            const utterance = new SpeechSynthesisUtterance(cleanText);
            
            // FORCE ENGLISH LANGUAGE FIRST - This is critical!
            utterance.lang = 'en-GB'; // Force British English (or 'en-US' for American)
            
            // Configure voice settings for a deep male therapist voice
            utterance.rate = 0.80;
            utterance.pitch = 0.75;
            utterance.volume = 1.0;
            utterance.text = cleanText;
            
            // Find the best British male therapist voice - STRICT SELECTION
            const voices = availableVoices.length > 0 ? availableVoices : window.speechSynthesis.getVoices();
            
            // Log all available voices for debugging
            console.log('Available voices:', voices.map(v => `${v.name} (${v.lang}) - ${v.default ? 'default' : ''}`));
            
            // STRICT: Reject these (female, French, etc.) - MORE AGGRESSIVE
            const rejectPatterns = [
                'female', 'woman', 'zira', 'samantha', 'hazel', 'karen', 'moira', 'tessa', 'veena', 'fiona',
                'french', 'fr-fr', 'fr-ca', 'fr-be', 'fr-ch', 'français', 'francais', 'france', 'fr ', 'fr-'
            ];
            
            // Function to check if voice is French (very strict)
            function isFrenchVoice(voice) {
                const lang = voice.lang.toLowerCase();
                const name = voice.name.toLowerCase();
                // Reject if language code contains 'fr' anywhere
                if (lang.includes('fr') && !lang.startsWith('en')) return true;
                // Reject if name contains French indicators
                if (name.includes('french') || name.includes('français') || name.includes('francais')) return true;
                return false;
            }
            
            // STRICT: Only accept these (British male voices)
            const acceptPatterns = [
                'uk', 'british', 'en-gb', 'gb', 'united kingdom', 'george', 'david', 'male'
            ];
            
            let selectedVoice = null;
            
            // FIRST: Look for explicit British male voices
            const britishMaleVoices = voices.filter(voice => {
                const nameLower = voice.name.toLowerCase();
                const lang = voice.lang.toLowerCase();
                
                // STRICT: Must be English (en-*)
                if (!lang.startsWith('en-') && !lang.startsWith('en_')) return false;
                
                // STRICT: Reject French completely
                if (isFrenchVoice(voice)) return false;
                
                // Must NOT be female or French
                for (const reject of rejectPatterns) {
                    if (nameLower.includes(reject) || lang.includes(reject)) {
                        return false;
                    }
                }
                
                // Must be British
                const isBritish = lang.includes('en-gb') || 
                                 lang.includes('gb') || 
                                 lang.includes('en_gb') ||
                                 nameLower.includes('uk') || 
                                 nameLower.includes('british') ||
                                 nameLower.includes('united kingdom');
                
                // Must be male (or at least not explicitly female)
                const isMale = nameLower.includes('male') || 
                              nameLower.includes('george') ||
                              nameLower.includes('david') ||
                              (!nameLower.includes('female') && !nameLower.includes('woman'));
                
                return isBritish && isMale;
            });
            
            if (britishMaleVoices.length > 0) {
                // Prefer voices with "male" or known male names
                selectedVoice = britishMaleVoices.find(v => 
                    v.name.toLowerCase().includes('male') ||
                    v.name.toLowerCase().includes('george') ||
                    v.name.toLowerCase().includes('david')
                ) || britishMaleVoices[0];
                
                console.log('Found British male voice:', selectedVoice.name, selectedVoice.lang);
            }
            
            // SECOND: If no British male, look for ANY British English voice (male preferred)
            if (!selectedVoice) {
                const britishVoices = voices.filter(voice => {
                    const lang = voice.lang.toLowerCase();
                    const nameLower = voice.name.toLowerCase();
                    
                    // STRICT: Must be English
                    if (!lang.startsWith('en-') && !lang.startsWith('en_')) return false;
                    
                    // STRICT: Reject French completely
                    if (isFrenchVoice(voice)) return false;
                    
                    // Reject French and female
                    for (const reject of rejectPatterns) {
                        if (nameLower.includes(reject) || lang.includes(reject)) {
                            return false;
                        }
                    }
                    
                    return lang.includes('en-gb') || lang.includes('gb') || lang.includes('en_gb') ||
                           nameLower.includes('uk') || nameLower.includes('british');
                });
                
                if (britishVoices.length > 0) {
                    // Prefer non-female
                    selectedVoice = britishVoices.find(v => 
                        !v.name.toLowerCase().includes('female') &&
                        !v.name.toLowerCase().includes('woman')
                    ) || britishVoices[0];
                    
                    console.log('Found British voice (male preferred):', selectedVoice.name, selectedVoice.lang);
                }
            }
            
            // THIRD: Fallback to any English male voice (NOT French)
            if (!selectedVoice) {
                const englishMaleVoices = voices.filter(voice => {
                    const lang = voice.lang.toLowerCase();
                    const nameLower = voice.name.toLowerCase();
                    
                    // STRICT: Must be English (en-*)
                    if (!lang.startsWith('en-') && !lang.startsWith('en_')) return false;
                    
                    // STRICT: Reject French completely
                    if (isFrenchVoice(voice)) return false;
                    
                    // STRICT: Reject French and female
                    for (const reject of rejectPatterns) {
                        if (nameLower.includes(reject) || lang.includes(reject)) {
                            return false;
                        }
                    }
                    
                    // Must be male
                    return nameLower.includes('male') ||
                           nameLower.includes('david') ||
                           nameLower.includes('alex') ||
                           nameLower.includes('daniel') ||
                           (!nameLower.includes('female') && !nameLower.includes('woman'));
                });
                
                if (englishMaleVoices.length > 0) {
                    selectedVoice = englishMaleVoices[0];
                    console.log('Found English male voice (fallback):', selectedVoice.name, selectedVoice.lang);
                }
            }
            
            // LAST RESORT: Any English voice that's NOT French and NOT explicitly female
            if (!selectedVoice) {
                selectedVoice = voices.find(voice => {
                    const lang = voice.lang.toLowerCase();
                    const nameLower = voice.name.toLowerCase();
                    
                    // STRICT: Must be English (en-*)
                    if (!lang.startsWith('en-') && !lang.startsWith('en_')) return false;
                    
                    // STRICT: Reject French completely
                    if (isFrenchVoice(voice)) return false;
                    
                    // STRICT: Reject French and female
                    for (const reject of rejectPatterns) {
                        if (nameLower.includes(reject) || lang.includes(reject)) {
                            return false;
                        }
                    }
                    
                    return true;
                });
                
                if (selectedVoice) {
                    console.log('Found English voice (last resort):', selectedVoice.name, selectedVoice.lang);
                }
            }
            
            // Set voice and FORCE English language
            if (selectedVoice) {
                utterance.voice = selectedVoice;
                // CRITICAL: Force English language (already set above, but ensure it)
                utterance.lang = 'en-GB'; // Force British English
                console.log('✅ FINAL SELECTION - Voice:', selectedVoice.name, '| Lang:', selectedVoice.lang, '| Forced to: en-GB');
            } else {
                // Even if no voice found, FORCE English language
                utterance.lang = 'en-GB'; // Already set, but ensure it
                console.warn('⚠️ No suitable voice found, using default with en-GB locale');
                console.warn('⚠️ If you hear French, your system may not have English voices installed');
            }
            
            // Add event handlers for better control
            utterance.onstart = () => {
                console.log('Speech started');
            };
            
            utterance.onerror = (event) => {
                console.error('Speech error:', event.error);
            };
            
            utterance.onend = () => {
                console.log('Speech ended');
            };
            
            // Speak the message
            window.speechSynthesis.speak(utterance);
        }, 100); // Small delay to ensure previous speech is cancelled
    } else {
        console.log('Speech synthesis not supported in this browser');
    }
}

function closeTherapistPopup() {
    // Stop any ongoing speech when closing the popup
    if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
    }
    
    // Hide speech bubble
    const speechBubble = document.getElementById('therapist-speech-bubble');
    const iconWrapper = document.getElementById('therapist-icon-wrapper');
    
    if (speechBubble) {
        speechBubble.classList.add('hidden');
    }
    if (iconWrapper) {
        iconWrapper.classList.remove('talking', 'angry', 'laughing');
    }
    
    // Hide old popup if it exists
    const popup = document.getElementById('therapist-popup');
    if (popup) {
        popup.classList.add('hidden');
    }
}

async function handleGameOver() {
    if (gameLoop) {
        cancelAnimationFrame(gameLoop);
        gameLoop = null;
    }
    
    try {
        const response = await fetch('/api/therapist/report/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCsrfToken(),
                'Content-Type': 'application/json',
            },
        });
        
        const data = await response.json();
        if (data.success) {
            displayGameOver(data.report);
        }
    } catch (error) {
        console.error('Error getting report:', error);
    }
}

function displayGameOver(report) {
    const overlay = document.getElementById('game-over-overlay');
    const scoreDiv = document.getElementById('final-score');
    const reportDiv = document.getElementById('therapy-report');
    
    overlay.classList.remove('hidden');
    
    scoreDiv.innerHTML = `
        <p>Final Score: <strong>${report.score.toLocaleString()}</strong></p>
        <p>Lines Cleared: <strong>${report.lines_cleared}</strong></p>
        <p>Level Reached: <strong>${report.level_reached}</strong></p>
    `;
    
    reportDiv.innerHTML = `
        <h4>🧠 Therapy Report</h4>
        <p><strong>Diagnosis:</strong> ${report.diagnosis}</p>
        <p><strong>Final Thoughts:</strong> ${report.final_roast}</p>
        <hr style="border-color: #00ff00; margin: 1rem 0;">
        <p><strong>Stats:</strong></p>
        <ul style="list-style: none; padding-left: 0;">
            <li>Pieces Placed: ${report.pieces_placed}</li>
            <li>Rotations per Piece: ${report.rotations_per_piece}</li>
            <li>Hold Uses: ${report.hold_uses}</li>
            <li>Hard Drops: ${report.hard_drops}</li>
            <li>Tetrises: ${report.tetris_count} (${report.tetris_rate}% rate)</li>
        </ul>
    `;
    
    // Speak the final roast
    if (report.final_roast) {
        speakTherapistMessage(report.final_roast);
    }
}

function getCsrfToken() {
    // Try meta tag first
    const metaTag = document.querySelector('meta[name="csrf-token"]');
    if (metaTag) {
        return metaTag.getAttribute('content');
    }
    
    // Fallback to cookie
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === 'csrftoken') {
            return value;
        }
    }
    
    // Try hidden input (from {% csrf_token %})
    const csrfInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
    if (csrfInput) {
        return csrfInput.value;
    }
    
    return '';
}

