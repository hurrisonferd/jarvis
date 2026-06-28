const canvas = document.getElementById('pong-canvas');
const ctx = canvas.getContext('2d');
const player1ScoreEl = document.getElementById('player1-score');
const player2ScoreEl = document.getElementById('player2-score');

// Game constants
const WINNING_SCORE = 11;
const PADDLE_WIDTH = 10;
const PADDLE_HEIGHT = 80;
const BALL_SIZE = 10;
const PADDLE_SPEED = 7;
const INITIAL_BALL_SPEED = 5;
const SPEED_INCREMENT = 0.2;

// Game state
let player1Score = 0;
let player2Score = 0;
let gameRunning = true;
let winner = null;

// Paddle objects
const leftPaddle = {
    x: 20,
    y: canvas.height / 2 - PADDLE_HEIGHT / 2,
    width: PADDLE_WIDTH,
    height: PADDLE_HEIGHT,
    dy: 0,
    color: '#00d4ff'
};

const rightPaddle = {
    x: canvas.width - 30,
    y: canvas.height / 2 - PADDLE_HEIGHT / 2,
    width: PADDLE_WIDTH,
    height: PADDLE_HEIGHT,
    dy: 0,
    color: '#ff6b6b'
};

// Ball object
const ball = {
    x: canvas.width / 2,
    y: canvas.height / 2,
    size: BALL_SIZE,
    dx: INITIAL_BALL_SPEED,
    dy: INITIAL_BALL_SPEED * (Math.random() > 0.5 ? 1 : -1) * 0.5,
    speed: INITIAL_BALL_SPEED
};

// Key tracking
const keys = {
    w: false,
    s: false,
    ArrowUp: false,
    ArrowDown: false
};

// Event listeners
document.addEventListener('keydown', (e) => {
    if (e.key in keys) {
        keys[e.key] = true;
        e.preventDefault();
    }
    if (e.key === ' ' && !gameRunning && winner) {
        resetGame();
    }
});

document.addEventListener('keyup', (e) => {
    if (e.key in keys) {
        keys[e.key] = false;
        e.preventDefault();
    }
});

function resetBall() {
    ball.x = canvas.width / 2;
    ball.y = canvas.height / 2;
    ball.speed = INITIAL_BALL_SPEED;
    ball.dx = INITIAL_BALL_SPEED * (Math.random() > 0.5 ? 1 : -1);
    ball.dy = INITIAL_BALL_SPEED * (Math.random() > 0.5 ? 1 : -1) * 0.5;
}

function resetGame() {
    player1Score = 0;
    player2Score = 0;
    player1ScoreEl.textContent = '0';
    player2ScoreEl.textContent = '0';
    leftPaddle.y = canvas.height / 2 - PADDLE_HEIGHT / 2;
    rightPaddle.y = canvas.height / 2 - PADDLE_HEIGHT / 2;
    winner = null;
    gameRunning = true;
    resetBall();
}

function updatePaddles() {
    // Left paddle (W/S keys)
    if (keys.w) {
        leftPaddle.dy = -PADDLE_SPEED;
    } else if (keys.s) {
        leftPaddle.dy = PADDLE_SPEED;
    } else {
        leftPaddle.dy = 0;
    }

    // Right paddle (Arrow keys)
    if (keys.ArrowUp) {
        rightPaddle.dy = -PADDLE_SPEED;
    } else if (keys.ArrowDown) {
        rightPaddle.dy = PADDLE_SPEED;
    } else {
        rightPaddle.dy = 0;
    }

    // Apply movement with boundary checking
    leftPaddle.y = Math.max(0, Math.min(canvas.height - leftPaddle.height, leftPaddle.y + leftPaddle.dy));
    rightPaddle.y = Math.max(0, Math.min(canvas.height - rightPaddle.height, rightPaddle.y + rightPaddle.dy));
}

function updateBall() {
    if (!gameRunning) return;

    ball.x += ball.dx;
    ball.y += ball.dy;

    // Top and bottom wall collision
    if (ball.y - ball.size / 2 <= 0 || ball.y + ball.size / 2 >= canvas.height) {
        ball.dy = -ball.dy;
        ball.y = ball.y - ball.size / 2 <= 0 ? ball.size / 2 : canvas.height - ball.size / 2;
    }

    // Left paddle collision
    if (ball.dx < 0 &&
        ball.x - ball.size / 2 <= leftPaddle.x + leftPaddle.width &&
        ball.x + ball.size / 2 >= leftPaddle.x &&
        ball.y >= leftPaddle.y &&
        ball.y <= leftPaddle.y + leftPaddle.height) {
        
        ball.dx = -ball.dx;
        ball.speed += SPEED_INCREMENT;
        
        // Adjust angle based on where ball hit the paddle
        const hitPos = (ball.y - leftPaddle.y) / leftPaddle.height;
        ball.dy = ball.speed * (hitPos - 0.5) * 2;
        ball.dx = Math.sqrt(ball.speed * ball.speed - ball.dy * ball.dy) * (ball.dx > 0 ? 1 : -1);
        
        ball.x = leftPaddle.x + leftPaddle.width + ball.size / 2;
    }

    // Right paddle collision
    if (ball.dx > 0 &&
        ball.x + ball.size / 2 >= rightPaddle.x &&
        ball.x - ball.size / 2 <= rightPaddle.x + rightPaddle.width &&
        ball.y >= rightPaddle.y &&
        ball.y <= rightPaddle.y + rightPaddle.height) {
        
        ball.dx = -ball.dx;
        ball.speed += SPEED_INCREMENT;
        
        // Adjust angle based on where ball hit the paddle
        const hitPos = (ball.y - rightPaddle.y) / rightPaddle.height;
        ball.dy = ball.speed * (hitPos - 0.5) * 2;
        ball.dx = -Math.sqrt(ball.speed * ball.speed - ball.dy * ball.dy);
        
        ball.x = rightPaddle.x - ball.size / 2;
    }

    // Scoring
    if (ball.x < 0) {
        player2Score++;
        player2ScoreEl.textContent = player2Score;
        checkWinner();
        if (gameRunning) resetBall();
    }

    if (ball.x > canvas.width) {
        player1Score++;
        player1ScoreEl.textContent = player1Score;
        checkWinner();
        if (gameRunning) resetBall();
    }
}

function checkWinner() {
    if (player1Score >= WINNING_SCORE) {
        winner = 'Player 1';
        gameRunning = false;
    } else if (player2Score >= WINNING_SCORE) {
        winner = 'Player 2';
        gameRunning = false;
    }
}

function drawRect(x, y, width, height, color) {
    ctx.fillStyle = color;
    ctx.fillRect(x, y, width, height);
}

function drawCircle(x, y, radius, color) {
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.arc(x, y, radius, 0, Math.PI * 2);
    ctx.fill();
}

function drawCenterLine() {
    ctx.setLineDash([10, 10]);
    ctx.strokeStyle = '#4a5568';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(canvas.width / 2, 0);
    ctx.lineTo(canvas.width / 2, canvas.height);
    ctx.stroke();
    ctx.setLineDash([]);
}

function drawGameOver() {
    ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    ctx.fillStyle = '#fff';
    ctx.font = 'bold 48px Segoe UI';
    ctx.textAlign = 'center';
    ctx.fillText(`${winner} Wins!`, canvas.width / 2, canvas.height / 2 - 30);
    
    ctx.font = '24px Segoe UI';
    ctx.fillStyle = '#718096';
    ctx.fillText('Press SPACE to play again', canvas.width / 2, canvas.height / 2 + 30);
}

function render() {
    // Clear canvas
    ctx.fillStyle = '#0a0a0f';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Draw center line
    drawCenterLine();

    // Draw paddles
    drawRect(leftPaddle.x, leftPaddle.y, leftPaddle.width, leftPaddle.height, leftPaddle.color);
    drawRect(rightPaddle.x, rightPaddle.y, rightPaddle.width, rightPaddle.height, rightPaddle.color);

    // Draw ball
    drawCircle(ball.x, ball.y, ball.size, '#fff');

    // Draw game over screen
    if (!gameRunning && winner) {
        drawGameOver();
    }
}

function gameLoop() {
    updatePaddles();
    updateBall();
    render();
    requestAnimationFrame(gameLoop);
}

// Start the game
gameLoop();