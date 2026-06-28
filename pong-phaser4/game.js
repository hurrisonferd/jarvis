import Phaser from 'https://cdn.jsdelivr.net/npm/phaser@4/dist/phaser.esm.min.js';

const config = {
    type: Phaser.AUTO,
    width: 800,
    height: 500,
    parent: 'game',
    backgroundColor: '#000',
    scene: { create, update }
};

const game = new Phaser.Game(config);
let player, cpu, ball, playerScore = 0, cpuScore = 0, scoreText;

function create() {
    player = this.add.rectangle(30, 250, 10, 80, 0xff8800);
    cpu = this.add.rectangle(770, 250, 10, 80, 0xff8800);
    ball = this.add.rectangle(400, 250, 10, 10, 0xffffff);
    scoreText = this.add.text(400, 30, '0 - 0', { fontSize: '32px', fill: '#ff8800' }).setOrigin(0.5);
    
    this.physics.add.existing(ball);
    ball.body.setVelocity(300, 0).setBounce(1);
}

function update() {
    if (this.input.keyboard.addKey('W').isDown) player.y -= 8;
    if (this.input.keyboard.addKey('S').isDown) player.y += 8;
    player.y = Phaser.Math.Clamp(player.y, 40, 460);
    
    cpu.y = Phaser.Math.Linear(cpu.y, ball.y, 0.05);
    
    this.physics.world.wrap(ball, 10);
    
    if (ball.x < 0) { cpuScore++; scoreText.setText(`${playerScore} - ${cpuScore}`); ball.body.reset(400, 250); }
    if (ball.x > 800) { playerScore++; scoreText.setText(`${playerScore} - ${cpuScore}`); ball.body.reset(400, 250); }
}