#enemy.py
import pygame
import math

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