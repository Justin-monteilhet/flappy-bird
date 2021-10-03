from typing import Tuple, Generator
from pygame import transform, image, Rect
import os


class Pipe:
    def __init__(self, surface, direction, position) -> None:
        assert direction in ('top', 'bottom')
        self.direction = direction
        surface = surface
        self.surface = transform.scale(surface, [int(d*1.5) for d in surface.get_size()])
        if direction == 'bottom':
            self.surface = transform.rotate(self.surface, 180)  

        self.set_pos(position)
        if self.pos[1] < 0:
            offset = abs(self.pos[1])
            height = self.surface.get_size()[1] - offset
            sub_rect = (0, offset, self.surface.get_size()[0], height)
            self.surface = self.surface.subsurface(sub_rect)
            self.pos = self.pos[0], 0

        self.passed_by_player, self.passed_limit = False, False

    def forward(self, dst=1):
        self.pos = self.pos[0]-dst, self.pos[1]
    
    def set_pos(self, pos:Tuple[int, int]):
        self.pos = pos[0], pos[1] - self.surface.get_size()[1]
        if self.direction == 'bottom' : self.pos = pos[0], pos[1] - self.surface.get_size()[1]
        elif self.direction == 'top' : self.pos = pos[0], pos[1]

    def is_passed(self) -> bool:
        return self.pos[0] + self.surface.get_size()[0] < 0 
    
    def get_rect(self):
        return Rect(*self.pos+self.surface.get_size())
    
    @classmethod
    def make_couple_pipes(cls, srfc, pos:Tuple[int, int], space=200):
        x, y = pos
        f_pipe = cls(srfc, 'bottom', (x, y))
        s_pipe = cls(srfc, 'top', (x, y+space))
        return CouplePipes(f_pipe, s_pipe)

class CouplePipes:
    def __init__(self, top:Pipe, bottom:Pipe) -> None:
        self.top, self.bottom = top, bottom
        self.is_passed_by_player = False
    
    def __iter__(self) -> Generator[Pipe, None, None]:
        return (p for p in [self.top, self.bottom])
    
    def __eq__(self, item) -> bool:
        return isinstance(item, type(self)) and item.top, item.bottom == self.top, self.bottom