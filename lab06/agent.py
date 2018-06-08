'''An agent with Seek, Flee, Arrive, Pursuit behaviours

Created for COS30002 AI for Games by Clinton Woodward cwoodward@swin.edu.au

'''

from vector2d import Vector2D
from vector2d import Point2D
from graphics import egi, KEY
from math import sin, cos, radians
from random import random, randrange, uniform
from path import Path

AGENT_MODES = {
    KEY._1: 'seek',
    KEY._2: 'arrive_slow',
    KEY._3: 'arrive_normal',
    KEY._4: 'arrive_fast',
    KEY._5: 'flee',
    KEY._6: 'follow_path',
    KEY._7: 'wander'
}

class Agent(object):

    # NOTE: Class Object (not *instance*) variables!
    DECELERATION_SPEEDS = {
        'slow': 0.9,
        'normal': 0.5,
        'fast': 0.1
    }

    def __init__(self, world=None, scale=30.0, mass=1.0, mode='seek'):
        # keep a reference to the world object
        self.world = world
        self.mode = mode
        # where am i and where am i going? random start pos
        dir = radians(random()*360)
        self.pos = Vector2D(randrange(world.cx), randrange(world.cy))
        self.vel = Vector2D()
        self.heading = Vector2D(sin(dir), cos(dir))
        self.side = self.heading.perp()
        self.scale = Vector2D(scale, scale)  # easy scaling of agent size
        # self.force = Vector2D()  # current steering force
        self.acceleration = Vector2D() # current acceleration due to force
        self.mass = mass

        ### path to follow?
        self.path = Path()
        self.randomise_path()
        self.waypoint_threshold = 10.0

        ### new wander info
        self.wander_target = Vector2D(1, 0)
        self.wander_dist = 1.0 * scale
        self.wander_radius = 1.0 * scale
        self.wander_jitter = 1.0 * scale
        self.bRadius = scale

        # speed and force limits
        self.max_speed = 20.0 * scale
        self.max_force = 200.0

        # data for drawing this agent
        self.color = 'ORANGE'
        self.vehicle_shape = [
            Point2D(-1.0, 0.6),
            Point2D(1.0, 0.0),
            Point2D(-1.0, -0.6)
        ]

        # debug draw info?
        self.show_info = False

    def randomise_path(self):
        cx = self.world.cx  # width
        cy = self.world.cy  # height
        margin = min(cx, cy) * (1/6)    # use this for padding in the next line
        # self.path.create_random_path(num_pts, minx, miny, maxx, maxy)
        self.path.create_random_path(8, margin, margin, cx - margin, cy - margin)

    def calculate(self, delta):
        # calculate the current steering force
        mode = self.mode
        if mode == 'seek':
            accel = self.seek(self.world.target)
        elif mode == 'arrive_slow':
            accel = self.arrive(self.world.target, 'slow')
        elif mode == 'arrive_normal':
            accel = self.arrive(self.world.target, 'normal')
        elif mode == 'arrive_fast':
            accel = self.arrive(self.world.target, 'fast')
        elif mode == 'flee':
            accel = self.flee(self.world.target, delta)
        elif mode == 'follow_path':
            accel = self.follow_path()
        elif mode == 'wander':
            accel = self.wander(delta)
        else:
            accel = Vector2D()
        self.acceleration = accel
        return accel

    def update(self, delta):
        ''' update vehicle position and orientation '''
        acceleration = self.calculate(delta)
        # new velocity
        self.vel += acceleration
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

    def render(self, color='Red'):
        # Draw the triangle agent with color
        egi.set_pen_color(name=self.color)
        pts = self.world.transform_points(self.vehicle_shape, self.pos,
                                          self.heading, self.side, self.scale)
        # draw it!
        egi.closed_shape(pts)

        # draw wander info
        if self.mode == 'wander':
            # calculate the center of the wander circle in front of the agent.
            wnd_pos = Vector2D(self.wander_dist, 0)
            wld_pos = self.world.transform_point(wnd_pos, self.pos, self.heading, self.side)
            # draw the wander circle.
            egi.green_pen()
            egi.circle(wld_pos, self.wander_radius)
            # draw the wander target (little circle on the big circle).
            egi.red_pen()
            wnd_pos = (self.wander_target + Vector2D(self.wander_dist, 0))
            wld_pos = self.world.transform_point(wnd_pos, self.pos, self.heading, self.side)
            egi.circle(wld_pos, 3)

    def speed(self):
        return self.vel.length()

    # --------------------------------------------------------------------------

    def seek(self, target_pos):
        ''' move towards target position '''
        desired_vel = (target_pos - self.pos).normalise() * self.max_speed
        if (target_pos - self.pos).length() < 5:
            return -self.vel
        return desired_vel - self.vel

    def flee(self, hunter_pos, delta):
        ''' move away from hunter position '''
        to_hunter = hunter_pos - self.pos
        desired_vel = self.wander(delta)
        if to_hunter.length() < 250:
            desired_vel += ((self.pos - hunter_pos).normalise()) * self.max_speed * ((325 - to_hunter.length()) / 325)
        return desired_vel

        # ## add panic distance (second)
        # panic_dist = 1000.0
        # hunter = hunter_pos - self.pos
        # dist = hunter.length()
        #
        # if dist < panic_dist:
        #     ## add flee calculations (first)
        #     return (self.pos - hunter_pos).normalise() * self.max_speed
        #
        #     return Vector2D

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

    def follow_path(self):
        self.path.render()
        if self.path.is_finished():
            return self.arrive(self.path.current_pt(), 'slow')
        else:
            if (self.path.current_pt() - self.pos).length() < 50:
                self.path.inc_current_pt()
            else:
                return self.seek(self.path.current_pt())
        return Vector2D()

    def wander(self, delta):
        ''' Random wandering using a projected jitter circle. '''
        wt = self.wander_target

        # this behaviour is dependent on the update rate, so this line must
        # be included when using time independent framerate.
        jitter_tts = self.wander_jitter * delta

        # this time slice
        # first, add a small random vector to the target's position.
        wt += Vector2D(uniform(-1, 1) * jitter_tts, uniform(-1, 1) * jitter_tts)

        # re-project this new vector back on to a unit circle.
        wt.normalise()

        # increase the length of the vector to the same as the radius of the wander circle.
        wt *= self.wander_radius

        # move the target into a position WanderDist in front of the agent.
        target = wt + Vector2D(self.wander_dist, 0)

        # project the target into world space
        wld_target = self.world.transform_point(target, self.pos, self.heading, self.side)

        # and steer towards it
        return self.seek(wld_target)
