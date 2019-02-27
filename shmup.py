# Shmup game
# Music by tgfcoder <https://twitter.com/tgfcoder> licensed under CC-BY-3
import pygame
import random
from os import path

# Define constants
WIDTH = 480
HEIGHT = 600
FPS = 60
POWERUP_TIME = 5000

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Set up assets folders
game_folder = path.dirname(__file__)
img_folder = path.join(game_folder, "assets", "img")
snd_folder = path.join(game_folder, "assets", "snd")

# Initialize pygame with sound and create screen
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Shmup!")
clock = pygame.time.Clock()


# Define functions
def draw_text(surface, text, size, x, y):
    font_name = pygame.font.match_font("arial")
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surface.blit(text_surface, text_rect)


def draw_shield_bar(surface, x, y, percentage):
    if percentage < 0:
        percentage = 0
    bar_length = 100
    bar_height = 10
    fill = (percentage * 0.01) * bar_length
    outline_rect = pygame.Rect(x, y, bar_length, bar_height)
    fill_rect = pygame.Rect(x, y, fill, bar_height)
    pygame.draw.rect(surface, GREEN, fill_rect)
    pygame.draw.rect(surface, WHITE, outline_rect, 2)


def draw_lives(surface, x, y, lives, img):
    for i in range(lives - 1):
        img_rect = img.get_rect()
        img_rect.x = x + 30 * i
        img_rect.y = y
        surface.blit(img, img_rect)


def show_game_over_screen():
    screen.blit(background_img, background_rect)
    draw_text(screen, "SHMUP!", 64, WIDTH * 0.5, HEIGHT * 0.25)
    draw_text(screen, "Press A and D to move, Space to fire", 22, WIDTH * 0.5, HEIGHT * 0.5)
    draw_text(screen, "Press any key to begin", 18, WIDTH * 0.5, HEIGHT * 0.75)
    pygame.display.flip()
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.KEYUP:
                waiting = False

def spawn_mob():
    m = Mob()
    all_sprites.add(m)
    mobs.add(m)


# Define classes
class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(player_img, (50, 38))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.radius = 20
        # pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
        self.rect.centerx = WIDTH * 0.5
        self.rect.bottom = HEIGHT - 10
        self.speedx = 0
        self.shield = 100
        self.shoot_delay = 250
        self.last_shot = pygame.time.get_ticks()
        self.lives = 3
        self.hidden = False
        self.hide_timer = pygame.time.get_ticks()
        self.power = 1
        self.power_timer = 0

    def update(self):
        # Timeout for powerups
        if self.power == 2 and pygame.time.get_ticks() - self.power_timer >= POWERUP_TIME:
            self.power -= 1
            self.power_timer = pygame.time.get_ticks()
        # Unhide player if hidden
        if self.hidden and pygame.time.get_ticks() - self.hide_timer >= 1000:
            self.hidden = False
            self.rect.centerx = WIDTH * 0.5
            self.rect.bottom = HEIGHT - 10
        self.speedx = 0
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_a]:
            self.speedx = -5
        if keystate[pygame.K_d]:
            self.speedx = 5
        if keystate[pygame.K_SPACE]:
            self.shoot()
        self.rect.x += self.speedx
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            if self.power == 1:
                bullet = Bullet(self.rect.centerx, self.rect.top)
                all_sprites.add(bullet)
                bullets.add(bullet)
                shoot_sound.play()
            elif self.power == 2:
                bullet1 = Bullet(self.rect.left, self.rect.centery)
                bullet2 = Bullet(self.rect.right, self.rect.centery)
                all_sprites.add(bullet1)
                all_sprites.add(bullet2)
                bullets.add(bullet1)
                bullets.add(bullet2)
                shoot_sound.play()

    def hide(self):
        # Hide the player temporarily
        self.hidden = True
        self.hide_timer = pygame.time.get_ticks()
        self.rect.center = (WIDTH * 0.5, HEIGHT + 200)

    def powerup(self):
        self.power += 1
        self.power_timer = pygame.time.get_ticks()


class Mob(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_orig = random.choice(meteor_images)
        self.image_orig.set_colorkey(BLACK)
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width * 0.85 * 0.5)
        # pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-150, -100)
        self.speedy = random.randrange(1, 8)
        self.speedx = random.randrange(-3, 3)
        self.rot = 0
        self.rot_speed = random.randrange(-8, 8)
        self.last_update = pygame.time.get_ticks()

    def rotate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update >= 25:
            self.last_update = now
            self.rot = (self.rot + self.rot_speed) % 360
            new_image = pygame.transform.rotate(self.image_orig, self.rot)
            old_center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center

    def update(self):
        self.rotate()
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT + 10 or self.rect.right < -10 or self.rect.left > WIDTH + 10:
            self.rect.x = random.randrange(WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(1, 8)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -10

    def update(self):
        self.rect.y += self.speedy
        # Destroy the bullet if it moves off the top of the screen
        if self.rect.bottom < 0:
            self.kill()


class Powerup(pygame.sprite.Sprite):
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(["shield", "gun"])
        self.image = powerup_images[self.type]
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speedy = 3

    def update(self):
        self.rect.y += self.speedy
        # Destroy the bullet if it moves off the top of the screen
        if self.rect.top > HEIGHT:
            self.kill()


class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = explosion_animation[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = -1
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 60

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(explosion_animation[self.size]):
                self.kill()
            else:
                center = self.rect.center
                self.image = explosion_animation[self.size][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center


# Load all game graphics
background_img = pygame.image.load(path.join(img_folder, "background.png")).convert()
background_rect = background_img.get_rect()
player_img = pygame.image.load(path.join(img_folder, "player.png")).convert()
player_mini_img = pygame.transform.scale(player_img, (25, 19))
player_mini_img.set_colorkey(BLACK)
bullet_img = pygame.image.load(path.join(img_folder, "laser.png")).convert()
meteor_images = []
meteor_list = ["meteor_big_1.png", "meteor_big_2.png", "meteor_big_3.png", "meteor_big_4.png", "meteor_med_1.png",
               "meteor_med_1.png", "meteor_small_1.png", "meteor_small_1.png", "meteor_tiny_1.png", "meteor_tiny_1.png"]
for img in meteor_list:
    meteor_images.append(pygame.image.load(path.join(img_folder, img)).convert())
explosion_animation = {"large": [], "small": [], "player": []}
for i in range(9):
    filename = "regularExplosion0{}.png".format(i)
    img = pygame.image.load(path.join(img_folder, filename)).convert()
    img.set_colorkey(BLACK)
    img_large = pygame.transform.scale(img, (75, 75))
    img_small = pygame.transform.scale(img, (32, 32))
    explosion_animation["large"].append(img_large)
    explosion_animation["small"].append(img_small)
    filename = "sonicExplosion0{}.png".format(i)
    img = pygame.image.load(path.join(img_folder, filename)).convert()
    img.set_colorkey(BLACK)
    img = pygame.transform.scale(img, (75, 75))
    explosion_animation["player"].append(img)
powerup_images = {}
powerup_images["shield"] = pygame.image.load(path.join(img_folder, "shield_gold.png")).convert()
powerup_images["gun"] = pygame.image.load(path.join(img_folder, "bolt_gold.png")).convert()

# Load all game sounds
shoot_sound = pygame.mixer.Sound(path.join(snd_folder, "laser.wav"))
shield_sound = pygame.mixer.Sound(path.join(snd_folder, "shield.wav"))
power_sound = pygame.mixer.Sound(path.join(snd_folder, "power.wav"))
explosion_sounds = []
for snd in ["explosion2.wav", "explosion3.wav"]:
    explosion_sounds.append(pygame.mixer.Sound(path.join(snd_folder, snd)))
player_die_sound = pygame.mixer.Sound(path.join(snd_folder, "rumble1.ogg"))
pygame.mixer.music.load(path.join(snd_folder, "music.ogg"))
pygame.mixer.music.set_volume(0.4)

# Start playing music
pygame.mixer.music.play(loops=1)

# Game loop
game_over = True
running = True
while running:
    if game_over:
        show_game_over_screen()
        game_over = False
        # Initialize sprite groups
        all_sprites = pygame.sprite.Group()
        mobs = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        powerups = pygame.sprite.Group()
        player = Player()
        all_sprites.add(player)
        for i in range(8):
            spawn_mob()
        # Initialize score
        score = 0

    # Keep loop running at the right speed
    clock.tick(FPS)

    # Process input (events)
    for event in pygame.event.get():
        # Check for closing the window
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_SPACE:
                player.shoot()

    # Update sprites (calculate stuff)
    all_sprites.update()

    # Check to see if a bullet hit a mob and respawn any dead mobs
    hits = pygame.sprite.groupcollide(mobs, bullets, True, True)
    for hit in hits:
        score += 52 - hit.radius
        random.choice(explosion_sounds).play()
        explosion = Explosion(hit.rect.center, "large")
        all_sprites.add(explosion)
        if random.random() > 0.9:
            powerup = Powerup(hit.rect.center)
            all_sprites.add(powerup)
            powerups.add(powerup)
        spawn_mob()

    # Check to see if a mob hit the player and damage the player shield if hit
    hits = pygame.sprite.spritecollide(player, mobs, True, pygame.sprite.collide_circle)
    for hit in hits:
        player.shield -= hit.radius
        explosion = Explosion(hit.rect.center, "small")
        all_sprites.add(explosion)
        spawn_mob()
        if player.shield <= 0:
            player_die_sound.play()
            death_explosion = Explosion(player.rect.center, "player")
            all_sprites.add(death_explosion)
            player.hide()
            player.lives -= 1
            if player.lives > 0:
                player.shield = 100

    # Check to see if player hit a powerup
    hits = pygame.sprite.spritecollide(player, powerups, True)
    for hit in hits:
        if hit.type == "shield":
            player.shield += 50  # random.randrange(10, 30)
            shield_sound.play()
            if player.shield > 100:
                player.shield = 100
        if hit.type == "gun":
            power_sound.play()
            if player.power == 1:
                player.powerup()
            elif player.power == 2:
                player.power_timer = pygame.time.get_ticks()

    # If the player died and the explosion has finished playing
    if player.lives == 0 and not death_explosion.alive():
        game_over = True

    # Draw / render
    screen.blit(background_img, background_rect)
    all_sprites.draw(screen)
    draw_text(screen, "Score: " + str(score), 20, WIDTH * 0.5, 10)
    draw_shield_bar(screen, 5, 5, player.shield)
    draw_lives(screen, WIDTH - 100, 5, player.lives, player_mini_img)

    # After drawing everything, flip the display
    pygame.display.flip()

pygame.quit()
