const canvas = document.getElementById('game');
const ctx = canvas.getContext('2d');
const scoreEl = document.getElementById('score');

canvas.width = 640;
canvas.height = 400;

const PADDLE_W = 10, PADDLE_H = 80, BALL_SIZE = 10;
const PADDLE_SPEED = 8, BALL_SPEED = 5;

const player = { x: 20, y: canvas.height/2 - PADDLE_H/2, score: 0 };
const cpu = { x: canvas.width - 30, y: canvas.height/2 - PADDLE_H/2, score: 0 };
const ball = { x: canvas.width/2, y: canvas.height/2, vx: BALL_SPEED, vy: 0 };

// FF-style touch control state
let touchActive = false;
let touchIndicator = { x: 0, y: 0, alpha: 0 };

const keys = {};
document.addEventListener('keydown', e => { keys[e.key] = true; e.preventDefault(); });
document.addEventListener('keyup', e => { keys[e.key] = false; });

// FF-style touch controls: paddle follows finger position anywhere on canvas
canvas.addEventListener('touchstart', e => {
    e.preventDefault();
    touchActive = true;
    handleTouchMove(e.touches[0]);
}, { passive: false });

canvas.addEventListener('touchmove', e => {
    e.preventDefault();
    if (touchActive) handleTouchMove(e.touches[0]);
}, { passive: false });

canvas.addEventListener('touchend', e => {
    e.preventDefault();
    touchActive = false;
    touchIndicator.alpha = 0;
});

canvas.addEventListener('touchcancel', e => {
    touchActive = false;
    touchIndicator.alpha = 0;
});

function handleTouchMove(touch) {
    const rect = canvas.getBoundingClientRect();
    const touchY = touch.clientY - rect.top;
    
    // Scale touch position to canvas coordinates
    const scaleY = canvas.height / rect.height;
    const targetY = touchY * scaleY;
    
    // Clamp paddle position (paddle center follows finger)
    player.y = Math.max(0, Math.min(canvas.height - PADDLE_H, targetY - PADDLE_H / 2));
    
    // Update touch indicator
    touchIndicator.x = player.x + PADDLE_W + 10;
    touchIndicator.y = player.y + PADDLE_H / 2;
    touchIndicator.alpha = 0.6;
}

function resetBall(dir) {
    ball.x = canvas.width/2;
    ball.y = canvas.height/2;
    ball.vx = BALL_SPEED * dir;
    ball.vy = (Math.random() - 0.5) * 4;
}

function update() {
    // Keyboard controls (still supported)
    if (keys['w'] || keys['W'] || keys['ArrowUp']) player.y -= PADDLE_SPEED;
    if (keys['s'] || keys['S'] || keys['ArrowDown']) player.y += PADDLE_SPEED;
    player.y = Math.max(0, Math.min(canvas.height - PADDLE_H, player.y));
    
    // Fade touch indicator when not touching
    if (!touchActive && touchIndicator.alpha > 0) {
        touchIndicator.alpha -= 0.05;
    }
    
    cpu.y += (ball.y - cpu.y - PADDLE_H/2) * 0.08;
    cpu.y = Math.max(0, Math.min(canvas.height - PADDLE_H, cpu.y));
    
    ball.x += ball.vx;
    ball.y += ball.vy;
    
    if (ball.y <= 0 || ball.y >= canvas.height) ball.vy *= -1;
    
    if (ball.x <= player.x + PADDLE_W && ball.y >= player.y && ball.y <= player.y + PADDLE_H && ball.vx < 0) {
        ball.vx = Math.abs(ball.vx) * 1.05;
        ball.vy += (ball.y - player.y - PADDLE_H/2) * 0.2;
    }
    if (ball.x >= cpu.x && ball.y >= cpu.y && ball.y <= cpu.y + PADDLE_H && ball.vx > 0) {
        ball.vx = -Math.abs(ball.vx) * 1.05;
        ball.vy += (ball.y - cpu.y - PADDLE_H/2) * 0.2;
    }
    
    if (ball.x < 0) { cpu.score++; scoreEl.textContent = `${player.score} - ${cpu.score}`; resetBall(1); }
    if (ball.x > canvas.width) { player.score++; scoreEl.textContent = `${player.score} - ${cpu.score}`; resetBall(-1); }
}

function draw() {
    ctx.fillStyle = '#000';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    ctx.fillStyle = '#00ff88';
    ctx.fillRect(player.x, player.y, PADDLE_W, PADDLE_H);
    ctx.fillRect(cpu.x, cpu.y, PADDLE_W, PADDLE_H);
    ctx.fillRect(ball.x - BALL_SIZE/2, ball.y - BALL_SIZE/2, BALL_SIZE, BALL_SIZE);
    
    ctx.strokeStyle = '#333';
    ctx.setLineDash([5, 5]);
    ctx.beginPath();
    ctx.moveTo(canvas.width/2, 0);
    ctx.lineTo(canvas.width/2, canvas.height);
    ctx.stroke();
    ctx.setLineDash([]);
    
    // Draw touch indicator (subtle vertical line showing touch position)
    if (touchIndicator.alpha > 0) {
        ctx.fillStyle = `rgba(0, 255, 136, ${touchIndicator.alpha * 0.3})`;
        ctx.beginPath();
        ctx.arc(touchIndicator.x, touchIndicator.y, 6, 0, Math.PI * 2);
        ctx.fill();
        
        ctx.strokeStyle = `rgba(0, 255, 136, ${touchIndicator.alpha})`;
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(player.x + PADDLE_W, touchIndicator.y);
        ctx.lineTo(touchIndicator.x - 5, touchIndicator.y);
        ctx.stroke();
        ctx.lineWidth = 1;
    }
}

function game() {
    update();
    draw();
    requestAnimationFrame(game);
}

resetBall(Math.random() < 0.5 ? -1 : 1);
game();
