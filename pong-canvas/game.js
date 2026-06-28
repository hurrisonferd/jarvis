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

const keys = {};
document.addEventListener('keydown', e => { keys[e.key] = true; e.preventDefault(); });
document.addEventListener('keyup', e => { keys[e.key] = false; });

// Touch controls: top half = move up, bottom half = move down
canvas.addEventListener('touchstart', e => {
    e.preventDefault();
    const touch = e.touches[0];
    const rect = canvas.getBoundingClientRect();
    const y = touch.clientY - rect.top;
    if (y < rect.height / 2) keys['touchUp'] = true;
    else keys['touchDown'] = true;
}, { passive: false });
canvas.addEventListener('touchend', e => {
    keys['touchUp'] = false;
    keys['touchDown'] = false;
});
canvas.addEventListener('touchcancel', e => {
    keys['touchUp'] = false;
    keys['touchDown'] = false;
});

function resetBall(dir) {
    ball.x = canvas.width/2;
    ball.y = canvas.height/2;
    ball.vx = BALL_SPEED * dir;
    ball.vy = (Math.random() - 0.5) * 4;
}

function update() {
    if (keys['w'] || keys['W'] || keys['ArrowUp'] || keys['touchUp']) player.y -= PADDLE_SPEED;
    if (keys['s'] || keys['S'] || keys['ArrowDown'] || keys['touchDown']) player.y += PADDLE_SPEED;
    player.y = Math.max(0, Math.min(canvas.height - PADDLE_H, player.y));
    
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
}

function game() {
    update();
    draw();
    requestAnimationFrame(game);
}

resetBall(Math.random() < 0.5 ? -1 : 1);
game();
