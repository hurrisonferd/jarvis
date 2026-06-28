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

const keys = {};
window.addEventListener('keydown', e => { keys[e.key] = true; });
window.addEventListener('keyup', e => { keys[e.key] = false; });

let playerScore = 0, cpuScore = 0, vx = 5, vy = 3;

app.ticker.add(() => {
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