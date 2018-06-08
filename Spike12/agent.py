from vector2d import Vector2D
from graphics import egi
from path import Path


class Agent(object):

    def __init__(self):
        self.pos = Vector2D(10, 10)
        self.color = 'GREEN'
        self.path = Path()

    def update(self):
        self.follow_path()

    def render(self, color=None):
        # draw
        egi.set_pen_color(name=self.color)
        egi.cross(self.pos,10)
        egi.circle(self.pos,10)

    def follow_path(self):
        to_target = self.path.current_pt() - self.pos
        dist = to_target.length()

        threshold = 5

        if dist < threshold and not self.path.is_finished():
            self.path.inc_current_pt()

        if self.pos.x > self.path.current_pt().x:
            self.pos.x -= 5
        if self.pos.x < self.path.current_pt().x:
            self.pos.x += 5
        if self.pos.y > self.path.current_pt().y:
            self.pos.y -= 5
        if self.pos.y < self.path.current_pt().y:
            self.pos.y += 5


