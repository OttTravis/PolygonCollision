# -*- coding: utf-8 -*-
"""
Created on Fri Oct 27 13:56:44 2017

@author: sinkovitsd
"""
import pygame
from vec2d import Vec2d
from coords import Coords
from polygon_stub import Polygon
from wall import Wall
from math import sqrt, acos, degrees, sin, cos
from random import uniform, randint, random

# Define some colors
BLACK    = (   0,   0,   0)
WHITE    = ( 255, 255, 255)
GREEN    = (   0, 255,   0)
RED      = ( 255,   0,   0)
BLUE     = (   0,   0, 255)
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
    result.clear()
    result1 = []
    result2 = []
    if a.check_collision(b, result1) and b.check_collision(a, result2):
        #print("collision")
        #print(a.color, result1[2:])
        #print(b.color, result2[2:])
        if result1[2] < result2[2]: # compare overlaps, which is smaller
            result.extend(result1)
        else:
            result.extend(result2)
        return True
    return False       

def resolve_collision(result):
    (a, b, d, n, pt) = result
    e = 0.7
    mu = 0.4
    m = a.mass*b.mass/(a.mass + b.mass) # reduced mass
    
    t = n.perpendicular()
    # depenetrate
    a.pos = a.pos + n * d
    # distance vectors
    
    # relative velocity of points in contact
    # target velocity change (delta v)
    ra = pt - a.pos
    ran = ra.dot(n)
    rat = ra.dot(t)
    
    rb = pt - b.pos
    rbn = rb.dot(n)
    rbt = rb.dot(t)
    
    vrel = (a.vel + a.angvel * ra.perpendicular()) - (b.vel + b.angvel * rb.perpendicular())
    
    chgVn = -(1 + e) * vrel.dot(n)
    chgVt = -vrel.dot(t)
    
    # matrix [[A B][C D]] [Jn Jt]T = [dvn dvt]T
    
    A = ((1/a.mass) + ((rat**2) / a.moment)) + ((1/b.mass) + (rbt**2)/b.moment)
    
    B = (-(ran * rat) / a.moment) - ((rbn * rbt) / b.moment)
    
    C = (-(ran * rat) / a.moment) - ((rbn * rbt) / b.moment)
    
    D = ((1/a.mass) + ((rat**2)/ a.moment)) + ((1/b.mass) + ((rbt**2)/b.moment))
    
    det = (A * D) - (B * C)
    

    
    # Solve matrix equation
    #if they are heading towards each other
    if chgVn > 0:
        #perfect Friction
        Jn = (1 / det) * ((D * chgVn) - (B * chgVt))
        Jt = (1 / det) * ((-C * chgVn) + (A * chgVt))
        if abs(Jt) > mu*Jn:
            #slinding Friction
            s = 0
            if Jt > 0:
                s = 1
            else:
                s = -1  
            A = ((1/a.mass) + ((rat**2) / a.moment)) + ((1/b.mass) + (rbt**2)/b.moment)
            B = (-(ran * rat) / a.moment) - ((rbn * rbt) / b.moment)
            C = -s*mu
            D = 1
            det = (A * D) - (B * C)
            Jn = (1/det) * ((D * chgVn) - (B * chgVt))
            Jt = s * mu * Jn
        # check if friction is strong enough to prevent slipping
        J = (Jn*n) + (Jt*t)
        a.impulse( J, pt)
        b.impulse(-J, pt)
 
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
              Vec2d(1,0.5),
              Vec2d(0.5,0.5),
              Vec2d(0.5,1),
              Vec2d(0,1),
              )
    #area = 2*1
    #print(area/12*(2**2 + 1**2))
    #area = 0.5*points[1].cross(points[2])
    #print(area)
    #print(abs(area/18*(points[1].mag2() + points[2].mag2() - points[1].dot(points[2]))))
    length = 2
    height = 1
    area = length*height
    objects.append(Polygon(Vec2d(0,-1), Vec2d(0,0), 1, make_rectangle(length, height), GRAY, 0, -1))
    objects.append(Polygon(Vec2d(-0.5,1), Vec2d(0,0), 1, make_polygon(0.2,4,0,10), RED, 0, 1))
    objects.append(Polygon(Vec2d(1,0), Vec2d(0,0), 1, make_polygon(0.3,7,0,3), BLUE, 0, -0.4))
    objects.append(Polygon(Vec2d(-1,0), Vec2d(0,0), 1, make_polygon(1,3,0,0.5), GREEN, 0, 2))
    
    # Walls
    objects.append(Wall(Vec2d(-1,-3), Vec2d(1,1), BLACK))
    objects.append(Wall(Vec2d(-1,-3), Vec2d(-1,2), BLACK))
    objects.append(Wall(Vec2d(-1,-3), Vec2d(0,1), BLACK))

    # -------- Main Program Loop -----------\
    #REDUCE TIME STEP TO INCREASE ACCURACY
    frame_rate = 60
    n_per_frame = 1
    playback_speed = 1 # 1 is real time, 10 is 10x real speed, etc.
    dt = playback_speed/frame_rate/n_per_frame
    #print("timestep =", dt)
    done = False
    paused = True
    max_collisions = 10
    result = []
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
            for N in range(n_per_frame):
                # Physics
                # Calculate the force on each object
                for obj in objects:
                    if obj.type != "wall":  
                        obj.force.zero()
                        obj.force += obj.mass*Vec2d(0,-10) # gravity
           
                # Move each object according to physics
                for obj in objects:
                    obj.update(dt)
                    
                for i in range(max_collisions):
                    collided = False
                    for i1 in range(len(objects)):
                        for i2 in range(i1):
                            if check_collision(objects[i1], objects[i2], result):
                                resolve_collision(result)
                                collided = True
                    if not collided: # if all collisions resolved, then we're done
                        break
 
        # Drawing
        screen.fill(WHITE) # wipe the screen
        for obj in objects:
            obj.draw(screen, coords) # draw object to screen

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
