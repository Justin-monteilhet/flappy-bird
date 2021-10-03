from json.decoder import JSONDecodeError
from json import loads, dumps, load, dump
from typing import List
from random import randrange

import pygame as pg
import os

from pygame.constants import K_RETURN, K_UP

from score import Score
from pipe import CouplePipes, Pipe
from bird import Bird

pg.init()
pg.font.init()
pg.mixer.init()

class Game:
    def __init__(self) -> None:
        self.size = (1000, 800)
        self.window = pg.display.set_mode(self.size)
        self.clock = pg.time.Clock()
        self.frames = 0
        self.fps = 60
        self.mode = 'menu'
        self.play = True
        digits_surfaces = [pg.image.load(os.path.join('ressources', 'images', 'digits', f'{digit}.png')) for digit in range(0, 10)]
        self.score = Score(digits_surfaces)
        with open('data.json', 'r') as f:
            data = load(f)
            if not 'highscore' in data : data['highscore'] = 0

        font_name = 'Fipps-Regular.otf'
        font_size = 30
        self.highscore_font = pg.font.Font(os.path.join('ressources', 'fonts', font_name), font_size)
        self.highscore_txt = self.highscore_font.render("HIGHSCORE", False, (255, 255, 255))

        self.highscore = Score(digits_surfaces, data['highscore'])
        
        background:pg.Surface = pg.image.load(os.path.join('ressources', 'images', 'background.png'))
        self.background:pg.Surface = pg.transform.scale(background, self.size)

        flappy_logo = pg.image.load(os.path.join('ressources', 'images', 'logo.png'))
        logo_size = flappy_logo.get_size()
        self.flappy_logo = pg.transform.scale(flappy_logo, (logo_size[0]//5, logo_size[1]//5))
        self.logo_size = self.flappy_logo.get_size()
        self.logo_pos = (self.size[0] // 2) - (self.logo_size[0] // 2), (self.size[1] // 2.5) - (self.logo_size[1] // 2) 
        self.logo_level = 0
        self.logo_dir = 'bottom'

        skin_up, skin_mid, skin_down = [pg.image.load(os.path.join('ressources', 'images', filename)) for filename in ['bird_down.png', 'bird_mid.png', 'bird_up.png']]
        self.start_pos = (30, self.size[1]/2)
        self.player = Bird(self.start_pos, [skin_up, skin_mid, skin_down, skin_mid])

        self.press_enter_font = pg.font.Font(os.path.join('ressources', 'fonts', font_name), font_size*2)
        self.press_enter = self.press_enter_font.render("PRESS ANY KEY", False, (255, 255, 255))

        self.pipes : List[CouplePipes] = []
        self.speed = self.base_speed = 3
        self.jumping = False

        sounds = {'jump':'jump.wav', 'loose':'loose.wav', 'start':'start.wav', 'background':'background.wav', 'pass':'pass.wav'}
        self.sounds = {name:sound for name, sound in zip(sounds.keys(), [pg.mixer.Sound(os.path.join('ressources', 'sounds', filename)) for filename in sounds.values()])}

    def run(self):
        while self.run :
            events = pg.event.get()
            for event in events:
                if event.type == pg.QUIT:
                    self.run = False
                
                if event.type == pg.KEYDOWN:
                    self.keydown_handler(event.key)

            if self.mode == 'menu' : self.menu_routine()
            if self.mode == 'game' : self.game_routine()
            self.draw_frame()

            self.clock.tick(self.fps) ; self.frames += 1
            pg.display.flip()

        pg.quit()

    def draw_frame(self):
        #background
        self.window.blit(self.background, (0, 0))

        if self.mode == 'menu':
            self.window.blit(self.flappy_logo, self.logo_pos)
            self.window.blit(self.press_enter, self.press_enter_pos)

            highscore_txt_pos = self.size[0]/7 - self.highscore_txt.get_width()/2, 20
            self.window.blit(self.highscore_txt, highscore_txt_pos)

            srfc = self.highscore.get_surface()
            highscore_pos = self.size[0]/7 - srfc.get_width()/2, highscore_txt_pos[1] + self.highscore_txt.get_height() - 10
            self.window.blit(srfc, highscore_pos)
        
        if self.mode == 'game':
            self.window.blit(self.player.surface, self.player.position)
            for couple in self.pipes : 
                for p in couple : self.window.blit(p.surface, p.pos)
            
            srfc = self.score.get_surface()
            score_pos = self.size[0]/2 - srfc.get_width()/2, 30
            self.window.blit(srfc, score_pos)

    def keydown_handler(self, key):
        if self.mode == 'menu':
            print('kd handler')
            self.mode = 'game'
            self.new_pipes()
            self.play_sound('background', loop=True, fade=2000)
            self.play_sound('start')
            return

        if self.mode == 'game':
            if key in (pg.K_SPACE, K_RETURN, K_UP):
                if not self.jumping : 
                    self.jumping = self.player.frame_jump()
                    self.play_sound('jump')

    def new_pipes(self):
        srfc = pg.image.load(os.path.join('ressources', 'images', 'pipe.png'))
        size = srfc.get_size()
        self.pipes.append(Pipe.make_couple_pipes(srfc, (self.size[0], randrange(150, 450)), space=250))

    def game_routine(self):
        if not self.frames % int(self.fps/3):
            self.player.switch_skin()

        for couple in self.pipes:
            for p in couple : p.forward(dst=self.speed)
            if couple.top.is_passed() : 
                self.pipes.remove(couple)
        
        if self.pipes :
            
            not_passed_pipes = [couple for couple in self.pipes if not couple.top.passed_limit]
            first_couple = not_passed_pipes[0]
            if first_couple.top.pos[0] <= self.size[0] * 0.7 and not first_couple.top.passed_limit:
                first_couple.top.passed_limit = True
                self.new_pipes()

            first_couple:CouplePipes= self.pipes[0]
            if first_couple.top.pos[0] <= self.player.position[0] and not first_couple.top.passed_by_player:
                self.pipe_passed()
                first_couple.top.passed_by_player = True

        if self.jumping : self.jumping = self.player.frame_jump()
        else : self.player.gravity()

        if self.loosing_conditions():
            self.loose()

    def menu_routine(self):
        if not self.frames % 30:
            if self.logo_dir == 'bottom' : 
                self.logo_pos = self.logo_pos[0], self.logo_pos[1]+10
                self.logo_level -= 1

            if self.logo_dir == 'top':
                self.logo_pos = self.logo_pos[0], self.logo_pos[1]-10
                self.logo_level += 1
            
            limit = 2
            if abs(self.logo_level) == limit:
                self.logo_dir = 'top' if self.logo_level == -limit else 'bottom'
                
        self.press_enter_pos = (self.size[0] // 2) - (self.press_enter.get_size()[0] // 2), int(self.size[1] * (6/10))

    def pipe_passed(self):
        self.score.score += 1
        if not self.score.score % 5 : self.speed *= 1.1
        self.play_sound('pass')

    def set_highscore(self, highscore):
        self.highscore.score = highscore
        with open('data.json', 'r') as f:
            data = load(f)
        
        data['highscore'] = highscore

        with open('data.json', 'w') as f:
            dump(data, f)

    def play_sound(self, sound:str, loop:bool=False, fade=0):
        loop = -1 if loop else 0
        self.sounds[sound].play(loops=loop, fade_ms=fade)

    def loosing_conditions(self):
        for couple in self.pipes :
            for p in couple: 
                if p.get_rect().colliderect(self.player.get_rect()):
                    return True
        
        if not (0 < self.player.position[1] < self.size[1])  : return True

        return False

    def loose(self):
        self.sounds['background'].fadeout(1500)
        self.play_sound('loose')
        self.pipes = []
        if self.score.score > self.highscore.score:
            self.set_highscore(self.score.score)

        self.score.score = 0
        self.mode = 'menu'
        self.player.position = self.start_pos
        self.speed = self.base_speed
