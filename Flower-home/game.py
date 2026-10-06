"""Flower Home: a Pygame kitchen adventure. Run with python game.py."""
import math
import random
import pygame

WIDTH, HEIGHT = 1000, 720
# Stronger gravity and jump impulse keep the height but shorten airtime.
GRAVITY = 2700
SPEED = 360
JUMP = -875
ATTACK_INTERVAL = 1.1
SLIME_SPEED = 285
RESPAWN_DELAY = 7.0
# x, y, width: successive shelves lead to the refrigerator.
PLATFORMS = [(0, 665, 1000), (95, 555, 155), (315, 455, 145),
             (100, 345, 150), (345, 245, 160), (620, 155, 270)]

def monster_message():
    return "OUCH!"




def family_help():
    """Return what the trapped family calls out."""
    return "HELP!"


class World:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x, self.y = 65.0, 640.0
        self.vy = 0
        self.grounded = True
        self.facing = 1
        self.state = 'playing'
        self.elapsed = 0.0
        self.ammo = 0
        self.health = 3
        self.monster_hp = 6
        self.invincible = 0
        self.cooldown = 0
        self.eyes = [[170, 526, 0], [385, 426, 0], [170, 316, 0], [415, 216, 0]]
        self.shots = []
        self.slime = []
        self.attack_timer = ATTACK_INTERVAL
        self.respawn_timer = 0.0
        self.hurt_timer = 0.0
        self.particles = []
        self.eaten_timer = 0.0

    def throw_eye(self):
        """Spend one collected eye and aim it toward the monster."""
        if self.state != 'playing' or not self.ammo or self.cooldown > 0 or self.monster_hp <= 0:
            return
        dx, dy = 545 - self.x, 390 - self.y
        distance = max(1, math.hypot(dx, dy))
        self.shots.append([self.x, self.y, dx/distance*610, dy/distance*610])
        self.ammo -= 1
        self.cooldown = .3

    def explode(self):
        """Burst into red droplets and stylized monster organs."""
        for i in range(100):
            angle = random.uniform(0, math.tau)
            speed = random.uniform(130, 650)
            self.particles.append([545., 430., math.cos(angle)*speed,
                                   math.sin(angle)*speed-150, random.randint(3, 9),
                                   'blood' if i < 92 else ('heart' if i % 2 else 'gut')])

    def update_battle(self, dt):
        """Collect eyes, move projectiles, and resolve monster hits."""
        if self.state != 'playing':
            return
        self.hurt_timer = max(0, self.hurt_timer-dt)
        self.cooldown = max(0, self.cooldown-dt)
        self.invincible = max(0, self.invincible-dt)
        if self.monster_hp <= 0 and self.respawn_timer > 0:
            self.respawn_timer = max(0, self.respawn_timer-dt)
            if self.respawn_timer == 0:
                self.monster_hp = 6
                self.state = 'eaten'
                self.health = 0
                self.eaten_timer = 0.0
                self.slime.clear()
                return
        for eye in self.eyes:
            eye[2] = max(0, eye[2]-dt)
            if eye[2] == 0 and math.hypot(self.x-eye[0], self.y-eye[1]) < 36:
                self.ammo += 1
                eye[2] = 3
        for shot in self.shots[:]:
            shot[0] += shot[2]*dt
            shot[1] += shot[3]*dt
            if math.hypot(shot[0]-545, shot[1]-390) < 60 and self.monster_hp > 0:
                self.monster_hp -= 1
                self.hurt_timer = .65
                self.shots.remove(shot)
                if self.monster_hp == 0:
                    self.respawn_timer = RESPAWN_DELAY
                    self.explode()
            elif not (-30 < shot[0] < 1030 and -30 < shot[1] < 750):
                self.shots.remove(shot)
        if self.monster_hp <= 0:
            self.slime.clear()
        else:
            self.attack_timer -= dt
            if self.attack_timer <= 0:
                dx, dy = self.x-545, self.y-390
                distance = max(1, math.hypot(dx, dy))
                self.slime.append([545, 390, dx/distance*SLIME_SPEED, dy/distance*SLIME_SPEED])
                self.attack_timer = ATTACK_INTERVAL
        for blob in self.slime[:]:
            blob[0] += blob[2]*dt
            blob[1] += blob[3]*dt
            if math.hypot(blob[0]-self.x, blob[1]-self.y) < 25 and not self.invincible:
                self.health -= 1
                self.invincible = 1.5
                self.slime.remove(blob)
                if self.health <= 0:
                    self.state = 'lost'
            elif not (-40 < blob[0] < 1040 and -40 < blob[1] < 760):
                self.slime.remove(blob)
        if self.state == 'playing' and self.x > 748 and self.y <= 130 and self.grounded and self.monster_hp <= 0:
            self.state = 'won'

    def jump(self):
        if self.grounded and self.state == 'playing':
            self.vy = JUMP
            self.grounded = False

    def update(self, dt, direction):
        if self.state == 'eaten':
            self.eaten_timer += dt
        if self.state != 'playing':
            return
        for particle in self.particles:
            if particle[1] < 657:
                particle[3] += 900*dt
                particle[0] = max(8, min(WIDTH-8, particle[0]+particle[2]*dt))
                particle[1] = min(657, particle[1]+particle[3]*dt)
        self.elapsed += dt
        if direction:
            self.facing = direction
        self.x = max(18, min(WIDTH - 18, self.x + direction * SPEED * dt))
        old_bottom = self.y + 25
        self.vy += GRAVITY * dt
        self.y += self.vy * dt
        self.grounded = False
        for px, py, pw in PLATFORMS:
            if self.vy >= 0 and old_bottom <= py <= self.y + 25 and px - 10 < self.x < px + pw + 10:
                self.y, self.vy, self.grounded = py - 25, 0, True
                break
        # The monster seals off the vase, even if you jump over the gate.
        if self.monster_hp > 0 and self.y < 170 and self.x > 714:
            self.x = 714
        self.update_battle(dt)


# All artwork is drawn here, so the game has no missing image-file dependencies.
def text(screen, message, x, y, size=22, color="#393447", center=False):
    font = pygame.font.Font(None, size)
    for line_number, line in enumerate(message.split("\n")):
        image = font.render(line, True, color)
        rect = image.get_rect(topleft=(x, y + line_number * size))
        if center:
            rect.midtop = (x, y + line_number * size)
        screen.blit(image, rect)


def draw_flower(screen, x, y, color="#ed8cad", scale=1):
    """Draw petals, a smiling face, stem and leaves using basic shapes."""
    pygame.draw.line(screen, "#4f785c", (x, y), (x, y+24*scale), max(1, int(5*scale)))
    for dx, dy in [(-12, 12), (3, 7)]:
        pygame.draw.ellipse(screen, "#77a379", (x+dx*scale, y+dy*scale, 12*scale, 8*scale))
    for i in range(7):
        angle = i * math.tau / 7
        pygame.draw.circle(screen, color,
                           (x+math.cos(angle)*15*scale, y+math.sin(angle)*15*scale), 10*scale)
    pygame.draw.circle(screen, "#ffe5a0", (x, y), 12*scale)
    for dx in (-5, 5):
        pygame.draw.circle(screen, "#343345", (x+dx*scale, y-2*scale), max(1, 2*scale))
    pygame.draw.arc(screen, "#343345", (x-5*scale, y-1*scale, 10*scale, 8*scale),
                    math.pi, math.tau, 2)


def draw_eye(screen, x, y):
    pygame.draw.ellipse(screen, "#706179", (x-12, y-10, 24, 20))
    pygame.draw.ellipse(screen, "#fffdf1", (x-10, y-8, 20, 16))
    pygame.draw.ellipse(screen, "#77a6a1", (x-4, y-6, 9, 12))
    pygame.draw.ellipse(screen, "#343345", (x-1, y-4, 4, 8))


def handle_input(world):
    """Read key presses. Return whether to keep playing and a move direction."""
    running = True
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_r and world.state != 'playing':
                world.reset()
            elif event.key in (pygame.K_SPACE, pygame.K_w, pygame.K_UP):
                world.jump()
            elif event.key in (pygame.K_e, pygame.K_j):
                world.throw_eye()
    keys = pygame.key.get_pressed()
    direction = int(keys[pygame.K_d] or keys[pygame.K_RIGHT]) - int(keys[pygame.K_a] or keys[pygame.K_LEFT])
    return running, direction


def draw(screen, world):
    """Redraw the kitchen, characters, projectiles, counters and outcome."""
    w = world
    screen.fill("#f5eddf")
    for x in range(0, WIDTH, 50):
        pygame.draw.line(screen, "#e9dfd1", (x, 110), (x, 665))
    for y in range(115, 665, 50):
        pygame.draw.line(screen, "#e9dfd1", (0, y), (WIDTH, y))
    pygame.draw.rect(screen, "#476d66", (620, 155, 270, 510), border_radius=12)
    pygame.draw.rect(screen, "#9ebbb3", (624, 159, 262, 506), border_radius=10)
    pygame.draw.line(screen, "#476d66", (625, 305), (885, 305), 3)
    for y in (195, 355):
        pygame.draw.rect(screen, "#f5eddf", (643, y, 8, 65), border_radius=4)
    pygame.draw.rect(screen, "#fff2bb", (727, 347, 80, 81))
    text(screen, "HOME", 767, 375, 23, "#476d66", True)
    for px, py, pw in PLATFORMS:
        pygame.draw.rect(screen, "#886b60", (px, py, pw, 12))
        pygame.draw.rect(screen, "#ba9580", (px, py, pw, 3))
    pygame.draw.rect(screen, "#453f50", (0, 677, WIDTH, 43))
    for x, color in [(760, "#cbb4e5"), (804, "#ee9c78"), (835, "#ed8cad")]:
        draw_flower(screen, x, 101, color, .8)
    pygame.draw.polygon(screen, "#536d93", [(747,115), (850,115), (834,155), (763,155)])
    pygame.draw.line(screen, "#7993b4", (751,120), (846,120), 4)
    text(screen, "FLOWER HOME", 26, 18, 36)
    text(screen, "Collect eyes. Defeat the monster. Reach your family's vase.", 27, 58, 21, "#736774")
    text(screen, f"PETALS  {w.health}/3     EYES  {w.ammo}", 712, 22, 26, "#8a4868")
    text(screen, "Eyes grow back every 3 seconds", 712, 58, 19, "#736774")
    text(screen, "A / D or arrows: move     SPACE: jump     E: throw (auto-aim)     ESC: quit",
         500, 691, 21, "#fff2dd", True)
    if w.monster_hp > 0:
        pygame.draw.line(screen, "#98638d", (736, 78), (736, 155), 6)
        for gate_y in range(80, 155, 14):
            pygame.draw.line(screen, "#98638d", (729, gate_y), (744, gate_y+9), 3)
    if w.state == 'playing':
        text(screen, family_help(), 805, 78, 20, "#ae4b53", True)
    for px, py, vx, vy, radius, kind in w.particles:
        if kind == 'blood':
            pygame.draw.circle(screen, "#a52b45", (px, py), radius)
        elif kind == 'heart':
            pygame.draw.circle(screen, "#d64b6e", (px-5, py-4), 8)
            pygame.draw.circle(screen, "#d64b6e", (px+5, py-4), 8)
            pygame.draw.polygon(screen, "#d64b6e", [(px-13,py-2),(px+13,py-2),(px,py+16)])
        else:
            points = [(px+i*5-15, py+math.sin(i*2)*7) for i in range(7)]
            pygame.draw.lines(screen, "#f18f9f", False, points, 8)
    if w.monster_hp > 0:
        pulse = math.sin(w.elapsed*3)*5
        for tx in (490, 530, 570):
            pygame.draw.lines(screen, "#5c4968", False, [(545,515), (tx,600), (tx-20,632)], 18)
        pygame.draw.ellipse(screen, "#3e354b", (475,310+pulse,135,265-pulse))
        pygame.draw.ellipse(screen, "#5c4968", (479,314+pulse,127,257-pulse))
        pygame.draw.ellipse(screen, "#f9efdb", (506,346+pulse,71,71))
        pygame.draw.ellipse(screen, "#b6c982", (530,365+pulse,26,36))
        pygame.draw.ellipse(screen, "#302e41", (540,370+pulse,10,25))
        pygame.draw.arc(screen, "#e4b9b5", (514,426,60,35), 0, math.pi, 4)
        pygame.draw.rect(screen, "#ded1d2", (484,285,114,10))
        pygame.draw.rect(screen, "#98638d", (484,285,114*w.monster_hp/6,10))
        text(screen, "THE FRIDGE FIEND", 540, 263, 19, "#514359", True)
        if w.attack_timer < .6:
            text(screen, "! DODGE !", 552, 237, 22, "#ae4b53", True)
    if w.hurt_timer > 0:
        message_function = globals().get('monster_message')
        message = message_function() if message_function else "OUCH!"
        pygame.draw.rect(screen, "#fff8e9", (568, 306, 92, 33), border_radius=9)
        text(screen, message, 614, 311, 25, "#ae4b53", True)
    if w.monster_hp <= 0:
        text(screen, f"RETURNS IN {math.ceil(w.respawn_timer)}s\nHurry home!", 530, 380, 24, "#ae4b53", True)
        pygame.draw.rect(screen, "#ded1d2", (475, 438, 115, 9))
        pygame.draw.rect(screen, "#ae4b53", (475, 438, 115*w.respawn_timer/RESPAWN_DELAY, 9))
    for ex, ey, timer in w.eyes:
        if timer == 0:
            draw_eye(screen, ex, ey+math.sin(w.elapsed*3)*3)
    for ex, ey, _, _ in w.shots:
        draw_eye(screen, ex, ey)
    for bx, by, _, _ in w.slime:
        pygame.draw.circle(screen, "#667849", (bx,by), 11)
        pygame.draw.circle(screen, "#a0b965", (bx,by), 9)
    if w.state == 'eaten':
        progress = min(1, w.eaten_timer / 1.2)
        pygame.draw.ellipse(screen, "#221b30", (514, 424, 64, 70))
        for tooth_x in range(520, 575, 12):
            pygame.draw.polygon(screen, "#fff2dd", [(tooth_x,426),(tooth_x+10,426),(tooth_x+5,440)])
        if progress < 1:
            draw_flower(screen, w.x+(545-w.x)*progress,
                        w.y+(452-w.y)*progress, scale=max(.1, 1-progress))
    elif not w.invincible or int(w.elapsed*12) % 2 == 0:
        draw_flower(screen, w.x, w.y)
    if w.state != "playing" and (w.state != "eaten" or w.eaten_timer >= 1.5):
        pygame.draw.rect(screen, "#886b80", (200,245,600,230), border_radius=18)
        pygame.draw.rect(screen, "#fff8e9", (203,248,594,224), border_radius=16)
        title = "TOGETHER AGAIN" if w.state == "won" else "A LITTLE REST..."
        if w.state == "eaten":
            title = "GULP! TOO LATE"
        subtitle = "You made it home to your family." if w.state == "won" else "The fiend got you. Your family is still waiting!"
        if w.state == "eaten":
            subtitle = "The monster returned and ate you!"
        text(screen, title, 500, 292, 44, "#664b69", True)
        text(screen, subtitle, 500, 351, 26, "#736774", True)
        text(screen, "Press R to play again", 500, 413, 25, "#476d66", True)


def main():
    """Run the same input, update, draw cycle discussed in class."""
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Flower Home - a kitchen adventure")
    clock = pygame.time.Clock()
    world = World()
    running = True
    while running:
        dt = min(clock.tick(60) / 1000, 1/30)
        running, direction = handle_input(world)
        world.update(dt, direction)
        draw(screen, world)
        pygame.display.flip()
    pygame.quit()


if __name__ == "__main__":
    main()
