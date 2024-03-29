# Assets: https://techwithtim.net/wp-content/uploads/2020/09/assets.zip
import pygame
from checkers.constants import WIDTH, HEIGHT, SQUARE_SIZE, RED, WHITE
from checkers.game import Game
import os
import sys

FPS = 60

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Checkers')


def get_row_col_from_mouse(pos):
    x, y = pos
    row = y // SQUARE_SIZE
    col = x // SQUARE_SIZE
    return row, col


def main():
    run = True
    clock = pygame.time.Clock()
    game = Game(WIN)

    # 0 indicates player. a postive single-digit int represents AI with depth of that val.
    # A double-digit int represents an AI with custom heuristic. If the digit is `XY`, it means heuristic X at depth Y.
    try:
        red = int(sys.argv[1])
        white = int(sys.argv[2])
    except:
        print("Input var(s) is not a valid int.")
        quit()
    if red < 0 or white < 0 or red > 99 or white > 99:
        print("Input var(s) is out of range.")
        quit()

    # attempt to get heuristic param inputs
    try:
        h_params = []
        for i in range(3, 8):
            h_params.append(int(sys.argv[i]))
    except:
        print("No custom params. Using default.")
        h_params = [2, 4, 2, 4, 4]

    # print info to player for visual clarity
    if red == 0:
        print("Red is a human player.")
    elif red >= 10:
        print("Red is an AI with custom heuristic #" + str(red)
              [:-1] + " at depth " + str(red)[1:] + ".")
    else:
        print("Red is an AI minimax with depth " + str(red) + ".")
    if white == 0:
        print("White is a human player.")
    elif white >= 10:
        print("White is an AI with custom heuristic #" + str(white)
              [:-1] + " at depth " + str(white)[1:] + ".")
    else:
        print("White is an AI minimax with depth " + str(white) + ".")

    while run:
        clock.tick(FPS)

        if game.winner() != None:
            if game.winner() == WHITE:
                winner = "White"
            elif game.winner() == RED:
                winner = "Red"
            else:
                winner = "no one. It was a draw"
            print("The game was won by " + winner + "!")
            run = False
            return winner

        # uncomment this to go through AI games move by move
        # mode = input()

        if game.turn == RED:
            if red == 0:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        run = False

                    if event.type == pygame.MOUSEBUTTONDOWN:
                        pos = pygame.mouse.get_pos()
                        row, col = get_row_col_from_mouse(pos)
                        game.select(row, col)
            else:
                game.computer_move(RED, red, h_params)

        elif game.turn == WHITE:
            if white == 0:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        run = False

                    if event.type == pygame.MOUSEBUTTONDOWN:
                        pos = pygame.mouse.get_pos()
                        row, col = get_row_col_from_mouse(pos)
                        game.select(row, col)
            else:
                game.computer_move(WHITE, white, h_params)

        game.update()

    pygame.quit()


main()
