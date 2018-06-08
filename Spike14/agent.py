'''An agent with Seek, Flee, Arrive, Pursuit behaviours

Created for COS30002 AI for Games by Clinton Woodward cwoodward@swin.edu.au

'''

from vector2d import Vector2D
from vector2d import Point2D
from graphics import egi, KEY
from math import sin, cos, radians
from random import random, randrange, uniform
from path import Path
from object import Projectile


class Agent(object):
    # NOTE: Class Object (not *instance*) variables!
    DECELERATION_SPEEDS = {
        'slow': 0.9,
        ### ADD 'normal' and 'fast' speeds here
        # ...
        # ...
    }

    def __init__(self, world=None, scale=30.0, mass=1.0, mode='patrol'):
        # keep a reference to the world object.py
        self.world = world
        self.mode = mode
        # where am i and where am i going? random start pos
        dir = radians(random() * 360)
        self.pos = Vector2D(randrange(world.cx), randrange(world.cy))
        self.vel = Vector2D()
        self.heading = Vector2D(sin(dir), cos(dir))
        self.side = self.heading.perp()
        self.scale = Vector2D(scale, scale)  # easy scaling of agent size
        self.force = Vector2D()  # current steering force
        self.accel = Vector2D()  # current acceleration due to force
        self.mass = mass

        # data for drawing this agent
        self.color = 'ORANGE'
        self.vehicle_shape = [
            Point2D(-1.0, 0.6),
            Point2D(1.0, 0.0),
            Point2D(-1.0, -0.6)
        ]
        ### path to follow?
        # self.path = ??
        self.path = Path()
        self.randomise_path(10)
        self.waypoint_threshold = 10.0
        ### wander details
        # self.wander_?? ...
        self.wander_target = Vector2D(1, 0)
        self.wander_dist = 1.0 * scale
        self.wander_radius = 1.0 * scale
        self.wander_jitter = 10.0 * scale
        self.bRadius = scale
        # limits?
        self.max_speed = 100.0
        self.max_force = 200.0
        self.bulletspeed = 500.0

        self.bullets = 6
        self.reload_time = 1
        self.current_reload_time = 0.0
        self.gun_state = 'loaded'

        # debug draw info?
        self.show_info = False

    def calculate(self, delta):
        # calculate the current steering force
        mode = self.mode
        if self.gun_state == 'reloading':
            if self.current_reload_time > self.reload_time:
                self.bullets = 6
                self.gun_state = 'loaded'
            else:
                self.current_reload_time += delta
        if mode == 'attack':
            if not self.world.targets:
                self.mode = 'patrol'
                return Vector2D()
            force = self.seek(self.world.targets[0].pos)
            if self.gun_state == 'loaded':

                self.shoot(self.world.targets[0].pos)
                self.bullets -= 1
                if self.bullets <= 0:
                    self.gun_state = 'reloading'
                    self.current_reload_time = 0.0

        elif mode == 'patrol':
            force = self.follow_path()
            if self.world.targets:
                self.mode = 'attack'
        else:
            force = Vector2D()
        self.force = force
        return force

    def update(self, delta):
        ''' update vehicle position and orientation '''
        # calculate and set self.force to be applied
        ## force = self.calculate()
        force = self.calculate(delta)  # <-- delta needed for wander
        ## limit force? <-- for wander
        # ...
        # determin the new accelteration
        self.accel = force / self.mass  # not needed if mass = 1.0
        # new velocity
        self.vel += self.accel * delta
        # check for limits of new velocity
        self.vel.truncate(self.max_speed)
        # update position
        self.pos += self.vel * delta
        # update heading is non-zero velocity (moving)
        if self.vel.length_sq() > 0.00000001:
            self.heading = self.vel.get_normalised()
            self.side = self.heading.perp()
        # treat world as continuous space - wrap new position if needed
        self.world.wrap_around(self.pos)

    def render(self, color=None):
        ''' Draw the triangle agent with color'''
        # draw the path if it exists and the mode is follow
        if self.path:
            ## ...
            self.path.render()

        # draw the ship
        egi.set_pen_color(name=self.color)
        pts = self.world.transform_points(self.vehicle_shape, self.pos,
                                          self.heading, self.side, self.scale)
        # draw it!
        egi.closed_shape(pts)

        # draw wander info?
        if self.mode == 'wander':
            ## ...
            wnd_pos = Vector2D(self.wander_dist, 0)
            wld_pos = self.world.transform_point(wnd_pos, self.pos, self.heading, self.side)

            egi.green_pen()
            egi.circle(wld_pos, self.wander_radius)

            egi.red_pen()
            wnd_pos = (self.wander_target + Vector2D(self.wander_dist, 0))
            wld_pos = self.world.transform_point(wnd_pos, self.pos, self.heading, self.side)
            egi.circle(wld_pos, 3)

        # add some handy debug drawing info lines - force and velocity
        if self.show_info:
            s = 0.5  # <-- scaling factor
            # force
            egi.red_pen()
            egi.line_with_arrow(self.pos, self.pos + self.force * s, 5)
            # velocity
            egi.grey_pen()
            egi.line_with_arrow(self.pos, self.pos + self.vel * s, 5)
            # net (desired) change
            egi.white_pen()
            egi.line_with_arrow(self.pos + self.vel * s, self.pos + (self.force + self.vel) * s, 5)
            egi.line_with_arrow(self.pos, self.pos + (self.force + self.vel) * s, 5)

    def speed(self):
        return self.vel.length()

    def randomise_path(self, num_pts):
        cx = self.world.cx
        cy = self.world.cy
        margin = min(cx, cy) * (1 / 6)
        self.path.create_random_path(num_pts, 0 + margin, 0 + margin, cx - margin, cy - margin, True)

    # --------------------------------------------------------------------------

    def seek(self, target_pos):
        ''' move towards target position '''
        desired_vel = (target_pos - self.pos).normalise() * self.max_speed
        return (desired_vel - self.vel) * 5

    def arrive(self, target_pos, speed):
        ''' this behaviour is similar to seek() but it attempts to arrive at
            the target position with a zero velocity'''
        decel_rate = self.DECELERATION_SPEEDS[speed]
        to_target = target_pos - self.pos
        dist = to_target.length()
        if dist > 0:
            # calculate the speed required to reach the target given the
            # desired deceleration rate
            speed = dist / decel_rate
            # make sure the velocity does not exceed the max
            speed = min(speed, self.max_speed)
            # from here proceed just like Seek except we don't need to
            # normalize the to_target vector because we have already gone to the
            # trouble of calculating its length for dist.
            desired_vel = to_target * (speed / dist)
            return (desired_vel - self.vel)
        return Vector2D(0, 0)

    def wander(self, delta):
        ''' Random wandering using a projected jitter circle. '''
        ## ...
        wt = self.wander_target
        jitter_tts = self.wander_jitter * delta
        wt += Vector2D(uniform(-1, 1) * jitter_tts, uniform(-1, 1) * jitter_tts)
        wt.normalise()
        wt *= self.wander_radius
        target = wt + Vector2D(self.wander_dist, 0)
        wld_target = self.world.transform_point(target, self.pos, self.heading, self.side)

        return self.seek(wld_target)

    def follow_path(self):

        if self.path.current_pt().distance(self.pos) < self.waypoint_threshold:
            self.path.inc_current_pt()
        return self.seek(self.path.current_pt())

    def shoot(self, aimpos):
        direction = aimpos - self.pos
        direction = direction.normalise()

        self.world.projectiles.append(Projectile(self.pos.x, self.pos.y, direction * self.bulletspeed, self.world))