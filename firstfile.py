import pygame

# Initializes Game
pygame.init()

# Sets Window
screen = pygame.display.set_mode((640, 640))

# Loads Images
princess_img = pygame.image.load('princess.jpg').convert()

# Scales the 2D bit character
princess_img = pygame.transform.scale(princess_img,
                                      (princess_img.get_width() / 5,
                                       princess_img.get_height() / 5))

# Gets rid of excess imaging
princess_img.set_colorkey((0, 0, 0))

# Creates multiples
princess = pygame.Surface((64, 64), pygame.SRCALPHA)
princess.blit(princess_img, (0, 0))
princess.blit(princess_img, (20, 0))
princess.blit(princess_img, (10, 10))

running = True
x = 0
# Timing
clock = pygame.time.Clock()

delta_time = 0.1

# Renders font
font = pygame.font.Font(None, size=30)

# Running the Window
while running:
    screen.fill((255, 255, 255))

    # Fades image out: princess_img.set_alpha(max(0, 255 - x))
    screen.blit(princess_img, (x, 30))

    # Collision hitbox
    hitbox = pygame.Rect(x, 30, princess_img.get_width(), princess_img.get_height())
    mpos = pygame.mouse.get_pos()

    # Changing Colors of hitbox
    target = pygame.Rect(300, 0, 160, 280)
    collision = hitbox.colliderect(target)
    m_collision = target.collidepoint(mpos)
    pygame.draw.rect(screen, (255 * collision, 255 * m_collision, 0), target)

    x += 50 * delta_time

    # Rendering text onto the screen
    text = font.render("Hello World!", True, (0, 0, 0))
    screen.blit(text, (300, 100))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pygame.display.flip()

    delta_time = clock.tick(60) / 1000
    delta_time = max(0.001, min(0.1, delta_time))

pygame.quit()
