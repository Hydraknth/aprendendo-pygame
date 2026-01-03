import pygame as p
from os.path import join
from random import randint, uniform
from sys import exit

p.init()
WIDTH, HEIGTH = 1280, 720
display_surface = p.display.set_mode((WIDTH, HEIGTH))
clock = p.time.Clock()
p.display.set_caption("Space")
p.mouse.set_visible(False)

font = p.font.Font(join("images", "Oxanium-Bold.ttf"), 40)
star_surface = p.image.load(join("images", "star.png")).convert_alpha()
meteor_surface = p.image.load(join("images", "meteor.png")).convert_alpha()
player_surface = p.image.load(join("images", "player.png")).convert_alpha()
laser_surface = p.image.load(join("images", "laser.png")).convert_alpha()
explosion_frames = [p.image.load(join("images", "explosion", f"{i}.png")).convert_alpha() for i in range(21)]

all_sprites = p.sprite.Group()
laser_sprite = p.sprite.Group()
star_sprite = p.sprite.Group()
meteor_sprite = p.sprite.Group()

game_music = p.mixer.Sound(join("audio", "game_music.wav"))
laser_sound = p.mixer.Sound(join("audio", "laser.wav"))
explosion_sound = p.mixer.Sound(join("audio", "explosion.wav"))

meteor_event = p.event.custom_type()
p.time.set_timer(meteor_event, 300)
star_event = p.event.custom_type()
p.time.set_timer(star_event, 1000)
dt = clock.tick() / 1000

class Config:
    def __init__(self):
       self.running = True
       self.volume = 0.1
       self.awsd = True
       self.arrows = False
       self.record = 0

config = Config()

class MenuBackground(p.sprite.Sprite):
    def __init__(self, surface, pos, groups, speed):
        super().__init__(groups)
        self.speed = speed
        self.image = surface
        self.rect = self.image.get_frect(center = pos)
        self.start_time = p.time.get_ticks()
        self.lifetime = 3000
    
    def update(self, dt):
        self.rect.centery += self.speed * dt
        if p.time.get_ticks() - self.start_time >= self.lifetime:
            self.kill

class Player(p.sprite.Sprite):
    def __init__(self,surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(center = (WIDTH  / 2, HEIGTH - 100))
        self.direction = p.Vector2()
        self.speed = 450
        self.can_shoot = True
        self.laser_shot_time = 0
        self.cooldown_duration = 3000
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

        mouse = p.mouse.get_pressed()
        if mouse[0] and self.can_shoot:
            Laser(laser_surface, self.rect.midtop, (all_sprites, laser_sprite))
            self.can_shoot = False
            self.laser_shot_time = p.time.get_ticks()
            laser_sound.play()

        self.laser_timer()

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
    def __init__(self, surface, pos, groups):
        super().__init__(groups)
        self.original_surface = surface
        self.image = self.original_surface
        self.rect = self.image.get_frect(center = pos)
        self.start_time = p.time.get_ticks()
        self.lifeline = 3000
        self.direction = p.Vector2(uniform(-0.5, 0.5), 1)
        self.speed = randint(300, 450)
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

def colisions():
    collison_sprites = p.sprite.spritecollide(player, meteor_sprite, True, p.sprite.collide_mask)
    if collison_sprites:
        config.running = False
        game_over()
    
    for laser in laser_sprite:
        collided_sprites = p.sprite.spritecollide(laser, meteor_sprite, True,)

        if collided_sprites:
            laser.kill()
            AnimatedExplosion(explosion_frames, laser.rect.midtop, all_sprites)
            explosion_sound.play()

def draw_text(text, font, surface, pos):
    text_surface = font.render(text, 1, (240, 240, 240))
    text_rect = text_surface.get_frect(center = pos)
    surface.blit(text_surface, text_rect)

class Interface:
    def score(self, font, clock):
        self.current_time = clock #p.time.get_ticks() // 1000
        config.record = self.current_time
        self.score_surface = font.render(str(self.current_time), True, (240, 240, 240))
        self.score_rect = self.score_surface.get_frect(center = (WIDTH - 50, 50))
        display_surface.blit(self.score_surface, self.score_rect)
        p.draw.rect(display_surface, (240, 240, 240), self.score_rect.inflate(20, 18).move(0, -10), 5, 10)
    
    def record(self, font, pos):
        self.record_surface = font.render(str(config.record), True, (240, 240, 240))
        self.record_rect = self.record_surface.get_frect(center = pos)
        display_surface.blit(self.record_surface, self.record_rect)
        p.draw.rect(display_surface, (240, 240, 240), self.score_rect.inflate(20, 18).move(0, -10), 5, 8)
        

player = Player(player_surface, all_sprites)
interface = Interface()

def start_screen():
    running = True
    game_music.set_volume(config.volume)
    game_music.play(loops = -1)

    while running:
        key = p.key.get_just_pressed()
        if key[p.K_SPACE]:
            game()

        for event in p.event.get():
            if event.type == p.QUIT:
                running = False

            if event.type == star_event:
                x, y = randint(0, WIDTH), randint(-30, -10)
                MenuBackground(star_surface, (x, y), star_sprite, 3)

        star_sprite.update(dt)
        display_surface.fill("#3a2e3f")
        
        draw_text("Aperte [espaço] para jogar", font, display_surface, (WIDTH / 2, HEIGTH / 2))

        all_sprites.draw(display_surface)
        star_sprite.draw(display_surface)
        p.display.update()

def game():
    game_running = p.event.custom_type()
    p.time.set_timer(game_running, 1000)
    time = 0

    while config.running:        
        gdt = clock.tick() / 1000
    
        for event in p.event.get():
            if event.type == p.QUIT:
                exit()

            if event.type == star_event:
                x, y = randint(0, WIDTH), randint(-20, -5)
                MenuBackground(star_surface, (x, y), star_sprite, 1)
            
            if event.type == meteor_event:
                x, y = randint(0, WIDTH), randint(-200, -100)
                Meteor(meteor_surface, (x, y), (all_sprites, meteor_sprite))
            
            if event.type == game_running:
                time += 1
        
        all_sprites.update(gdt)
        star_sprite.update(dt)
        meteor_sprite.update(gdt)
        display_surface.fill("#3a2e3f")

        colisions()
        
        interface.score(font, time)
        interface.record(font, (WIDTH - 50, 150))
        all_sprites.draw(display_surface)
        star_sprite.draw(display_surface)
        meteor_sprite.draw(display_surface)
        p.display.update()

def game_over():
    running = True

    while running:
        for event in p.event.get():
            if event.type == p.QUIT:
                exit()
            
        display_surface.fill((0, 0, 0))
        draw_text("GAME OVER", font, display_surface, (WIDTH / 2, HEIGTH / 2))

        interface.record(font, (WIDTH / 2, HEIGTH / 2 + 50))

        p.display.update()

start_screen()
