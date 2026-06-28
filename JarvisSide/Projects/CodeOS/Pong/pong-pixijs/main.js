const app = new PIXI.Application({
    width: 640,
    height: 400,
    backgroundColor: 0x111111
});

document.body.appendChild(app.view);

const player = new PIXI.Graphics().beginFill(0x0088ff).drawRect(0, 0, 10, 80).endFill();
player.x = 20; player.y = 160;
app.stage.addChild(player);

const cpu = new PIXI.Graphics().beginFill(0x0088ff).drawRect(0, 0, 10, 80).endFill();
cpu.x = 610; cpu.y = 160;
app.stage.addChild(cpu);

const ball = new PIXI.Graphics().beginFill(0xffffff).drawRect(0, 0, 10, 10).endFill();
ball.x = 315; ball.y = 195;
app.stage.addChild(ball);

const score = new PIXI.Text('0 - 0', { fontSize: 32, fill: 0x0088ff });
score.x = 320; score.y = 20; score.anchor.set(0.5);
app.stage.addChild(score);

// Touch indicator (subtle circle at touch position)
const touchIndicator = new PIXI.Graphics();
app.stage.addChild(touchIndicator);

// FF-style touch control state
let touchActive = false;

const keys = {};
window.addEventListener('keydown', e => { keys[e.key] = true; });
window.addEventListener('keyup', e => { keys[e.key] = false; });

// FF-style touch controls: paddle follows finger position anywhere on canvas
app.view.addEventListener('touchstart', e => {
    e.preventDefault();
    touchActive = true;
    handleTouchMove(e.touches[0]);
}, { passive: false });

app.view.addEventListener('touchmove', e => {
    e.preventDefault();
    if (touchActive) handleTouchMove(e.touches[0]);
}, { passive: false });

app.view.addEventListener('touchend', e => {
    e.preventDefault();
    touchActive = false;
    touchIndicator.clear();
});

app.view.addEventListener('touchcancel', e => {
    touchActive = false;
    touchIndicator.clear();
});

function handleTouchMove(touch) {
    const rect = app.view.getBoundingClientRect();
    const touchY = touch.clientY - rect.top;
    
    // Scale touch position to canvas coordinates
    const scaleY = 400 / rect.height;
    const targetY = touchY * scaleY;
    
    // Clamp paddle position (paddle center follows finger)
    player.y = Math.max(0, Math.min(320, targetY - 40));
    
    // Update touch indicator
    touchIndicator.clear();
    if (touchActive) {
        touchIndicator.beginFill(0x0088ff, 0.3);
        touchIndicator.drawCircle(40, player.y + 40, 6);
        touchIndicator.endFill();
        touchIndicator.lineStyle(2, 0x0088ff, 0.6);
        touchIndicator.moveTo(30, player.y + 40);
        touchIndicator.lineTo(35, player.y + 40);
    }
}

let playerScore = 0, cpuScore = 0, vx = 5, vy = 3;

app.ticker.add(() => {
    // Keyboard controls (still supported)
    if (keys['w'] || keys['W']) player.y -= 8;
    if (keys['s'] || keys['S']) player.y += 8;
    player.y = Math.max(0, Math.min(320, player.y));
    
    cpu.y += (ball.y - cpu.y - 40) * 0.08;
    
    ball.x += vx;
    ball.y += vy;
    
    if (ball.y <= 0 || ball.y >= 390) vy *= -1;
    
    if (vx < 0 && ball.x <= 30 && ball.y >= player.y && ball.y <= player.y + 80) {
        vx = Math.abs(vx) * 1.05;
        vy += (ball.y - player.y - 40) * 0.2;
    }
    if (vx > 0 && ball.x >= 600 && ball.y >= cpu.y && ball.y <= cpu.y + 80) {
        vx = -Math.abs(vx) * 1.05;
        vy += (ball.y - cpu.y - 40) * 0.2;
    }
    
    if (ball.x < 0) { cpuScore++; score.text = `${playerScore} - ${cpuScore}`; ball.x = 315; ball.y = 195; vx = 5; }
    if (ball.x > 640) { playerScore++; score.text = `${playerScore} - ${cpuScore}`; ball.x = 315; ball.y = 195; vx = -5; }
});