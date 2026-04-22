#master_level_blocks.py
import pygame

MAZE_MAP = [
    "                                        ",
    "                                        ",
    "                                        ",
    "                                        ",
    "                                        ",
    " BBBBBBBBBBBBBBB     BBBBBBBBBBBBBBBBBB ",
    "                                        ",
    "                                        ",
    "                                        ",
    "                                        ",
    "                                        ",
    "BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB    ",
    "                                        ",
    "                                        ",
    "                                        ",
    "                                        ",
    "                                        ",
    "    BB  BBBBBB  BBBBBB  BBBBB  BBBB  BBB",
    "   BB                                   ",
    "                                        ",
    "                                        ",
    "BBB                  B               BBB",
    "                  B  B                  ",
    "B              B  B                     ",
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