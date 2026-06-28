/**
 * Space Invaders - HTML5 Canvas Implementation
 * ES6 Module-based game engine
 * Canvas: 480x640 (portrait), scales to container
 * Input: Keyboard (arrows + space) + Touch (mobile)
 */

// ============================================================
// Constants & Configuration
// ============================================================

const CONFIG = {
    CANVAS_WIDTH: 480,
    CANVAS_HEIGHT: 640,
    TARGET_FPS: 60,
    PLAYER_WIDTH: 40,
    PLAYER_HEIGHT: 40,
    PLAYER_SPEED: 5,
    PLAYER_COLOR: '#00ff00',
    BULLET_WIDTH: 6,
    BULLET_HEIGHT: 15,
    BULLET_SPEED: 7,
    BULLET_COLOR: '#ffff00',
    ENEMY_BULLET_COLOR: '#ff6400',
    SHOOT_COOLDOWN_MS: 250,
    FLEET_COLS: 8,
    FLEET_ROWS: 4,
    FLEET_SPACING_X: 55,
    FLEET_SPACING_Y: 45,
    FLEET_START_X: 30,
    FLEET_START_Y: 60,
    FLEET_MOVE_INTERVAL: 30,
    FLEET_DROP_AMOUNT: 20,
    ENEMY_SHOOT_INTERVAL: 60,
    ENEMY_SHOOT_CHANCE: 0.3
};

const COLORS = {
    GREEN: '#00ff00',
    YELLOW: '#ffff00',
    RED: '#ff0000',
    WHITE: '#ffffff',
    BLACK: '#000000',
    BG_COLOR: '#000000'
};

// ============================================================
// Game State Enum
// ============================================================

const GameState = Object.freeze({
    MENU: 'menu',
    PLAYING: 'playing',
    GAME_OVER: 'gameover'
});

// ============================================================
// Input Handler
// ============================================================

class InputHandler {
    constructor() {
        this.keysPressed = new Set();
        this.keysJustPressed = new Set();
        this.keysJustReleased = new Set();
        this.touchStartX = 0;
        this.touchActive = false;
        
        this._bindKeyboardEvents();
        this._bindTouchEvents();
    }
    
    _bindKeyboardEvents() {
        window.addEventListener('keydown', (e) => {
            if (['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown', 'Space', ' '].includes(e.code)) {
                e.preventDefault();
            }
            const keyCode = this._getKeyCode(e.code);
            if (!this.keysPressed.has(keyCode)) {
                this.keysJustPressed.add(keyCode);
            }
            this.keysPressed.add(keyCode);
        });
        
        window.addEventListener('keyup', (e) => {
            const keyCode = this._getKeyCode(e.code);
            if (this.keysPressed.has(keyCode)) {
                this.keysPressed.delete(keyCode);
                this.keysJustReleased.add(keyCode);
            }
        });
    }
    
    _bindTouchEvents() {
        const canvas = document.getElementById('gameCanvas');
        if (!canvas) return;
        
        canvas.addEventListener('touchstart', (e) => {
            e.preventDefault();
            this.touchActive = true;
            this.touchStartX = e.touches[0].clientX;
            // Simulate space press for shooting on touch
            if (!this.keysPressed.has(32)) {
                this.keysJustPressed.add(32);
            }
            this.keysPressed.add(32);
        });
        
        canvas.addEventListener('touchmove', (e) => {
            e.preventDefault();
            if (this.touchActive && e.touches.length > 0) {
                const currentX = e.touches[0].clientX;
                const deltaX = currentX - this.touchStartX;
                
                // Clear directional keys first
                this.keysPressed.delete(37); // Left
                this.keysPressed.delete(39); // Right
                
                // Set new directional keys based on swipe
                if (deltaX < -20) {
                    this.keysPressed.add(37);
                } else if (deltaX > 20) {
                    this.keysPressed.add(39);
                }
            }
        });
        
        canvas.addEventListener('touchend', (e) => {
            e.preventDefault();
            this.touchActive = false;
            this.keysPressed.delete(37);
            this.keysPressed.delete(39);
            this.keysPressed.delete(32);
        });
    }
    
    _getKeyCode(code) {
        const keyMap = {
            'ArrowLeft': 37,
            'ArrowUp': 38,
            'ArrowRight': 39,
            'ArrowDown': 40,
            'Space': 32,
            ' ': 32,
            'KeyW': 87,
            'KeyA': 65,
            'KeyS': 83,
            'KeyD': 68,
            'Escape': 27
        };
        return keyMap[code] || code.charCodeAt(0);
    }
    
    endFrame() {
        this.keysJustPressed.clear();
        this.keysJustReleased.clear();
    }
    
    isKeyPressed(keyCode) {
        return this.keysPressed.has(keyCode);
    }
    
    isKeyJustPressed(keyCode) {
        return this.keysJustPressed.has(keyCode);
    }
    
    isKeyJustReleased(keyCode) {
        return this.keysJustReleased.has(keyCode);
    }
    
    reset() {
        this.keysPressed.clear();
        this.keysJustPressed.clear();
        this.keysJustReleased.clear();
    }
}

// ============================================================
// Player
// ============================================================

class Player {
    constructor(screenWidth, screenHeight) {
        this.width = CONFIG.PLAYER_WIDTH;
        this.height = CONFIG.PLAYER_HEIGHT;
        this.x = (screenWidth - this.width) / 2;
        this.y = screenHeight - this.height - 20;
        this.speed = CONFIG.PLAYER_SPEED;
        this.health = 3;
        this.maxHealth = 3;
        this.screenWidth = screenWidth;
        this.screenHeight = screenHeight;
        this.animationFrame = 0;
    }
    
    moveLeft() {
        this.x = Math.max(0, this.x - this.speed);
    }
    
    moveRight() {
        this.x = Math.min(this.screenWidth - this.width, this.x + this.speed);
    }
    
    moveUp() {
        this.y = Math.max(0, this.y - this.speed);
    }
    
    moveDown() {
        this.y = Math.min(this.screenHeight - this.height, this.y + this.speed);
    }
    
    getRect() {
        return { x: this.x, y: this.y, width: this.width, height: this.height };
    }
    
    takeDamage() {
        this.health = Math.max(0, this.health - 1);
        return this.health > 0;
    }
    
    isAlive() {
        return this.health > 0;
    }
    
    reset(screenWidth, screenHeight) {
        this.screenWidth = screenWidth;
        this.screenHeight = screenHeight;
        this.x = (screenWidth - this.width) / 2;
        this.y = screenHeight - this.height - 20;
        this.health = this.maxHealth;
    }
    
    draw(ctx) {
        const cx = this.x + this.width / 2;
        const cy = this.y + this.height / 2;
        
        // Draw triangle ship
        ctx.fillStyle = CONFIG.PLAYER_COLOR;
        ctx.beginPath();
        ctx.moveTo(cx, this.y); // Top point
        ctx.lineTo(this.x, this.y + this.height); // Bottom left
        ctx.lineTo(this.x + this.width, this.y + this.height); // Bottom right
        ctx.closePath();
        ctx.fill();
        
        // Draw white border
        ctx.strokeStyle = COLORS.WHITE;
        ctx.lineWidth = 2;
        ctx.stroke();
        
        // Engine glow animation
        this.animationFrame++;
        if (this.animationFrame > 10) this.animationFrame = 0;
        
        const glowIntensity = Math.sin(this.animationFrame * 0.6) * 0.3 + 0.7;
        ctx.fillStyle = `rgba(0, 255, 255, ${glowIntensity})`;
        ctx.beginPath();
        ctx.moveTo(cx - 5, this.y + this.height);
        ctx.lineTo(cx, this.y + this.height + 8 + this.animationFrame % 4);
        ctx.lineTo(cx + 5, this.y + this.height);
        ctx.closePath();
        ctx.fill();
    }
}

// ============================================================
// Bullet
// ============================================================

class Bullet {
    constructor(x, y, isEnemy = false) {
        this.width = CONFIG.BULLET_WIDTH;
        this.height = CONFIG.BULLET_HEIGHT;
        this.x = x - this.width / 2;
        this.y = y;
        this.speed = isEnemy ? 5 : -CONFIG.BULLET_SPEED;
        this.isEnemy = isEnemy;
        this.active = true;
    }
    
    update() {
        this.y += this.speed;
        if (this.isEnemy) {
            if (this.y > CONFIG.CANVAS_HEIGHT) {
                this.active = false;
            }
        } else {
            if (this.y + this.height < 0) {
                this.active = false;
            }
        }
    }
    
    getRect() {
        return { x: this.x, y: this.y, width: this.width, height: this.height };
    }
    
    deactivate() {
        this.active = false;
    }
    
    isActive() {
        return this.active;
    }
    
    draw(ctx) {
        if (!this.active) return;
        
        // Main bullet
        ctx.fillStyle = this.isEnemy ? CONFIG.ENEMY_BULLET_COLOR : CONFIG.BULLET_COLOR;
        ctx.fillRect(this.x, this.y, this.width, this.height);
        
        // Glow effect
        ctx.fillStyle = this.isEnemy ? '#ffcc00' : '#ffffcc';
        ctx.fillRect(this.x + 1, this.y + 1, this.width - 2, this.height - 2);
    }
}

// ============================================================
// Enemy Base Class
// ============================================================

class Enemy {
    constructor(x, y, width = 40, height = 30, health = 1, speed = 1.0, points = 10, color = COLORS.GREEN) {
        this.x = x;
        this.y = y;
        this.width = width;
        this.height = height;
        this.health = health;
        this.maxHealth = health;
        this.speed = speed;
        this.points = points;
        this.color = color;
        this.active = true;
    }
    
    get rect() {
        return { x: this.x, y: this.y, width: this.width, height: this.height };
    }
    
    get center() {
        return { x: this.x + this.width / 2, y: this.y + this.height / 2 };
    }
    
    get bottom() {
        return this.y + this.height;
    }
    
    takeDamage(damage = 1) {
        this.health -= damage;
        if (this.health <= 0) {
            this.active = false;
            return true;
        }
        return false;
    }
    
    move(dx, dy) {
        this.x += dx * this.speed;
        this.y += dy * this.speed;
    }
    
    draw(ctx) {
        if (!this.active) return;
        
        ctx.fillStyle = this.color;
        ctx.fillRect(this.x, this.y, this.width, this.height);
        ctx.strokeStyle = COLORS.WHITE;
        ctx.lineWidth = 2;
        ctx.strokeRect(this.x, this.y, this.width, this.height);
    }
}

// ============================================================
// Basic Enemy
// ============================================================

class BasicEnemy extends Enemy {
    constructor(x, y) {
        super(x, y, 40, 30, 1, 1.0, 10, COLORS.GREEN);
    }
    
    draw(ctx) {
        if (!this.active) return;
        
        ctx.fillStyle = this.color;
        ctx.fillRect(this.x, this.y, this.width, this.height);
        
        // Antennae
        ctx.strokeStyle = this.color;
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(this.x + 8, this.y);
        ctx.lineTo(this.x + 5, this.y - 5);
        ctx.moveTo(this.x + this.width - 8, this.y);
        ctx.lineTo(this.x + this.width - 5, this.y - 5);
        ctx.stroke();
        
        // Eyes
        ctx.fillStyle = COLORS.BLACK;
        ctx.beginPath();
        ctx.arc(this.x + 12, this.y + 10, 4, 0, Math.PI * 2);
        ctx.arc(this.x + this.width - 12, this.y + 10, 4, 0, Math.PI * 2);
        ctx.fill();
        
        // Border
        ctx.strokeStyle = COLORS.WHITE;
        ctx.lineWidth = 2;
        ctx.strokeRect(this.x, this.y, this.width, this.height);
    }
}

// ============================================================
// Fast Enemy
// ============================================================

class FastEnemy extends Enemy {
    constructor(x, y) {
        super(x, y, 30, 25, 1, 1.8, 20, COLORS.YELLOW);
    }
    
    draw(ctx) {
        if (!this.active) return;
        
        const cx = this.x + this.width / 2;
        const topY = this.y + 5;
        const bottomY = this.y + this.height - 5;
        
        // Diamond shape
        ctx.fillStyle = this.color;
        ctx.beginPath();
        ctx.moveTo(cx, topY);
        ctx.lineTo(this.x + this.width, this.y + this.height / 2);
        ctx.lineTo(cx, bottomY);
        ctx.lineTo(this.x, this.y + this.height / 2);
        ctx.closePath();
        ctx.fill();
        
        // Speed lines
        ctx.strokeStyle = this.color;
        ctx.lineWidth = 1;
        for (let i = 0; i < 3; i++) {
            const lineY = this.y - 3 - i * 3;
            ctx.beginPath();
            ctx.moveTo(this.x + 5, lineY);
            ctx.lineTo(this.x + 10, lineY);
            ctx.moveTo(this.x + this.width - 10, lineY);
            ctx.lineTo(this.x + this.width - 5, lineY);
            ctx.stroke();
        }
        
        // Border
        ctx.strokeStyle = COLORS.WHITE;
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(cx, topY);
        ctx.lineTo(this.x + this.width, this.y + this.height / 2);
        ctx.lineTo(cx, bottomY);
        ctx.lineTo(this.x, this.y + this.height / 2);
        ctx.closePath();
        ctx.stroke();
    }
}

// ============================================================
// Tank Enemy
// ============================================================

class TankEnemy extends Enemy {
    constructor(x, y) {
        super(x, y, 50, 40, 3, 0.6, 30, COLORS.RED);
    }
    
    draw(ctx) {
        if (!this.active) return;
        
        // Main body
        ctx.fillStyle = this.color;
        ctx.fillRect(this.x, this.y, this.width, this.height);
        
        // Armor plating
        ctx.fillStyle = '#b40000';
        ctx.fillRect(this.x + 2, this.y + 2, this.width - 4, 10);
        
        // Shield lines
        ctx.strokeStyle = '#640000';
        ctx.lineWidth = 2;
        for (let i = 0; i < 3; i++) {
            const lineX = this.x + 12 + i * 12;
            ctx.beginPath();
            ctx.moveTo(lineX, this.y);
            ctx.lineTo(lineX, this.y + this.height);
            ctx.stroke();
        }
        
        // Eyes
        ctx.fillStyle = COLORS.BLACK;
        const eyeY = this.y + 20;
        for (let i = 0; i < 3; i++) {
            const eyeX = this.x + 12 + i * 13;
            ctx.beginPath();
            ctx.arc(eyeX, eyeY, 3, 0, Math.PI * 2);
            ctx.fill();
        }
        
        // Border
        ctx.strokeStyle = COLORS.WHITE;
        ctx.lineWidth = 3;
        ctx.strokeRect(this.x, this.y, this.width, this.height);
        
        // Health bar
        this._drawHealthBar(ctx);
    }
    
    _drawHealthBar(ctx) {
        const barWidth = this.width;
        const barHeight = 4;
        const barY = this.y + this.height + 3;
        
        // Background
        ctx.fillStyle = '#323232';
        ctx.fillRect(this.x, barY, barWidth, barHeight);
        
        // Health fill
        const healthRatio = this.health / this.maxHealth;
        const fillWidth = barWidth * healthRatio;
        
        let healthColor;
        if (healthRatio > 0.6) healthColor = COLORS.GREEN;
        else if (healthRatio > 0.3) healthColor = COLORS.YELLOW;
        else healthColor = COLORS.RED;
        
        ctx.fillStyle = healthColor;
        ctx.fillRect(this.x, barY, fillWidth, barHeight);
    }
}

// ============================================================
// Alien Fleet
// ============================================================

class AlienFleet {
    constructor() {
        this.cols = CONFIG.FLEET_COLS;
        this.rows = CONFIG.FLEET_ROWS;
        this.spacingX = CONFIG.FLEET_SPACING_X;
        this.spacingY = CONFIG.FLEET_SPACING_Y;
        this.startX = CONFIG.FLEET_START_X;
        this.startY = CONFIG.FLEET_START_Y;
        
        this.enemies = [];
        this.bullets = [];
        
        this.direction = 1;
        this.baseSpeed = 1.0;
        this.moveTimer = 0;
        this.moveInterval = CONFIG.FLEET_MOVE_INTERVAL;
        this.dropAmount = CONFIG.FLEET_DROP_AMOUNT;
        
        this.shootInterval = CONFIG.ENEMY_SHOOT_INTERVAL;
        this.shootTimer = 0;
        this.shootChance = CONFIG.ENEMY_SHOOT_CHANCE;
        
        this.screenWidth = CONFIG.CANVAS_WIDTH;
        this.screenHeight = CONFIG.CANVAS_HEIGHT;
        this.minX = 10;
        this.maxX = CONFIG.CANVAS_WIDTH - 10;
        
        this._initializeFleet();
    }
    
    _initializeFleet() {
        this.enemies = [];
        
        for (let row = 0; row < this.rows; row++) {
            const enemyRow = [];
            for (let col = 0; col < this.cols; col++) {
                const x = this.startX + col * this.spacingX;
                const y = this.startY + row * this.spacingY;
                
                let enemy;
                if (row === 0) {
                    enemy = new TankEnemy(x, y);
                } else if (row === 1) {
                    enemy = new FastEnemy(x, y);
                } else {
                    enemy = new BasicEnemy(x, y);
                }
                
                enemyRow.push(enemy);
            }
            this.enemies.push(enemyRow);
        }
    }
    
    getAllEnemies() {
        const allEnemies = [];
        for (const row of this.enemies) {
            for (const enemy of row) {
                if (enemy.active) {
                    allEnemies.push(enemy);
                }
            }
        }
        return allEnemies;
    }
    
    getActiveCount() {
        return this.getAllEnemies().length;
    }
    
    isEmpty() {
        return this.getActiveCount() === 0;
    }
    
    getFleetBounds() {
        const allEnemies = this.getAllEnemies();
        if (allEnemies.length === 0) {
            return { minX: 0, minY: 0, maxX: 0, maxY: 0 };
        }
        
        let minX = Infinity;
        let minY = Infinity;
        let maxX = -Infinity;
        let maxY = -Infinity;
        
        for (const enemy of allEnemies) {
            minX = Math.min(minX, enemy.x);
            minY = Math.min(minY, enemy.y);
            maxX = Math.max(maxX, enemy.x + enemy.width);
            maxY = Math.max(maxY, enemy.y + enemy.height);
        }
        
        return { minX, minY, maxX, maxY };
    }
    
    update() {
        this.moveTimer++;
        
        // Calculate current move interval based on remaining enemies
        const currentInterval = Math.max(5, Math.floor(this.moveInterval * (50 / Math.max(this.getActiveCount(), 1))));
        
        // Move the fleet
        if (this.moveTimer >= currentInterval) {
            this.moveTimer = 0;
            this._moveFleet();
        }
        
        // Update bullets
        this._updateBullets();
        
        // Handle shooting
        this.shootTimer++;
        if (this.shootTimer >= this.shootInterval) {
            this.shootTimer = 0;
            this._enemyShoot();
        }
    }
    
    _moveFleet() {
        const bounds = this.getFleetBounds();
        const moveAmount = this.baseSpeed * 10 * this.direction;
        
        let shouldDrop = false;
        if (this.direction > 0 && bounds.maxX + moveAmount > this.maxX) {
            shouldDrop = true;
        } else if (this.direction < 0 && bounds.minX + moveAmount < this.minX) {
            shouldDrop = true;
        }
        
        if (shouldDrop) {
            for (const enemy of this.getAllEnemies()) {
                enemy.y += this.dropAmount;
            }
            this.direction *= -1;
        } else {
            for (const enemy of this.getAllEnemies()) {
                enemy.x += moveAmount;
            }
        }
    }
    
    _updateBullets() {
        for (const bullet of this.bullets) {
            bullet.update();
        }
        this.bullets = this.bullets.filter(b => b.active);
    }
    
    _enemyShoot() {
        const shooters = this._getShooters();
        
        if (shooters.length === 0) return;
        
        for (const enemy of shooters) {
            if (Math.random() < this.shootChance) {
                const bullet = new Bullet(
                    enemy.x + enemy.width / 2,
                    enemy.y + enemy.height,
                    true
                );
                bullet.speed = 4 + enemy.speed;
                this.bullets.push(bullet);
            }
        }
    }
    
    _getShooters() {
        const shooters = [];
        
        for (let col = 0; col < this.cols; col++) {
            let bottomEnemy = null;
            let bottomY = -Infinity;
            
            for (let row = this.rows - 1; row >= 0; row--) {
                const enemy = this.enemies[row][col];
                if (enemy.active && enemy.y > bottomY) {
                    bottomY = enemy.y;
                    bottomEnemy = enemy;
                }
            }
            
            if (bottomEnemy) {
                shooters.push(bottomEnemy);
            }
        }
        
        return shooters;
    }
    
    draw(ctx) {
        for (const enemy of this.getAllEnemies()) {
            enemy.draw(ctx);
        }
        
        for (const bullet of this.bullets) {
            bullet.draw(ctx);
        }
    }
    
    checkCollision(rect) {
        for (const enemy of this.getAllEnemies()) {
            if (this._rectsCollide(enemy.rect, rect)) {
                return enemy;
            }
        }
        return null;
    }
    
    _rectsCollide(a, b) {
        return a.x < b.x + b.width &&
               a.x + a.width > b.x &&
               a.y < b.y + b.height &&
               a.y + a.height > b.y;
    }
    
    removeBullet(bullet) {
        bullet.active = false;
    }
    
    reset() {
        this.bullets = [];
        this.direction = 1;
        this.moveTimer = 0;
        this.shootTimer = 0;
        this._initializeFleet();
    }
    
    getLowestEnemyY() {
        let lowestY = 0;
        for (const enemy of this.getAllEnemies()) {
            if (enemy.y + enemy.height > lowestY) {
                lowestY = enemy.y + enemy.height;
            }
        }
        return lowestY;
    }
    
    reachedPlayerLine(playerY) {
        return this.getLowestEnemyY() >= playerY;
    }
}

// ============================================================
// Collision Detection
// ============================================================

class CollisionDetector {
    static rectsCollide(a, b) {
        return a.x < b.x + b.width &&
               a.x + a.width > b.x &&
               a.y < b.y + b.height &&
               a.y + a.height > b.y;
    }
}

// ============================================================
// Game Controller
// ============================================================

class GameController {
    constructor(screenWidth, screenHeight) {
        this.screenWidth = screenWidth;
        this.screenHeight = screenHeight;
        
        this.player = new Player(screenWidth, screenHeight);
        this.fleet = new AlienFleet();
        this.playerBullets = [];
        
        this.shootCooldownMs = CONFIG.SHOOT_COOLDOWN_MS;
        this.lastShotTime = 0;
    }
    
    handleInput(inputHandler) {
        if (inputHandler.isKeyPressed(37) || inputHandler.isKeyPressed(65)) { // Left or A
            this.player.moveLeft();
        }
        if (inputHandler.isKeyPressed(39) || inputHandler.isKeyPressed(68)) { // Right or D
            this.player.moveRight();
        }
        if (inputHandler.isKeyPressed(38) || inputHandler.isKeyPressed(87)) { // Up or W
            this.player.moveUp();
        }
        if (inputHandler.isKeyPressed(40) || inputHandler.isKeyPressed(83)) { // Down or S
            this.player.moveDown();
        }
    }
    
    canShoot() {
        const currentTimeMs = Date.now();
        return (currentTimeMs - this.lastShotTime) >= this.shootCooldownMs;
    }
    
    shoot() {
        if (this.canShoot()) {
            const bulletX = this.player.x + this.player.width / 2;
            const bulletY = this.player.y;
            const newBullet = new Bullet(bulletX, bulletY);
            this.playerBullets.push(newBullet);
            this.lastShotTime = Date.now();
            return true;
        }
        return false;
    }
    
    update(inputHandler) {
        this.handleInput(inputHandler);
        
        // Update player bullets
        for (const bullet of this.playerBullets) {
            bullet.update();
        }
        
        // Remove inactive bullets
        this.playerBullets = this.playerBullets.filter(b => b.isActive());
        
        // Update fleet
        this.fleet.update();
    }
    
    checkCollisions() {
        let scoreGained = 0;
        
        // Check player bullets vs enemies
        for (const bullet of this.playerBullets) {
            if (!bullet.isActive()) continue;
            
            const enemy = this.fleet.checkCollision(bullet.getRect());
            if (enemy) {
                bullet.deactivate();
                if (enemy.takeDamage()) {
                    scoreGained += enemy.points;
                }
            }
        }
        
        // Check enemy bullets vs player
        const playerRect = this.player.getRect();
        for (const bullet of this.fleet.bullets) {
            if (!bullet.isActive()) continue;
            
            if (CollisionDetector.rectsCollide(bullet.getRect(), playerRect)) {
                bullet.deactivate();
                this.player.takeDamage();
            }
        }
        
        return scoreGained;
    }
    
    draw(ctx) {
        this.player.draw(ctx);
        
        for (const bullet of this.playerBullets) {
            bullet.draw(ctx);
        }
        
        this.fleet.draw(ctx);
    }
    
    getPlayer() {
        return this.player;
    }
    
    isPlayerAlive() {
        return this.player.isAlive();
    }
    
    isFleetEmpty() {
        return this.fleet.isEmpty();
    }
    
    fleetReachedPlayer() {
        return this.fleet.reachedPlayerLine(this.player.y);
    }
    
    reset(screenWidth, screenHeight) {
        this.screenWidth = screenWidth;
        this.screenHeight = screenHeight;
        this.player.reset(screenWidth, screenHeight);
        this.playerBullets = [];
        this.fleet.reset();
        this.lastShotTime = 0;
    }
}

// ============================================================
// Renderer
// ============================================================

class Renderer {
    constructor(ctx, canvas) {
        this.ctx = ctx;
        this.canvas = canvas;
        this.backgroundColor = COLORS.BG_COLOR;
    }
    
    clear() {
        this.ctx.fillStyle = this.backgroundColor;
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
    }
    
    drawText(text, x, y, options = {}) {
        const {
            size = 24,
            color = COLORS.WHITE,
            center = false,
            bold = false
        } = options;
        
        this.ctx.font = `${bold ? 'bold ' : ''}${size}px Arial`;
        this.ctx.fillStyle = color;
        this.ctx.textAlign = center ? 'center' : 'left';
        this.ctx.textBaseline = center ? 'middle' : 'top';
        this.ctx.fillText(text, x, y);
    }
    
    drawRect(x, y, width, height, options = {}) {
        const {
            color = COLORS.WHITE,
            filled = true,
            borderWidth = 0
        } = options;
        
        this.ctx.fillStyle = color;
        if (filled) {
            this.ctx.fillRect(x, y, width, height);
        }
        if (borderWidth > 0) {
            this.ctx.strokeStyle = color;
            this.ctx.lineWidth = borderWidth;
            this.ctx.strokeRect(x, y, width, height);
        }
    }
}

// ============================================================
// Main Game Class
// ============================================================

class Game {
    constructor() {
        this.canvas = document.getElementById('gameCanvas');
        if (!this.canvas) {
            throw new Error('Canvas element not found');
        }
        
        this.ctx = this.canvas.getContext('2d');
        this.renderer = new Renderer(this.ctx, this.canvas);
        this.inputHandler = new InputHandler();
        
        this.state = GameState.MENU;
        this.score = 0;
        this.lives = 3;
        this.frameCount = 0;
        this.lastFrameTime = 0;
        this.targetFrameTime = 1000 / CONFIG.TARGET_FPS;
        
        this.gameController = null;
        
        this._scaleCanvas();
        window.addEventListener('resize', () => this._scaleCanvas());
        
        this._setupStartButton();
    }
    
    _scaleCanvas() {
        const container = this.canvas.parentElement;
        if (!container) return;
        
        const containerWidth = container.clientWidth;
        const containerHeight = container.clientHeight;
        
        const scaleX = containerWidth / CONFIG.CANVAS_WIDTH;
        const scaleY = containerHeight / CONFIG.CANVAS_HEIGHT;
        const scale = Math.min(scaleX, scaleY);
        
        this.canvas.width = CONFIG.CANVAS_WIDTH;
        this.canvas.height = CONFIG.CANVAS_HEIGHT;
        this.canvas.style.width = `${CONFIG.CANVAS_WIDTH * scale}px`;
        this.canvas.style.height = `${CONFIG.CANVAS_HEIGHT * scale}px`;
    }
    
    _setupStartButton() {
        const startButton = document.getElementById('startButton');
        if (startButton) {
            startButton.addEventListener('click', () => this._startGame());
        }
    }
    
    _startGame() {
        this.state = GameState.PLAYING;
        this.score = 0;
        this.lives = 3;
        this.inputHandler.reset();
        this.gameController = new GameController(CONFIG.CANVAS_WIDTH, CONFIG.CANVAS_HEIGHT);
        
        const startScreen = document.getElementById('startScreen');
        if (startScreen) {
            startScreen.style.display = 'none';
        }
    }
    
    _endGame() {
        this.state = GameState.GAME_OVER;
    }
    
    run() {
        this._gameLoop();
    }
    
    _gameLoop() {
        const currentTime = performance.now();
        const deltaTime = currentTime - this.lastFrameTime;
        
        if (deltaTime >= this.targetFrameTime) {
            this.lastFrameTime = currentTime - (deltaTime % this.targetFrameTime);
            this._processEvents();
            this._update();
            this._render();
            this.frameCount++;
        }
        
        requestAnimationFrame(() => this._gameLoop());
    }
    
    _processEvents() {
        if (this.state === GameState.MENU) {
            if (this.inputHandler.isKeyJustPressed(32)) { // Space
                this._startGame();
            }
        } else if (this.state === GameState.GAME_OVER) {
            if (this.inputHandler.isKeyJustPressed(32)) { // Space
                this._startGame();
            }
        }
        
        this.inputHandler.endFrame();
    }
    
    _update() {
        if (this.state !== GameState.PLAYING || !this.gameController) return;
        
        // Handle shooting
        if (this.inputHandler.isKeyPressed(32)) { // Space
            this.gameController.shoot();
        }
        
        // Update game controller
        this.gameController.update(this.inputHandler);
        
        // Check collisions
        const pointsGained = this.gameController.checkCollisions();
        this.score += pointsGained;
        
        // Check game over conditions
        if (!this.gameController.isPlayerAlive()) {
            this.lives--;
            if (this.lives <= 0) {
                this._endGame();
            } else {
                // Reset player position but keep score and fleet
                this.gameController.reset(CONFIG.CANVAS_WIDTH, CONFIG.CANVAS_HEIGHT);
                this.gameController = new GameController(CONFIG.CANVAS_WIDTH, CONFIG.CANVAS_HEIGHT);
                this.gameController.score = this.score;
            }
        }
        
        if (this.gameController.isFleetEmpty()) {
            // Reset fleet for next wave
            this.gameController.reset(CONFIG.CANVAS_WIDTH, CONFIG.CANVAS_HEIGHT);
            this.gameController.score = this.score;
        }
        
        if (this.gameController.fleetReachedPlayer()) {
            this._endGame();
        }
    }
    
    _render() {
        this.renderer.clear();
        
        if (this.state === GameState.MENU) {
            this._renderMenu();
        } else if (this.state === GameState.PLAYING) {
            this._renderPlaying();
        } else if (this.state === GameState.GAME_OVER) {
            this._renderGameOver();
        }
    }
    
    _renderMenu() {
        this.renderer.drawText('SPACE INVADERS', CONFIG.CANVAS_WIDTH / 2, 200, {
            size: 42,
            color: COLORS.WHITE,
            center: true,
            bold: true
        });
        
        this.renderer.drawText('Press SPACE to Start', CONFIG.CANVAS_WIDTH / 2, 320, {
            size: 22,
            color: '#cccccc',
            center: true
        });
        
        this.renderer.drawText('Arrow Keys to Move | SPACE to Fire', CONFIG.CANVAS_WIDTH / 2, 420, {
            size: 16,
            color: '#999999',
            center: true
        });
    }
    
    _renderPlaying() {
        if (this.gameController) {
            this.gameController.draw(this.ctx);
        }
        
        // Draw HUD
        this.renderer.drawText(`Score: ${this.score}`, 20, 20, { size: 18, color: COLORS.WHITE });
        this.renderer.drawText(`Lives: ${this.lives}`, CONFIG.CANVAS_WIDTH - 20, 20, {
            size: 18,
            color: COLORS.WHITE,
            center: true
        });
    }
    
    _renderGameOver() {
        this.renderer.drawText('GAME OVER', CONFIG.CANVAS_WIDTH / 2, 200, {
            size: 42,
            color: COLORS.RED,
            center: true,
            bold: true
        });
        
        this.renderer.drawText(`Final Score: ${this.score}`, CONFIG.CANVAS_WIDTH / 2, 300, {
            size: 28,
            color: COLORS.WHITE,
            center: true
        });
        
        this.renderer.drawText('Press SPACE to Restart', CONFIG.CANVAS_WIDTH / 2, 400, {
            size: 22,
            color: '#cccccc',
            center: true
        });
    }
}

// ============================================================
// Initialize Game
// ============================================================

let gameInstance = null;
let jarvisBridge = null;

class JarvisBridge {
    constructor() {
        window.addEventListener('message', (e) => {
            if (e.data && e.data.type === 'jarvis_input') {
                this.handleInput(e.data.action);
            }
        });
    }
    
    handleInput(action) {
        if (!gameInstance) return;
        const input = gameInstance.input;
        switch(action) {
            case 'up': input.keysJustPressed.add('ArrowUp'); break;
            case 'down': input.keysJustPressed.add('ArrowDown'); break;
            case 'left': input.keysJustPressed.add('ArrowLeft'); break;
            case 'right': input.keysJustPressed.add('ArrowRight'); break;
            case 'a': input.keysJustPressed.add('Space'); break;
            case 'b': input.keysJustPressed.add('Escape'); break;
            case 'start': input.keysJustPressed.add('Enter'); break;
        }
    }
}

function initGame() {
    try {
        jarvisBridge = new JarvisBridge();
        gameInstance = new Game();
        gameInstance.run();
    } catch (error) {
        console.error('Failed to initialize game:', error);
    }
}

// Start game when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initGame);
} else {
    initGame();
}

// Export for debugging
export { Game, GameController, Player, Enemy, Bullet, AlienFleet, InputHandler };
