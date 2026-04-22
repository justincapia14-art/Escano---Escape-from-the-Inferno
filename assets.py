#assets.py
import pygame

# =====================================================================
# ASSET LOADING (AUDIO, IMAGES, RECTANGLES)
# =====================================================================

# --- Music & Sounds ---
click_sound = pygame.mixer.Sound("music/ui-click-retro-game-click-01.wav")
key_collect = pygame.mixer.Sound("music/key.wav")
exit_music = pygame.mixer.Sound("music/exit_now.wav")
coin_sound = pygame.mixer.Sound("music/coin.wav")
victory_sound = pygame.mixer.Sound("music/victory.wav")
natamaan_fire = pygame.mixer.Sound("music/natamaan.wav")
enemy_shoot_sound = pygame.mixer.Sound("music/enemy_aim.wav")
player_shoot_sound = pygame.mixer.Sound("music/bala_player.wav")
enemy_dead_sound = pygame.mixer.Sound("music/enemy_dead.wav")
life_sound = pygame.mixer.Sound("music/life.wav")
charging = pygame.mixer.Sound("music/charging.wav")
ultimate_sound = pygame.mixer.Sound("music/ult_shoot.wav")
defeat_sound = pygame.mixer.Sound("music/defeat.wav")
master_music = pygame.mixer.Sound("music/master_music.wav")
roll_sound = pygame.mixer.Sound("music/Rolling.wav")
boss_shoot_sound = pygame.mixer.Sound("music/enemy_shoot_sound.wav")

# --- Backgrounds ---
background_menu = pygame.image.load("background/background menu.png").convert()
background_menu_scaled = pygame.transform.scale(background_menu, (800, 510))

background = pygame.image.load("background/background.png")
background = pygame.transform.scale(background, (800, 510))

levels_background = pygame.image.load("background/m2/PRE_ORIG_SIZE.png")
levels_background = pygame.transform.scale(levels_background, (800, 500))

level_selection_background = pygame.image.load("background/level_selection.png")
level_selection_background = pygame.transform.scale(level_selection_background, (790, 510))

exit_now = pygame.image.load("background/exit_now.png").convert_alpha()
victory_bg = pygame.image.load("background/victory.png").convert_alpha()
defeat = pygame.image.load("background/defeat.png").convert_alpha()

black = pygame.image.load("background/black.png").convert_alpha()
black = pygame.transform.scale(black, (800, 500))
black.set_alpha(128)

enter = pygame.image.load("background/fed_exit.png").convert_alpha()
enter = pygame.transform.scale(enter, (800, 500))

exit_confirm_bg = pygame.image.load("background/are_you_sure.png").convert_alpha()
exit_confirm_bg = pygame.transform.scale(exit_confirm_bg, (400, 250))

counter = pygame.image.load("background/score_count.png").convert_alpha()
blur_back  = pygame.image.load('background/blur_back.png').convert_alpha()

# --- Player Animations ---
player_right = pygame.image.load("player anim/player_right.png")
player_right = pygame.transform.scale(player_right, (20, 20))

player_left = pygame.image.load("player anim/player_left.png")
player_left = pygame.transform.scale(player_left, (20, 20))

player_face = pygame.image.load("player anim/player_face.png")
player_face = pygame.transform.scale(player_face, (20, 20))

aim_right = pygame.image.load("player anim/aim_right.png")
aim_right = pygame.transform.scale(aim_right, (20, 20))

aim_left = pygame.image.load("player anim/aim_left.png")
aim_left = pygame.transform.scale(aim_left, (20, 20))

break_block_right = pygame.image.load("player anim/break_block_right.png")
break_block_right = pygame.transform.scale(break_block_right, (20, 20))

break_block_left = pygame.image.load("player anim/break_block_left.png")
break_block_left = pygame.transform.scale(break_block_left, (20, 20))

# --- Enemy Animations ---
enemy_right = pygame.image.load("enemy/enemy_right.png")
enemy_aim = pygame.image.load("enemy/enemy_aim.png")
enemy_left = pygame.image.load("enemy/enemy_left.png")

# --- Environment Elements ---
ground1 = pygame.image.load("Platformer/Ground_06.png").convert_alpha()
ground1 = pygame.transform.scale(ground1, (20, 20))

ground2 = pygame.image.load("Platformer/Ground_02.png").convert_alpha()
ground2 = pygame.transform.scale(ground2, (20, 20))

brick1 = pygame.image.load("Platformer/Brick_01.png").convert_alpha()
brick1 = pygame.transform.scale(brick1, (20, 20))

brick2 = pygame.image.load("Platformer/Brick_02.png").convert_alpha()
brick2 = pygame.transform.scale(brick2, (20, 20))

sign1 = pygame.image.load("Environment/Sign_01.png").convert_alpha()
sign1 = pygame.transform.scale(sign1, (20, 20))

sign2 = pygame.image.load("Environment/Sign_02.png").convert_alpha()
sign2 = pygame.transform.scale(sign2, (20, 20))

stone1 = pygame.image.load("Environment/Decor_Statue.png").convert_alpha()
stone1 = pygame.transform.scale(stone1, (80, 80))

close_door = pygame.image.load("background/close_door.png").convert_alpha()
open_door = pygame.image.load("background/open_door.png").convert_alpha()

bigBoss = pygame.image.load("enemy/BigBoss.png").convert_alpha()

# --- Collectibles ---
key1 = pygame.image.load("Collectable Object/Key_02.png").convert_alpha()
key1 = pygame.transform.scale(key1, (20, 10))

light = pygame.image.load("Collectable Object/Light.png").convert_alpha()
light = pygame.transform.scale(light, (40, 40))

life = pygame.image.load("Collectable Object/Life.png").convert_alpha()
life = pygame.transform.scale(life, (20, 20))

coin_frames = [
    pygame.image.load("Collectable Object/Coin_01.png"),
    pygame.image.load("Collectable Object/Coin_02.png"),
    pygame.image.load("Collectable Object/Coin_03.png"),
    pygame.image.load("Collectable Object/Coin_04.png"),
    pygame.image.load("Collectable Object/Coin_05.png"),
    pygame.image.load("Collectable Object/Coin_06.png"),
]
coin_frames = [pygame.transform.scale(img, (20, 20)) for img in coin_frames]

# --- Buttons & UI ---
play_button = pygame.image.load("buttons/play.png").convert_alpha()
play_button_scaled = pygame.transform.scale(play_button, (150, 40))
play_button_hover = pygame.image.load("buttons/play_hover.png").convert_alpha()
play_button_hover_scaled = pygame.transform.scale(play_button_hover, (150, 40))
play_button_rect = play_button_scaled.get_rect(topleft=(320, 350))

settings_button = pygame.image.load("buttons/settings.png").convert_alpha()
settings_button_scaled = pygame.transform.scale(settings_button, (150, 40))
settings_button_hover = pygame.image.load("buttons/settings_hover.png").convert_alpha()
settings_button_hover_scaled = pygame.transform.scale(settings_button_hover, (150, 40))
settings_button_rect = settings_button_scaled.get_rect(topleft=(320, 400))

exit_button = pygame.image.load("buttons/exit.png").convert_alpha()
exit_button_scaled = pygame.transform.scale(exit_button, (150, 40))
exit_button_hover = pygame.image.load("buttons/exit_hover.png").convert_alpha()
exit_button_hover_scaled = pygame.transform.scale(exit_button_hover, (150, 40))
exit_button_rect = exit_button_scaled.get_rect(topleft=(320, 450))

back_button = pygame.image.load("buttons/back.png").convert_alpha()
back_button = pygame.transform.scale(back_button, (75, 20))
back_button_hover = pygame.image.load("buttons/back_hover.png").convert_alpha()
back_button_hover = pygame.transform.scale(back_button_hover, (75, 20))
back_button_rect = back_button.get_rect(topleft=(365, 395))

yes_button = pygame.image.load("buttons/yes.png").convert_alpha()
yes_button = pygame.transform.scale(yes_button, (100, 30))
yes_button_hover = pygame.image.load("buttons/yes_hover.png").convert_alpha()
yes_button_hover = pygame.transform.scale(yes_button_hover, (100, 30))
yes_rect = yes_button.get_rect(topleft=(280, 290))

no_button = pygame.image.load("buttons/no.png").convert_alpha()
no_button = pygame.transform.scale(no_button, (100, 30))
no_button_hover = pygame.image.load("buttons/no_hover.png").convert_alpha()
no_button_hover = pygame.transform.scale(no_button_hover, (100, 30))
no_rect = no_button.get_rect(topleft=(420, 290))

beginner_button = pygame.image.load("buttons/beginner.png").convert_alpha()
beginner_button = pygame.transform.scale(beginner_button, (150, 50))
beginner_button_hover = pygame.image.load("buttons/beginner_hover.png").convert_alpha()
beginner_button_hover = pygame.transform.scale(beginner_button_hover, (150, 50))
beginner_button_rect = beginner_button.get_rect(topleft=(328, 150))

intermediate_button = pygame.image.load("buttons/intermediate.png").convert_alpha()
intermediate_button = pygame.transform.scale(intermediate_button, (150, 50))
intermediate_button_hover = pygame.image.load("buttons/intermediate_hover.png").convert_alpha()
intermediate_button_hover = pygame.transform.scale(intermediate_button_hover, (150, 50))
intermediate_button_rect = intermediate_button.get_rect(topleft=(328, 210))

advanced_button = pygame.image.load("buttons/advanced.png").convert_alpha()
advanced_button = pygame.transform.scale(advanced_button, (150, 50))
advanced_button_hover = pygame.image.load("buttons/advanced_hover.png").convert_alpha()
advanced_button_hover = pygame.transform.scale(advanced_button_hover, (150, 50))
advanced_button_rect = advanced_button.get_rect(topleft=(328, 270))

master_button = pygame.image.load("buttons/master.png").convert_alpha()
master_button = pygame.transform.scale(master_button, (150, 50))
master_button_hover = pygame.image.load("buttons/master_hover.png").convert_alpha()
master_button_hover = pygame.transform.scale(master_button_hover, (150, 50))
master_button_rect = master_button.get_rect(topleft=(328, 330))