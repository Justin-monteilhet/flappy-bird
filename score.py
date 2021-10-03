from typing import List
from pygame import Surface, SRCALPHA

class Score:
    def __init__(self, digits:List[Surface], init_value=0) -> None:
        self.score = init_value
        self.digits = digits
    
    def get_surface(self):
        if self.score < 10:
            return self.digits[self.score]

        surfaces = []
        for digit in str(self.score):
            surfaces.append(self.digits[int(digit)])
        
        width = sum([s.get_width() for s in surfaces])
        all_digits = Surface((width, surfaces[0].get_height()), SRCALPHA)

        for index, srfc in enumerate(surfaces):
            padding = 0
            if index : padding = sum([s.get_width() for s in surfaces[:index]])
            all_digits.blit(srfc, (padding, 0))
        
        return all_digits
    