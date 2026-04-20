#enemy.py
import pygame
import math
from particle import Particle 

class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.facing = "left"

        # -----BUHAY NG KALABAN ---
        self.max_hp = 100   # baguhin kung gaano kakunat ang kalaban
        self.hp = self.max_hp
        
        # --- FADE OUT VARIABLES ---
        self.alpha = 255
        self.is_dead = False

        self.idle_img = pygame.transform.scale(
            pygame.image.load("enemy/enemy_right.png"), (40, 40)
        )
        self.aim_img = pygame.transform.scale(
            pygame.image.load("enemy/enemy_aim.png"), (40, 40)
        )

        self.state = "idle"
        self.shoot_timer = 0
        self.bullets = []

    def update(self, player_rect, shoot_sound, dead_sound):
        # Kapag patay na ang kalaban
        if self.hp <= 0:
            if not self.is_dead:
                self.bullets.clear() # Tanggalin lahat ng bala niya sa screen
                self.is_dead = True

                if dead_sound:
                    dead_sound.play()
                
            if self.alpha > 0:
                self.alpha -= 5 # mag-fade ANG KALABAN
            return # I-stop na ang pag-aim at pag-shoot

        # KUNG BUHAY PA, tuloy ang logic ng kalaban:
        dx = player_rect.centerx - self.x
        dy = player_rect.centery - self.y

        distance = math.sqrt(dx * dx + dy * dy)

        #  FACE PLAYER (LEFT / RIGHT)
        if player_rect.centerx < self.x:
            self.facing = "left"
        else:
            self.facing = "right"

        # AIM STATE
        if distance < 200:   # pwede adjust range ng bala
            self.state = "aim"
            self.shoot_timer += 1

            # shoot every 60 frames
            if self.shoot_timer > 60:
                self.shoot_timer = 0

                if distance == 0:
                    return

                dx /= distance
                dy /= distance

                speed = 1.5

                self.bullets.append([
                    self.x,
                    self.y,
                    dx * speed,
                    dy * speed
                ])

                #bala ng kalaban sound
                if shoot_sound:
                    shoot_sound.play()
        else:
            self.state = "idle"
            self.shoot_timer = 0

    def draw(self, screen):
        if self.alpha <= 0:
            return

        img = self.aim_img if self.state == "aim" else self.idle_img

        if self.facing == "left":
            img = pygame.transform.flip(img, True, False)

        # I-apply ang transparency (fade out effect)
        img_copy = img.copy() 
        img_copy.set_alpha(self.alpha)
        
        screen.blit(img_copy, (self.x, self.y))

    def update_bullets(self, player_rect, player_hp, hit_cooldown, p_x, p_y, natamaan_fire):
        # move bullets
        for bullet in self.bullets:
            bullet[0] += bullet[2]
            bullet[1] += bullet[3]

        # check collision
        for bullet in self.bullets[:]:
            b_rect = pygame.Rect(bullet[0], bullet[1], 10, 10)

            if b_rect.colliderect(player_rect):
                if hit_cooldown <= 0:
                    print("Hit!")
                    natamaan_fire.play()

                    player_hp -= 10
                    hit_cooldown = 30

                    # knockback
                    if player_rect.centerx < bullet[0]:
                        p_x -= 20
                    else:
                        p_x += 20

                    p_y -= 10

                if bullet in self.bullets:
                    self.bullets.remove(bullet)
            elif bullet[0] < 0 or bullet[0] > 800 or bullet[1] < 0 or bullet[1] > 500:
                if bullet in self.bullets:
                    self.bullets.remove(bullet)
                    
        return player_hp, hit_cooldown, p_x, p_y

    def draw_hp_bar(self, screen):
        # I-draw lang kung buhay pa at hindi pa nagfe-fade out
        if self.hp > 0: 
            bar_width = 40
            bar_height = 1
            ratio = self.hp / self.max_hp
            
            pygame.draw.rect(screen, (255, 0, 0), (self.x, self.y - 2, bar_width, bar_height))
            pygame.draw.rect(screen, (0, 255, 0), (self.x, self.y - 2, bar_width * ratio, bar_height))



class Boss:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 40  # Sukat ng boss
        self.height = 40
        
        # ----- BUHAY NG BOSS -----
        self.max_hp = 500  
        self.hp = self.max_hp
        self.is_dead = False
        
        self.speed = 3.5  # Bibilisan natin konti para ramdam ang sugod
        self.angle = 0  

        # ---> STATE MACHINE VARIABLES <---
        self.state = "wait"  # Pwedeng "wait" o "roll"
        self.timer = 180     # Magsisimula sa 120 frames (2 seconds cooldown)

        self.image = pygame.transform.scale(
            pygame.image.load("enemy/Boss.png").convert_alpha(), (self.width, self.height)
        )

    def update(self, player_rect, particles_list):
        if self.hp <= 0:
            self.is_dead = True
            return

        boss_centerx = self.x + self.width // 2
        boss_centery = self.y + self.height // 2

        # Kapag magka-level ang Boss at Player sa Y-axis
        if abs(player_rect.centery - boss_centery) < 50:
            
            # STATE 1: WAITING / COOLDOWN (Nakahinto)
            if self.state == "wait":
                self.timer -= 1  # Bawasan ang cooldown timer
                
                # Kapag 0 na ang wait timer, oras na para sumugod!
                if self.timer <= 0:
                    self.state = "roll"
                    self.timer = 90  # Gugulong siya ng 1.5 seconds (90 frames)
            
            # STATE 2: ROLLING / CHARGING (Sumusugod)
            elif self.state == "roll":
                # Sumunod sa X position ng player
                if player_rect.centerx < boss_centerx:
                    self.x -= self.speed
                    self.angle += 12  # Mas mabilis na ikot
                elif player_rect.centerx > boss_centerx:
                    self.x += self.speed
                    self.angle -= 12  # Mas mabilis na ikot

                # Maglalabas ng particles habang gumugulong
                particles_list.append(Particle(boss_centerx, self.y + self.height))
                
                self.timer -= 1  # Bawasan ang rolling timer
                
                # Kapag tapos na siyang gumulong, babalik sa pagiging waiting
                if self.timer <= 0:
                    self.state = "wait"
                    self.timer = 180  # Balik ulit sa 2 seconds cooldown
        else:
            # KUNG UMALIS ANG PLAYER SA LINYA NIYA:
            # Titigil ang boss at babalik sa cooldown mode para ready ulit pagbalik ng player.
            self.state = "wait"
            self.timer = 120

    def draw(self, screen):
        if self.hp <= 0:
            return
            
        # I-rotate ang image
        rotated_img = pygame.transform.rotate(self.image, self.angle)
        
        # Kunin ang bagong center para hindi mag-wobble ang bilog
        new_rect = rotated_img.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
        screen.blit(rotated_img, new_rect.topleft)

    def draw_hp_bar(self, screen):
        if self.hp > 0:
            bar_width = self.width
            bar_height = 5
            ratio = self.hp / self.max_hp
            
            # Red/Green HP bar sa taas ng Boss
            pygame.draw.rect(screen, (255, 0, 0), (self.x, self.y - 15, bar_width, bar_height))
            pygame.draw.rect(screen, (0, 255, 0), (self.x, self.y - 15, bar_width * ratio, bar_height))


class Boss1:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 80  # Sukat ng boss
        self.height = 80
        
        # ----- BUHAY NG BOSS -----
        self.max_hp = 500  
        self.hp = self.max_hp
        self.is_dead = False
        
        self.speed = 3.5  # Bibilisan natin konti para ramdam ang sugod
        self.angle = 0  

        # ---> STATE MACHINE VARIABLES <---
        self.state = "wait"  # Pwedeng "wait" o "roll"
        self.timer = 180     # Magsisimula sa 120 frames (2 seconds cooldown)

        self.image = pygame.transform.scale(
            pygame.image.load("enemy/Boss.png").convert_alpha(), (self.width, self.height)
        )

    def update(self, player_rect, particles_list):
        if self.hp <= 0:
            self.is_dead = True
            return

        boss_centerx = self.x + self.width // 2
        boss_centery = self.y + self.height // 2

        # Kapag magka-level ang Boss at Player sa Y-axis
        if abs(player_rect.centery - boss_centery) < 50:
            
            # STATE 1: WAITING / COOLDOWN (Nakahinto)
            if self.state == "wait":
                self.timer -= 1  # Bawasan ang cooldown timer
                
                # Kapag 0 na ang wait timer, oras na para sumugod!
                if self.timer <= 0:
                    self.state = "roll"
                    self.timer = 90  # Gugulong siya ng 1.5 seconds (90 frames)
            
            # STATE 2: ROLLING / CHARGING (Sumusugod)
            elif self.state == "roll":
                # Sumunod sa X position ng player
                if player_rect.centerx < boss_centerx:
                    self.x -= self.speed
                    self.angle += 12  # Mas mabilis na ikot
                elif player_rect.centerx > boss_centerx:
                    self.x += self.speed
                    self.angle -= 12  # Mas mabilis na ikot

                # Maglalabas ng particles habang gumugulong
                particles_list.append(Particle(boss_centerx, self.y + self.height))
                
                self.timer -= 1  # Bawasan ang rolling timer
                
                # Kapag tapos na siyang gumulong, babalik sa pagiging waiting
                if self.timer <= 0:
                    self.state = "wait"
                    self.timer = 180  # Balik ulit sa 2 seconds cooldown
        else:
            # KUNG UMALIS ANG PLAYER SA LINYA NIYA:
            # Titigil ang boss at babalik sa cooldown mode para ready ulit pagbalik ng player.
            self.state = "wait"
            self.timer = 120

    def draw(self, screen):
        if self.hp <= 0:
            return
            
        # I-rotate ang image
        rotated_img = pygame.transform.rotate(self.image, self.angle)
        
        # Kunin ang bagong center para hindi mag-wobble ang bilog
        new_rect = rotated_img.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
        screen.blit(rotated_img, new_rect.topleft)

    def draw_hp_bar(self, screen):
        if self.hp > 0:
            bar_width = self.width
            bar_height = 5
            ratio = self.hp / self.max_hp
            
            # Red/Green HP bar sa taas ng Boss
            pygame.draw.rect(screen, (255, 0, 0), (self.x, self.y - 15, bar_width, bar_height))
            pygame.draw.rect(screen, (0, 255, 0), (self.x, self.y - 15, bar_width * ratio, bar_height))