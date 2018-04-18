# -*- coding: utf-8 -*-
"""
Created on Fri Oct 27 13:56:44 2017

@author: sinkovitsd
"""
from vec2d import Vec2d

class Coords:
    def __init__(self, origin=Vec2d(0,0), scale=1, yflip=False):
        self.scale = scale
        self.origin = origin.copy()
        self.yflip = yflip
        
    # Scales scalar values from internal (coords) units to screen (pixel) units
    def scalar_to_screen(self, scalar):
        return self.scale*scalar

    # Scales scalar values from screen (pixel) units to internal (coords) units
    def scalar_to_coords(self, scalar):
        return scalar/self.scale
    
    # Scales and translates position vectors from internal (coords) units to screen (pixel) units
    def pos_to_screen(self, pos):
        v = pos.copy()
        if self.yflip:
            v.y *= -1    
        return self.origin + self.scale*v
    
    # Scales and translates position vectors from screen (pixel) units to internal (coords) units
    def pos_to_coords(self, pos):
        v = (pos - self.origin)/self.scale
        if self.yflip:
            v.y *= -1
        return v
    
    # Scales vector values from internal (coords) units to screen (pixel) units
    def vec_to_screen(self, vec):
        v = self.scale*vec
        if self.yflip:
            v.y *= -1
        return v
     
    # Scales vector values from screen (pixel) units to internal (coords) units
    def vec_to_coords(self, vec):
        v = vec/self.scale
        if self.yflip:
            v.y *= -1
        return v

    # Returns a unit vector for the other coordinate system (just flips y or does nothing)
    def unitvec_to_other(self, unit):
        v = unit.copy()
        if self.yflip:
            v.y *= -1
        return v

    # Translates the screen view by a vector in screen (pixel) units
    def pan_in_screen(self, vec):
        self.origin -= vec

    # Translates the screen view by a vector in internal (coords) units
    def pan_in_coords(self, vec):
        v = self.vec_to_screen(vec)
        self.pan_in_screen(v)
        
    # Zooms in by the given factor at a location given in screen (pixel) units
    def zoom_at_screen(self, center, factor):
        self.origin -= center
        self.origin *= factor
        self.origin += center
        self.scale *= factor
    
    # Zooms in by the given factor at a location given in screen (pixel) units
    def zoom_at_coords(self, center, factor):
        c = self.pos_to_screen(center)
        self.zoom_at_screen(c, factor)
        
    # Pans the screen view such that a location in screen (pixel) units 
    # matches a location in internal (coords) units
    def match_screen_and_coords(self, screen=Vec2d(0,0), coords=Vec2d(0,0)):
        v = self.scale*coords
        if self.yflip:
            v.y *= -1
        self.origin.copy_in(screen - v)
