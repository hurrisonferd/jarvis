#include "game.h"
#include <SDL2/SDL.h>
#include <stdio.h>

int main(int argc, char *argv[]) {
    (void)argc;
    (void)argv;

    if (SDL_Init(SDL_INIT_VIDEO) < 0) {
        fprintf(stderr, "SDL init failed: %s\n", SDL_GetError());
        return 1;
    }

    Game game;
    game.window = SDL_CreateWindow(
        "Pong - C/SDL2",
        SDL_WINDOWPOS_CENTERED,
        SDL_WINDOWPOS_CENTERED,
        SCREEN_WIDTH,
        SCREEN_HEIGHT,
        SDL_WINDOW_SHOWN
    );

    if (!game.window) {
        fprintf(stderr, "Window creation failed: %s\n", SDL_GetError());
        SDL_Quit();
        return 1;
    }

    game.renderer = SDL_CreateRenderer(game.window, -1, SDL_RENDERER_ACCELERATED);
    if (!game.renderer) {
        fprintf(stderr, "Renderer creation failed: %s\n", SDL_GetError());
        SDL_DestroyWindow(game.window);
        SDL_Quit();
        return 1;
    }

    srand((unsigned int)time(NULL));
    init_game(&game);

    printf("=== PONG - C/SDL2 ===\n");
    printf("Controls:\n");
    printf("  Player 1 (Left): W/S or Up/Down arrows\n");
    printf("  Player 2 (Right): I/K\n");
    printf("  Space: Pause\n");
    printf("  ESC: Quit\n");
    printf("First to %d wins!\n\n", WIN_SCORE);

    while (game.running) {
        handle_events(&game);
        update_game(&game);
        render_game(&game);
        SDL_Delay(16);
    }

    printf("\n=== GAME OVER ===\n");
    if (game.left.score >= WIN_SCORE) {
        printf("Player 1 (Left) WINS!\n");
    } else {
        printf("Player 2 (Right) WINS!\n");
    }
    printf("Final Score: %d - %d\n", game.left.score, game.right.score);

    SDL_DestroyRenderer(game.renderer);
    SDL_DestroyWindow(game.window);
    SDL_Quit();

    return 0;
}
