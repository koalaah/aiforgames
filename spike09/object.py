from vector2d import *
from graphics import egi, KEY
from random import randrange


class Attacker(object):
    WEAPON_TYPES = {
        KEY._1: 'Rifle',
        KEY._2: 'Rocket',
        KEY._3: 'Pistol',
        KEY._4: 'Grenade'
    }

    def __init__(self, world=None):
        self.world = world
        self.pos = Vector2D(world.cx / 2, 100)
        self.radius = 10
        self.target = self.world.target
        self.weapon = 'Rifle'

    def shoot(self):
        self.world.projectiles.append(Projectile(self.world, self.weapon))

    def render(self):
        egi.green_pen()
        egi.circle(self.pos, self.radius)

class Projectile(object):
    def __init__(self, world=None, proj_type='Rifle'):
        self.world = world
        self.pos = Vector2D(world.cx / 2, 110)
        self.vel = Vector2D()
        self.radius = 5
        self.proj_type = proj_type
        self.cur_targ_pos = Vector2D(world.target.pos.x, world.target.pos.y)

        if self.proj_type == 'Rifle':
            self.speed = 550
            deviation_rate = 0
            self.leading = world.target.speed
        elif self.proj_type == 'Rocket':
            self.speed = 250
            deviation_rate = 0
            self.leading = world.target.speed * 1.5
        elif self.proj_type == 'Pistol':
            self.speed = 550
            deviation_rate = 7
            self.leading = world.target.speed
        elif self.proj_type == 'Grenade':
            self.speed = 250
            deviation_rate = 7
            self.leading = world.target.speed * 1.5

        if randrange(10) < deviation_rate:
            deviation = randrange(-110, 130, 40)
            self.target = Vector2D(world.target.pos.x + deviation, 450)
        else:
            if world.target.destination == Vector2D(100, 400):
                if world.target.pos.x > self.pos.x:
                    if self.speed == 250:
                        self.leading *= 3
                    self.target = Vector2D(self.world.target.pos.x - self.leading / 5, world.target.pos.y + 50)
                else:
                    self.target = Vector2D(world.target.pos.x - self.leading, world.target.pos.y + 50)
            else:
                if world.target.pos.x < self.pos.x:
                    if self.speed == 250:
                        self.leading *= 3
                    self.target = Vector2D(world.target.pos.x + self.leading / 5, world.target.pos.y + 50)
                else:
                    self.target = Vector2D(world.target.pos.x + self.leading, world.target.pos.y + 50)
        self.force = Vector2D()

    def calculate(self, delta):
        target_pos = self.target
        desired_vel = (target_pos - self.pos).normalise() * 500
        return (desired_vel)

    def update(self, delta):
        force = self.calculate(delta)
        force.truncate(self.speed)
        self.vel = force
        self.pos += self.vel * delta
        target_pos = self.world.target.pos

        if (self.pos.x >= target_pos.x - 10) and (self.pos.x <= target_pos.x + 10) and (self.pos.y > target_pos.y):
            self.world.target.on_hit()
            self.world.projectiles.remove(self)

        elif self.pos.y > self.target.y:
            self.world.projectiles.remove(self)

    def render(self):
        egi.white_pen()
        egi.circle(self.pos, 3)


class Target(object):

    def __init__(self, world=None):
        self.world = world
        self.pos = Vector2D(world.cx / 2, 400)
        self.vel = Vector2D()
        self.size = 10
        self.destination = Vector2D(400, 400)
        self.speed = 50
        self.growing = True

    def calculate(self, delta):
        target_pos = self.destination
        desired_vel = (target_pos - self.pos).normalise() * 500
        return desired_vel

    def render(self):
        egi.red_pen()
        egi.circle(self.pos, self.size)

    def update(self, delta):
        self.vel = self.calculate(delta)
        self.vel.truncate(self.speed)
        self.pos += self.vel * delta

        if self.pos.x >= 400:
            self.destination = Vector2D(100, 400)

        elif self.pos.x <= 100:
            self.destination = Vector2D(400, 400)

    def on_hit(self):
        if self.size == 15:
            self.growing = False
        elif self.size == 5:
            self.growing = True
        if self.growing:
            self.size += 1
        else:
            self.size -= 1

