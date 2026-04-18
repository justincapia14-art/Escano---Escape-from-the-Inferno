import pygame
import sys
import random
import math
import os

from enemy import Enemy
from particle import Particle
from hindilalabas import apply_screen_bounds
from camera import draw_zoomed_camera

from mechanics import (
    check_key_collection, 
    check_coin_collection, 
    check_pre_gravity_ground, 
    handle_horizontal_collision, 
    handle_vertical_collision,
    check_life_collection,
    HealEffect,
    EscanoUltimate
)

# ====================================================
# PYGAME INITIALIZATION & WINDOW SETUP
# Start Pygame engine, screen size, and window title
# ====================================================
pygame.init()
pygame.mixer.init()

width = 800
height = 500
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Escano")

# ====================================================
# NEW: CTYPES OS WINDOW SETUP (100% Working sa Windows)
# ====================================================
try:
    if sys.platform == "win32":
        import ctypes
        # Kunin ang Window ID (HWND)
        hwnd = pygame.display.get_wm_info()['window']
        
        class RECT(ctypes.Structure):
            _fields_ = [("left", ctypes.c_long),
                        ("top", ctypes.c_long),
                        ("right", ctypes.c_long),
                        ("bottom", ctypes.c_long)]
                        
        def get_window_pos():
            rect = RECT()
            ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(rect))
            return rect.left, rect.top
            
        def set_window_pos(x, y):
            # 0x0005 = SWP_NOSIZE | SWP_NOZORDER (Hindi babaguhin ang size, posisyon lang)
            ctypes.windll.user32.SetWindowPos(hwnd, 0, int(x), int(y), 0, 0, 0x0005)
            
        original_window_pos = get_window_pos()
        can_shake_os = True
    else:
        print("Hindi naka-Windows, OS Shake disabled.")
        can_shake_os = False
        original_window_pos = (0, 0)
except Exception as e:
    print("Error sa OS Shake:", e)
    can_shake_os = False
    original_window_pos = (0, 0)

clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 20, bold=True)

# ====================================================
# CAMERA SETUP
# Make a surface to draw the game world before zooming
# ====================================================
world_surface = pygame.Surface((width, height))

# ====================================================
# ASSETS & PLATFORMS
# Get platforms and pictures from other files
# ====================================================
from assets import *
from beginner_level_blocks import get_platforms, draw_platforms

# ====================================================
# GAME STATE & VARIABLES
# ====================================================
time = 0
game_state = "menu"
direction = "face"
running = True
particles = []
loading_progress = 0
target_level = ""     
target_music = ""
is_playing_charge_sound = False
os_window_shake_frames = 0  # Timer para sa OS window shake

#scroll wheel of mouse to change skills
skills_list = ["Gun", "Ultimate"]
current_skill_index = 0
current_skill = skills_list[current_skill_index]
skill_ui_timer = 0  

# ====================================================
# PLAYER POSITIONING & STATS
# ====================================================
player_hp = 100
max_hp = 100
hit_cooldown = 0
x = 400
y = 440
speed = 1.5
gravity = 0.2  
velocity_y = 0  
jump_speed = -5
player_width, player_height = 20, 20
player_angle = 0

# ====================================================
# PLAYER SHOOTING VARIABLES
# ====================================================
player_bullets = []
player_shoot_cooldown = 0 
max_shoot_cooldown = 30  

# ====================================================
# AIM ANIMATION
# ====================================================
shoot_anim_timer = 0
aim_direction = "right"
# ----------------------------------------------

# ====================================================
# KEYS VARIABLES
# ====================================================
keys_collected = 0
TOTAL_KEYS = 3
key1_collected = False
key2_collected = False
key3_collected = False
key1_rect = pygame.Rect(180, 380, 20, 10)
key2_rect = pygame.Rect(780, 320, 20, 10)
key3_rect = pygame.Rect(425, 154, 20, 20)
door_rect = pygame.Rect(80, 82, 80, 80)

# life positions and collection status
life_rects_beginner = [
    pygame.Rect(250, 370, 20, 20),
    pygame.Rect(400, 175, 20, 20),
    pygame.Rect(700, 440, 20, 20),
]
lives_collected = [False] * len(life_rects_beginner)

# ====================================================
# COINS VARIABLES
# ====================================================
frame_index = 0
animation_speed = 0.10 

coin_rects = [
    pygame.Rect(420, 300, 20, 20),
    pygame.Rect(420, 320, 20, 20),
    pygame.Rect(440, 320, 20, 20),
    pygame.Rect(440, 300, 20, 20),
    pygame.Rect(460, 320, 20, 20),
    pygame.Rect(460, 300, 20, 20),
]
coins_collected = [False] * len(coin_rects)
coin_count = 0

# ====================================================
# EXIT VARIABLES
# ====================================================
exit_fade_start = None
exit_fade_done = False
frozen_game_frame = None

# ====================================================
# FUNCTIONS
# ====================================================

def reset_beginner_level():
    global x, y, velocity_y, player_angle
    global keys_collected, key1_collected, key2_collected, key3_collected
    global coins_collected, coin_count
    global exit_fade_start, exit_fade_done
    global player_hp, hit_cooldown
    global enemies, player_bullets, shoot_anim_timer
    global lives_collected
    global breakable_bricks
    global os_window_shake_frames

    player_hp = max_hp
    hit_cooldown = 0
    os_window_shake_frames = 0

    charging.stop()
    is_playing_charge_sound = False

    # player reset
    x = 400
    y = 440
    velocity_y = 0
    player_angle = 0

    # keys reset
    keys_collected = 0
    key1_collected = False
    key2_collected = False
    key3_collected = False

    # coins reset
    coins_collected = [False] * len(coin_rects)
    coin_count = 0

    lives_collected = [False] * len(life_rects_beginner)

    # exit effect reset
    exit_fade_start = None
    exit_fade_done = False

    enemies = [
        Enemy(580, 160),
        Enemy(740, 360),
        Enemy(280, 280),
        Enemy(400, 360)
    ]

    breakable_bricks = [
        pygame.Rect(780, 320, 20, 20),
        pygame.Rect(780, 300, 20, 20),
        pygame.Rect(760, 300, 20, 20),
        pygame.Rect(760, 320, 20, 20),
        
        *[pygame.Rect(i, 380, 20, 20) for i in range(140, 280, 20)],
        *[pygame.Rect(i, 360, 20, 20) for i in range(180, 280, 20)],
        *[pygame.Rect(i, 340, 20, 20) for i in range(180, 280, 20)],
        *[pygame.Rect(i, 320, 20, 20) for i in range(0, 280, 20)]
    ]
    
    player_bullets.clear()
    active_heal_effects.clear()
    shoot_anim_timer = 0

def generate_vignette(w, h):
    mini_w, mini_h = w // 10, h // 10
    vignette = pygame.Surface((mini_w, mini_h), pygame.SRCALPHA)
    center_x, center_y = mini_w / 2, mini_h / 2
    max_dist = math.hypot(center_x, center_y)
    
    for y in range(mini_h):
        for x in range(mini_w):
            dist = math.hypot(x - center_x, y - center_y)
            alpha = int(255 * (dist / max_dist) ** 1.2) 
            alpha = min(255, alpha) 
            vignette.set_at((x, y), (0, 0, 0, alpha))
            
    return pygame.transform.smoothscale(vignette, (w, h))

vignette_surface = generate_vignette(width, height)

escano_ult = EscanoUltimate()
screen_shake_frames = 0
enemies = []
active_heal_effects = []

while running:
    moving = False
    mouse_pos = pygame.mouse.get_pos()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEWHEEL and game_state == "level_beginner":
            current_skill_index = (current_skill_index + event.y) % len(skills_list)
            current_skill = skills_list[current_skill_index]
            skill_ui_timer = 120  
            click_sound.play()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if game_state == "victory":
                reset_beginner_level()
                game_state = "menu"
            if game_state == "defeat":
                reset_beginner_level()
                game_state = "menu"

            if game_state == "menu":
                if play_button_rect.collidepoint(event.pos):
                    game_state = "levels"
                    click_sound.play()
                    continue
                if settings_button_rect.collidepoint(event.pos):
                    click_sound.play()
                    continue
                if exit_button_rect.collidepoint(event.pos):
                    game_state = "exit_confirm"
                    click_sound.play()

            elif game_state == "exit_confirm":
                if yes_rect.collidepoint(event.pos):
                    click_sound.play()
                    pygame.quit()
                    sys.exit()
                elif no_rect.collidepoint(event.pos):
                    click_sound.play()
                    game_state = "menu"

            elif game_state == "levels":
                if beginner_button_rect.collidepoint(event.pos):
                    click_sound.play()
                    loading_progress = 0
                    target_level = "level_beginner"        
                    target_music = "music/beginner_music.wav"   
                    game_state = "loading"
                elif intermediate_button_rect.collidepoint(event.pos):
                    click_sound.play()
                elif advanced_button_rect.collidepoint(event.pos):
                    click_sound.play()
                elif master_button_rect.collidepoint(event.pos):
                    click_sound.play()
                elif back_button_rect.collidepoint(event.pos):
                    click_sound.play()
                    game_state = "menu"

    if game_state == "menu":
        screen.blit(background_menu_scaled, (0, 0))

        if play_button_rect.collidepoint(mouse_pos) or settings_button_rect.collidepoint(mouse_pos) or exit_button_rect.collidepoint(mouse_pos):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        if play_button_rect.collidepoint(mouse_pos):
            screen.blit(play_button_hover_scaled, play_button_rect)
        else:
            screen.blit(play_button_scaled, play_button_rect)
        
        if settings_button_rect.collidepoint(mouse_pos):
            screen.blit(settings_button_hover_scaled, settings_button_rect)
        else:
            screen.blit(settings_button_scaled, settings_button_rect)

        if exit_button_rect.collidepoint(mouse_pos):
            screen.blit(exit_button_hover_scaled, exit_button_rect)
        else:
            screen.blit(exit_button_scaled, exit_button_rect)

    elif game_state == "levels":
        screen.blit(blur_back, (0, 0))
        screen.blit(level_selection_background, (0, 0))

        if (beginner_button_rect.collidepoint(mouse_pos) or
            intermediate_button_rect.collidepoint(mouse_pos) or
            advanced_button_rect.collidepoint(mouse_pos) or
            master_button_rect.collidepoint(mouse_pos) or
            back_button_rect.collidepoint(mouse_pos)):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        if beginner_button_rect.collidepoint(mouse_pos):
            screen.blit(beginner_button_hover, beginner_button_rect)
        else:
            screen.blit(beginner_button, beginner_button_rect)

        if intermediate_button_rect.collidepoint(mouse_pos):
            screen.blit(intermediate_button_hover, intermediate_button_rect)
        else:
            screen.blit(intermediate_button, intermediate_button_rect)

        if advanced_button_rect.collidepoint(mouse_pos):
            screen.blit(advanced_button_hover, advanced_button_rect)
        else:
            screen.blit(advanced_button, advanced_button_rect)

        if master_button_rect.collidepoint(mouse_pos):
            screen.blit(master_button_hover, master_button_rect)
        else:
            screen.blit(master_button, master_button_rect)

        if back_button_rect.collidepoint(mouse_pos):
            screen.blit(back_button_hover, back_button_rect)
        else:
            screen.blit(back_button, back_button_rect)

    elif game_state == "loading":
        screen.blit(background_menu_scaled, (0, 0))
        load_text = font.render("LOADING...", True, (255, 255, 255))
        screen.blit(load_text, (width // 2 - 50, height // 2 + 50))

        bar_width = 400
        bar_height = 20
        bar_x = (width // 2) - (bar_width // 2)
        bar_y = (height // 2) + 90

        pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
        fill_width = int((loading_progress / 100) * bar_width)
        pygame.draw.rect(screen, (255, 215, 0), (bar_x, bar_y, fill_width, bar_height))
        pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 2)

        loading_progress += 10 

        if loading_progress >= 100:
            if target_level == "level_beginner":
                reset_beginner_level()
                game_state = "level_beginner"
                pygame.mixer.music.load(target_music)
                pygame.mixer.music.set_volume(0.5)
                pygame.mixer.music.play(-1)

    elif game_state == "exit_confirm":
        screen.blit(blur_back, (0, 0))
        screen.blit(exit_confirm_bg, (200, 140))

        if yes_rect.collidepoint(mouse_pos) or no_rect.collidepoint(mouse_pos):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        if yes_rect.collidepoint(mouse_pos):
            screen.blit(yes_button_hover, yes_rect)
        else:
            screen.blit(yes_button, yes_rect)

        if no_rect.collidepoint(mouse_pos):
            screen.blit(no_button_hover, no_rect)
        else:
            screen.blit(no_button, no_rect)

    elif game_state == "victory":
        exit_music.fadeout(1000)
        screen.blit(victory_bg, (0, 0))

    elif game_state == "defeat":
        exit_music.fadeout(1000)
        pygame.mixer.music.fadeout(1000)
        
        if frozen_game_frame:
            screen.blit(frozen_game_frame, (0, 0))
            
        tint = pygame.Surface((width, height), pygame.SRCALPHA)
        tint.fill((20, 0, 0, 150)) 
        screen.blit(tint, (0, 0))
        
        glitch_chance = random.randint(1, 100)
        
        if glitch_chance > 85:
            blink = pygame.Surface((width, height), pygame.SRCALPHA)
            blink.fill((5, 5, 5, 220)) 
            screen.blit(blink, (0, 0))
            
        elif glitch_chance > 60:
            shift_x = random.randint(-15, 15)
            shift_y = random.randint(-10, 10)
            
            if frozen_game_frame:
                screen.blit(frozen_game_frame, (shift_x, shift_y))
            screen.blit(tint, (shift_x, shift_y))
            screen.blit(defeat, (shift_x, shift_y))
            
            for _ in range(random.randint(5, 15)):
                line_y = random.randint(0, height)
                line_thickness = random.randint(2, 8)
                pygame.draw.rect(screen, (20, 20, 20), (0, line_y, width, line_thickness))
                
        else:
            screen.blit(defeat, (0, 0))

    elif game_state == "level_beginner":
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        if hit_cooldown > 0:
            hit_cooldown -= 1

        keys = pygame.key.get_pressed()
        player_angle %= 360
        player_rect = pygame.Rect(x, y, player_width, player_height)

        escano_ult.update()
        mouse_buttons = pygame.mouse.get_pressed()
        left_click = mouse_buttons[0]
        right_click = mouse_buttons[2]

        if player_shoot_cooldown > 0:
            player_shoot_cooldown -= 1
            
        if shoot_anim_timer > 0:
            shoot_anim_timer -= 1

        if current_skill == "Ultimate":
            solid_platforms = get_platforms() 
            
            if escano_ult.handle_input(left_click, right_click, x, y, player_width, player_height, solid_platforms):
                screen_shake_frames = 15 
                ultimate_sound.play()   

        else:
            escano_ult.is_charging = False
            escano_ult.charge_timer = 0
            
            if current_skill == "Gun":
                if left_click and player_shoot_cooldown <= 0:
                    player_bullets.append([x, y + (player_height // 2), -7]) 
                    player_shoot_cooldown = max_shoot_cooldown
                    shoot_anim_timer = 15
                    aim_direction = "left"
                    player_shoot_sound.play()
                    
                elif right_click and player_shoot_cooldown <= 0:
                    player_bullets.append([x + player_width, y + (player_height // 2), 7])
                    player_shoot_cooldown = max_shoot_cooldown
                    shoot_anim_timer = 15
                    aim_direction = "right"
                    player_shoot_sound.play()

        if escano_ult.is_charging:
            if not is_playing_charge_sound:
                charging.play(loops=-1) 
                is_playing_charge_sound = True
        else:
            if is_playing_charge_sound:
                charging.stop()
                is_playing_charge_sound = False

        if escano_ult.active_laser:
            laser = escano_ult.active_laser
            laser_rect = laser['rect']
            
            if laser['current_breaks'] < laser['max_breaks']:
                hit_bricks = [b for b in breakable_bricks if laser_rect.colliderect(b)]
                
                if laser['dir'] == "right":
                    hit_bricks.sort(key=lambda b: b.x)
                else:
                    hit_bricks.sort(key=lambda b: b.x, reverse=True) 
                
                for b in hit_bricks:
                    if laser['current_breaks'] < laser['max_breaks']:
                        if b in breakable_bricks:
                            breakable_bricks.remove(b)
                            laser['current_breaks'] += 1
                            for _ in range(40):
                                particles.append(Particle(b.x + 10, b.y + 10))
                    else:
                        break

            if 'hit_enemies' not in escano_ult.active_laser:
                escano_ult.active_laser['hit_enemies'] = []

            for e in enemies:
                e_rect = pygame.Rect(e.x, e.y, 40, 40)
                if e.hp > 0 and laser_rect.colliderect(e_rect):
                    if e not in escano_ult.active_laser['hit_enemies']:
                        e.hp -= 40  
                        escano_ult.active_laser['hit_enemies'].append(e) 
                        
                        if e.hp <= 0:
                            enemy_dead_sound.play() 
                            for _ in range(100):  
                                particles.append(Particle(e.x + 20, e.y + 20))

        platforms = get_platforms()
        for b in breakable_bricks:
            platforms.append(b)

        for bullet in player_bullets[:]:
            bullet[0] += bullet[2] 

            if bullet[0] < 0 or bullet[0] > width:
                if bullet in player_bullets:
                    player_bullets.remove(bullet)
                continue

            bullet_rect = pygame.Rect(bullet[0] - 4, bullet[1] - 4, 8, 8)
            
            for e in enemies:
                e_rect = pygame.Rect(e.x, e.y, 40, 40)
                if e.hp > 0 and bullet_rect.colliderect(e_rect):
                    e.hp -= 15 
                    
                    if bullet in player_bullets:
                        player_bullets.remove(bullet)

                    if e.hp <= 0:
                        for _ in range(1000):  
                            particles.append(Particle(e.x + 20, e.y + 20))
                    break
            
            bullet_hit_wall = False
            for plat in platforms:
                if bullet_rect.colliderect(plat):
                    if bullet in player_bullets:
                        player_bullets.remove(bullet)
                    bullet_hit_wall = True
                    
                    for _ in range(5):
                        particles.append(Particle(bullet[0], bullet[1]))
                        
                    break

            if bullet_hit_wall:
                continue

        if keys_collected == 3:
            pygame.mixer.music.fadeout(1000)
            if keys[pygame.K_RETURN] and player_rect.colliderect(door_rect):
                victory_sound.play()
                game_state = "victory"

        key1_collected, keys_collected = check_key_collection(player_rect, key1_rect, key1_collected, keys_collected, key_collect)
        key2_collected, keys_collected = check_key_collection(player_rect, key2_rect, key2_collected, keys_collected, key_collect)
        key3_collected, keys_collected = check_key_collection(player_rect, key3_rect, key3_collected, keys_collected, key_collect)

        coins_collected, coin_count = check_coin_collection(player_rect, coin_rects, coins_collected, coin_count, coin_sound)

        lives_collected, player_hp, just_healed = check_life_collection(player_rect, life_rects_beginner, lives_collected, player_hp, max_hp, 20, life_sound)
        
        if just_healed:
            active_heal_effects.append(HealEffect())

        platforms = get_platforms()
        for b in breakable_bricks:
            platforms.append(b)

        player_rect = pygame.Rect(x, y, player_width, player_height)
        on_ground, baliktadrotate, y, velocity_y = check_pre_gravity_ground(player_rect, platforms, y, velocity_y)

        dx = 0

        if (keys[pygame.K_SPACE] or keys[pygame.K_w]) and on_ground:
            velocity_y = jump_speed
            moving = True
            
            for _ in range(100):
                particles.append(Particle(x + player_width // 2, y + player_height))

        if keys[pygame.K_a]:
            dx = -speed
            moving = True
            if baliktadrotate == "no":
                direction = "left"
                player_angle += 8
            else:
                direction = "right"
                player_angle -= 8

        elif keys[pygame.K_d]:
            dx = speed
            moving = True
            if baliktadrotate == "no":
                direction = "right"
                player_angle -= 8
            else:
                direction = "left"
                player_angle += 8
        else:
            moving = False

        x += dx
        player_rect = pygame.Rect(x, y, player_width, player_height)

        x = handle_horizontal_collision(player_rect, platforms, x, dx, player_width)

        velocity_y += gravity
        y += velocity_y

        player_rect = pygame.Rect(x, y, player_width, player_height)

        y, velocity_y, on_ground, baliktadrotate = handle_vertical_collision(player_rect, platforms, y, velocity_y, player_height, baliktadrotate)
        x, y = apply_screen_bounds(x, y, player_width, player_height, width, height)

        if y >= height - player_height:
            velocity_y = 0
            on_ground = True
            baliktadrotate = "no"

        if moving:
            for _ in range(2):  
                particles.append(Particle(x + player_width // 2, y + player_height))

            player_hp -= 0.03
            if player_hp < 0:
                player_hp = 0

        world_surface.blit(levels_background, (0, 0))

        if keys_collected == 3:
            world_surface.blit(open_door, (60, 82))
        else:
            world_surface.blit(close_door, (100, 82))

        world_surface.blit(sign1, (380, 440))
        world_surface.blit(sign1, (460, 440))
        world_surface.blit(sign2, (540, 440))
        world_surface.blit(stone1, (200, 320))

        time += 0.08
        offset = math.sin(time) * 5

        for i, life_rect in enumerate(life_rects_beginner):
            if not lives_collected[i]:
                world_surface.blit(life, (life_rect.x, life_rect.y + offset))

        key1_rect.topleft = (180, 380 + offset)
        key2_rect.topleft = (780, 320 + offset)
        key3_rect.topleft = (425, 154 + offset)

        if not key1_collected:
            world_surface.blit(light, (170, 365 + offset))
            world_surface.blit(key1, (180, 380 + offset))

        if not key2_collected:
            world_surface.blit(light, (770, 305 + offset))
            world_surface.blit(key1, (780, 320 + offset))

        if not key3_collected:
            world_surface.blit(light, (420, 140 + offset))
            world_surface.blit(key1, (430, 154 + offset))

        draw_platforms(world_surface, ground1, ground2, brick1, brick2)

        for b in breakable_bricks:
            world_surface.blit(brick2, (b.x, b.y))

        # ====================================================
        # ENEMIES UPDATE AND OS SHAKE TRIGGER
        # ====================================================
        for e in enemies:
            e_rect = pygame.Rect(e.x, e.y, 40, 40)
            
            e.update(player_rect, enemy_shoot_sound, enemy_dead_sound)
            player_hp, hit_cooldown, x, y = e.update_bullets(player_rect, player_hp, hit_cooldown, x, y, natamaan_fire)

            if e.hp > 0:
                if player_rect.colliderect(e_rect):
                    if hit_cooldown <= 0:
                        natamaan_fire.play() 

                        player_hp -= 15 
                        hit_cooldown = 30 
                        
                        # =======================================
                        # NEW: DITO MATI-TRIGGER YUNG WINDOW SHAKE
                        # =======================================
                        if can_shake_os:
                            os_window_shake_frames = 15
                            original_window_pos = get_window_pos() # Save posisyon bago mag-shake

                        if player_rect.centerx < e_rect.centerx:
                            x -= 40
                        else:
                            x += 40
                        
                        y -= 20 
                        velocity_y = 0 
            
            e.draw(world_surface)
            e.draw_hp_bar(world_surface)
            
            for bullet in e.bullets:
                pygame.draw.circle(world_surface, (255, 0, 0), (int(bullet[0]), int(bullet[1])), 5)

        frame_index += animation_speed
        if frame_index >= len(coin_frames):
            frame_index = 0

        current_frame = coin_frames[int(frame_index)]

        for i, coin_rect in enumerate(coin_rects):
            if not coins_collected[i]:
                world_surface.blit(current_frame, coin_rect.topleft)

        for particle in particles[:]:
            particle.update()
            particle.draw(world_surface)
            if particle.lifetime <= 0:
                particles.remove(particle)

        for effect in active_heal_effects[:]:
            effect.update()
            effect.draw(world_surface, x + player_width // 2, y + player_height // 2)
            if effect.timer <= 0:
                active_heal_effects.remove(effect)

        shake_x, shake_y = escano_ult.get_player_shake()
        escano_ult.draw_glow(world_surface, x, y, player_width, player_height)

        if escano_ult.is_charging:
            if escano_ult.charge_direction == "left":
                world_surface.blit(break_block_left, (x + shake_x, y + shake_y))
            else:
                world_surface.blit(break_block_right, (x + shake_x, y + shake_y))
                
        elif shoot_anim_timer > 0:
            if aim_direction == "left":
                world_surface.blit(aim_left, (x + shake_x, y + shake_y))
            else:
                world_surface.blit(aim_right, (x + shake_x, y + shake_y))
                
        elif moving:
            rotated_player = pygame.transform.rotate(player_face, player_angle)
            new_rect = rotated_player.get_rect(center=(x + player_width // 2, y + player_height // 2))
            world_surface.blit(rotated_player, (new_rect.x + shake_x, new_rect.y + shake_y))
            
        else:
            world_surface.blit(player_face, (x + shake_x, y + shake_y))
        
        escano_ult.draw_ui(world_surface, x + shake_x, y + shake_y)

        if escano_ult.active_laser:
            laser = escano_ult.active_laser
            rect = laser['rect']
            
            for _ in range(100):
                px = random.randint(rect.left, rect.right)
                py = random.randint(rect.top, rect.bottom) 
                size = random.randint(1, 5) 
                color = random.choice([(255, 150, 0), (255, 200, 0), (255, 255, 150)]) 
                
                glow_surf = pygame.Surface((size * 4, size * 4), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (*color, 60), (size * 2, size * 2), size * 2)
                world_surface.blit(glow_surf, (px - size * 2, py - size * 2))
                pygame.draw.circle(world_surface, color, (px, py), size)

        for bullet in player_bullets:
            pygame.draw.circle(world_surface, (255, 255, 0), (int(bullet[0]), int(bullet[1])), 4)

        cam_shake_x, cam_shake_y = 0, 0
        if screen_shake_frames > 0:
            cam_shake_x = random.randint(-10, 10)
            cam_shake_y = random.randint(-10, 10)
            screen_shake_frames -= 1

        draw_zoomed_camera(screen, world_surface, x + cam_shake_x, y + cam_shake_y, player_width, player_height, width, height, zoom=2)

        if player_rect.colliderect(door_rect):
            screen.blit(enter, (0, 0 + offset))

        screen.blit(vignette_surface, (0, 0))

        text = font.render(f"{keys_collected}/3", True, (255, 255, 255))

        if keys_collected == 3 and not exit_fade_done:
            if exit_fade_start is None:
                exit_music.play(loops=-1, fade_ms=2000)
                exit_fade_start = pygame.time.get_ticks()

            elapsed = pygame.time.get_ticks() - exit_fade_start

            if elapsed <= 3000:
                if elapsed < 1000:
                    alpha = int((elapsed / 1000) * 255)
                elif elapsed < 2000:
                    alpha = 255
                else:
                    alpha = int(((3000 - elapsed) / 1000) * 255)

                exit_now.set_alpha(alpha)
                screen.blit(exit_now, (0, 0 + offset))
            else:
                exit_fade_done = True

        screen.blit(counter, (0, 0))
        screen.blit(text, (30, 25))

        hp_bar_width = 120
        hp_ratio = player_hp / max_hp
        hp_x = 670 
        hp_y = 20  

        if player_hp < 30:
            hp_color = (255, 0, 0)   
        else:
            hp_color = (0, 255, 0)   

        pygame.draw.rect(screen, (60, 60, 60), (hp_x, hp_y, hp_bar_width, 15))  
        pygame.draw.rect(screen, hp_color, (hp_x, hp_y, hp_bar_width * hp_ratio, 15))  
        pygame.draw.rect(screen, (255, 255, 255), (hp_x, hp_y, hp_bar_width, 15), 2)  

        coin_text = font.render(f"{coin_count}", True, (255, 255, 255))
        screen.blit(coin_text, (35,65))

        if skill_ui_timer > 0:
            skill_ui_timer -= 1
            
            if current_skill == "Gun":
                text_color = (100, 255, 100) 
            else:
                text_color = (255, 150, 0)   
                
            ui_text = font.render(f"EQUIPPED: {current_skill.upper()}", True, text_color)
            text_rect = ui_text.get_rect(center=(width // 2, height - 30))
                     
            alpha = min(255, int((skill_ui_timer / 120) * 255 * 2))
            ui_surface = pygame.Surface((text_rect.width + 20, text_rect.height + 10), pygame.SRCALPHA)
            pygame.draw.rect(ui_surface, (0, 0, 0, alpha // 2), ui_surface.get_rect(), border_radius=5)
            
            ui_text.set_alpha(alpha)
            screen.blit(ui_surface, (text_rect.x - 10, text_rect.y - 5))
            screen.blit(ui_text, text_rect)

        if hit_cooldown > 0:
            red_flash = pygame.Surface((width, height), pygame.SRCALPHA)
            alpha = int((hit_cooldown / 30) * 40) 
            red_flash.fill((255, 0, 0, alpha)) 
            screen.blit(red_flash, (0, 0))

        if keys[pygame.K_RETURN] and player_rect.colliderect(door_rect):
            screen.blit(black, (0, 0))

        if player_hp <= 0:
            defeat_sound.play()
            game_state = "defeat"
            frozen_game_frame = screen.copy()

    # ====================================================
    # NEW: CTYPES OS WINDOW SHAKE EXECUTION
    # ====================================================
    if can_shake_os:
        if os_window_shake_frames > 0:
            shake_x = original_window_pos[0] + random.randint(-20, 20)
            shake_y = original_window_pos[1] + random.randint(-20, 20)
            set_window_pos(shake_x, shake_y)
            os_window_shake_frames -= 1
            
            if os_window_shake_frames <= 0:
                # Ibalik sa original na pwesto pag tapos na mag-shake
                set_window_pos(original_window_pos[0], original_window_pos[1])
        else:
            # I-update ang base position kung hinila ng player ang window gamit mouse
            original_window_pos = get_window_pos()

    pygame.display.update()
    clock.tick(60)

pygame.quit()
sys.exit()