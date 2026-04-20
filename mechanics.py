#mechanics.py
import pygame
import random

def check_key_collection(player_rect, key_rect, key_collected, keys_collected, sound):
    if player_rect.colliderect(key_rect) and not key_collected:
        sound.play()
        return True, keys_collected + 1
    return key_collected, keys_collected

def check_coin_collection(player_rect, coin_rects, coins_collected, coin_count, sound):
    for i, coin_rect in enumerate(coin_rects):
        if player_rect.colliderect(coin_rect) and not coins_collected[i]:
            coins_collected[i] = True
            coin_count += 1
            sound.play()
    return coins_collected, coin_count

def check_pre_gravity_ground(player_rect, platforms, y, velocity_y):
    on_ground = False
    baliktadrotate = "no" 
    new_y = y
    new_vy = velocity_y
    
    for plat_rect in platforms:
        if player_rect.bottom >= plat_rect.top and \
           player_rect.bottom <= plat_rect.top + 10 and \
           player_rect.right > plat_rect.left and \
           player_rect.left < plat_rect.right:
            on_ground = True
            baliktadrotate = "no"
            break

        elif player_rect.top <= plat_rect.bottom and \
             player_rect.top >= plat_rect.bottom - 10 and \
             player_rect.right > plat_rect.left and \
             player_rect.left < plat_rect.right:
            new_y = plat_rect.bottom
            baliktadrotate = "yes"
            new_vy = 0
            
    return on_ground, baliktadrotate, new_y, new_vy

def handle_horizontal_collision(player_rect, platforms, x, dx, player_width):
    new_x = x
    for plat_rect in platforms:
        if player_rect.colliderect(plat_rect):
            if dx > 0:  
                new_x = plat_rect.left - player_width
            elif dx < 0:  
                new_x = plat_rect.right
    return new_x

def handle_vertical_collision(player_rect, platforms, y, velocity_y, player_height, current_baliktadrotate):
    new_y = y
    new_vy = velocity_y
    on_ground = False
    baliktadrotate = current_baliktadrotate

    for plat_rect in platforms:
        if player_rect.colliderect(plat_rect):
            if velocity_y > 0:
                new_y = plat_rect.top - player_height
                new_vy = 0
                on_ground = True
                baliktadrotate = "no"
            elif velocity_y < 0:
                new_y = plat_rect.bottom
                new_vy = 0
                baliktadrotate = "yes"
                
    return new_y, new_vy, on_ground, baliktadrotate



def check_life_collection(player_rect, life_rects, lives_collected, current_hp, maximum_hp, heal_amount, sound):
    just_healed = False

    for i, life_rect in enumerate(life_rects):
        if not lives_collected[i] and player_rect.colliderect(life_rect):
            lives_collected[i] = True
            current_hp += heal_amount

            sound.play()

            just_healed = True

            if current_hp > maximum_hp:
                current_hp = maximum_hp
    return lives_collected, current_hp, just_healed


# mechanics.py (Sa pinakababa)

class HealEffect:
    def __init__(self):
        self.timer = 30 #frame of effect duration
        self.max_time = 30
        self.radius = 5  # start of circle size

    def update(self):
        self.timer -= 1
        self.radius += 2.5  #how fast the circle grows

    def draw(self, surface, center_x, center_y):
        if self.timer > 0:
            size = int(self.radius * 4)
            if size <= 0: return
            effect_surf = pygame.Surface((size, size), pygame.SRCALPHA)
            
            alpha = max(0, int((self.timer / self.max_time) * 200))
            
            # green fade
            pygame.draw.circle(effect_surf, (0, 255, 0, alpha // 2), (size // 2, size // 2), self.radius)
            
            # circle outline
            pygame.draw.circle(effect_surf, (50, 255, 50, alpha), (size // 2, size // 2), int(self.radius * 1.2), 3)
            
            surface.blit(effect_surf, (center_x - size // 2, center_y - size // 2))


class EscanoUltimate:
    def __init__(self):
        self.cooldown_max = 600  # 10 seconds
        self.cooldown_timer = 0
        self.charge_max = 120    # 2 seconds na hold
        self.charge_timer = 0
        self.is_charging = False
        self.charge_direction = None
        self.active_laser = None 
        self.charge_particles = [] # DITO MASI-SAVE ANG ENERGY PARTICLES

    def update(self):
        # Update ng cooldown
        if self.cooldown_timer > 0:
            self.cooldown_timer -= 1
        
        # Update ng active laser
        if self.active_laser:
            self.active_laser['timer'] -= 1
            if self.active_laser['timer'] <= 0:
                self.active_laser = None

        # Update ng Energy Particles (para lumipad pataas at mawala)
        for p in self.charge_particles[:]:
            p['x'] += p['dx']
            p['y'] += p['dy']
            p['lifetime'] -= 1
            p['size'] = max(0, p['size'] - 0.15) # Dahan-dahang lumiliit
            
            if p['lifetime'] <= 0 or p['size'] <= 0:
                self.charge_particles.remove(p)

    def handle_input(self, left_click, right_click, player_x, player_y, player_width, player_height, platforms):
        # Kapag ready na at nagho-hold ng click
        if self.cooldown_timer <= 0:
            if left_click:
                self.is_charging = True
                self.charge_direction = "left"
                self.charge_timer += 1
                return False
            elif right_click:
                self.is_charging = True
                self.charge_direction = "right"
                self.charge_timer += 1
                return False
            
        # Kapag binitawan ang click
        if self.is_charging:
            if self.charge_timer >= self.charge_max:
                # FULL CHARGE! FIRE ULTIMATE!
                self.cooldown_timer = self.cooldown_max
                
                # Setup the laser attack area
                laser_y = player_y - 10
                laser_height = 40
                
                # Para sa collision: Kunin lang ang exact center (para i-ignore ang sahig)
                laser_center_y = player_y + (player_height // 2)
                
                if self.charge_direction == "right":
                    start_x = player_x + player_width
                    end_x = start_x + 800 # Default max length
                    
                    # I-check ang mga platforms para paikliin ang laser kung may pader
                    for plat in platforms:
                        # Check kung tinatamaan ng center line ng laser yung wall block
                        if plat.top < laser_center_y < plat.bottom:
                            # Kung nasa kanan ng player at mas malapit, putulin ang laser dito
                            if plat.left > start_x and plat.left < end_x:
                                end_x = plat.left
                                
                    laser_rect = pygame.Rect(start_x, laser_y, max(0, end_x - start_x), laser_height)
                    
                else: # Kaliwa
                    start_x = player_x
                    end_x = start_x - 800 # Default max length pakaliwa
                    
                    for plat in platforms:
                        # Check kung tinatamaan ng center line ng laser yung wall block
                        if plat.top < laser_center_y < plat.bottom:
                            # Kung nasa kaliwa ng player at mas malapit
                            if plat.right < start_x and plat.right > end_x:
                                end_x = plat.right
                                
                    laser_rect = pygame.Rect(end_x, laser_y, max(0, start_x - end_x), laser_height)
                
                # Random limit for how many blocks the laser can break (between 3 to 9)
                break_limit = random.randint(3, 9)
                
                self.active_laser = {
                    'rect': laser_rect, 
                    'timer': 15, 
                    'dir': self.charge_direction,
                    'max_breaks': break_limit,
                    'current_breaks': 0
                }
                
                self.is_charging = False
                self.charge_timer = 0
                return True # Mag-ttrigger ng screen shake sa main
            else:
                # Na-cancel
                self.is_charging = False
                self.charge_timer = 0
        return False

    def get_player_shake(self):
        if self.is_charging:
            intensity = int((self.charge_timer / self.charge_max) * 4)
            return random.randint(-intensity, intensity), random.randint(-intensity, intensity)
        return 0, 0

    def draw_glow(self, surface, player_x, player_y, player_width, player_height):
        # 1. MAG-SPAWN NG PARTICLES HABANG NAG-CHACHARGE
        if self.is_charging:
            # Mag-spawn ng 3 particles per frame para makapal ang aura
            for _ in range(3):
                self.charge_particles.append({
                    'x': player_x + random.uniform(0, player_width), 
                    'y': player_y + player_height,                 
                    'dx': random.uniform(-1, 1),                    
                    'dy': random.uniform(-4, -1),                   
                    'lifetime': random.randint(15, 30),
                    'size': random.uniform(3, 6),
                    # Kulay Apoy / Kuryente (Orange, Yellow, Yellow-White)
                    'color': random.choice([(255, 150, 0), (255, 200, 0), (255, 255, 100)]) 
                })

        # 2. I-DRAW ANG PARTICLES NA MAY "GLOW" EFFECT
        for p in self.charge_particles:
            size = int(p['size'])
            if size > 0:
                # Faint outer glow (naka-transparent na circle sa likod)
                glow_surf = pygame.Surface((size * 4, size * 4), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (*p['color'], 80), (size * 2, size * 2), size * 2)
                surface.blit(glow_surf, (p['x'] - size * 2, p['y'] - size * 2))

                # Solid na core ng particle (sa gitna)
                pygame.draw.circle(surface, p['color'], (int(p['x']), int(p['y'])), size)

    def draw_ui(self, surface, player_x, player_y):
        center_x = player_x + 10
        center_y = player_y - 20
        radius = 7
        
        pygame.draw.circle(surface, (50, 50, 50), (center_x, center_y), radius)
        pygame.draw.circle(surface, (255, 255, 255), (center_x, center_y), radius, 1)
        
        if self.cooldown_timer <= 0:
            pygame.draw.circle(surface, (255, 200, 0), (center_x, center_y), radius - 1)
        else:
            ratio = 1 - (self.cooldown_timer / self.cooldown_max)
            current_radius = int((radius - 1) * ratio)
            if current_radius > 0:
                pygame.draw.circle(surface, (255, 200, 0), (center_x, center_y), current_radius)