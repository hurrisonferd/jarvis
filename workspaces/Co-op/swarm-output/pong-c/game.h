#ifndef GAME_H
#define GAME_H

#include <stdbool.h>
#include <SDL2/SDL.h>

#define SCREEN_WIDTH 800
#define SCREEN_HEIGHT 600
#define PADDLE_WIDTH 15
#define PADDLE_HEIGHT 100
#define PADDLE_MARGIN 30
#define PADDLE_SPEED 8
#define BALL_SIZE 15
#define BALL_SPEED 7
#define WIN_SCORE 11

typedef struct {
    float x, y;
    float vx, vy;
} Ball;

typedef struct {
    float x, y;
    int score;
} Paddle;

typedef struct {
    Paddle left;
    Paddle right;
    Ball ball;
    bool running;
    bool paused;
    SDL_Window *window;
    SDL_Renderer *renderer;
} Game;

void init_game(Game *game);
void update_game(Game *game);
void render_game(Game *game);
void handle_events(Game *game);
void reset_ball(Game *game, bool to_left);

#endif
