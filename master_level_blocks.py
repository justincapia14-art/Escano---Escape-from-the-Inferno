#master_level_blocks.py
import pygame

MAZE_MAP = [
    "B BBBBBBBBBBBBBBBB B BBBBBBBBBBBBBBBBB B",
    "B                  B                   B",
    "B          B       B       B           B",
    "B   BBBBBBBBBBBB   B   BBBBBBBBBBBBB   B",
    "B   B          B       B           B   B",
    "B   B   BBBB   BBBBBBBBB   BBBBB   BB  B",
    "BB  B      B               B       B   B",
    "B   BBBB   BBBBBBBBBBBBBBBBB   BBBBB  BB",
    "B   B      B           B       B       B",
    "B  BB   BBBB   BBBBB   B   BBBBB   BBBBB",
    "B   B   B      B               B       B",
    "B   B   B   BBBB   BBBBBBBBB   BBBB    B",
    "BB  B   B                  B       B   B",
    "B   B   B   B   BBBBBBBB   BBBBB      BB",
    "B   B   B   B          B       B   B   B",
    "B  BB   B   BBBBBBBB   BBBBB   B      BB",
    "B   B   B                      B   B   B",
    "B   B   BBBBBBBBBBBBBBBB   BBBBB      BB",
    "BB  B                      B       B   B",
    "B   B BBBBBBBBBBBBBBBBBBBB B   BBBBB   B",
    "B                                      B",
    "BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB   BBBBB",
    "B                                      B",
    "B             B          B             B",
    "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG"
]

def master_get_platforms():
    platforms = []
    
    for row_index, row in enumerate(MAZE_MAP):
        for col_index, tile in enumerate(row):
            if tile == 'B' or tile == 'G':
                x = col_index * 20
                y = row_index * 20
                platforms.append(pygame.Rect(x, y, 20, 20))
                
    return platforms


def master_draw_platforms(screen, ground1, ground2, brick1, brick2):
    for row_index, row in enumerate(MAZE_MAP):
        for col_index, tile in enumerate(row):
            x = col_index * 20
            y = row_index * 20
            
            if tile == 'B':
                screen.blit(brick1, (x, y))
            elif tile == 'G':
                screen.blit(ground2, (x, y))
                # if col_index % 2 == 0:
                #     screen.blit(ground2, (x, y))
                # else:
                #     screen.blit(ground2, (x, y))