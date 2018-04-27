# -*- coding: utf-8 -*-
"""
Created on Wed Mar  7 15:52:54 2018

@author: sinkovitsd
"""
import pygame
from vec2d import Vec2d

class Wall:
    def __init__(self, pos, normal, color, mass=1e99, vel=Vec2d(0,0)):
        self.pos = pos.copy()
        self.normal = normal.normalized() # makes a copy automatically
        self.pos = pos.copy()
        self.vel = vel.copy()
        self.mass = mass
        self.mom = self.vel*self.mass
        self.angvel = 0
        self.angmom = 0
        self.moment = 1e99
        self.color = color
        self.force = Vec2d(0,0)
        self.type = "wall"
    
    def update_mom(self, dt):
        self.mom += self.force*dt
        self.update_vel()
        
    def set_vel(self, vel):
        self.vel.copy_in(vel)
        self.mom.copy_in(self.vel*self.mass)

    def update_vel(self):
        self.vel.copy_in(self.mom/self.mass)

    def update_pos(self, dt):
        self.pos += self.vel*dt

    def update(self, dt):
        self.update_mom(dt)
        self.update_pos(dt)
                
    def impulse(self, imp, point=None):
        self.mom += imp
        self.update_vel()

    def nudge(self, nudge, point=None):
        pass

    def draw(self, screen, coords):
        pos = coords.pos_to_screen(self.pos)
        normal = coords.unitvec_to_other(self.normal)
        X = screen.get_width()-1
        Y = screen.get_height()-1
        perp = normal.perpendicular()
        if perp.x == 0:
            start = Vec2d(pos.x, 0)
            end   = Vec2d(pos.x, Y)
        elif perp.y == 0:
            start = Vec2d(0, pos.y)
            end   = Vec2d(X, pos.y)
        else:
            s = []
            s.append((0-pos.x)/perp.x)                
            s.append((0-pos.y)/perp.y)                
            s.append((X-pos.x)/perp.x)                
            s.append((Y-pos.y)/perp.y)
            s.sort()
            start = pos + perp*s[1]
            end   = pos + perp*s[2]
        pygame.draw.line(screen, self.color, start, end, 1)
    
    def check_collision(self, other, result=[]):
        if other.type == "polygon":
            result.extend([self, other, 1e99, None, None])
            return True
        elif other.type == "wall":
            return False
        