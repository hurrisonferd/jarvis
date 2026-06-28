const config = {
    type: Phaser.AUTO,
    width: 640,
    height: 400,
    parent: 'game',
    backgroundColor: '#000',
    physics: { default: false },
    scene: { create, update }
};

const game = new Phaser.Game(config);
let player, cpu, ball, playerScore = 0, cpuScore = 0, scoreText;
let ballVx = 5, ballVy = 3;
const keys = {};
let touchActive = false;
let touchIndicator;

function create() {
    const graphics = this.add.graphics();
    
    // Player paddle
    graphics.fillStyle(0xff8800);
    graphics.fillRect(20, 160, 10, 80);
    player = { x: 20, y: 160, width: 10, height: 80 };
    
    // CPU paddle
    graphics.fillStyle(0xff8800);
    graphics.fillRect(610, 160, 10, 80);
    cpu = { x: 610, y: 160, width: 10, height: 80 };
    
    // Ball
    graphics.fillStyle(0xffffff);
    graphics.fillRect(315, 195, 10, 10);
    ball = { x: 315, y: 195, size: 10 };
    
    // Center line
    graphics.lineStyle(1, 0x333333);
    for (let y = 0; y < 400; y += 15) {
        graphics.lineBetween(320, y, 320, y + 10);
    }
    
    scoreText = this.add.text(320, 30, '0 - 0', { fontSize: '32px', fill: '#ff8800' }).setOrigin(0.5);
    
    // Touch indicator (subtle circle at touch position)
    touchIndicator = this.add.graphics();
    touchIndicator.setDepth(1);
    
    // Keyboard
    this.input.keyboard.on('keydown', e => { keys[e.code] = true; });
    this.input.keyboard.on('keyup', e => { keys[e.code] = false; });
    
    // FF-style touch controls: paddle follows finger position anywhere on canvas
    this.input.on('pointerdown', (pointer) => {
        touchActive = true;
        handleTouchMove(pointer);
    });
    
    this.input.on('pointermove', (pointer) => {
        if (touchActive) handleTouchMove(pointer);
    });
    
    this.input.on('pointerup', () => {
        touchActive = false;
        touchIndicator.clear();
    });
    
    this.input.on('pointercancel', () => {
        touchActive = false;
        touchIndicator.clear();
    });
}

function handleTouchMove(pointer) {
    // Scale pointer Y position to game coordinates
    const scaleY = 400 / this.scale.height;
    const targetY = pointer.y * scaleY;
    
    // Clamp paddle position (paddle center follows finger)
    player.y = Math.max(0, Math.min(320, targetY - 40));
    
    // Update touch indicator
    touchIndicator.clear();
    if (touchActive) {
        touchIndicator.fillStyle(0xff8800, 0.4);
        touchIndicator.fillCircle(40, player.y + 40, 6);
        touchIndicator.lineStyle(2, 0xff8800, 0.6);
        touchIndicator.lineBetween(30, player.y + 40, 35, player.y + 40);
    }
}

function resetBall(dir) {
    ball.x = 315;
    ball.y = 195;
    ballVx = 5 * dir;
    ballVy = (Math.random() - 0.5) * 4;
}

function update() {
    // Keyboard controls (still supported)
    if (keys['KeyW'] || keys['ArrowUp']) player.y -= 8;
    if (keys['KeyS'] || keys['ArrowDown']) player.y += 8;
    player.y = Math.max(0, Math.min(320, player.y));
    
    cpu.y += (ball.y - cpu.y - 40) * 0.08;
    cpu.y = Math.max(0, Math.min(320, cpu.y));
    
    ball.x += ballVx;
    ball.y += ballVy;
    
    if (ball.y <= 0 || ball.y >= 390) ballVy *= -1;
    
    if (ballVx < 0 && ball.x <= 30 && ball.y >= player.y && ball.y <= player.y + 80) {
        ballVx = Math.abs(ballVx) * 1.05;
        ballVy += (ball.y - player.y - 40) * 0.2;
    }
    if (ballVx > 0 && ball.x >= 600 && ball.y >= cpu.y && ball.y <= cpu.y + 80) {
        ballVx = -Math.abs(ballVx) * 1.05;
        ballVy += (ball.y - cpu.y - 40) * 0.2;
    }
    
    if (ball.x < 0) { cpuScore++; scoreText.setText(`${playerScore} - ${cpuScore}`); resetBall(1); }
    if (ball.x > 640) { playerScore++; scoreText.setText(`${playerScore} - ${cpuScore}`); resetBall(-1); }
}