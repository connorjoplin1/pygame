import pygame
import os

# Initialize Game
pygame.init()
# Screen Width and Height
SCREENH = 720
SCREENW = 720
font = pygame.font.Font("Physics/fonts/inter.ttf", 15)
font1 = pygame.font.Font("Physics/fonts/bolded.ttf", 20)
# Milliball Health Box
health = 1000000
text_surface = font.render(f"Milliball Health: {health}", True,
                           (255, 255, 255))
text_rect = text_surface.get_rect()
text_rect.topleft = (85, 60)
# Total Bounces Box
count = 0
text_surface1 = font.render(f"Total Bounces: {count}", True, (255, 255, 255))
text_rect1 = text_surface1.get_rect()
text_rect1.topright = (500, 60)
# TITLE Box
text_surface2 = font1.render("FIBBONACCI VS 1MILLION", True, (255, 255, 255))
text_rect2 = text_surface2.get_rect()
one_fourth = SCREENW / 4
text_rect2.topleft = (one_fourth + 20, 0)

screen = pygame.display.set_mode((SCREENH, SCREENW))
fiboball_img = pygame.image.load(os.path.join(
    "Physics/images/Fib.webp")).convert_alpha()
fiboball_img = pygame.transform.scale(
    fiboball_img,
    (int(fiboball_img.get_width() / 10), int(fiboball_img.get_height() / 10))
)

million_img = pygame.image.load(os.path.join(
    "Physics/images/1milli.webp")).convert_alpha()
million_img = pygame.transform.scale(
    million_img,
    (int(million_img.get_width() / 4), int(million_img.get_height() / 4))
)

million_rect = million_img.get_rect()
million_rect.center = (400, 100)
million_rect.top = 80

player_rect = fiboball_img.get_rect()
player_rect.center = (100, 100)


# Physics
velocity_y_1 = 3.0
velocity_x_1 = 3.0
velocity_x_2 = 2
velocity_y_2 = 2
SPEED_MULTIPLIER = 1.10
MAX_SPEED = 30
ground_y = SCREENH - 80
right_x = SCREENW - 80


clock = pygame.time.Clock()
running = True
million_alive = True


def fibbonaci(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


while running:
    clock.tick(60)
    screen.fill((255, 255, 255))
    box = pygame.draw.rect(screen, (0, 0, 0), screen.get_rect(), 80)
    # Fibbonaci Ball Physics
    player_rect.y += velocity_y_1
    player_rect.x += velocity_x_1
    if player_rect.left <= 80 or player_rect.right >= right_x:
        velocity_x_1 *= -1
    if player_rect.top <= 80 or player_rect.bottom >= ground_y:
        velocity_y_1 *= -1
    screen.blit(fiboball_img, player_rect)
    # 1 Million Ball Physics
    if million_alive:
        million_rect.y += velocity_y_2
        million_rect.x += velocity_x_2
        if million_rect.left <= 80 or million_rect.right >= right_x:
            velocity_x_2 *= -1
        if million_rect.top <= 80 or million_rect.bottom >= ground_y:
            velocity_y_2 *= -1
        screen.blit(million_img, million_rect)
    # Collision
    if million_alive and million_rect.colliderect(player_rect):
        overlap_x = min(player_rect.right, million_rect.right)
        - max(player_rect.left, million_rect.left)
        overlap_y = min(player_rect.bottom, million_rect.bottom)
        - max(player_rect.top, million_rect.top)
        if overlap_x < overlap_y:
            velocity_x_1 *= -1
            velocity_x_2 *= -1
            velocity_x_1 *= SPEED_MULTIPLIER
            velocity_y_1 *= SPEED_MULTIPLIER
            velocity_x_1 = max(-MAX_SPEED, min(MAX_SPEED, velocity_x_1))
            velocity_y_1 = max(-MAX_SPEED, min(MAX_SPEED, velocity_y_1))
            count += 1
            damage = fibbonaci(count)
            health -= damage
            print("count:", count, "damage:", damage, "health:", health)
            if health <= 0:
                health = 0
                million_alive = False
                velocity_y_1 = 0
                velocity_x_1 = 0
        else:
            velocity_y_1 *= -1
            velocity_y_2 *= -1
            velocity_x_1 *= SPEED_MULTIPLIER
            velocity_y_1 *= SPEED_MULTIPLIER
            velocity_x_1 = max(-MAX_SPEED, min(MAX_SPEED, velocity_x_1))
            velocity_y_1 = max(-MAX_SPEED, min(MAX_SPEED, velocity_y_1))
            count += 1
            damage = fibbonaci(count)
            health -= damage
            print("count:", count, "damage:", damage, "health:", health)
            if health <= 0:
                health = 0
                million_alive = False
                velocity_y_1 = 0
                velocity_x_1 = 0
    text_surface1 = font.render(f"Total Bounces: {count}", True,
                                (255, 255, 255))
    text_surface = font.render(f"Milliball Health: {health}", True,
                               (255, 255, 255))
    screen.blit(text_surface, text_rect)
    screen.blit(text_surface1, text_rect1)
    screen.blit(text_surface2, text_rect2)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    pygame.display.flip()
pygame.quit()
