#beginner_level_blocks.py
import pygame

def get_platforms():
    platforms = []
    # horizontal
    for i in range(0, 800, 20):
        platforms.append(pygame.Rect(i, 480, 20, 20))  # ground1
        platforms.append(pygame.Rect(i, 460, 20, 20))  # ground2
    for i in range(40, 320, 20):
        platforms.append(pygame.Rect(i, 400, 20, 20))  # brick1
    for i in range(380, 600, 20):
        platforms.append(pygame.Rect(i, 400, 20, 20))  # brick1
    for i in range(400, 700, 20):
        platforms.append(pygame.Rect(i, 340, 20, 20))  # brick1
    for i in range(640, 800, 20):
        platforms.append(pygame.Rect(i, 400, 20, 20))  # brick1
    for i in range(400, 760, 20):
        platforms.append(pygame.Rect(i, 220, 20, 20))  # brick1
    for i in range(380, 800, 20):
        platforms.append(pygame.Rect(i, 80, 20, 20))   # brick1
    for i in range(400, 800, 20):
        platforms.append(pygame.Rect(i, 100, 20, 20))  # brick1
    for i in range(440, 780, 20):
        platforms.append(pygame.Rect(i, 120, 20, 20))  # brick1
    for i in range(380, 800, 20):
        platforms.append(pygame.Rect(i, 60, 20, 20))   # brick1
    for i in range(380, 800, 20):
        platforms.append(pygame.Rect(i, 40, 20, 20))   # brick1
    for i in range(380, 760, 20):
        platforms.append(pygame.Rect(i, 200, 20, 20))
    for i in range(0, 280, 20):
        platforms.append(pygame.Rect(i, 160, 20, 20))

    # vertical
    for j in range(320, 400, 20):
        platforms.append(pygame.Rect(280, j, 20, 20))
    for j in range(320, 400, 20):
        platforms.append(pygame.Rect(380, j, 20, 20))
    for j in range(100, 240, 20):
        platforms.append(pygame.Rect(380, j, 20, 20))
    for j in range(80, 280, 20):
        platforms.append(pygame.Rect(280, j, 20, 20))

    # solo bricks
    platforms.append(pygame.Rect(360, 360, 20, 20))
    platforms.append(pygame.Rect(780, 260, 20, 20))
    platforms.append(pygame.Rect(780, 280, 20, 20))
    platforms.append(pygame.Rect(760, 280, 20, 20))
    platforms.append(pygame.Rect(300, 320, 20, 20))
    platforms.append(pygame.Rect(780, 340, 20, 20))
    platforms.append(pygame.Rect(760, 340, 20, 20))
    platforms.append(pygame.Rect(780, 360, 20, 20))
    platforms.append(pygame.Rect(780, 380, 20, 20))
    platforms.append(pygame.Rect(340, 280, 20, 20))
    platforms.append(pygame.Rect(300, 220, 20, 20))
    platforms.append(pygame.Rect(340, 160, 20, 20))
    platforms.append(pygame.Rect(300, 120, 20, 20))

    return platforms


def draw_platforms(screen, ground1, ground2, brick1, brick2):
    # horizontal
    for i in range(0, 800, 20):
        screen.blit(ground1, (i, 480)) # ground
        screen.blit(ground2, (i, 460)) # ground2
    for i in range(40, 320, 20):
        screen.blit(brick1, (i, 400))  # brick1
    for i in range(380, 600, 20):
        screen.blit(brick1, (i, 400))  # brick1
    for i in range(400, 700, 20):
        screen.blit(brick1, (i, 340))
    for i in range(640, 800, 20):
        screen.blit(brick1, (i, 400))
    for i in range(400, 760, 20):
        screen.blit(brick1, (i, 220))
    for i in range(380, 800, 20):
        screen.blit(brick1, (i, 80))
    for i in range(400, 800, 20):
        screen.blit(brick1, (i, 100))
    for i in range(440, 780, 20):
        screen.blit(brick1, (i, 120))
    for i in range(380, 800, 20):
        screen.blit(brick1, (i, 60))
    for i in range(380, 800, 20):
        screen.blit(brick1, (i, 40))
    for i in range(380, 760, 20):
        screen.blit(brick1, (i, 200))
    for i in range(0, 280, 20):
        screen.blit(brick1, (i, 160))

    # vertical
    for j in range(320, 400, 20):
        screen.blit(brick1, (280, j))  # brick1
    for j in range(320, 400, 20):      # brick1
        screen.blit(brick1, (380, j))
    for j in range(100, 240, 20):      # brick1
        screen.blit(brick1, (380, j))
    for j in range(80, 280, 20):       # brick1
        screen.blit(brick1, (280, j))

    # solo bricks
    screen.blit(brick1, (360, 360))
    screen.blit(brick1, (780, 260))
    screen.blit(brick1, (780, 280))
    screen.blit(brick1, (760, 280))
    screen.blit(brick1, (300, 320))
    screen.blit(brick1, (780, 340))
    screen.blit(brick1, (760, 340))
    screen.blit(brick1, (780, 360))
    screen.blit(brick1, (780, 380))
    screen.blit(brick1, (340, 280))
    screen.blit(brick1, (300, 220))
    screen.blit(brick1, (340, 160))
    screen.blit(brick1, (300, 120))