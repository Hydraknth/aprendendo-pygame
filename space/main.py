import pygame as p
from os.path import join
from random import randint, uniform

p.init()
WIDTH, HEIGTH = 1280, 720
display_surface = p.display.set_mode((WIDTH, HEIGTH))
running = True
game_over_screen = False
clock = p.time.Clock()

class Player(p.sprite.Sprite):
    def __init__(self,surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(center = (WIDTH  / 2, HEIGTH - 100))
        self.direction = p.Vector2()
        self.speed = 450
        self.can_shoot = True
        self.laser_shot_time = 0
        self.cooldown_duration = 5000
        self.mask = p.mask.from_surface(self.image)

    def laser_timer(self):
        if not self.can_shoot:
            current_time = p.time.get_ticks()
            if current_time - self.laser_shot_time >= self.cooldown_duration:
                self.can_shoot = True
    
    def update(self, dt):
        keys = p.key.get_pressed()
        self.direction.x = int(keys[p.K_d] - int(keys[p.K_a]))
        self.direction.y = int(keys[p.K_s] - int(keys[p.K_w]))
        self.direction = self.direction.normalize() if self. direction else self.direction
        self.rect.center += self.direction * self.speed * dt

        recent_keys = p.key.get_just_pressed()
        mouse = p.mouse.get_pressed()
        if mouse[0] and self.can_shoot:
            Laser(laser_surface, self.rect.midtop, (all_sprites, laser_sprites))
            self.can_shoot = False
            self.laser_shot_time = p.time.get_ticks()
            laser_sound.play()

        self.laser_timer()

class Star(p.sprite.Sprite):
    def __init__(self, groups, surface):
        super().__init__(groups)
        self.image = surface
        self.rect = self.image.get_frect(center = (randint(1, WIDTH), randint(1, HEIGTH)))

class Laser(p.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(midbottom = pos)
    
    def update(self, dt):
        self.rect.centery -=  400 * dt
        
        if self.rect.bottom < 0:
            self.kill()

class Meteor(p.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.original_surface = surf
        self.image = self.original_surface
        self.rect = self.image.get_frect(center = pos)
        self.start_time = p.time.get_ticks()
        self.lifeline = 3000
        self.direction = p.Vector2(uniform(-0.5, 0.5), 1)
        self.speed = randint(550, 700)
        self.rotation = 0
        
    
    def update(self, dt):
        self.rect.center += self.direction * self.speed * dt

        if p.time.get_ticks() - self.start_time >=  self.lifeline:
            self.kill()

        self.rotation += 100 * dt
        self.image = p.transform.rotozoom(self.original_surface, self.rotation, 1)
        self.rect = self.image.get_frect(center = self.rect.center)

class AnimatedExplosion(p.sprite.Sprite):
    def __init__(self, frames, pos, groups):
        super().__init__(groups)
        self.frames = frames
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_frect(center = pos)
    
    def update(self, dt):
        self.frame_index += 50 * dt
        
        if self.frame_index < len(self.frames):
            self.image = self.frames[int(self.frame_index)]
        else:
            self.kill()
        
def collisions():
    global running
    global game_over_screen

    collison_sprites = p.sprite.spritecollide(player, meteor_sprite, True, p.sprite.collide_mask)
    if collison_sprites:
        game_over_screen = True
        running = False
    
    for laser in laser_sprites:
        collided_sprites = p.sprite.spritecollide(laser, meteor_sprite, True,)

        if collided_sprites:
            laser.kill()
            AnimatedExplosion(explosion_frames, laser.rect.midtop, all_sprites)
            explosion_sound.play()

def diplay_score():
    current_time = p.time.get_ticks() // 1000
    text_surface = font.render(str(current_time), True, (240, 240, 240))
    text_rect = text_surface.get_frect(midbottom = (WIDTH / 2, HEIGTH - 50))
    display_surface.blit(text_surface, text_rect)
    p.draw.rect(display_surface, (240, 240, 240), text_rect.inflate(20, 12).move(0, -10), 5, 15)

meteor_event = p.event.custom_type()
p.time.set_timer(meteor_event, 300)

laser_sound = p.mixer.Sound(join("audio", "laser.wav"))
laser_sound.set_volume(0.5)
explosion_sound = p.mixer.Sound(join("audio", "explosion.wav"))
explosion_sound.set_volume(0.5)
game_music = p.mixer.Sound(join("audio", "game_music.wav"))
game_music.set_volume(0.5)
game_music.play(loops = -1)

player_surface = p.image.load(join("images", "player.png")).convert_alpha()
star_surface = p.image.load(join("images", "star.png")).convert_alpha()
meteor_surface = p.image.load(join("images", "meteor.png")).convert_alpha()
laser_surface = p.image.load(join("images", "laser.png")).convert_alpha()
font = p.font.Font(join("images", "Oxanium-Bold.ttf"), 40)
explosion_frames = [p.image.load(join("images", "explosion", f"{i}.png")).convert_alpha() for i in range(21)]
all_sprites = p.sprite.Group()
meteor_sprite = p.sprite.Group()
laser_sprites = p.sprite.Group()

for i in range(20):
    Star(all_sprites, star_surface)

player = Player(player_surface, all_sprites)


def start_screen():
    global running

    text_surface = font.render("Aperte espaço para jogar", True, (240, 240, 240))
    text_rect = text_surface.get_frect(center = (WIDTH / 2, (HEIGTH / 2) - 50))
    movement_surface = font.render("Movimento: AWSD", True, (240, 240, 240))
    movement_rect = movement_surface.get_frect(center = (WIDTH / 2, HEIGTH / 2))
    laser_surface = font.render("Laser: botão esquerdo do mouse", True, (240, 240, 240))
    laser_rect = laser_surface.get_frect(center = (WIDTH / 2, (HEIGTH / 2) + 50))

    while running:
        for event in p.event.get():
            if event.type == p.QUIT:
                running = False
            
        is_pressed = p.key.get_just_pressed()

        display_surface.fill("#3a2e3f")
        display_surface.blit(text_surface, text_rect)
        display_surface.blit(movement_surface, movement_rect)
        display_surface.blit(laser_surface, laser_rect)

        p.display.update()

        if is_pressed[p.K_SPACE]:
            playing()


def playing():
    global running

    while running:
        dt = clock.tick() / 1000
        for event in p.event.get():
            if event.type == p.QUIT:
                running = False
            
            if event.type == meteor_event:
                x, y = randint(0, WIDTH), randint(-200, -100)
                Meteor(meteor_surface, (x, y), (all_sprites, meteor_sprite))
        
        all_sprites.update(dt)

        collisions() 
        display_surface.fill("#3a2e3f")        
        
        diplay_score()
        all_sprites.draw(display_surface)

        p.display.update()

start_screen()

def game_over():
    global game_over_screen

    text_surface = font.render("GAME OVER", True, (240, 240, 240))
    text_rect = text_surface.get_frect(center = (WIDTH / 2, HEIGTH / 2))
    explosion_sound.play()
    game_music.set_volume(0)

    while game_over_screen:
        for event in p.event.get():
            if event.type == p.QUIT:
                game_over_screen = False
        
        display_surface.blit(text_surface, text_rect)
        

        p.display.update()

game_over()