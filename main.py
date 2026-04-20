import pygame
import sys
import random
import math
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

pygame.init()
pygame.mixer.init()

width = 800
height = 500
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Escano")

clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 20, bold=True)

world_surface = pygame.Surface((width, height))

from assets import *
from beginner_level_blocks import get_platforms, draw_platforms
from master_level_blocks import master_get_platforms, master_draw_platforms

time = 0
game_state = "menu"
direction = "face"
running = True
particles = []
loading_progress = 0
target_level = ""     
target_music = ""
is_playing_charge_sound = False

#scroll wheel of mouse to change skills
skills_list = ["Gun", "Ultimate"]
current_skill_index = 0
current_skill = skills_list[current_skill_index]
skill_ui_timer = 0  # Timer para ipakita yung text sa screen

# ====================================================
# PLAYER POSITIONING & STATS
# Player health, (x,y) position, and physics (speed, gravity, jump)
# ====================================================
player_hp = 100
max_hp = 100
hit_cooldown = 1
x = 400
y = 440
speed = 1.5
gravity = 0.2  # pababa po
velocity_y = 0  # vertical speed
jump_speed = -5
player_width, player_height = 20, 20
player_angle = 0

# ====================================================
# PLAYER SHOOTING VARIABLES
# List of bullets and waiting time to stop fast shooting
# ====================================================
player_bullets = []
player_shoot_cooldown = 0 
max_shoot_cooldown = 30  # Wait time for player bullets

# ====================================================
# AIM ANIMATION
# Timer and direction for the gun aiming animation
# ====================================================
shoot_anim_timer = 0
aim_direction = "right"
# ----------------------------------------------

# ====================================================
# KEYS VARIABLES
# Number of keys needed and their positions (Rectangles)
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
# Coin positions and how fast they animate
# ====================================================
frame_index = 0
animation_speed = 0.10  # lower is slower

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

# This resets the whole level back to start (health, position, keys)
def reset_beginner_level():
    global x, y, velocity_y, player_angle
    global keys_collected, key1_collected, key2_collected, key3_collected
    global coins_collected, coin_count
    global exit_fade_start, exit_fade_done
    global player_hp, hit_cooldown
    global enemies, player_bullets, shoot_anim_timer
    global lives_collected
    global breakable_bricks

    player_hp = max_hp
    hit_cooldown = 0

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
    
    # Clear player bullets so no flying bullets are left after restart
    player_bullets.clear()
    active_heal_effects.clear()
    shoot_anim_timer = 0

# Function to make a "vignette" or dark shadow on the screen edges
def generate_vignette(w, h):
    mini_w, mini_h = w // 10, h // 10
    vignette = pygame.Surface((mini_w, mini_h), pygame.SRCALPHA)
    center_x, center_y = mini_w / 2, mini_h / 2
    max_dist = math.hypot(center_x, center_y)
    
    for y in range(mini_h):
        for x in range(mini_w):
            dist = math.hypot(x - center_x, y - center_y)
            alpha = int(255 * (dist / max_dist) ** 1.2) 
            alpha = min(255, alpha) # can be darker
            vignette.set_at((x, y), (0, 0, 0, alpha))
            
    return pygame.transform.smoothscale(vignette, (w, h))

# Makes the vignette effect
vignette_surface = generate_vignette(width, height)

#breakable brick ultimate
escano_ult = EscanoUltimate()
screen_shake_frames = 0

# ====================================================
# OBJECT INSTANTIATION
# Spawns the enemy in the game
# ====================================================
enemies = []
active_heal_effects = []

while running:
    moving = False
    # mouse position
    mouse_pos = pygame.mouse.get_pos()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # DETECTION OF MOUSE SCROLL
        if event.type == pygame.MOUSEWHEEL and game_state in ["level_beginner", "level_master"]:
            current_skill_index = (current_skill_index + event.y) % len(skills_list)
            current_skill = skills_list[current_skill_index]
            skill_ui_timer = 120  # Ipakita ang text sa loob ng 2 seconds (120 frames)
            click_sound.play()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if game_state == "victory":
                reset_beginner_level()
                game_state = "menu"
            if game_state == "defeat":
                reset_beginner_level()
                game_state = "menu"

            # sound
            if game_state == "menu":
                if play_button_rect.collidepoint(event.pos):
                    game_state = "levels"
                    print("Play button clicked")
                    click_sound.play()
                    continue
                if settings_button_rect.collidepoint(event.pos):
                    print("Settings button clicked")
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
                    print("Beginner clicked")
                    loading_progress = 0
                    target_level = "level_beginner"         
                    target_music = "music/beginner_music.wav"   
                    game_state = "loading"
                elif intermediate_button_rect.collidepoint(event.pos):
                    click_sound.play()
                    print("Intermediate clicked")
                elif advanced_button_rect.collidepoint(event.pos):
                    click_sound.play()
                    print("Advanced clicked")
                elif master_button_rect.collidepoint(event.pos):
                    click_sound.play()
                    print("Master clicked")
                    loading_progress = 0
                    target_level = "level_master"
                    # target_music = "music/master_music.wav"
                    game_state = "loading"
                elif back_button_rect.collidepoint(event.pos):
                    click_sound.play()
                    game_state = "menu"
                    print("Back Clicked")

    # ==========================================
    # GAME STATES & RENDERING
    # ==========================================
    if game_state == "menu":
        # main menu background
        screen.blit(background_menu_scaled, (0, 0))

        # cursor hover
        if play_button_rect.collidepoint(mouse_pos) or settings_button_rect.collidepoint(mouse_pos) or exit_button_rect.collidepoint(mouse_pos):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        # play button/hover
        if play_button_rect.collidepoint(mouse_pos):
            screen.blit(play_button_hover_scaled, play_button_rect)
        else:
            screen.blit(play_button_scaled, play_button_rect)
        
        # settings button/hover
        if settings_button_rect.collidepoint(mouse_pos):
            screen.blit(settings_button_hover_scaled, settings_button_rect)
        else:
            screen.blit(settings_button_scaled, settings_button_rect)

        # exit button/hover
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

    # ====================================================
    # LOADING SCREEN STATE
    # ====================================================
    elif game_state == "loading":
        # Background image
        screen.blit(background_menu_scaled, (0, 0))

        # Text
        load_text = font.render("LOADING...", True, (255, 255, 255))
        screen.blit(load_text, (width // 2 - 50, height // 2 + 50))

        # Sukat
        bar_width = 400
        bar_height = 20
        bar_x = (width // 2) - (bar_width // 2)
        bar_y = (height // 2) + 90

        #  bar (Gray)
        pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))

        # Yellow 
        fill_width = int((loading_progress / 100) * bar_width)
        pygame.draw.rect(screen, (255, 215, 0), (bar_x, bar_y, fill_width, bar_height))

        #border
        pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 2)

        # Dagdagan ang progress kungbgusto kong pabagalin o pabilisin
        loading_progress += 10 

        if loading_progress >= 100:
            if target_level == "level_beginner":
                reset_beginner_level()
                game_state = "level_beginner"
                pygame.mixer.music.load(target_music)
                pygame.mixer.music.set_volume(0.5)
                pygame.mixer.music.play(-1)

            elif target_level == "level_master":
                # reset_master_level() # temporary function, since master level isn't made yet
                game_state = "level_master"
                master_music.play(fade_ms=1000)
                master_music.set_volume(0.5)
                master_music.play(-1)
                
    # ====================================================

    # exit confirm screen
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
        
        # draw the last game play
        if frozen_game_frame:
            screen.blit(frozen_game_frame, (0, 0))
            
        # DEATH TINT, manipis na layer kulay red
        tint = pygame.Surface((width, height), pygame.SRCALPHA)
        tint.fill((20, 0, 0, 150)) # Semi-transparent na dark red
        screen.blit(tint, (0, 0))
        
        # 3. ROBOTIC BLINK / GLITCH EFFECT
        glitch_chance = random.randint(1, 100)
        
        if glitch_chance > 85:
            # Matinding blink (Gagawing medyo maitim ang screen saglit)
            blink = pygame.Surface((width, height), pygame.SRCALPHA) #SRCALPHA for activating transparency
            blink.fill((5, 5, 5, 220)) 
            screen.blit(blink, (0, 0))
            
        elif glitch_chance > 60:
            # Glitch effect: Magshi-shift yung laro at yung defeat image
            shift_x = random.randint(-15, 15)
            shift_y = random.randint(-10, 10)
            
            # I-draw ulit yung game background na naka-shift
            if frozen_game_frame:
                screen.blit(frozen_game_frame, (shift_x, shift_y))
            screen.blit(tint, (shift_x, shift_y))
            
            # I-draw yung defeat image na naka-shift din
            screen.blit(defeat, (shift_x, shift_y))
            
            # Dagdag static "scanlines" para mas mukhang sirang monitor
            for _ in range(random.randint(5, 15)):
                line_y = random.randint(0, height)
                line_thickness = random.randint(2, 8)
                pygame.draw.rect(screen, (20, 20, 20), (0, line_y, width, line_thickness))
                
        else:
            # Normal na display ng defeat text sa ibabaw ng frozen game
            screen.blit(defeat, (0, 0))

    elif game_state == "level_beginner":
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        if hit_cooldown > 0:
            hit_cooldown -= 1

        keys = pygame.key.get_pressed()
        player_angle %= 360
        player_rect = pygame.Rect(x, y, player_width, player_height)

        # ====================================================
        # ULTIMATE & SHOOTING MOUSE CONTROLS AND LOGIC
        # ====================================================
        escano_ult.update()
        mouse_buttons = pygame.mouse.get_pressed()
        left_click = mouse_buttons[0]
        right_click = mouse_buttons[2]

        if player_shoot_cooldown > 0:
            player_shoot_cooldown -= 1
            
        if shoot_anim_timer > 0:
            shoot_anim_timer -= 1

        # KUNG ULTIMATE ANG GAMIT
        if current_skill == "Ultimate":
            # Kunin ang solid walls bago i-fire para alam ng ultimate kung saan hihinto
            solid_platforms = get_platforms() 
            
            if escano_ult.handle_input(left_click, right_click, x, y, player_width, player_height, solid_platforms):
                screen_shake_frames = 15 
                ultimate_sound.play()   

        else:
            # KUNG HINDI ULTIMATE, I-CANCEL ANG CHARGING 
            escano_ult.is_charging = False
            escano_ult.charge_timer = 0
            
            # KUNG GUN ANG GAMIT 
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

        # ====================================================
        # SOUND LOGIC PARA SA CHARGING (LOOPING)
        # ====================================================
        if escano_ult.is_charging:
            if not is_playing_charge_sound:
                charging.play(loops=-1) 
                is_playing_charge_sound = True
        else:
            if is_playing_charge_sound:
                charging.stop()
                is_playing_charge_sound = False

        # ====================================================
        # CHECK ULTIMATE COLLISION (BRICKS & ENEMIES)
        # ====================================================
        # If the ultimate laser is currently active
        if escano_ult.active_laser:
            # Get the laser object (dictionary)
            laser = escano_ult.active_laser
            # Collision rectangle of the laser
            laser_rect = laser['rect']


            # Ensure laser has not exceeded max number of allowed breaks
            if laser['current_breaks'] < laser['max_breaks']:
                # Get all bricks currently hit by the laser
                hit_bricks = [b for b in breakable_bricks if laser_rect.colliderect(b)]
                
                # Sort bricks based on laser direction for consistent destruction order
                if laser['dir'] == "right":
                    hit_bricks.sort(key=lambda b: b.x)
                else:
                    hit_bricks.sort(key=lambda b: b.x, reverse=True) 
                
                # Process each hit brick
                for b in hit_bricks:
                    # Check again if laser can still break more bricks
                    if laser['current_breaks'] < laser['max_breaks']:
                        if b in breakable_bricks:
                            # Remove brick (destroy it)
                            breakable_bricks.remove(b)
                            laser['current_breaks'] += 1
                            for _ in range(40):
                                particles.append(Particle(b.x + 10, b.y + 10))
                    else:
                        break

            if 'hit_enemies' not in escano_ult.active_laser:
                escano_ult.active_laser['hit_enemies'] = []

            # Loop through all enemies
            for e in enemies:
                # Create collision box for enemy
                e_rect = pygame.Rect(e.x, e.y, 40, 40)
                # Check if laser hits enemy and enemy is alive
                if e.hp > 0 and laser_rect.colliderect(e_rect):
                    # I-check kung HINDI pa siya natatamaan ng laser na ito
                    if e not in escano_ult.active_laser['hit_enemies']:
                        e.hp -= 60  # Ultimate does 60 damage per hit
                        escano_ult.active_laser['hit_enemies'].append(e) # I-record na natamaan na siya
                        
                        # I-play lang ang death sound at explosion KAPAG naging 0 na ang buhay
                        if e.hp <= 0:
                            enemy_dead_sound.play() 
                            for _ in range(100):  
                                particles.append(Particle(e.x + 20, e.y + 20))

        # ====================================================
        # PHYSICS INTEGRATION
        # ====================================================
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
            
            # I-check kung aling kalaban ang natamaan
            for e in enemies:
                e_rect = pygame.Rect(e.x, e.y, 40, 40)
                if e.hp > 0 and bullet_rect.colliderect(e_rect):
                    e.hp -= 15 
                    print("Enemy Hit!")
                    
                    if bullet in player_bullets:
                        player_bullets.remove(bullet)

                    # EXPLOSION EFFECT KAPAG NAMATAY
                    if e.hp <= 0:
                        for _ in range(1000):  
                            particles.append(Particle(e.x + 20, e.y + 20))
                    break
            
            #hindi na tatagos bala ng player sa walls
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

        # KEY COLLISION
        key1_collected, keys_collected = check_key_collection(player_rect, key1_rect, key1_collected, keys_collected, key_collect)
        key2_collected, keys_collected = check_key_collection(player_rect, key2_rect, key2_collected, keys_collected, key_collect)
        key3_collected, keys_collected = check_key_collection(player_rect, key3_rect, key3_collected, keys_collected, key_collect)

        # COIN COLLISION
        coins_collected, coin_count = check_coin_collection(player_rect, coin_rects, coins_collected, coin_count, coin_sound)

        #LIFE COLLISION
        lives_collected, player_hp, just_healed = check_life_collection(player_rect, life_rects_beginner, lives_collected, player_hp, max_hp, 20, life_sound)
        
        if just_healed:
            active_heal_effects.append(HealEffect())

        # PLATFORM LIST
        platforms = get_platforms()
        for b in breakable_bricks:
            platforms.append(b)

        # check if on ground BEFORE applying gravity

        # check if on ground BEFORE applying gravity
        player_rect = pygame.Rect(x, y, player_width, player_height)
        on_ground, baliktadrotate, y, velocity_y = check_pre_gravity_ground(player_rect, platforms, y, velocity_y)

        dx = 0

        # jump
        if (keys[pygame.K_SPACE] or keys[pygame.K_w]) and on_ground:
            velocity_y = jump_speed
            moving = True
            
            # spawn jump particles
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

        # apply gravity
        velocity_y += gravity
        y += velocity_y

        # collision with platforms
        player_rect = pygame.Rect(x, y, player_width, player_height)

        y, velocity_y, on_ground, baliktadrotate = handle_vertical_collision(player_rect, platforms, y, velocity_y, player_height, baliktadrotate)
        x, y = apply_screen_bounds(x, y, player_width, player_height, width, height)

        # Kung tumama ang player sa pinakailalim ng screen
        if y >= height - player_height:
            velocity_y = 0
            on_ground = True
            baliktadrotate = "no"

        if moving:
            # create small particles behind the player
            for _ in range(2):  # how many particles per frame
                particles.append(Particle(x + player_width // 2, y + player_height))

            # nababawasan buhay kapag naglalakad
            player_hp -= 0.03
            
            if player_hp < 0:
                player_hp = 0

       # draw background
        world_surface.blit(levels_background, (0, 0))

        # exit
        if keys_collected == 3:
            world_surface.blit(open_door, (60, 82))
        else:
            world_surface.blit(close_door, (100, 82))

        # environment no collision for this
        world_surface.blit(sign1, (380, 440))
        world_surface.blit(sign1, (460, 440))
        world_surface.blit(sign2, (540, 440))
        world_surface.blit(stone1, (200, 320))

        # lutang effect
        time += 0.08
        offset = math.sin(time) * 5

                # Draw Lives (ONLY IF NOT COLLECTED)
        for i, life_rect in enumerate(life_rects_beginner):
            if not lives_collected[i]:
                world_surface.blit(life, (life_rect.x, life_rect.y + offset))


        key1_rect.topleft = (180, 380 + offset)
        key2_rect.topleft = (780, 320 + offset)
        key3_rect.topleft = (425, 154 + offset)

        # KEY 1
        if not key1_collected:
            world_surface.blit(light, (170, 365 + offset))
            world_surface.blit(key1, (180, 380 + offset))

        # KEY 2
        if not key2_collected:
            world_surface.blit(light, (770, 305 + offset))
            world_surface.blit(key1, (780, 320 + offset))

        # KEY 3
        if not key3_collected:
            world_surface.blit(light, (420, 140 + offset))
            world_surface.blit(key1, (430, 154 + offset))

                # DRAW PLATFORMS
        draw_platforms(world_surface, ground1, ground2, brick1, brick2)

        for b in breakable_bricks:
            world_surface.blit(brick2, (b.x, b.y))

        # ====================================================
        # MULTIPLE ENEMIES UPDATE, COLLISION, & DRAW
        # ====================================================
        for e in enemies:
            e_rect = pygame.Rect(e.x, e.y, 40, 40)
            
            # Update Enemy at mga bala niya
            e.update(player_rect, enemy_shoot_sound, enemy_dead_sound)
            player_hp, hit_cooldown, x, y = e.update_bullets(player_rect, player_hp, hit_cooldown, x, y, natamaan_fire)

            # COLLISION at KNOCKBACK KUNG BUHAY PA ANG KALABAN
            if e.hp > 0:
                if player_rect.colliderect(e_rect):
                    if hit_cooldown <= 0:
                        print("ouch nadikitan ko kalaban HAHAHA")
                        natamaan_fire.play() 

                        player_hp -= 15 
                        hit_cooldown = 30 

                        if player_rect.centerx < e_rect.centerx:
                            x -= 40
                        else:
                            x += 40
                        
                        y -= 20 
                        velocity_y = 0 
            
            # Draw Kalaban at HP Bar
            e.draw(world_surface)
            e.draw_hp_bar(world_surface)
            
            # Draw Bala ng Kalaban
            for bullet in e.bullets:
                pygame.draw.circle(world_surface, (255, 0, 0), (int(bullet[0]), int(bullet[1])), 5)
        # ====================================================

        # animation ng pera
        frame_index += animation_speed
        if frame_index >= len(coin_frames):
            frame_index = 0

        current_frame = coin_frames[int(frame_index)]

        # Draw Coins (ONLY IF NOT COLLECTED)
        for i, coin_rect in enumerate(coin_rects):
            if not coins_collected[i]:
                world_surface.blit(current_frame, coin_rect.topleft)

        # update and draw particles
        for particle in particles[:]:
            particle.update()
            particle.draw(world_surface)
            if particle.lifetime <= 0:
                particles.remove(particle)

        # ====================================================
        # DRAW HEAL EFFECTS
        # ====================================================
        for effect in active_heal_effects[:]:
            effect.update()
            effect.draw(world_surface, x + player_width // 2, y + player_height // 2)
            if effect.timer <= 0:
                active_heal_effects.remove(effect)

        shake_x, shake_y = escano_ult.get_player_shake()
        escano_ult.draw_glow(world_surface, x, y, player_width, player_height)

        # draw player
        # Kunin ang shake at i-draw ang glow sa likod BAGO i-draw ang player
        shake_x, shake_y = escano_ult.get_player_shake()
        escano_ult.draw_glow(world_surface, x, y, player_width, player_height)

        # ====================================================
        # DRAW PLAYER
        # ====================================================
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
            # rotate the player sprite kapag naglalakad
            rotated_player = pygame.transform.rotate(player_face, player_angle)
            new_rect = rotated_player.get_rect(center=(x + player_width // 2, y + player_height // 2))
            world_surface.blit(rotated_player, (new_rect.x + shake_x, new_rect.y + shake_y))
            
        else:
            world_surface.blit(player_face, (x + shake_x, y + shake_y))
        
        # Draw the Cooldown UI Circle 
        escano_ult.draw_ui(world_surface, x + shake_x, y + shake_y)

        # ====================================================
        # DRAW ULTIMATE BEAM AS PARTICLES
        # ====================================================
        if escano_ult.active_laser:
            laser = escano_ult.active_laser
            rect = laser['rect']
            
            for _ in range(100):
                px = random.randint(rect.left, rect.right)
                
                py = random.randint(rect.top, rect.bottom) 
                
                size = random.randint(1, 5) # nipis or kapal ng particle
                
                color = random.choice([(255, 150, 0), (255, 200, 0), (255, 255, 150)]) 
                
                glow_surf = pygame.Surface((size * 4, size * 4), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (*color, 60), (size * 2, size * 2), size * 2)
                world_surface.blit(glow_surf, (px - size * 2, py - size * 2))

                pygame.draw.circle(world_surface, color, (px, py), size)
                
            # pygame.draw.line(world_surface, (255, 255, 255), (rect.left, rect.centery), (rect.right, rect.centery), 3)

        # ====================================================
        # I-DRAW ANG PLAYER BULLETS
        # ====================================================
        for bullet in player_bullets:
            pygame.draw.circle(world_surface, (255, 255, 0), (int(bullet[0]), int(bullet[1])), 4)
        # ====================================================

        # ==========================================================
        # CAMERA & ZOOM LOGIC WITH SCREEN SHAKE
        # ==========================================================
        cam_shake_x, cam_shake_y = 0, 0
        if screen_shake_frames > 0:
            cam_shake_x = random.randint(-10, 10)
            cam_shake_y = random.randint(-10, 10)
            screen_shake_frames -= 1

        draw_zoomed_camera(screen, world_surface, x + cam_shake_x, y + cam_shake_y, player_width, player_height, width, height, zoom=2)

        if player_rect.colliderect(door_rect):
            screen.blit(enter, (0, 0 + offset))

        #applying vignette
        # ==========================================================
        screen.blit(vignette_surface, (0, 0))
        # =======================================================

        # key counter
        text = font.render(f"{keys_collected}/3", True, (255, 255, 255))

        if keys_collected == 3 and not exit_fade_done:
            # start timer and play music ONCE
            if exit_fade_start is None:
                exit_music.play(loops=-1, fade_ms=2000)
                exit_fade_start = pygame.time.get_ticks()

            elapsed = pygame.time.get_ticks() - exit_fade_start

            if elapsed <= 3000:
                if elapsed < 1000:
                    # fade in (0 → 255)
                    alpha = int((elapsed / 1000) * 255)
                elif elapsed < 2000:
                    # stay (fully visible)
                    alpha = 255
                else:
                    # fade out (255 → 0)
                    alpha = int(((3000 - elapsed) / 1000) * 255)

                exit_now.set_alpha(alpha)
                screen.blit(exit_now, (0, 0 + offset))
            else:
                # done forever
                exit_fade_done = True

        screen.blit(counter, (0, 0))
        screen.blit(text, (30, 25))

        # HP BAR (left side)
        # HP BAR 
        hp_bar_width = 120
        hp_ratio = player_hp / max_hp

        # HP ADJUSTMENT POS
        hp_x = 670 
        hp_y = 20  
        # =======================================

        # COLOR OF HP
        if player_hp < 30:
            hp_color = (255, 0, 0)   # RED
        else:
            hp_color = (0, 255, 0)   # GREEN

        pygame.draw.rect(screen, (60, 60, 60), (hp_x, hp_y, hp_bar_width, 15))  # background
        pygame.draw.rect(screen, hp_color, (hp_x, hp_y, hp_bar_width * hp_ratio, 15))  # HP fill
        pygame.draw.rect(screen, (255, 255, 255), (hp_x, hp_y, hp_bar_width, 15), 2)  # border

        coin_text = font.render(f"{coin_count}", True, (255, 255, 255))
        screen.blit(coin_text, (35,65))

        # =======================================
        # DRAW SKILL UI INDICATOR
        # =======================================
        if skill_ui_timer > 0:
            skill_ui_timer -= 1
            
            # Kulay depende sa skill
            if current_skill == "Gun":
                text_color = (100, 255, 100) # Greenish
            else:
                text_color = (255, 150, 0)   # Orange/Gold
                
            # background box 
            ui_text = font.render(f"EQUIPPED: {current_skill.upper()}", True, text_color)
            text_rect = ui_text.get_rect(center=(width // 2, height - 30))
                     
            # Fade effect para sa UI (fade in then fade out)
            alpha = min(255, int((skill_ui_timer / 120) * 255 * 2))
            ui_surface = pygame.Surface((text_rect.width + 20, text_rect.height + 10), pygame.SRCALPHA)
            pygame.draw.rect(ui_surface, (0, 0, 0, alpha // 2), ui_surface.get_rect(), border_radius=5)
            
            # Draw border
            ui_text.set_alpha(alpha)
            screen.blit(ui_surface, (text_rect.x - 10, text_rect.y - 5))
            screen.blit(ui_text, text_rect)

        # Dugo / Red Flash effect kapag natatamaan
        if hit_cooldown > 0:
            red_flash = pygame.Surface((width, height), pygame.SRCALPHA)
            # Habang paubos ang cooldown, pababa rin ang opacity (alpha) para mag-fade
            alpha = int((hit_cooldown / 30) * 40) 
            red_flash.fill((255, 0, 0, alpha)) # Red color na may transparency
            screen.blit(red_flash, (0, 0))

        if keys[pygame.K_RETURN] and player_rect.colliderect(door_rect):
            screen.blit(black, (0, 0))

        if player_hp <= 0:
            defeat_sound.play()
            game_state = "defeat"
            frozen_game_frame = screen.copy()

    elif game_state == "level_master":
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        # ==========================================
        # STEP 1: COOLDOWNS AT BASIC INPUTS
        # ==========================================
        if hit_cooldown > 0:
            hit_cooldown -= 1

        keys = pygame.key.get_pressed()
        player_angle %= 360
        player_rect = pygame.Rect(x, y, player_width, player_height)

        if player_shoot_cooldown > 0:
            player_shoot_cooldown -= 1
            
        if shoot_anim_timer > 0:
            shoot_anim_timer -= 1

        # ==========================================
        # STEP 2: MOUSE CONTROLS, ULTIMATE, AT GUN
        # ==========================================
        escano_ult.update()
        mouse_buttons = pygame.mouse.get_pressed()
        left_click = mouse_buttons[0]
        right_click = mouse_buttons[2]

        if current_skill == "Ultimate":
            solid_platforms = master_get_platforms() # Gamit ang master platforms
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

        # CHARGING SOUND LOGIC
        if escano_ult.is_charging:
            if not is_playing_charge_sound:
                charging.play(loops=-1) 
                is_playing_charge_sound = True
        else:
            if is_playing_charge_sound:
                charging.stop()
                is_playing_charge_sound = False

        # BULLET POSITION UPDATE
        for bullet in player_bullets[:]:
            bullet[0] += bullet[2] 
            if bullet[0] < 0 or bullet[0] > width:
                if bullet in player_bullets:
                    player_bullets.remove(bullet)
                continue

        # ==========================================
        # STEP 3: PLATFORMS, GRAVITY, AT MOVEMENT
        # ==========================================
        platforms = master_get_platforms() # Para hindi lumutang sa master level map
        player_rect = pygame.Rect(x, y, player_width, player_height)
        on_ground, baliktadrotate, y, velocity_y = check_pre_gravity_ground(player_rect, platforms, y, velocity_y)

        dx = 0

        # JUMP
        if (keys[pygame.K_SPACE] or keys[pygame.K_w]) and on_ground:
            velocity_y = jump_speed
            moving = True
            for _ in range(100):
                particles.append(Particle(x + player_width // 2, y + player_height))

        # MOVE LEFT / RIGHT
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

        # ==========================================
        # STEP 4: HORIZONTAL / VERTICAL COLLISION
        # ==========================================
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

        # ==========================================
        # STEP 5: DRAW ENVIRONMENT AT PLAYER
        # ==========================================
        screen.blit(levels_background, (0, 0))
        master_draw_platforms(screen, ground1, ground2, brick1, brick2)

        shake_x, shake_y = escano_ult.get_player_shake()
        escano_ult.draw_glow(screen, x, y, player_width, player_height)

        if escano_ult.is_charging:
            if escano_ult.charge_direction == "left":
                screen.blit(break_block_left, (x + shake_x, y + shake_y))
            else:
                screen.blit(break_block_right, (x + shake_x, y + shake_y))
        elif shoot_anim_timer > 0:
            if aim_direction == "left":
                screen.blit(aim_left, (x + shake_x, y + shake_y))
            else:
                screen.blit(aim_right, (x + shake_x, y + shake_y))
        elif moving:
            rotated_player = pygame.transform.rotate(player_face, player_angle)
            new_rect = rotated_player.get_rect(center=(x + player_width // 2, y + player_height // 2))
            screen.blit(rotated_player, (new_rect.x + shake_x, new_rect.y + shake_y))
        else:
            screen.blit(player_face, (x + shake_x, y + shake_y))

        escano_ult.draw_ui(screen, x + shake_x, y + shake_y)

        for bullet in player_bullets:
            pygame.draw.circle(screen, (255, 255, 0), (int(bullet[0]), int(bullet[1])), 4)

        if skill_ui_timer > 0:
            skill_ui_timer -= 1
                    # Kulay depende sa skill
            if current_skill == "Gun":
                text_color = (100, 255, 100) # Greenish
            else:
                text_color = (255, 150, 0)   # Orange/Gold
                    
            # background box 
            ui_text = font.render(f"EQUIPPED: {current_skill.upper()}", True, text_color)
            text_rect = ui_text.get_rect(center=(width // 2, height - 30))
                        
            # Fade effect para sa UI (fade in then fade out)
            alpha = min(255, int((skill_ui_timer / 120) * 255 * 2))
            ui_surface = pygame.Surface((text_rect.width + 20, text_rect.height + 10), pygame.SRCALPHA)
            pygame.draw.rect(ui_surface, (0, 0, 0, alpha // 2), ui_surface.get_rect(), border_radius=5)
                
            # Draw border
            ui_text.set_alpha(alpha)
            screen.blit(ui_surface, (text_rect.x - 10, text_rect.y - 5))
            screen.blit(ui_text, text_rect)

    pygame.display.update()
    clock.tick(60)

pygame.quit()
sys.exit()