const app = new PIXI.Application();
await app.init({ width: 800, height: 500, backgroundColor: 0x111111 });

document.body.appendChild(app.canvas);

const player = new PIXI.Graphics().rect(0, 0, 10, 80).fill(0x0088ff);
player.x = 30; player.y = 210;
app.stage.addChild(player);

const cpu = new PIXI.Graphics().rect(0, 0, 10, 80).fill(0x0088ff);
cpu.x = 760; cpu.y = 210;
app.stage.addChild(cpu);

const ball = new PIXI.Graphics().rect(0, 0, 10, 10).fill(0xffffff);
ball.x = 395; ball.y = 245;
app.stage.addChild(ball);

const score = new PIXI.Text({ text: '0 - 0', style: { fontSize: 32, fill: 0x0088ff } });
score.x = 400; score.y = 20; score.anchor.set(0.5);
app.stage.addChild(score);

const keys = {};
window.addEventListener('keydown', e => { keys[e.key] = true; });
window.addEventListener('keyup', e => { keys[e.key] = false; });

let playerScore = 0, cpuScore = 0, vx = 5, vy = 3;

app.ticker.add(() => {
    if (keys['w'] || keys['W']) player.y -= 8;
    if (keys['s'] || keys['S']) player.y += 8;
    player.y = Math.max(0, Math.min(420, player.y));
    
    cpu.y += (ball.y - cpu.y - 40) * 0.08;
    
    ball.x += vx;
    ball.y += vy;
    
    if (ball.y <= 0 || ball.y >= 490) vy *= -1;
    
    if (vx < 0 && ball.x <= 40 && ball.y >= player.y && ball.y <= player.y + 80) {
        vx = Math.abs(vx) * 1.05;
        vy += (ball.y - player.y - 40) * 0.2;
    }
    if (vx > 0 && ball.x >= 750 && ball.y >= cpu.y && ball.y <= cpu.y + 80) {
        vx = -Math.abs(vx) * 1.05;
        vy += (ball.y - cpu.y - 40) * 0.2;
    }
    
    if (ball.x < 0) { cpuScore++; score.text = `${playerScore} - ${cpuScore}`; ball.x = 400; ball.y = 250; vx = 5; }
    if (ball.x > 800) { playerScore++; score.text = `${playerScore} - ${cpuScore}`; ball.x = 400; ball.y = 250; vx = -5; }
});