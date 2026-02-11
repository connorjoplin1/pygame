import pygame
import random
import math
import os
import sys

pygame.init()
pygame.font.init()

# ----------------------------
# SETTINGS
# ----------------------------


def resource_path(rel_path: str) -> str:
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, rel_path)
W, H = 640, 640
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Princess vs Heart Boss")
clock = pygame.time.Clock()

# Text / UI
font = pygame.font.Font(None, 28)
big_font = pygame.font.Font(None, 44)
small_font = pygame.font.Font(None, 18)

TEXTBOX_PADDING = 10
TEXTBOX_BG = (245, 245, 245)
TEXTBOX_BORDER = (20, 20, 20)
TEXTBOX_TEXT = (10, 10, 10)

# Field dialogue distances
interaction_radius = 300
interaction_radius2 = 110
tengen_message = "Hey! Come closer to talk. Flashy!"
tengen_message2 = "You have to kill THE HEART to win!"

# Player movement
PLAYER_SPEED = 190

# Player shooting (press E)
PLAYER_BULLET_SPEED = 460
PLAYER_SHOT_COOLDOWN = 0.18
PLAYER_BULLET_SIZE = 8

# Boss: heart speed
HEART_SPEED_MULT = 1.8

# Boss: heart attacks (enemy bullets)
ENEMY_PROJECTILE_SPEED = 260
SHOT_INTERVAL_BASE = 1.1
PLAYER_IFRAMES = 0.9

# Volcano hazards
VOLCANO_RADIUS = 50
VOLCANO_DAMAGE = 1

# Background palettes
FIELD_BG = (0, 195, 0)
BOSS_BG = (90, 20, 20)        # scary dark red
BOSS_GLOW = (255, 90, 40)     # orange accent
DIALOG_BG = (0, 0, 0)         # pure black

# Boss UI health bar
BOSS_MAX_HP = 3
BAR_W = 420
BAR_H = 18
BAR_Y = 12

# ----------------------------
# LOAD + SCALE IMAGES
# ----------------------------
princess_img = pygame.image.load(resource_path(os.path.join("firstgame", "princess.png"))).convert_alpha()
tengen_img = pygame.image.load(resource_path(os.path.join("firstgame", "tengen.png"))).convert_alpha()
heart_img = pygame.image.load(resource_path(os.path.join("firstgame", "heart.png"))).convert_alpha()
volcano_img = pygame.image.load(resource_path(os.path.join("firstgame", "volcano.png"))).convert_alpha()

princess_img = pygame.transform.scale(
    princess_img,
    (int(princess_img.get_width() / 8), int(princess_img.get_height() / 8))
)
tengen_img = pygame.transform.scale(
    tengen_img,
    (int(tengen_img.get_width() / 20), int(tengen_img.get_height() / 20))
)
heart_img = pygame.transform.scale(
    heart_img,
    (int(heart_img.get_width() / 10), int(heart_img.get_height() / 10))
)
volcano_img = pygame.transform.scale(
    volcano_img,
    (int(volcano_img.get_width() / 10), int(volcano_img.get_height() / 10))
)

princess_rect = princess_img.get_rect(topleft=(20, 30))
tengen_rect = tengen_img.get_rect(topright=(550, 250))

# ----------------------------
# GRASS SETUP (field only)
# ----------------------------
STEP = 10
BASE_COLOR = (0, 156, 0)
THICKNESS = 2
WIND_AMPLITUDE = 2.0
WIND_SPEED = 1.6

grass_blades = []
for x in range(0, W, STEP):
    for y in range(0, H, STEP):
        base_x = x + random.randint(-3, 3)
        base_y = y
        height = random.randint(14, 26)
        phase = random.random() * math.tau
        amp = WIND_AMPLITUDE * (0.6 + 0.8 * random.random())
        grass_blades.append((base_x, base_y, height, phase, amp))
wind_t = 0.0

# ----------------------------
# HELPERS
# ----------------------------
def draw_textbox(anchor_rect, message):
    text_surf = font.render(message, True, TEXTBOX_TEXT)
    box_w = text_surf.get_width() + TEXTBOX_PADDING * 2
    box_h = text_surf.get_height() + TEXTBOX_PADDING * 2

    r = pygame.Rect(
        anchor_rect.centerx - box_w // 2,
        anchor_rect.top - box_h - 10,
        box_w,
        box_h
    )
    r.clamp_ip(screen.get_rect())

    pygame.draw.rect(screen, TEXTBOX_BG, r)
    pygame.draw.rect(screen, TEXTBOX_BORDER, r, 2)
    screen.blit(text_surf, (r.x + TEXTBOX_PADDING, r.y + TEXTBOX_PADDING))


def spawn_hearts(count, difficulty_level):
    hearts = []
    for _ in range(count):
        r = heart_img.get_rect()
        r.center = (random.randint(140, W - 140), random.randint(140, H - 140))

        speed = (70 + 25 * difficulty_level) * HEART_SPEED_MULT
        angle = random.random() * math.tau
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed

        hp = 3
        hearts.append({"rect": r, "vx": vx, "vy": vy, "hp": hp})
    return hearts


def spawn_player_bullet(start_pos, direction):
    dx, dy = direction
    length = math.hypot(dx, dy)
    if length == 0:
        dx, dy = 1, 0
        length = 1
    dx /= length
    dy /= length

    rect = pygame.Rect(0, 0, PLAYER_BULLET_SIZE, PLAYER_BULLET_SIZE)
    rect.center = start_pos
    return {"rect": rect, "vx": dx * PLAYER_BULLET_SPEED, "vy": dy * PLAYER_BULLET_SPEED}


def spawn_enemy_bullet(from_pos, to_pos, speed):
    fx, fy = from_pos
    tx, ty = to_pos
    dx = tx - fx
    dy = ty - fy
    d = math.hypot(dx, dy)
    if d == 0:
        d = 1.0
    vx = dx / d * speed
    vy = dy / d * speed

    rect = pygame.Rect(0, 0, 10, 10)
    rect.center = (fx, fy)
    return {"rect": rect, "vx": vx, "vy": vy}


def bar_color(frac):
    # frac: 1.0 full -> green, 0.0 empty -> red, middle -> yellow
    frac = max(0.0, min(1.0, frac))
    if frac >= 0.5:
        t = (1.0 - frac) / 0.5  # 0->1 as goes 1.0->0.5
        r = int(0 + (255 - 0) * t)
        g = 255
        b = 0
    else:
        t = frac / 0.5  # 0->1 as goes 0.0->0.5
        r = 255
        g = int(0 + (255 - 0) * t)
        b = 0
    return (r, g, b)


def draw_boss_bar():
    # title
    title = big_font.render("THE HEART", True, (255, 240, 240))
    screen.blit(title, title.get_rect(midtop=(W // 2, 6)))

    # bar background + border
    x = (W - BAR_W) // 2
    bg = pygame.Rect(x, BAR_Y + 48, BAR_W, BAR_H)
    pygame.draw.rect(screen, (20, 10, 10), bg)
    pygame.draw.rect(screen, (255, 240, 240), bg, 2)

    # fill
    frac = boss_hp / BOSS_MAX_HP if BOSS_MAX_HP > 0 else 0.0
    fill_w = int(BAR_W * max(0.0, min(1.0, frac)))
    fill = pygame.Rect(x, BAR_Y + 48, fill_w, BAR_H)
    pygame.draw.rect(screen, bar_color(frac), fill)

    # small HP text
    hp_txt = small_font.render(f"{max(0, boss_hp)} / {BOSS_MAX_HP}", True, (255, 240, 240))
    screen.blit(hp_txt, hp_txt.get_rect(midtop=(W // 2, BAR_Y + 68)))


def enter_boss():
    global state, hearts, difficulty_level
    global player_projectiles, player_shot_timer, last_dir
    global enemy_projectiles, shot_timer
    global player_hp, player_iframe
    global volcanoes
    global boss_hp

    state = "BOSS"
    princess_rect.center = (W - 80, H // 2)

    difficulty_level = 1
    hearts = spawn_hearts(1, difficulty_level)

    player_projectiles = []
    player_shot_timer = 0.0
    last_dir = (1, 0)

    enemy_projectiles = []
    shot_timer = 0.0

    player_hp = 3
    player_iframe = 0.0

    volcanoes = [
        {"pos": (170, 470), "radius": VOLCANO_RADIUS},
        {"pos": (470, 170), "radius": VOLCANO_RADIUS},
    ]

    boss_hp = BOSS_MAX_HP


def make_dialog():
    global state, dialog_text, yes_rect, no_rect
    state = "DIALOG"
    dialog_text = "Will you be my valentine?"
    yes_rect = pygame.Rect(0, 0, 160, 56)
    no_rect = pygame.Rect(0, 0, 160, 56)
    yes_rect.center = (W // 2 - 100, H // 2 + 70)
    no_rect.center = (W // 2 + 100, H // 2 + 70)


def draw_dialog():
    overlay = pygame.Surface((W, H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    screen.blit(overlay, (0, 0))

    box = pygame.Rect(0, 0, 520, 240)
    box.center = (W // 2, H // 2)

    pygame.draw.rect(screen, (30, 30, 30), box)
    pygame.draw.rect(screen, (220, 220, 220), box, 2)

    title = big_font.render(dialog_text, True, (230, 230, 230))
    screen.blit(title, title.get_rect(center=(W // 2, H // 2 - 40)))

    pygame.draw.rect(screen, (50, 50, 50), yes_rect)
    pygame.draw.rect(screen, (220, 220, 220), yes_rect, 2)
    pygame.draw.rect(screen, (50, 50, 50), no_rect)
    pygame.draw.rect(screen, (220, 220, 220), no_rect, 2)

    y = font.render("YES", True, (230, 230, 230))
    n = font.render("NO", True, (230, 230, 230))
    screen.blit(y, y.get_rect(center=yes_rect.center))
    screen.blit(n, n.get_rect(center=no_rect.center))


def draw_boss_ui():
    top = font.render(f"HP: {player_hp}", True, (255, 240, 240))
    hint = small_font.render("Shoot: E    Move: WASD    Avoid volcano zones", True, (255, 240, 240))
    screen.blit(top, (12, 12))
    screen.blit(hint, (12, 36))


# ----------------------------
# GAME STATE
# ----------------------------
state = "FIELD"
running = True

hearts = []
difficulty_level = 1

player_projectiles = []
player_shot_timer = 0.0
last_dir = (1, 0)

enemy_projectiles = []
shot_timer = 0.0

player_hp = 3
player_iframe = 0.0

volcanoes = []

boss_hp = BOSS_MAX_HP

dialog_text = ""
yes_rect = pygame.Rect(0, 0, 160, 56)
no_rect = pygame.Rect(0, 0, 160, 56)

# ----------------------------
# MAIN LOOP
# ----------------------------
while running:
    dt = clock.tick(60) / 1000.0
    wind_t += dt

    shoot_pressed = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_e:
                shoot_pressed = True

        if state == "DIALOG" and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            if yes_rect.collidepoint(mx, my):
                state = "WIN"
            elif no_rect.collidepoint(mx, my):
                state = "BOSS"
                difficulty_level += 1
                hearts = spawn_hearts(2 ** difficulty_level, difficulty_level)

                enemy_projectiles = []
                shot_timer = 0.0
                player_projectiles = []
                player_shot_timer = 0.0

                boss_hp = BOSS_MAX_HP + 6 * (difficulty_level - 1)

    # movement
    keys = pygame.key.get_pressed()
    move_x = 0
    move_y = 0

    if state in ("FIELD", "BOSS"):
        if keys[pygame.K_d]:
            move_x += 1
        if keys[pygame.K_a]:
            move_x -= 1
        if keys[pygame.K_s]:
            move_y += 1
        if keys[pygame.K_w]:
            move_y -= 1

        if move_x != 0 or move_y != 0:
            last_dir = (move_x, move_y)

        princess_rect.x += move_x * PLAYER_SPEED * dt
        princess_rect.y += move_y * PLAYER_SPEED * dt

    # state logic
    if state == "FIELD":
        if princess_rect.right > W:
            princess_rect.right = W
        if princess_rect.top < 0:
            princess_rect.top = 0
        if princess_rect.bottom > H:
            princess_rect.bottom = H

        if princess_rect.right < 0:
            enter_boss()

    elif state == "BOSS":
        princess_rect.clamp_ip(screen.get_rect())

        player_shot_timer = max(0.0, player_shot_timer - dt)
        player_iframe = max(0.0, player_iframe - dt)

        # hearts move + bounce
        for h in hearts:
            h["rect"].x += h["vx"] * dt
            h["rect"].y += h["vy"] * dt

            if h["rect"].left < 0:
                h["rect"].left = 0
                h["vx"] *= -1
            if h["rect"].right > W:
                h["rect"].right = W
                h["vx"] *= -1
            if h["rect"].top < 0:
                h["rect"].top = 0
                h["vy"] *= -1
            if h["rect"].bottom > H:
                h["rect"].bottom = H
                h["vy"] *= -1

        # volcano damage zone (50 px radius)
        if player_iframe == 0.0:
            for v in volcanoes:
                if math.hypot(princess_rect.centerx - v["pos"][0], princess_rect.centery - v["pos"][1]) <= v["radius"]:
                    player_hp -= VOLCANO_DAMAGE
                    player_iframe = PLAYER_IFRAMES
                    break

        if player_hp <= 0:
            state = "LOSE"

        # player shooting
        if shoot_pressed and player_shot_timer == 0.0:
            player_projectiles.append(spawn_player_bullet(princess_rect.center, last_dir))
            player_shot_timer = PLAYER_SHOT_COOLDOWN

        # move player bullets
        for b in player_projectiles:
            b["rect"].x += b["vx"] * dt
            b["rect"].y += b["vy"] * dt

        player_projectiles = [
            b for b in player_projectiles
            if -30 <= b["rect"].x <= W + 30 and -30 <= b["rect"].y <= H + 30
        ]

        # bullet hits hearts + reduces boss hp
        bullets_to_remove = []
        for b in player_projectiles:
            for h in hearts:
                if b["rect"].colliderect(h["rect"]):
                    h["hp"] -= 1
                    boss_hp -= 1
                    bullets_to_remove.append(b)
                    break

        if bullets_to_remove:
            player_projectiles = [b for b in player_projectiles if b not in bullets_to_remove]
        hearts = [h for h in hearts if h["hp"] > 0]

        # enemy shooting
        shot_timer += dt
        shot_interval = max(0.22, SHOT_INTERVAL_BASE - 0.12 * (difficulty_level - 1))

        if shot_timer >= shot_interval and len(hearts) > 0:
            shot_timer = 0.0
            shooter = random.choice(hearts)
            speed_scale = 1.0 + 0.18 * (difficulty_level - 1)
            enemy_projectiles.append(
                spawn_enemy_bullet(shooter["rect"].center, princess_rect.center, ENEMY_PROJECTILE_SPEED * speed_scale)
            )

        for p in enemy_projectiles:
            p["rect"].x += p["vx"] * dt
            p["rect"].y += p["vy"] * dt

        enemy_projectiles = [
            p for p in enemy_projectiles
            if -30 <= p["rect"].x <= W + 30 and -30 <= p["rect"].y <= H + 30
        ]

        if player_iframe == 0.0:
            hit_bullet = None
            for p in enemy_projectiles:
                if princess_rect.colliderect(p["rect"]):
                    hit_bullet = p
                    break
            if hit_bullet is not None:
                enemy_projectiles.remove(hit_bullet)
                player_hp -= 1
                player_iframe = PLAYER_IFRAMES

        if player_hp <= 0:
            state = "LOSE"

        # if boss hp depleted -> dialog
        if boss_hp <= 0 and state == "BOSS":
            make_dialog()

    # ----------------------------
    # DRAW
    # ----------------------------
    if state == "FIELD":
        screen.fill(FIELD_BG)

        for base_x, base_y, height, phase, amp in grass_blades:
            sway = math.sin(wind_t * WIND_SPEED + phase) * amp
            blade_x = int(base_x + sway)
            pygame.draw.line(screen, BASE_COLOR, (blade_x, base_y), (blade_x, base_y - height), THICKNESS)

        screen.blit(princess_img, princess_rect)
        screen.blit(tengen_img, tengen_rect)

        d = math.hypot(princess_rect.centerx - tengen_rect.centerx, princess_rect.centery - tengen_rect.centery)
        if d <= interaction_radius:
            draw_textbox(tengen_rect, tengen_message)
        if d <= interaction_radius2:
            draw_textbox(tengen_rect, tengen_message2)

        hint = small_font.render("Walk LEFT off-screen to enter boss.", True, (0, 0, 0))
        screen.blit(hint, (12, H - 24))

    elif state == "BOSS":
        screen.fill(BOSS_BG)

        # boss bar + title
        draw_boss_bar()

        for v in volcanoes:
            img_rect = volcano_img.get_rect(center=v["pos"])
            screen.blit(volcano_img, img_rect)
            pygame.draw.circle(screen, BOSS_GLOW, v["pos"], v["radius"], 2)

        if player_iframe > 0.0:
            if int(pygame.time.get_ticks() / 80) % 2 == 0:
                screen.blit(princess_img, princess_rect)
        else:
            screen.blit(princess_img, princess_rect)

        for h in hearts:
            screen.blit(heart_img, h["rect"])

        for b in player_projectiles:
            pygame.draw.rect(screen, (255, 230, 120), b["rect"])

        for p in enemy_projectiles:
            pygame.draw.ellipse(screen, BOSS_GLOW, p["rect"])

        draw_boss_ui()

    elif state == "DIALOG":
        screen.fill(DIALOG_BG)
        draw_dialog()

    elif state == "WIN":
        screen.fill((10, 10, 10))
        win1 = big_font.render("YOU WIN!", True, (255, 255, 255))
        win2 = font.render("You said YES. THANK YOU BABY.", True, (255, 255, 255))
        win3 = font.render("You have more coming your way soon ;)", True, (255, 255, 255))
        win4 = small_font.render("Tengen: Congrats! Flashy.", True, (255, 255, 255))
        screen.blit(win1, win1.get_rect(center=(W // 2, H // 2 - 30)))
        screen.blit(win2, win2.get_rect(center=(W // 2, H // 2 + 20)))
        screen.blit(win3, win3.get_rect(center=(W // 2, H // 2 + 55)))
        screen.blit(win4, win4.get_rect(center=(W // 2, H // 2 + 85)))

    elif state == "LOSE":
        screen.fill((10, 0, 0))
        lose1 = big_font.render("YOU LOSE!", True, (255, 255, 255))
        lose2 = font.render("You got overwhelmed.", True, (255, 255, 255))
        lose3 = small_font.render("Press ESC to quit.", True, (255, 255, 255))
        screen.blit(lose1, lose1.get_rect(center=(W // 2, H // 2 - 30)))
        screen.blit(lose2, lose2.get_rect(center=(W // 2, H // 2 + 10)))
        screen.blit(lose3, lose3.get_rect(center=(W // 2, H // 2 + 40)))

    pygame.display.flip()

pygame.quit()
