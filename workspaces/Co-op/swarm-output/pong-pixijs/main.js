// Pong Game - PixiJS v8
const CONFIG = {
    CANVAS_WIDTH: 800,
    CANVAS_HEIGHT: 600,
    PADDLE_WIDTH: 15,
    PADDLE_HEIGHT: 100,
    PADDLE_SPEED: 8,
    BALL_SIZE: 15,
    BALL_SPEED: 7,
    BALL_MAX_SPEED: 15,
    WINNING_SCORE: 11,
    COLORS: {
        PADDLE: 0x00ff88,
        BALL: 0xffffff,
        COURT: 0x333333,
        NET: 0x444444
    }
};

class PongGame {
    constructor() {
        this.app = null;
        this.leftPaddle = null;
        this.rightPaddle = null;
        this.ball = null;
        this.leftScore = 0;
        this.rightScore = 0;
        this.ballVelocity = { x: 0, y: 0 };
        this.keys = {};
        this.gameRunning = false;
        this.animationId = null;

        this.init();
    }

    async init() {
        this.app = new PIXI.Application();

        await this.app.init({
            width: CONFIG.CANVAS_WIDTH,
            height: CONFIG.CANVAS_HEIGHT,
            canvas: document.getElementById('game-canvas'),
            backgroundColor: 0x111111,
            antialias: true,
            resolution: window.devicePixelRatio || 1,
            autoDensity: true
        });

        this.createCourt();
        this.createPaddles();
        this.createBall();
        this.setupControls();
        this.setupUI();

        this.app.ticker.add(this.gameLoop.bind(this));
    }

    createCourt() {
        const court = new PIXI.Graphics();
        
        // Court border
        court.rect(2, 2, CONFIG.CANVAS_WIDTH - 4, CONFIG.CANVAS_HEIGHT - 4);
        court.stroke({ width: 2, color: CONFIG.COLORS.COURT });

        // Center line (dashed)
        const dashHeight = 20;
        const gapHeight = 15;
        for (let y = dashHeight / 2; y < CONFIG.CANVAS_HEIGHT; y += dashHeight + gapHeight) {
            court.rect(CONFIG.CANVAS_WIDTH / 2 - 2, y, 4, dashHeight);
            court.fill({ color: CONFIG.COLORS.NET });
        }

        this.app.stage.addChild(court);
    }

    createPaddles() {
        const paddleOptions = {
            width: CONFIG.PADDLE_WIDTH,
            height: CONFIG.PADDLE_HEIGHT,
            fill: CONFIG.COLORS.PADDLE,
            radius: 5
        };

        // Left paddle
        this.leftPaddle = new PIXI.Graphics();
        this.leftPaddle.roundRect(0, 0, paddleOptions.width, paddleOptions.height, paddleOptions.radius);
        this.leftPaddle.fill(paddleOptions.fill);
        this.leftPaddle.x = 30;
        this.leftPaddle.y = (CONFIG.CANVAS_HEIGHT - CONFIG.PADDLE_HEIGHT) / 2;
        this.app.stage.addChild(this.leftPaddle);

        // Right paddle
        this.rightPaddle = new PIXI.Graphics();
        this.rightPaddle.roundRect(0, 0, paddleOptions.width, paddleOptions.height, paddleOptions.radius);
        this.rightPaddle.fill(paddleOptions.fill);
        this.rightPaddle.x = CONFIG.CANVAS_WIDTH - 30 - CONFIG.PADDLE_WIDTH;
        this.rightPaddle.y = (CONFIG.CANVAS_HEIGHT - CONFIG.PADDLE_HEIGHT) / 2;
        this.app.stage.addChild(this.rightPaddle);
    }

    createBall() {
        this.ball = new PIXI.Graphics();
        this.ball.circle(0, 0, CONFIG.BALL_SIZE);
        this.ball.fill(CONFIG.COLORS.BALL);
        this.ball.x = CONFIG.CANVAS_WIDTH / 2;
        this.ball.y = CONFIG.CANVAS_HEIGHT / 2;
        this.app.stage.addChild(this.ball);
    }

    resetBall(direction = 1) {
        this.ball.x = CONFIG.CANVAS_WIDTH / 2;
        this.ball.y = CONFIG.CANVAS_HEIGHT / 2;
        
        const angle = (Math.random() * 0.5 - 0.25) * Math.PI;
        const speed = CONFIG.BALL_SPEED;
        
        this.ballVelocity.x = Math.cos(angle) * speed * direction;
        this.ballVelocity.y = Math.sin(angle) * speed;
    }

    setupControls() {
        window.addEventListener('keydown', (e) => {
            this.keys[e.key] = true;
            if (['ArrowUp', 'ArrowDown', 'w', 's', 'W', 'S'].includes(e.key)) {
                e.preventDefault();
            }
        });

        window.addEventListener('keyup', (e) => {
            this.keys[e.key] = false;
        });
    }

    setupUI() {
        const startBtn = document.getElementById('start-btn');
        const restartBtn = document.getElementById('restart-btn');

        startBtn.addEventListener('click', () => this.startGame());
        restartBtn.addEventListener('click', () => this.startGame());
    }

    startGame() {
        document.getElementById('start-overlay').classList.add('hidden');
        document.getElementById('win-overlay').classList.add('hidden');
        
        this.leftScore = 0;
        this.rightScore = 0;
        this.updateScoreDisplay();
        
        this.resetBall(Math.random() > 0.5 ? 1 : -1);
        this.gameRunning = true;
    }

    updateScoreDisplay() {
        document.getElementById('score-left').textContent = this.leftScore;
        document.getElementById('score-right').textContent = this.rightScore;
    }

    checkWin() {
        if (this.leftScore >= CONFIG.WINNING_SCORE) {
            this.endGame('Player 1 Wins!');
            return true;
        }
        if (this.rightScore >= CONFIG.WINNING_SCORE) {
            this.endGame('Player 2 Wins!');
            return true;
        }
        return false;
    }

    endGame(message) {
        this.gameRunning = false;
        document.getElementById('win-message').textContent = message;
        document.getElementById('win-overlay').classList.remove('hidden');
    }

    updatePaddles() {
        // Left paddle - W/S or Up/Down arrows
        if (this.keys['w'] || this.keys['W'] || this.keys['ArrowUp']) {
            this.leftPaddle.y -= CONFIG.PADDLE_SPEED;
        }
        if (this.keys['s'] || this.keys['S'] || this.keys['ArrowDown']) {
            this.leftPaddle.y += CONFIG.PADDLE_SPEED;
        }

        // Clamp left paddle
        this.leftPaddle.y = Math.max(0, Math.min(
            CONFIG.CANVAS_HEIGHT - CONFIG.PADDLE_HEIGHT,
            this.leftPaddle.y
        ));

        // Simple AI for right paddle
        const paddleCenter = this.rightPaddle.y + CONFIG.PADDLE_HEIGHT / 2;
        const ballCenter = this.ball.y;
        const aiSpeed = CONFIG.PADDLE_SPEED * 0.7;

        if (ballCenter < paddleCenter - 10) {
            this.rightPaddle.y -= aiSpeed;
        } else if (ballCenter > paddleCenter + 10) {
            this.rightPaddle.y += aiSpeed;
        }

        // Clamp right paddle
        this.rightPaddle.y = Math.max(0, Math.min(
            CONFIG.CANVAS_HEIGHT - CONFIG.PADDLE_HEIGHT,
            this.rightPaddle.y
        ));
    }

    updateBall() {
        if (!this.gameRunning) return;

        this.ball.x += this.ballVelocity.x;
        this.ball.y += this.ballVelocity.y;

        // Top/bottom collision
        if (this.ball.y - CONFIG.BALL_SIZE <= 0) {
            this.ball.y = CONFIG.BALL_SIZE;
            this.ballVelocity.y *= -1;
        }
        if (this.ball.y + CONFIG.BALL_SIZE >= CONFIG.CANVAS_HEIGHT) {
            this.ball.y = CONFIG.CANVAS_HEIGHT - CONFIG.BALL_SIZE;
            this.ballVelocity.y *= -1;
        }

        // Left paddle collision
        if (this.ballVelocity.x < 0 &&
            this.ball.x - CONFIG.BALL_SIZE <= this.leftPaddle.x + CONFIG.PADDLE_WIDTH &&
            this.ball.x - CONFIG.BALL_SIZE >= this.leftPaddle.x &&
            this.ball.y >= this.leftPaddle.y &&
            this.ball.y <= this.leftPaddle.y + CONFIG.PADDLE_HEIGHT) {
            
            this.ball.x = this.leftPaddle.x + CONFIG.PADDLE_WIDTH + CONFIG.BALL_SIZE;
            
            const hitPos = (this.ball.y - this.leftPaddle.y) / CONFIG.PADDLE_HEIGHT;
            const angle = (hitPos - 0.5) * Math.PI * 0.6;
            
            const speed = Math.min(
                Math.sqrt(this.ballVelocity.x ** 2 + this.ballVelocity.y ** 2) * 1.05,
                CONFIG.BALL_MAX_SPEED
            );
            
            this.ballVelocity.x = Math.cos(angle) * speed;
            this.ballVelocity.y = Math.sin(angle) * speed;
        }

        // Right paddle collision
        if (this.ballVelocity.x > 0 &&
            this.ball.x + CONFIG.BALL_SIZE >= this.rightPaddle.x &&
            this.ball.x + CONFIG.BALL_SIZE <= this.rightPaddle.x + CONFIG.PADDLE_WIDTH &&
            this.ball.y >= this.rightPaddle.y &&
            this.ball.y <= this.rightPaddle.y + CONFIG.PADDLE_HEIGHT) {
            
            this.ball.x = this.rightPaddle.x - CONFIG.BALL_SIZE;
            
            const hitPos = (this.ball.y - this.rightPaddle.y) / CONFIG.PADDLE_HEIGHT;
            const angle = Math.PI - (hitPos - 0.5) * Math.PI * 0.6;
            
            const speed = Math.min(
                Math.sqrt(this.ballVelocity.x ** 2 + this.ballVelocity.y ** 2) * 1.05,
                CONFIG.BALL_MAX_SPEED
            );
            
            this.ballVelocity.x = Math.cos(angle) * speed;
            this.ballVelocity.y = Math.sin(angle) * speed;
        }

        // Score detection
        if (this.ball.x - CONFIG.BALL_SIZE <= 0) {
            this.rightScore++;
            this.updateScoreDisplay();
            if (!this.checkWin()) {
                this.resetBall(-1);
            }
        }
        if (this.ball.x + CONFIG.BALL_SIZE >= CONFIG.CANVAS_WIDTH) {
            this.leftScore++;
            this.updateScoreDisplay();
            if (!this.checkWin()) {
                this.resetBall(1);
            }
        }
    }

    gameLoop() {
        if (this.gameRunning) {
            this.updatePaddles();
            this.updateBall();
        }
    }
}

// Initialize game when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new PongGame();
});