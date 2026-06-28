#include "game.h"
#include <stdlib.h>
#include <time.h>
#include <SDL2/SDL_ttf.h>
#include <math.h>

void init_game(Game *game) {
    game->left.x = PADDLE_MARGIN;
    game->left.y = SCREEN_HEIGHT / 2 - PADDLE_HEIGHT / 2;
    game->left.score = 0;

    game->right.x = SCREEN_WIDTH - PADDLE_MARGIN - PADDLE_WIDTH;
    game->right.y = SCREEN_HEIGHT / 2 - PADDLE_HEIGHT / 2;
    game->right.score = 0;

    game->running = true;
    game->paused = false;

    reset_ball(game, false);
}

void reset_ball(Game *game, bool to_left) {
    game->ball.x = SCREEN_WIDTH / 2 - BALL_SIZE / 2;
    game->ball.y = SCREEN_HEIGHT / 2 - BALL_SIZE / 2;
    
    float angle = ((float)rand() / RAND_MAX) * M_PI / 3 - M_PI / 6;
    float direction = to_left ? -1.0f : 1.0f;
    
    game->ball.vx = direction * BALL_SPEED * cos(angle);
    game->ball.vy = BALL_SPEED * sin(angle);
}

void handle_events(Game *game) {
    SDL_Event event;
    while (SDL_PollEvent(&event)) {
        if (event.type == SDL_QUIT) {
            game->running = false;
        } else if (event.type == SDL_KEYDOWN) {
            if (event.key.keysym.sym == SDLK_ESCAPE) {
                game->running = false;
            } else if (event.key.keysym.sym == SDLK_SPACE) {
                game->paused = !game->paused;
            }
        }
    }

    const Uint8 *keys = SDL_GetKeyboardState(NULL);
    
    if (keys[SDL_SCANCODE_W] || keys[SDL_SCANCODE_UP]) {
        game->left.y -= PADDLE_SPEED;
    }
    if (keys[SDL_SCANCODE_S] || keys[SDL_SCANCODE_DOWN]) {
        game->left.y += PADDLE_SPEED;
    }
    if (keys[SDL_SCANCODE_I]) {
        game->right.y -= PADDLE_SPEED;
    }
    if (keys[SDL_SCANCODE_K]) {
        game->right.y += PADDLE_SPEED;
    }

    if (game->left.y < 0) game->left.y = 0;
    if (game->left.y > SCREEN_HEIGHT - PADDLE_HEIGHT) {
        game->left.y = SCREEN_HEIGHT - PADDLE_HEIGHT;
    }
    if (game->right.y < 0) game->right.y = 0;
    if (game->right.y > SCREEN_HEIGHT - PADDLE_HEIGHT) {
        game->right.y = SCREEN_HEIGHT - PADDLE_HEIGHT;
    }
}

void update_game(Game *game) {
    if (game->paused) return;

    game->ball.x += game->ball.vx;
    game->ball.y += game->ball.vy;

    if (game->ball.y <= 0) {
        game->ball.y = 0;
        game->ball.vy = -game->ball.vy;
    }
    if (game->ball.y >= SCREEN_HEIGHT - BALL_SIZE) {
        game->ball.y = SCREEN_HEIGHT - BALL_SIZE;
        game->ball.vy = -game->ball.vy;
    }

    if (game->ball.x <= game->left.x + PADDLE_WIDTH &&
        game->ball.x + BALL_SIZE >= game->left.x &&
        game->ball.y + BALL_SIZE >= game->left.y &&
        game->ball.y <= game->left.y + PADDLE_HEIGHT) {
        game->ball.x = game->left.x + PADDLE_WIDTH;
        float hit_pos = (game->ball.y + BALL_SIZE / 2) - 
                        (game->left.y + PADDLE_HEIGHT / 2);
        float angle = hit_pos / (PADDLE_HEIGHT / 2) * (M_PI / 4);
        float speed = sqrt(game->ball.vx * game->ball.vx + game->ball.vy * game->ball.vy);
        speed *= 1.05f;
        if (speed > 15) speed = 15;
        game->ball.vx = speed * cos(angle);
        game->ball.vy = speed * sin(angle);
    }

    if (game->ball.x + BALL_SIZE >= game->right.x &&
        game->ball.x <= game->right.x + PADDLE_WIDTH &&
        game->ball.y + BALL_SIZE >= game->right.y &&
        game->ball.y <= game->right.y + PADDLE_HEIGHT) {
        game->ball.x = game->right.x - BALL_SIZE;
        float hit_pos = (game->ball.y + BALL_SIZE / 2) - 
                        (game->right.y + PADDLE_HEIGHT / 2);
        float angle = hit_pos / (PADDLE_HEIGHT / 2) * (M_PI / 4);
        float speed = sqrt(game->ball.vx * game->ball.vx + game->ball.vy * game->ball.vy);
        speed *= 1.05f;
        if (speed > 15) speed = 15;
        game->ball.vx = -speed * cos(angle);
        game->ball.vy = speed * sin(angle);
    }

    if (game->ball.x < 0) {
        game->right.score++;
        if (game->right.score >= WIN_SCORE) {
            game->running = false;
        } else {
            reset_ball(game, false);
        }
    }
    if (game->ball.x > SCREEN_WIDTH) {
        game->left.score++;
        if (game->left.score >= WIN_SCORE) {
            game->running = false;
        } else {
            reset_ball(game, true);
        }
    }
}

void render_game(Game *game) {
    SDL_SetRenderDrawColor(game->renderer, 0, 0, 0, 255);
    SDL_RenderClear(game->renderer);

    SDL_SetRenderDrawColor(game->renderer, 255, 255, 255, 255);
    SDL_Rect left_paddle = { (int)game->left.x, (int)game->left.y, PADDLE_WIDTH, PADDLE_HEIGHT };
    SDL_RenderFillRect(game->renderer, &left_paddle);

    SDL_Rect right_paddle = { (int)game->right.x, (int)game->right.y, PADDLE_WIDTH, PADDLE_HEIGHT };
    SDL_RenderFillRect(game->renderer, &right_paddle);

    SDL_Rect ball = { (int)game->ball.x, (int)game->ball.y, BALL_SIZE, BALL_SIZE };
    SDL_RenderFillRect(game->renderer, &ball);

    for (int i = 0; i < SCREEN_HEIGHT; i += 20) {
        SDL_Rect center_line = { SCREEN_WIDTH / 2 - 2, i, 4, 10 };
        SDL_RenderFillRect(game->renderer, &center_line);
    }

    if (TTF_Init() == 0) {
        TTF_Font *font = TTF_OpenFont("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 48);
        if (font) {
            char score_text[16];
            SDL_Color white = {255, 255, 255, 255};
            
            sprintf(score_text, "%d", game->left.score);
            SDL_Surface *surf = TTF_RenderText_Solid(font, score_text, white);
            if (surf) {
                SDL_Texture *tex = SDL_CreateTextureFromSurface(game->renderer, surf);
                SDL_Rect dest = { SCREEN_WIDTH / 2 - 100, 30, surf->w, surf->h };
                SDL_RenderCopy(game->renderer, tex, NULL, &dest);
                SDL_FreeSurface(surf);
                SDL_DestroyTexture(tex);
            }

            sprintf(score_text, "%d", game->right.score);
            surf = TTF_RenderText_Solid(font, score_text, white);
            if (surf) {
                SDL_Texture *tex = SDL_CreateTextureFromSurface(game->renderer, surf);
                SDL_Rect dest = { SCREEN_WIDTH / 2 + 60, 30, surf->w, surf->h };
                SDL_RenderCopy(game->renderer, tex, NULL, &dest);
                SDL_FreeSurface(surf);
                SDL_DestroyTexture(tex);
            }
            TTF_CloseFont(font);
        }
        TTF_Quit();
    }

    if (game->paused) {
        if (TTF_Init() == 0) {
            TTF_Font *font = TTF_OpenFont("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 36);
            if (font) {
                SDL_Color white = {255, 255, 255, 255};
                SDL_Surface *surf = TTF_RenderText_Solid(font, "PAUSED", white);
                if (surf) {
                    SDL_Texture *tex = SDL_CreateTextureFromSurface(game->renderer, surf);
                    SDL_Rect dest = { SCREEN_WIDTH / 2 - surf->w / 2, SCREEN_HEIGHT / 2 - surf->h / 2, surf->w, surf->h };
                    SDL_RenderCopy(game->renderer, tex, NULL, &dest);
                    SDL_FreeSurface(surf);
                    SDL_DestroyTexture(tex);
                }
                TTF_CloseFont(font);
            }
            TTF_Quit();
        }
    }

    SDL_RenderPresent(game->renderer);
}
