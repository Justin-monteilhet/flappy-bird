from typing import List, Tuple
from pygame import Surface
from pygame.transform import scale



class Bird:
    def __init__(self, pos:Tuple[int, int], skins:List[Surface], size=(80, 60), jump=130, speed=4, jump_speed=6) -> None:
        self.surface = self.set_surface(skins[0], size, 10)
        self.position = pos[0], int(pos[1] - self.surface.get_size()[1]/2)
        self.size, self.speed = size, speed
        self.jump_duration = 0.4
        self.jump_start = (None, None)  # time since start, height at start
        self.jumping = False
        self.skins = skins
        self.skin_index = 0
    
    def set_surface(self, surface, size, chop_ratio):
        self.surface = scale(surface, size)
        chop_ratio = 0
        x_offset, y_offset = [i * (chop_ratio/100) for i in self.surface.get_size()]
        x_size, y_size = self.surface.get_size()[0] - 2*x_offset, self.surface.get_size()[1] - 2*y_offset
        return self.surface.subsurface((x_offset, y_offset, x_size, y_size))

    def switch_skin(self):
        if self.skin_index >= len(self.skins)-1:
            self.skin_index = -1
        
        self.skin_index+=1
        self.surface = self.set_surface(self.skins[self.skin_index], self.size, 10)

    def jump(self, clock_time):
        if not self.jumping : self.jumping = True
        
        time_since_jump_start = (clock_time - self.jump_start[0])
        
        self.position = self.position[0], self.jump_start[1] - self.jump_func(time_since_jump_start)
        
        if time_since_jump_start >= self.jump_duration:
            self.jumping = False
    
    def gravity(self):
        self.position = self.position[0], self.position[1] + self.speed
    
    def get_rect(self):
        return self.position + self.surface.get_size()

    def jump_func(self, t:float) -> float:
        return 8.1 * t * (2*self.jump_duration - t) * 100 