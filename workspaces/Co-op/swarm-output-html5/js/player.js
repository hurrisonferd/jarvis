/**
 * Player class for HTML5 Space Invaders game.
 * Ported from pygame implementation.
 */

export class Player {
  /**
   * Initialize the player at bottom center of screen.
   * @param {number} screenWidth - Width of the game screen
   * @param {number} screenHeight - Height of the game screen
   * @param {string} spriteStyle - Sprite style - "triangle", "detailed", or "classic"
   */
  constructor(screenWidth, screenHeight, spriteStyle = 'triangle') {
    // Size: 40x40 pixels
    this.width = 40;
    this.height = 40;

    // Position: start at bottom center
    this.x = (screenWidth - this.width) / 2;
    this.y = screenHeight - this.height - 20; // 20px from bottom

    // Velocity for smooth movement
    this.vx = 0;
    this.vy = 0;

    // Movement speed: 5 pixels per frame
    this.speed = 5;

    // Health: 3 lives
    this.health = 3;
    this.maxHealth = 3;

    // Screen boundaries
    this.screenWidth = screenWidth;
    this.screenHeight = screenHeight;

    // Sprite style
    this.spriteStyle = spriteStyle;
    this.animationFrame = 0;

    // Shooting cooldown (milliseconds)
    this.shootCooldown = 250; // 250ms between shots
    this.lastShotTime = 0;

    // Input state
    this.keys = {
      left: false,
      right: false,
      up: false,
      down: false,
      shoot: false
    };

    // Colors (from pygame sprites)
    this.mainColor = '#00ff00';
    this.secondaryColor = '#00b400';
    this.accentColor = '#00ffff';
    this.cockpitColor = '#64ffff';
    this.engineColor = '#ff6400';
  }

  /**
   * Set up keyboard event listeners.
   * @param {HTMLCanvasElement} canvas - The game canvas
   */
  setupInput(canvas) {
    const handleKeyDown = (e) => {
      switch (e.code) {
        case 'ArrowLeft':
        case 'KeyA':
          this.keys.left = true;
          e.preventDefault();
          break;
        case 'ArrowRight':
        case 'KeyD':
          this.keys.right = true;
          e.preventDefault();
          break;
        case 'ArrowUp':
        case 'KeyW':
          this.keys.up = true;
          e.preventDefault();
          break;
        case 'ArrowDown':
        case 'KeyS':
          this.keys.down = true;
          e.preventDefault();
          break;
        case 'Space':
          this.keys.shoot = true;
          e.preventDefault();
          break;
      }
    };

    const handleKeyUp = (e) => {
      switch (e.code) {
        case 'ArrowLeft':
        case 'KeyA':
          this.keys.left = false;
          break;
        case 'ArrowRight':
        case 'KeyD':
          this.keys.right = false;
          break;
        case 'ArrowUp':
        case 'KeyW':
          this.keys.up = false;
          break;
        case 'ArrowDown':
        case 'KeyS':
          this.keys.down = false;
          break;
        case 'Space':
          this.keys.shoot = false;
          break;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    window.addEventListener('keyup', handleKeyUp);

    // Return cleanup function
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      window.removeEventListener('keyup', handleKeyUp);
    };
  }

  /**
   * Update player position based on input.
   */
  update() {
    // Calculate velocity from input
    this.vx = 0;
    this.vy = 0;

    if (this.keys.left) this.vx = -this.speed;
    if (this.keys.right) this.vx = this.speed;
    if (this.keys.up) this.vy = -this.speed;
    if (this.keys.down) this.vy = this.speed;

    // Update position
    this.x += this.vx;
    this.y += this.vy;

    // Clamp to screen bounds
    this.x = Math.max(0, Math.min(this.screenWidth - this.width, this.x));
    this.y = Math.max(0, Math.min(this.screenHeight - this.height, this.y));

    // Animate engine
    this.animationFrame++;
    if (this.animationFrame > 10) {
      this.animationFrame = 0;
    }
  }

  /**
   * Check if player can shoot (cooldown elapsed).
   * @returns {boolean}
   */
  canShoot() {
    return Date.now() - this.lastShotTime >= this.shootCooldown;
  }

  /**
   * Try to shoot a bullet. Returns bullet data if successful, null if on cooldown.
   * @returns {{x: number, y: number, width: number, height: number, speed: number, active: boolean}|null}
   */
  shoot() {
    if (!this.canShoot()) {
      return null;
    }

    this.lastShotTime = Date.now();

    return {
      x: this.x + this.width / 2 - 3, // Center horizontally, 6px wide
      y: this.y,
      width: 6,
      height: 15,
      speed: 7,
      active: true
    };
  }

  /**
   * Get the player's collision rectangle.
   * @returns {{x: number, y: number, width: number, height: number}}
   */
  getRect() {
    return {
      x: this.x,
      y: this.y,
      width: this.width,
      height: this.height
    };
  }

  /**
   * Get current position.
   * @returns {{x: number, y: number}}
   */
  getPosition() {
    return { x: this.x, y: this.y };
  }

  /**
   * Reduce health by 1. Returns true if player is still alive.
   * @returns {boolean}
   */
  takeDamage() {
    this.health = Math.max(0, this.health - 1);
    return this.health > 0;
  }

  /**
   * Check if player still has health remaining.
   * @returns {boolean}
   */
  isAlive() {
    return this.health > 0;
  }

  /**
   * Draw the player ship on canvas.
   * @param {CanvasRenderingContext2D} ctx - Canvas 2D context
   */
  draw(ctx) {
    ctx.save();

    if (this.spriteStyle === 'triangle') {
      this.drawTriangleShip(ctx);
    } else if (this.spriteStyle === 'detailed') {
      this.drawDetailedShip(ctx);
    } else if (this.spriteStyle === 'classic') {
      this.drawClassicShip(ctx);
    } else {
      this.drawTriangleShip(ctx);
    }

    ctx.restore();
  }

  /**
   * Draw triangle Space Invaders style ship.
   * @param {CanvasRenderingContext2D} ctx
   */
  drawTriangleShip(ctx) {
    const { x, y, width, height } = this;

    // Main body triangle
    ctx.fillStyle = this.mainColor;
    ctx.beginPath();
    ctx.moveTo(x + width / 2, y);
    ctx.lineTo(x, y + height);
    ctx.lineTo(x + width, y + height);
    ctx.closePath();
    ctx.fill();

    // Inner triangle (detail)
    ctx.fillStyle = this.secondaryColor;
    ctx.beginPath();
    ctx.moveTo(x + width / 2, y + height / 3);
    ctx.lineTo(x + width / 4, y + height);
    ctx.lineTo(x + 3 * width / 4, y + height);
    ctx.closePath();
    ctx.fill();

    // Cockpit
    ctx.fillStyle = this.cockpitColor;
    ctx.beginPath();
    ctx.ellipse(x + width / 2, y + height / 4 + 5, 4, 5, 0, 0, Math.PI * 2);
    ctx.fill();
  }

  /**
   * Draw detailed Space Invaders style ship with wings.
   * @param {CanvasRenderingContext2D} ctx
   */
  drawDetailedShip(ctx) {
    const { x, y, width, height } = this;
    const centerX = x + width / 2;

    // Main body (central rectangle)
    ctx.fillStyle = this.mainColor;
    ctx.fillRect(x + width / 3, y + height / 4, width / 3, height / 2);

    // Nose cone (triangle)
    ctx.fillStyle = this.mainColor;
    ctx.beginPath();
    ctx.moveTo(centerX, y);
    ctx.lineTo(x + width / 4, y + height / 3);
    ctx.lineTo(x + 3 * width / 4, y + height / 3);
    ctx.closePath();
    ctx.fill();

    // Left wing
    ctx.fillStyle = this.secondaryColor;
    ctx.beginPath();
    ctx.moveTo(x, y + height / 2);
    ctx.lineTo(x + width / 4, y + height / 2);
    ctx.lineTo(x + width / 3, y + height);
    ctx.lineTo(x, y + height);
    ctx.closePath();
    ctx.fill();

    // Right wing
    ctx.fillStyle = this.secondaryColor;
    ctx.beginPath();
    ctx.moveTo(x + width, y + height / 2);
    ctx.lineTo(x + 3 * width / 4, y + height / 2);
    ctx.lineTo(x + 2 * width / 3, y + height);
    ctx.lineTo(x + width, y + height);
    ctx.closePath();
    ctx.fill();

    // Cockpit window
    ctx.fillStyle = this.cockpitColor;
    ctx.beginPath();
    ctx.ellipse(centerX, y + height / 3 + 4, 5, 4, 0, 0, Math.PI * 2);
    ctx.fill();

    // Engine glow
    ctx.fillStyle = this.engineColor;
    ctx.beginPath();
    ctx.arc(centerX, y + height - 3, 4, 0, Math.PI * 2);
    ctx.fill();
  }

  /**
   * Draw classic Space Invaders player ship.
   * @param {CanvasRenderingContext2D} ctx
   */
  drawClassicShip(ctx) {
    const { x, y, width, height } = this;

    // Base rectangle
    ctx.fillStyle = this.mainColor;
    ctx.fillRect(x + 2, y, width - 4, height - 5);

    // Top cannon
    ctx.fillStyle = this.accentColor;
    ctx.fillRect(x + width / 2 - 3, y, 6, height / 3);

    // Side details
    ctx.fillStyle = this.secondaryColor;
    ctx.fillRect(x, y + height / 2, 5, height / 3);
    ctx.fillRect(x + width - 5, y + height / 2, 5, height / 3);

    // Bottom engine area
    ctx.fillStyle = this.engineColor;
    ctx.fillRect(x + 5, y + height - 8, width - 10, 5);
  }

  /**
   * Draw animated engine flames.
   * @param {CanvasRenderingContext2D} ctx
   */
  drawEngineFlame(ctx) {
    const { x, y, width, height } = this;
    const centerX = x + width / 2;
    const flameHeight = 8 + (this.animationFrame % 3) * 3;

    // Main flame
    ctx.fillStyle = this.engineColor;
    ctx.beginPath();
    ctx.moveTo(centerX - 8, y + height);
    ctx.lineTo(centerX + 8, y + height);
    ctx.lineTo(centerX, y + height + flameHeight);
    ctx.closePath();
    ctx.fill();

    // Inner flame (brighter)
    ctx.fillStyle = '#ffc832';
    ctx.beginPath();
    ctx.moveTo(centerX - 4, y + height);
    ctx.lineTo(centerX + 4, y + height);
    ctx.lineTo(centerX, y + height + flameHeight - 4);
    ctx.closePath();
    ctx.fill();
  }

  /**
   * Reset player to starting position.
   * @param {number} screenWidth - Width of the game screen
   * @param {number} screenHeight - Height of the game screen
   */
  reset(screenWidth, screenHeight) {
    this.screenWidth = screenWidth;
    this.screenHeight = screenHeight;
    this.x = (screenWidth - this.width) / 2;
    this.y = screenHeight - this.height - 20;
    this.health = this.maxHealth;
  }
}

/**
 * Projectile class for player bullets.
 * Ported from pygame implementation.
 */
export class Bullet {
  /**
   * Initialize bullet at given position.
   * @param {number} x - X position (left edge)
   * @param {number} y - Y position (top edge)
   */
  constructor(x, y) {
    // Bullet size: 6x15 pixels
    this.width = 6;
    this.height = 15;

    // Position
    this.x = x;
    this.y = y;

    // Movement speed: 7 pixels per frame (upward)
    this.speed = 7;

    // Bullet color (yellow/laser style)
    this.color = '#ffff00';

    // Active state
    this.active = true;
  }

  /**
   * Update bullet position.
   * @param {number} screenHeight - Height of the game screen
   */
  update(screenHeight) {
    this.y -= this.speed;
    if (this.y + this.height < 0) {
      this.active = false;
    }
  }

  /**
   * Get the bullet's collision rectangle.
   * @returns {{x: number, y: number, width: number, height: number}}
   */
  getRect() {
    return {
      x: this.x,
      y: this.y,
      width: this.width,
      height: this.height
    };
  }

  /**
   * Get current position.
   * @returns {{x: number, y: number}}
   */
  getPosition() {
    return { x: this.x, y: this.y };
  }

  /**
   * Get center position of bullet.
   * @returns {{x: number, y: number}}
   */
  getCenter() {
    return {
      x: this.x + this.width / 2,
      y: this.y + this.height / 2
    };
  }

  /**
   * Mark bullet as inactive.
   */
  deactivate() {
    this.active = false;
  }

  /**
   * Check if bullet is still active.
   * @returns {boolean}
   */
  isActive() {
    return this.active;
  }

  /**
   * Draw the bullet on canvas.
   * @param {CanvasRenderingContext2D} ctx - Canvas 2D context
   */
  draw(ctx) {
    if (!this.active) return;

    // Main bullet
    ctx.fillStyle = this.color;
    ctx.fillRect(this.x, this.y, this.width, this.height);

    // Glow effect
    ctx.fillStyle = '#ffffc8';
    ctx.fillRect(this.x + 1, this.y + 1, this.width - 2, this.height - 2);
  }
}