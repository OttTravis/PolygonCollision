# -*- coding: utf-8 -*-
"""
Created on Fri Oct 27 13:56:44 2017

@author: sinkovitsd
"""
import pygame
from vec2d import Vec2d
from coords import Coords
from polygon_stub import Polygon
from math import sqrt, acos, degrees, sin, cos
from random import uniform, randint, random

# Define some colors
BLACK    = (   0,   0,   0)
WHITE    = ( 255, 255, 255)
GREEN    = (   0, 255,   0)
RED      = ( 255,   0,   0)
BLUE     = (   0,   0, 255)
CYAN     = (   0, 255, 255)
MAGENTA  = ( 255,   0, 255)
YELLOW   = ( 255, 255,   0)
GRAY     = ( 127, 127, 127)

def random_color():
    return (randint(0,255), randint(0,255), randint(0,255))

def random_bright_color():
    i = randint(0,2)
    d = randint(1,2)
    c = int(256*random()**0.5)
    color = [0,0,0]
    color[i] = 255
    color[(i+d)%3] = c
    return color

def make_polygon(radius, n, angle=0, factor=1, axis=Vec2d(1,0)):
    axis = axis.normalized()
    vec = Vec2d(0, -radius).rotated(180/n+angle)
    p = []
    for i in range(n):
        v = vec.rotated(360*i/n)
        v += v.dot(axis)*(factor-1)*axis
        p.append(v)
    #print(p)
    return p

def make_rectangle(length, height, angle=0):
    points = (Vec2d(-0.5,-0.5),
              Vec2d(+0.5,-0.5),
              Vec2d(+0.5,+0.5),
              Vec2d(-0.5,+0.5),
              )
    c = cos(angle)
    s = sin(angle)
    for p in points:
        p.x *= length
        p.y *= height
        x = p.x*c - p.y*s
        y = p.y*c + p.x*s
        p.x = x
        p.y = y
    return points
        
def check_collision(a, b, result=[]):
    """ I'm using result as a convenient way to pass back a list of data,
        while still allowing a plain boolean as a return value.
        It keeps the code very compact. Polygon.py does the same. 
        You must use extend() because restult = rebinds the variable, 
        so the data doesn't make it back to the calling function. """
    result.clear()
    result1 = []
    result2 = []
    if a.check_collision(b, result1) and b.check_collision(a, result2):
        """ Pass back the result which has smaller overlap and return True. 
            For example:
                result.extend(result1)
                return True
                """
    return False       

def main():
    pygame.init()
 
    width = 800
    height = 600
    screen = pygame.display.set_mode([width,height])
    screen_center = Vec2d(width/2, height/2)
    coords = Coords(screen_center.copy(), 1, True)
    zoom = 100
    coords.zoom_at_coords(Vec2d(0,0), zoom) 
    
    # Used to manage how fast the screen updates
    clock = pygame.time.Clock()

    # Create initial objects to demonstrate
    objects = []
    points = (Vec2d(0,0),
              Vec2d(1,0),
              Vec2d(0,1),
              )
    zero = Vec2d(0,0)
    objects.append(Polygon(zero, zero, 1, make_polygon(1.5,5,0,1.5), RED))
    objects.append(Polygon(zero, zero, 1, make_polygon(2,3,0,0.5), BLUE))
    # -------- Main Program Loop -----------\
    seconds_per_frame = 0.5
    frame_rate = 1/seconds_per_frame
    done = False
    paused = True
    background_color = WHITE
    collided = False
    while not done:
        # --- Main event loop
        for event in pygame.event.get(): 
            if event.type == pygame.QUIT: # If user clicked close
                done = True
                paused = True
            elif event.type == pygame.MOUSEBUTTONDOWN: 
                paused = False
            elif event.type == pygame.KEYDOWN: 
                if event.key == pygame.K_ESCAPE:
                    done = True
                    paused = True 
                elif event.key == pygame.K_SPACE:
                    paused = not paused
                else:
                    paused = False
        
        if not paused:
            # If not overlapping, move objects to a new random position
            if not collided:
                for obj in objects:
                    x = uniform(width*0.25, width*0.75)
                    y = uniform(height*0.25, height*0.75)
                    obj.pos = coords.pos_to_coords(Vec2d(x,y))
                    obj.angle = uniform(0, degrees(360))
                    obj.update_points_normals()
    
            # Check for collision
            collided = False
            result = []
            for i1 in range(len(objects)):
                for i2 in range(i1):
                    if check_collision(objects[i1], objects[i2], result):
                        collided = True
        
        # Drawing
        if collided:
            background_color = YELLOW
        else:
            background_color = WHITE
        screen.fill(background_color) # wipe the screen

        for obj in objects:
            obj.draw(screen, coords) # draw object to screen

        if collided:
            (obj1, obj2, overlap, normal, point) = result
            pygame.draw.circle(screen, BLACK, coords.pos_to_screen(point).int(), 5)
            pygame.draw.line(screen, BLACK, coords.pos_to_screen(point).int(),
                             coords.pos_to_screen(point + overlap*normal).int())
            # Separate objects accoring to position
            """ Move obj1 overlap distance in the direction of normal. """
              
        # --- Update the screen with what we've drawn.
        pygame.display.update()
        
        # This limits the loop to the specified frame rate
        clock.tick(frame_rate)
        
    pygame.quit()

if __name__ == "__main__":
    try:
        main()
    except Exception:
        pygame.quit()
        raise
