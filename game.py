import os
import random
import math
import pygame
from os import listdir
from os.path import isfile, join

pygame.init()

pygame.display.set_caption("Ninja Frog")

WIDTH, HEIGHT = 1400, 1000
FPS = 60
PLAYER_VEL = 5

window = pygame.display.set_mode((WIDTH, HEIGHT))


def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]


def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    path = join("assets", dir1, dir2)
    images = [f for f in listdir(path) if isfile(join(path, f))]

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()

        sprites = []
        for i in range(sprite_sheet.get_width() // width):
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0, 0), rect)
            sprites.append(pygame.transform.scale2x(surface))

        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites

    return all_sprites


def get_block(size):
    path = join("assets", "Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(96, 0, size, size)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)


class Player(pygame.sprite.Sprite):
    COLOR = (255, 0, 0)
    GRAVITY = 1
    SPRITES = load_sprite_sheets("MainCharacters", "NinjaFrog", 32, 32, True)
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 10
        self.y_vel = 10
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.hit = False
        self.hit_count = 0
        self.score = 0
        self.lives = 3
        self.level = 1


    def jump(self):
        self.y_vel = -self.GRAVITY * 8
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
            self.fall_count = 0

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def make_hit(self):
        if not self.hit:
            self.hit = True
            self.lives -= 1

    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    def loop(self, fps):
        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.move(self.x_vel, self.y_vel)

        if self.hit:
            self.hit_count += 1
        if self.hit_count > fps * 3:
            self.hit = False
            self.hit_count = 0

        self.fall_count += 1
        self.update_sprite()

    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0

    def hit_head(self):
        self.count = 0
        self.y_vel *= -1

    def update_sprite(self):
        sprite_sheet = "idle"
        if self.hit:
            sprite_sheet = "hit"
        elif self.y_vel < 0:
            if self.jump_count == 1:
                sprite_sheet = "jump"
            elif self.jump_count == 2:
                sprite_sheet = "double_jump"
        elif self.y_vel > self.GRAVITY * 2:
            sprite_sheet = "fall"
        elif self.x_vel != 0:
            sprite_sheet = "run"

        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def draw(self, win, offset_x):
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))


class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name
        self.image.set_colorkey((0, 0, 0))

    def draw(self, win, offset_x):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))


class Coin(Object):
    ANIMATION_DELAY = 3  # Example animation delay

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "coin")
        self.sprite_sheet = pygame.image.load("assets/coin.png").convert_alpha()
        self.frames = []
        for i in range(self.sprite_sheet.get_width() // width):
            frame = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            frame.blit(self.sprite_sheet, (0, 0), (i * width, 0, width, height))
            self.frames.append(frame)
        self.image = self.frames[0]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0

    def update(self):
        self.animation_count += 1
        frame_index = (self.animation_count // self.ANIMATION_DELAY) % len(self.frames)
        self.image = self.frames[frame_index]
        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

class Mushroom(Object):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "mushroom")
        self.sprite_sheet = pygame.image.load("assets/20_Enemies.png").convert_alpha()
        self.image.blit(self.sprite_sheet, (0, 0), (286, 364, width, height))
        self.x_vel = 2  # Example horizontal velocity
        
    def update(self):
        self.rect.x += self.x_vel
        # Example logic to make the enemy move back and forth
        if self.rect.left <= 0 or self.rect.right >= WIDTH:
            self.x_vel = -self.x_vel



class Spike(Object):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "spike")
        self.sprite_sheet = pygame.image.load("assets/20_Enemies.png").convert_alpha()
        self.image.blit(self.sprite_sheet, (0, 0), (147, 58, width, height))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.x_vel = 2  # Example horizontal velocity

    def update(self):
        self.rect.x += self.x_vel
        # Example logic to make the enemy move back and forth
        if self.rect.left <= 0 or self.rect.right >= WIDTH:
            self.x_vel = -self.x_vel
    

class Marker(Object):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "marker")
        self.sprite_sheet = pygame.image.load("assets/20_Enemies.png").convert_alpha()
        self.image.blit(self.sprite_sheet, (0, 0), (154, 347, width, height))

class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = get_block(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)


class Fire(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "fire")
        self.fire = load_sprite_sheets("Traps", "Fire", width, height)
        self.image = self.fire["off"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "off"

    def on(self):
        self.animation_name = "on"

    def off(self):
        self.animation_name = "off"

    def loop(self):
        sprites = self.fire[self.animation_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0


def get_background(name):
    image = pygame.image.load(join("assets", "Background", name))
    _, _, width, height = image.get_rect()
    tiles = []

    for i in range(WIDTH // width + 1):
        for j in range(HEIGHT // height + 1):
            pos = (i * width, j * height)
            tiles.append(pos)

    return tiles, image


def draw(window, background, bg_image, player, objects, offset_x):
    for tile in background:
        window.blit(bg_image, tile)

    for obj in objects:
        obj.draw(window, offset_x)

    player.draw(window, offset_x)

    font = pygame.font.Font(None, 36)
    score_text = font.render(f"Score: {player.score}", True, (0, 0, 0))
    lives_text = font.render(f"Lives: {max(player.lives, 0)}", True, (0, 0, 0))
    level_text = font.render(f"Level: {player.level}", True, (0, 0, 0))
    window.blit(score_text, (20, 10))
    window.blit(lives_text, (20, 50))
    window.blit(level_text, (20, 90))

    pygame.display.update()


def handle_vertical_collision(player: Player, objects, dy):
    collided_objects = []
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            if dy > 0:
                player.rect.bottom = obj.rect.top
                player.landed()
            elif dy < 0:
                player.rect.top = obj.rect.bottom
                player.hit_head()

            collided_objects.append(obj)

    return collided_objects


def collide(player: Player, objects, dx):
    player.move(dx, 0)
    player.update()
    collided_object = None
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            collided_object = obj
            break

    player.move(-dx, 0)
    player.update()
    return collided_object


def handle_move(player: Player, objects):
    keys = pygame.key.get_pressed()

    player.x_vel = 0
    collide_left = collide(player, objects, -PLAYER_VEL * 2)
    collide_right = collide(player, objects, PLAYER_VEL * 2)

    if keys[pygame.K_LEFT] and not collide_left:
        player.move_left(PLAYER_VEL)
    if keys[pygame.K_RIGHT] and not collide_right:
        player.move_right(PLAYER_VEL)

    vertical_collide = handle_vertical_collision(player, objects, player.y_vel)
    to_check = [collide_left, collide_right, *vertical_collide]

    for obj in to_check:
        if obj and obj.name in ("fire", "mushroom", "spike"):
            player.make_hit()


def lose_life_below_screen(player: Player,  last_safe_position: int, offset_x: int):
    player.lives -= 1
    player.hit = True
    player.rect.top = 200
    player.rect.left = last_safe_position
    player.y_vel = 0
    player.x_vel = 0
    offset_x = player.rect.left - WIDTH // 2
    return (
        player.lives,
        player.rect.top,
        player.rect.left,
        player.y_vel,
        player.x_vel,
        offset_x,
    )

def draw_buttons(window, play_again_button, quit_button):
    pygame.draw.rect(window, (0, 0, 0), play_again_button)
    pygame.draw.rect(window, (0, 0, 0), quit_button)
    font = pygame.font.Font(None, 36)
    play_again_text = font.render("Play Again", True, (255, 255, 255))
    quit_text = font.render("Quit", True, (255, 255, 255))
    play_again_text_rect = play_again_text.get_rect(center=play_again_button.center)
    quit_text_rect = quit_text.get_rect(center=quit_button.center)
    window.blit(play_again_text, play_again_text_rect)
    window.blit(quit_text, quit_text_rect)

def generate_floor(block_size, width, height):
    floor = []
    gap_size = 0
    for i in range(-width // block_size, (width * 4) // block_size):  # Zwiększ długość poziomu
        if gap_size > 0:
            gap_size -= 1
        else:
            if random.randint(0, 10) < 1:  # 20% szans na dziurę
                gap_size = random.randint(0, 1)  # Dziura o rozmiarze 1 lub 2 bloki
            else:
                floor.append(Block(i * block_size, height - block_size, block_size))
    return floor

def generate_floating_blocks(block_size, width, height):
    floating_blocks = []
    for _ in range(3):  # Dodaj więcej losowych bloków wiszących w powietrzu
        x = random.randint(0, width * 4)  # Zwiększ zakres x
        y = random.randint(height // 2, height - block_size * 4)
        floating_blocks.append(Block(x, y, block_size))
    return floating_blocks

def generate_rock_shelves(block_size, width, height):
    rock_shelves = []
    for _ in range(10):  # Dodaj 10 losowych półek skalnych
        x = random.randint(0, width * 4)  # Zwiększ zakres x
        y = random.randint(height // 2, height - block_size * 3)
        shelf_length = random.randint(2, 5)  # Długość półki skalnej od 2 do 5 bloków
        for i in range(shelf_length):
            rock_shelves.append(Block(x + i * block_size, y, block_size))
    return rock_shelves

def generate_enemies_and_hazards(block_size, width, height):
    enemies_and_hazards = []
    for _ in range(5): 
        x = random.randint(0, width * 4)  # Zwiększ zakres x
        y = random.randint(height // 2, height - block_size * 4)
        mushroom = Mushroom(x, y, 90, 50)
        enemies_and_hazards.append(mushroom)
    for _ in range(5):
        x = random.randint(0, width * 4)
        y = height - block_size - 48
        spike = Spike(x, y, 83, 50)
        enemies_and_hazards.append(spike)
    for _ in range(4):
        x = random.randint(0, width * 4) 
        fire = Fire(x, y, 16, 32)
        fire.on()
        enemies_and_hazards.append(fire)
    return enemies_and_hazards

def generate_coins(block_size, width, height, blocks):
    coins = []
    coin_size = 32
    for _ in range(120):
        while True:
            x = random.randint(0, width * 4)
            y = random.randint(height // 4, height - block_size)
            coin = Coin(x, y, coin_size, coin_size)
            if not any(coin.rect.colliderect(block.rect) for block in blocks):
                coins.append(coin)
                break
    return coins

def main(window):
    clock = pygame.time.Clock()
    background, bg_image = get_background("Pink.png")

    block_size = 96

    player = Player(100, 100, 50, 50)
    floor = generate_floor(block_size, WIDTH, HEIGHT)
    floating_blocks = generate_floating_blocks(block_size, WIDTH, HEIGHT)
    rock_shelves = generate_rock_shelves(block_size, WIDTH, HEIGHT)
    enemies_and_hazards = generate_enemies_and_hazards(block_size, WIDTH, HEIGHT)
    marker1 = Marker(100, 100, 120, 120)
    marker2 = Marker(2700, 100, 120, 120)
    coins = generate_coins(block_size, WIDTH, HEIGHT, floor + floating_blocks + rock_shelves)

    objects = [
        *floor,
        *floating_blocks,
        *enemies_and_hazards,
        *rock_shelves,
        *coins,
        Block(0, HEIGHT - block_size * 2, block_size),
        Block(block_size * 3, HEIGHT - block_size * 4, block_size),
        Block(block_size * 6, HEIGHT - block_size * 6, block_size), marker1, marker2
    ]


    offset_x = 0
    scroll_area_width = 200

    last_safe_position = player.rect.left
    player.score = 0
    
    play_again_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 150, 200, 50)
    quit_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 220, 200, 50)

    run = True
    game_over = False
    while run:
        if player.lives < 0:
            game_over = True
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player.jump_count < 2:
                    player.jump()
            
            if event.type == pygame.MOUSEBUTTONDOWN and game_over:
                mouse_pos = event.pos
                if play_again_button.collidepoint(mouse_pos):
                    # Reset game
                    player = Player(100, 100, 50, 50)
                    floor = generate_floor(block_size, WIDTH, HEIGHT)
                    floating_blocks = generate_floating_blocks(block_size, WIDTH, HEIGHT)
                    enemies_and_hazards = generate_enemies_and_hazards(block_size, WIDTH, HEIGHT)
                    objects = [
                        *floor,
                        *floating_blocks,
                        *enemies_and_hazards,
                        Block(0, HEIGHT - block_size * 2, block_size),
                        Block(block_size * 3, HEIGHT - block_size * 4, block_size),
                        Block(block_size * 6, HEIGHT - block_size * 6, block_size)
                    ]
                    last_safe_position = player.rect.left
                    game_over = False
                elif quit_button.collidepoint(mouse_pos):
                    run = False
                    break
                
        if not game_over:
            player.loop(FPS)
            handle_move(player, objects)
            draw(window, background, bg_image, player, objects, offset_x)
            
            
            for obj in objects:
                if isinstance(obj, Mushroom):
                    obj.update()
                if isinstance(obj, Fire):
                    obj.loop()
                if isinstance(obj, Spike):
                    obj.update()
                if isinstance(obj, Coin):
                    obj.update()


            for coin in coins[:]:
                if pygame.sprite.collide_mask(player, coin):
                    player.score += 150
                    coins.remove(coin)
                    objects.remove(coin)

            if player.rect.top <= HEIGHT:
                last_safe_position = player.rect.left

            if player.rect.top > HEIGHT:
                (
                    player.lives,
                    player.rect.top,
                    player.rect.left,
                    player.y_vel,
                    player.x_vel,
                    offset_x,
                ) = lose_life_below_screen(player, last_safe_position, offset_x)
                

            if (
                (player.rect.right - offset_x >= WIDTH - scroll_area_width)
                and player.x_vel > 0
            ) or (
                (player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0
            ):
                offset_x += player.x_vel
        else:
            font1 = pygame.font.Font(None, 150)
            game_over_text = font1.render("GAME OVER", True, (255, 255, 255))
            font2 = pygame.font.Font(None, 90)
            final_score_text = font2.render(f"Final Score: {player.score}", True, (255, 0, 0))
            window.blit(
                game_over_text,
                (
                    WIDTH // 2 - game_over_text.get_width() // 2,
                    HEIGHT // 2 - game_over_text.get_height() // 2,
                ),
            )
            window.blit(
                final_score_text,
                (
                    WIDTH // 2 - final_score_text.get_width() // 2,
                    HEIGHT // 2 + 50,
            )
            )
            draw_buttons(window, play_again_button, quit_button)
            pygame.display.flip()

    pygame.quit()
    quit()


if __name__ == "__main__":
    main(window)
