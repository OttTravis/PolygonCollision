# -*- coding: utf-8 -*-

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

gameOver = False
paused = True

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

def makeRandomPolygon():
    sideCount = randint(3, 8)
    radius = 0.3
    return make_polygon(radius, sideCount)
    
        
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
    mu = 0.7
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
        
        if b.type == "wall":
            global gameOver
            global paused
            gameOver = True
            paused = True
 
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
    # length = 2
    # height = 1
    
    # objects.append(Polygon(Vec2d(0,-1), Vec2d(0,0), 1, make_rectangle(length, height), GRAY, 0, -1))
    # objects.append(Polygon(Vec2d(-0.5,1), Vec2d(0,0), 1, make_polygon(0.2,4,0,10), RED, 0, 1))
    # objects.append(Polygon(Vec2d(1,0), Vec2d(0,0), 1, make_polygon(0.3,7,0,3), BLUE, 0, -0.4))
    # objects.append(Polygon(Vec2d(-1,0), Vec2d(0,0), 1, make_polygon(1,3,0,0.5), GREEN, 0, 2))
    
    #
    objects.append(Polygon(Vec2d(0, -2), Vec2d(0,0), 9000000000, make_rectangle(4, 0.1), BLUE, 0, 0,"stackSurface"))
    # Walls
    objects.append(Wall(Vec2d(0,-3), Vec2d(0,1), BLACK))
    # objects.append(Wall(Vec2d(-1,-3), Vec2d(-1,2), BLACK))
    # objects.append(Wall(Vec2d(-1,-3), Vec2d(0,1), BLACK))

    # -------- Main Program Loop -----------\
    #REDUCE TIME STEP TO INCREASE ACCURACY
    frame_rate = 60
    n_per_frame = 1
    playback_speed = 1 # 1 is real time, 10 is 10x real speed, etc.
    dt = playback_speed/frame_rate/n_per_frame
    #print("timestep =", dt)
    done = False
    
    score = 0
    
    cooldown = frame_rate * 2
    gameMouse = pygame.mouse
    textFont = pygame.font.Font(None, 40)
    gameOverFont = pygame.font.Font(None, 100)
    
    max_collisions = 10
    result = []
    while not done:
        global paused
        # Mouse values for loop
        mouseVec = Vec2d(gameMouse.get_pos()[0], gameMouse.get_pos()[1])
        coordMouseVec = coords.pos_to_coords(mouseVec)
        # --- Main event loop
        for event in pygame.event.get(): 
            if event.type == pygame.QUIT: # If user clicked close
                done = True
                paused = True
            elif event.type == pygame.MOUSEBUTTONDOWN and not gameOver:
                if (paused == True):
                    paused = False
                else:
                    if (cooldown > 2 * frame_rate):
                        paused = True
                        objects.append(Polygon(coordMouseVec, Vec2d(0,0), 1, makeRandomPolygon(), random_color()))
                        score = score + 1
                        cooldown = 0
                        
            elif event.type == pygame.KEYDOWN: 
                if event.key == pygame.K_ESCAPE:
                    done = True
                    paused = True 
                #elif event.key == pygame.K_SPACE:
                 #   paused = not paused
                #else:
                 #   paused = False
        
        # In paused state, allow player to set position of new polygon
        if paused:
            if(objects[-1].type == "polygon"):
                objects[-1].pos = coordMouseVec
           #     print("Updating polygon position")
                
        if not paused:
            for N in range(n_per_frame):
                # Physics
                # Calculate the force on each object
                for obj in objects:
                    if obj.type != "wall" and obj.type != "stackSurface":  
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

        scoreSurface = textFont.render("Score: " + str(score), 0, BLUE)
        gameOverSurface = gameOverFont.render("GAME OVER", 0, RED)
        screen.blit(scoreSurface, (220,530))
        if gameOver:
            screen.blit(gameOverSurface, (width/2 - width/4, height/2- height/10))
        
        # --- Update the screen with what we've drawn.
        pygame.display.update()
        
        # This limits the loop to the specified frame rate
        clock.tick(frame_rate)
        
        # Increment the cooldown
        cooldown = cooldown + 1
        
    pygame.quit()

if __name__ == "__main__":
    try:
        main()
    except Exception:
        pygame.quit()
        raise
