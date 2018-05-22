from vector2d import Vector2D
from graphics import egi, KEY
from random import randrange

class Obstacle(object):
    def __init__(self, world=None):
        self.world = world
        self.pos = Vector2D(randrange(world.cx), randrange(world.cy))

    def render(self, color=None):
        egi.red_pen()
        egi.circle(self.pos, 30)