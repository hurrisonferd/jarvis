// Phaser 4 Pong Game
const config = {
    type: Phaser.AUTO,
    width: 800,
    height: 600,
    parent: 'game-container',
    backgroundColor: '#1a1a2e',
    physics: {
        default: 'arcade',
        arcade: {
            gravity: { y: 0 },
            debug: false
        }
    },
    scene: {
        preload: preload,
        create: create,
        update: update
    }
};

const game = new Phaser.Game(config);

// Game constants
const PADDLE_SPEED = 400;
const BALL_SPEED = 400;
const WIN_SCORE = 11;
const PADDLE_HEIGHT = 100;
const PADDLE_WIDTH = 15;
const BALL_SIZE = 15;

// Game state
let player1Score = 0;
let player2Score = 0;
let player1Paddle, player2Paddle, ball;
let player1ScoreText, player2ScoreText, gameOverText;
let cursors;
let gameState = 'playing'; // 'playing', 'gameover'
let ballVelocity = { x: 0, y: 0 };

function preload() {
    // No external assets needed - we draw everything
}

function create() {
    const centerY = config.height / 2;
    const centerX = config.width / 2;
    
    // Draw center line
    const graphics = this.add.graphics();
    graphics.lineStyle(2, '#333366', 0.5);
    for (let y = 0; y < config.height; y += 20) {
        graphics.lineBetween(centerX, y, centerX, y + 10);
    }
    
    // Create player 1 paddle (left side)
    player1Paddle = this.physics.add.staticBody(
        30, centerY, PADDLE_WIDTH, PADDLE_HEIGHT
    );
    const paddle1Graphics = this.add.graphics();
    paddle1Graphics.fillStyle(0x00ff88, 1);
    paddle1Graphics.fillRoundedRect(
        player1Paddle.body.x - PADDLE_WIDTH/2,
        player1Paddle.body.y - PADDLE_HEIGHT/2,
        PADDLE_WIDTH, PADDLE_HEIGHT, 5
    );
    
    // Create player 2 paddle (right side) - AI controlled
    player2Paddle = this.physics.add.staticBody(
        config.width - 30, centerY, PADDLE_WIDTH, PADDLE_HEIGHT
    );
    const paddle2Graphics = this.add.graphics();
    paddle2Graphics.fillStyle(0xff6600, 1);
    paddle2Graphics.fillRoundedRect(
        player2Paddle.body.x - PADDLE_WIDTH/2,
        player2Paddle.body.y - PADDLE_HEIGHT/2,
        PADDLE_WIDTH, PADDLE_HEIGHT, 5
    );
    
    // Create ball
    ball = this.physics.add.body(centerX, centerY, BALL_SIZE, BALL_SIZE);
    const ballGraphics = this.add.graphics();
    ballGraphics.fillStyle(0xffffff, 1);
    ballGraphics.fillCircle(ball.body.x + BALL_SIZE/2, ball.body.y + BALL_SIZE/2, BALL_SIZE/2);
    
    // Store graphics references for updates
    ball.graphics = ballGraphics;
    player1Paddle.graphics = paddle1Graphics;
    player2Paddle.graphics = paddle2Graphics;
    
    // Set up keyboard input
    cursors = this.input.keyboard.createCursorKeys();
    this.wKey = this.input.keyboard.addKey(Phaser.Input.Keyboard.KeyCodes.W);
    this.sKey = this.input.keyboard.addKey(Phaser.Input.Keyboard.KeyCodes.S);
    
    // Set up collision between ball and paddles
    this.physics.addCollider(ball, player1Paddle, handlePaddleHit, null, this);
    this.physics.addCollider(ball, player2Paddle, handlePaddleHit, null, this);
    
    // Create score display
    player1ScoreText = this.add.text(centerX - 100, 30, '0', {
        fontSize: '48px',
        fontFamily: 'Courier New',
        color: '#00ff88'
    }).setOrigin(0.5);
    
    player2ScoreText = this.add.text(centerX + 100, 30, '0', {
        fontSize: '48px',
        fontFamily: 'Courier New',
        color: '#ff6600'
    }).setOrigin(0.5);
    
    // Game over text (hidden initially)
    gameOverText = this.add.text(centerX, centerY, '', {
        fontSize: '36px',
        fontFamily: 'Courier New',
        color: '#ffffff',
        align: 'center'
    }).setOrigin(0.5).setVisible(false);
    
    // Start ball movement
    resetBall(this, 1);
    
    // Set up boundary collisions
    this.physics.world.on('worldbounds', handleWallHit, this);
    ball.body.setCollideWorldBounds(true);
    player1Paddle.body.setCollideWorldBounds(true);
    player2Paddle.body.setCollideWorldBounds(true);
}

function update(time, delta) {
    if (gameState === 'gameover') return;
    
    // Player 1 controls (W/S or Arrow Up/Down)
    if (cursors.up.isDown || this.wKey.isDown) {
        player1Paddle.body.y -= PADDLE_SPEED * (delta / 1000);
    }
    if (cursors.down.isDown || this.sKey.isDown) {
        player1Paddle.body.y += PADDLE_SPEED * (delta / 1000);
    }
    
    // Clamp player 1 paddle position
    const halfPaddle = PADDLE_HEIGHT / 2;
    player1Paddle.body.y = Phaser.Math.Clamp(
        player1Paddle.body.y, halfPaddle, config.height - halfPaddle
    );
    
    // AI for player 2 - follows the ball with some delay
    const aiSpeed = PADDLE_SPEED * 0.75;
    const ballCenter = ball.body.y + BALL_SIZE / 2;
    const paddleCenter = player2Paddle.body.y;
    const diff = ballCenter - paddleCenter;
    
    if (Math.abs(diff) > 10) {
        player2Paddle.body.y += Math.sign(diff) * aiSpeed * (delta / 1000);
    }
    
    // Clamp player 2 paddle position
    player2Paddle.body.y = Phaser.Math.Clamp(
        player2Paddle.body.y, halfPaddle, config.height - halfPaddle
    );
    
    // Update paddle graphics
    updatePaddleGraphics(player1Paddle, 0x00ff88);
    updatePaddleGraphics(player2Paddle, 0xff6600);
    
    // Check for scoring (ball past paddles)
    if (ball.body.x < 0) {
        // Player 2 scores
        player2Score++;
        player2ScoreText.setText(player2Score.toString());
        checkWinCondition(this, 2);
    } else if (ball.body.x > config.width) {
        // Player 1 scores
        player1Score++;
        player1ScoreText.setText(player1Score.toString());
        checkWinCondition(this, 1);
    }
    
    // Update ball position based on velocity
    ball.body.x += ballVelocity.x * (delta / 1000);
    ball.body.y += ballVelocity.y * (delta / 1000);
    
    // Ball collision with top/bottom walls
    if (ball.body.y <= 0) {
        ball.body.y = 0;
        ballVelocity.y = -ballVelocity.y;
    } else if (ball.body.y + BALL_SIZE >= config.height) {
        ball.body.y = config.height - BALL_SIZE;
        ballVelocity.y = -ballVelocity.y;
    }
    
    // Update ball graphics
    ball.graphics.clear();
    ball.graphics.fillStyle(0xffffff, 1);
    ball.graphics.fillCircle(ball.body.x + BALL_SIZE/2, ball.body.y + BALL_SIZE/2, BALL_SIZE/2);
}

function updatePaddleGraphics(paddle, color) {
    paddle.graphics.clear();
    paddle.graphics.fillStyle(color, 1);
    paddle.graphics.fillRoundedRect(
        paddle.body.x - PADDLE_WIDTH/2,
        paddle.body.y - PADDLE_HEIGHT/2,
        PADDLE_WIDTH, PADDLE_HEIGHT, 5
    );
}

function handlePaddleHit(ball, paddle) {
    // Calculate bounce angle based on where ball hits paddle
    const ballCenter = ball.body.y + BALL_SIZE / 2;
    const paddleTop = paddle.body.y - PADDLE_HEIGHT / 2;
    const paddleBottom = paddle.body.y + PADDLE_HEIGHT / 2;
    
    // Calculate relative hit position (-1 to 1)
    const relativeIntersect = (ballCenter - paddle.body.y) / (PADDLE_HEIGHT / 2);
    const clampedIntersect = Phaser.Math.Clamp(relativeIntersect, -1, 1);
    
    // Calculate bounce angle (max 60 degrees)
    const bounceAngle = clampedIntersect * (Math.PI / 3);
    
    // Get current speed
    const speed = Math.sqrt(ballVelocity.x * ballVelocity.x + ballVelocity.y * ballVelocity.y);
    const newSpeed = Math.min(speed * 1.02, BALL_SPEED * 2); // Slight speed increase, cap at 2x
    
    // Determine direction based on which paddle
    const direction = ballVelocity.x > 0 ? -1 : 1;
    
    // Set new velocity
    ballVelocity.x = direction * newSpeed * Math.cos(bounceAngle);
    ballVelocity.y = newSpeed * Math.sin(bounceAngle);
    
    // Push ball out of paddle to prevent multiple hits
    if (direction < 0) {
        ball.body.x = paddle.body.x + PADDLE_WIDTH/2 + 1;
    } else {
        ball.body.x = paddle.body.x - PADDLE_WIDTH/2 - BALL_SIZE - 1;
    }
}

function handleWallHit(body, gameObject) {
    // Wall collision handled in update loop
}

function checkWinCondition(scene, scoringPlayer) {
    if (player1Score >= WIN_SCORE) {
        gameState = 'gameover';
        gameOverText.setText('Player 1 Wins!\nPress SPACE to restart').setVisible(true);
        ballVelocity.x = 0;
        ballVelocity.y = 0;
        setupRestart(scene);
    } else if (player2Score >= WIN_SCORE) {
        gameState = 'gameover';
        gameOverText.setText('Player 2 (AI) Wins!\nPress SPACE to restart').setVisible(true);
        ballVelocity.x = 0;
        ballVelocity.y = 0;
        setupRestart(scene);
    } else {
        // Reset ball toward the player who was scored on
        resetBall(scene, scoringPlayer === 1 ? 2 : 1);
    }
}

function resetBall(scene, direction) {
    ball.body.x = config.width / 2;
    ball.body.y = config.height / 2;
    
    // Random angle between -30 and 30 degrees
    const angle = (Math.random() - 0.5) * (Math.PI / 3);
    
    ballVelocity.x = direction * BALL_SPEED * Math.cos(angle);
    ballVelocity.y = BALL_SPEED * Math.sin(angle);
}

function setupRestart(scene) {
    scene.input.keyboard.once('keydown-SPACE', () => {
        player1Score = 0;
        player2Score = 0;
        player1ScoreText.setText('0');
        player2ScoreText.setText('0');
        gameOverText.setVisible(false);
        gameState = 'playing';
        
        player1Paddle.body.y = config.height / 2;
        player2Paddle.body.y = config.height / 2;
        
        resetBall(scene, Math.random() > 0.5 ? 1 : -1);
    });
}
