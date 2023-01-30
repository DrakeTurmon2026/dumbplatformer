# Simple pygame program

# Import and initialize the pygame library
import pygame
import numpy
import math
pygame.init()

#note to self
#complete intersections should not be registered as a collision

# Set up the drawing window
screen = pygame.display.set_mode([1000, 1000])

# Run until the user asks to quit
playerpos = [500,850]

Blocks = []

clock = pygame.time.Clock()

class char:
    def __init__(self,startpos,maxspeed,frictionforce,stopforce,gravity):
        self.Position = startpos
        self.Velocity = [0,0]
        self.MaxSpeed = maxspeed or 128
        self.MaxAccel = self.MaxSpeed * 10
        self.gravity = gravity
        self.frictionforce = frictionforce
        self.stopforce = stopforce
        self.grounded = False
    def Jump(self, height):
        if self.grounded:
            self.Velocity[1] = math.sqrt(self.gravity*2*height) * -1
    def updatevelocity(self,wishdir,deltatime):
        #THIS IS FROM QUAKE III ARENA!!!!!!
        if self.grounded:
            self.Velocity = friction(self.Velocity, deltatime, self)

        #math
        currentspeed = numpy.dot(self.Velocity, wishdir)
        addspeed = numpy.clip(self.MaxSpeed - currentspeed,0,self.MaxAccel * deltatime)

        #this shortens the code a little by directly editing velocity instead of doing it in main
        self.Velocity = numpy.add(self.Velocity,numpy.multiply(wishdir,addspeed))
        #im shoving gravity here because its easy
        self.Velocity = numpy.add(self.Velocity,(0,self.gravity * deltatime))

player = char(playerpos,256,6,400,512)

class block:
    def __init__(self, x, y, sizex, sizey, cancollide):
        self.rect = pygame.rect.Rect(x or 0, y or 0,sizex or 100, sizey or 100)
        self.cancollide = cancollide or True

#add a floor
Blocks.append(block(0,1000,1000,100, True))

def magnitude(vec):
    return math.sqrt(vec[0]*vec[0] + vec[1]*vec[1])

def friction(vel, deltatime, plr):
    speed = magnitude(vel)
    drop = 0

    control = speed > plr.stopforce and plr.stopforce or speed
    drop += control*plr.frictionforce*deltatime

    newspeed = speed - drop
    if newspeed < 0:
        newspeed = 0
    if speed > 0:
        newspeed /= speed
    else:
        newspeed = 0

    return (vel[0]*newspeed,vel[1])

running = True
while running:
    dt = clock.tick(clock.get_fps())/1000
    
    # Did the user click the window close button?
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                player.Jump(128)
                

    # Fill the background with grey
    screen.fill((52, 52, 52))

    #quake movement will be good in 2d right?
    keys = pygame.key.get_pressed()
    xmove = (keys[pygame.K_RIGHT] and 1 or 0) - (keys[pygame.K_LEFT] and 1 or 0)
    move = (xmove,0)

    if magnitude(move) > 1:
        move = numpy.divide(move,abs(magnitude(move)))

    player.updatevelocity(move,dt)
    #vertical collisions
    player.grounded = False
    for i, col in enumerate(Blocks):
        if col.cancollide:
            #vertical collisions
            if player.Position[0] >= col.rect.x - 16 and player.Position[0] <= col.rect.x + col.rect.width + 16:
                if player.Position[1] > col.rect.y - 16 and player.Position[1] < col.rect.y + col.rect.height + 16:
                    #centered position of block
                    centeredblockpos = [col.rect.x + (col.rect.width / 2),col.rect.y + (col.rect.height / 2)]
                    #get what side of the block the player is on (ie)
                    leftright = centeredblockpos[0] > player.Position[0]
                    updown = centeredblockpos[1] > player.Position[1]
                    #pick contact direction priority
                    direct = numpy.subtract(player.Position, centeredblockpos)
                    if abs(direct[0]) > (col.rect.width/2) and abs(direct[1]) < ((col.rect.height/2) + 16):
                        if (leftright and player.Velocity[0] > 0) or (not leftright and player.Velocity[0] < 0):
                            player.Velocity[0] = 0
                        player.Position[0] = (leftright and col.rect.x - 16 or col.rect.x + col.rect.width + 16)
                    elif abs(direct[1]) > (col.rect.height/2) and abs(direct[1]) < ((col.rect.width/2) + 16):
                        player.grounded = True
                        if player.Velocity[1] > 0 or not updown:
                            player.Velocity[1] = 2
                        player.Position[1] = (updown and col.rect.y - 16 or col.rect.y + col.rect.height + 16)

    player.Position += numpy.multiply(player.Velocity,dt)
    #draw player as a square
    pygame.draw.rect(screen, (220, 0, 0), pygame.rect.Rect((screen.get_width()/2)-16,(screen.get_height()/2)-16,32,32))
    #draw blocks
    for i, blk in enumerate(Blocks):
        pygame.draw.rect(screen, (0,0,0),pygame.rect.Rect(blk.rect.left - player.Position[0] + (screen.get_width()/2), blk.rect.top - player.Position[1] + (screen.get_height()/2), blk.rect.width, blk.rect.height))
    # Flip the display
    pygame.display.flip()

# Done! Time to quit.
pygame.quit()