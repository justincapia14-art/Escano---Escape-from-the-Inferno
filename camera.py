# camera.py
import pygame

def draw_zoomed_camera(screen, world_surface, target_x, target_y, target_width, target_height, screen_width, screen_height, zoom=2):
    cam_width = screen_width // zoom
    cam_height = screen_height // zoom

    # Kunin ang CENTER ng camera DEPENDE sa player (target)
    cam_x = target_x + (target_width // 2) - (cam_width // 2)
    cam_y = target_y + (target_height // 2) - (cam_height // 2)

    #buong MAPA para hindi lumagpas ang camera
    world_width, world_height = world_surface.get_size()
    cam_x = max(0, min(cam_x, world_width - cam_width))
    cam_y = max(0, min(cam_y, world_height - cam_height))

    # Kunin ang maliit na rectangle view mula sa world_surface
    camera_rect = pygame.Rect(cam_x, cam_y, cam_width, cam_height)
    zoomed_view = world_surface.subsurface(camera_rect)

    # I-scale palaki para mapuno yung buong screen window
    scaled_view = pygame.transform.scale(zoomed_view, (screen_width, screen_height))

    # I-blit ang na-zoom na view sa pinaka-main screen
    screen.blit(scaled_view, (0, 0))
    