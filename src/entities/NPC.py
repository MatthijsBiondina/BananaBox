import pygame
import math
import numpy as np
from network.Vision import *
from network.Brain  import *

"""Class for an NPC. NPCs' behaviours are determined by a neural network"""
class NPC():
    blocking = True
    updateable = True

    #these are the controls NPCs have access to. Currently only the wasd keys are implemented for movement
    keys = {'1':False,'2':False,'3':False,
            'q':False,'w':False,'e':False,
            'a':False,'s':False,'d':False,
            'z':False,'x':False,'c':False,
            'left-mouse':False,'right-mouse':False}
    threshold = 0.6
    
    def __init__(self,name,x,y,o,hp,max_hp,sprite_name,color_heat,genome,model):
        self.name = name
        self.x = x
        self.y = y
        self.o = o
        self.hp = hp
        self.max_hp = max_hp
        self.sprites = self.loadSprites(sprite_name)
        self.model = model
        self.c_heat = color_heat
        
        self.maxmom = 6
        (self.x_grid,self.y_grid) = model.getGridPosition(x,y)
        self.x_mom  = 0
        self.y_mom  = 0
        self.d_mom  = 0.33
        self.speed  = 2

        self.V = Vision( self.model.getGrid(), 11, self.model)
        self.genome = genome
        self.network = Brain(genome)
        
    #Initialize the sprites for this NPC.
    #Animations are not yet implemented
    #The sprite displayed will depend only on the orientation of the NPC for now
    def loadSprites(self,sprite_name):
        path = "../res/sprites/%s/" % (sprite_name)
        sprites = {8:pygame.image.load(path+'N.png' ),
                   9:pygame.image.load(path+'NE.png'),
                   6:pygame.image.load(path+'E.png' ),
                   3:pygame.image.load(path+'SE.png'),
                   2:pygame.image.load(path+'S.png' ),
                   1:pygame.image.load(path+'SW.png'),
                   4:pygame.image.load(path+'W.png' ),
                   7:pygame.image.load(path+'NW.png')}
        return sprites

    #Currently unused
    #Deal damage to the NPC
    def damage(self,amount):
        self.hp = max(0,self.hp-amount)

    #Currently unused
    #Heal the NPC
    def heal(self,amount):
        self.hp = min(self.max_hp, self.hp+amount)

    #Update the NPC one game tick
    def update(self):
        #First run an iteration of the ANN
        self.queryNetwork()

        #Update movement related parameters based on current value and ANN output
        (self.x_mom, self.y_mom)    = self.updateMoment(self.x_mom, self.y_mom)
        (self.x,self.y,x_spd,y_spd) = self.updateCoords(self.x,self.y,self.x_mom,self.y_mom)
        self.o                      = self.determineOrientation(x_spd,y_spd)

        #Update real and grid positions based on movement parameters
        old_x_grid = self.x_grid
        old_y_grid = self.y_grid
        (self.x_grid,self.y_grid) = self.model.getGridPosition(self.x,self.y)

        #Return both the old and new positions on the grid.
        #If old and new positions differ, the model will need to update its game logic
        return (old_x_grid,old_y_grid,self.x_grid,self.y_grid)

    """NETWORK METHODS"""

    #Run an iteration of the ANN
    def queryNetwork(self):
        #Construct inputs of the network.
        #Not yet implemented inputs remain 0
        #NB, since the bias node is not part of the input, these index positions and the respective input nodes are offset by 1
        #   so index 0 goes into node 1
        net_input = [0]*64

        #Construct the visual input for this frame
        vis_input = self.getVision()
        for i in range(10,32):
            net_input[i] = vis_input[i-10]

        #Query the ANN with constructed inputs
        output = self.network.query(net_input)

        #Update NPC's controls
        self.controls(output)
        
    #Determine which keys are pressed based on the output of the ANN
    #Output index and respective key must be consistend, o/w evolution is impossible
    def controls(self,output):
        #If activation of an output node is greater than the threshold,
        #the respective key is pressed
        t = self.threshold
        self.keys['1']           = output[0] > t
        self.keys['2']           = output[1] > t
        self.keys['3']           = output[2] > t
        self.keys['q']           = output[3] > t
        self.keys['w']           = output[4] > t
        self.keys['e']           = output[5] > t
        self.keys['a']           = output[6] > t
        self.keys['s']           = output[7] > t
        self.keys['d']           = output[8] > t
        self.keys['z']           = output[9] > t
        self.keys['x']           = output[10] > t
        self.keys['c']           = output[11] > t
        self.keys['left-mouse']  = output[12] > t
        self.keys['right-mouse'] = output[13] > t
        

    """MOVEMENT METHODS"""

    #Based on speed in x and y direction, determine which direction the NPC is facing
    #   orientations are represented as numbers which correspond with the directions of the numbers on the numpad
    def determineOrientation(self,dx,dy):
        o = self.o
        if (self.keys['w'] or self.keys['a'] or self.keys['s'] or self.keys['d']) and not (dx == 0 and dy == 0):
            if dx > 2*abs(dy):        o = 6 #east
            elif -dx > 2*abs(dy):     o = 4 #west
            elif dy > 2*abs(dx):      o = 2 #south
            elif -dy > 2*abs(dx):     o = 8 #north
            elif dx >= 0 and dy >= 0: o = 3 #south-east
            elif dx <= 0 and dy >= 0: o = 1 #south-west
            elif dx <= 0 and dy <= 0: o = 7 #north-west
            elif dx >= 0 and dy <= 0: o = 9 #north-east
        return o

    #Based on the previous state and the keys that the NPC is pressing, update the momentum for the current frame
    #NB actual speed is influenced indirectly through momentum; this means that an NPC has to press a button for a few consecutive frames
    #   to accelerate in that direction. The reason for this is that NPCs don't change direction every second or so to see what is behind
    #   them (they can only see forward). With this method, they are still allowed to do so, but it will come at a penalty to their movement
    #   speed.
    #Controls are interpreted relative to the direction the NPC is facing, so 'w' moves the NPC in the direction it
    #is currently facing, 's' slows down or turns around, 'd' moves to the right and 'a' moves to the left
    def updateMoment(self,x_mom,y_mom):
        w = self.keys['w']
        a = self.keys['a']
        s = self.keys['s']
        d = self.keys['d']
        dx = x_mom
        dy = y_mom
        dm = self.d_mom #how much momentum can change in a frame

        #the change in momentum (dx and dy for x- and y-direction) based on pressed keys
        #NB (0,0) is at the top left corner of the screen, so y-direction is reversed (ie. positive is south)
        if self.o == 8:
            dx = (dx + (dm if d else 0) - (dm if a else 0)) if (d or a) else ( max( dx - dm, 0 ) if dx > 0 else min( dx + dm, 0 ) )
            dy = (dy + (dm if s else 0) - (dm if w else 0)) if (s or w) else ( max( dy - dm, 0 ) if dy > 0 else min( dy + dm, 0 ) )
        if self.o == 9:
            dx = (dx + (dm if w or d else 0) - (dm if s or a else 0)) if (w or a or s or d) and not ((w and a)or(s and d)) else ( max( dx - dm, 0 ) if dx > 0 else min( dx + dm, 0 ) )
            dy = (dy + (dm if s or d else 0) - (dm if w or a else 0)) if (w or a or s or d) and not ((w and d)or(a and s)) else ( max( dy - dm, 0 ) if dy > 0 else min( dy + dm, 0 ) )
        if self.o == 6:
            dx = (dx + (dm if w else 0) - (dm if s else 0)) if (w or s) else ( max( dx - dm, 0 ) if dx > 0 else min( dx + dm, 0 ) )
            dy = (dy + (dm if d else 0) - (dm if a else 0)) if (d or a) else ( max( dy - dm, 0 ) if dy > 0 else min( dy + dm, 0 ) )
        if self.o == 3:
            dx = (dx + (dm if w or a else 0) - (dm if s or d else 0)) if (w or a or s or d) and not ((w and d)or(s and a)) else ( max( dx - dm, 0 ) if dx > 0 else min( dx + dm, 0 ) )
            dy = (dy + (dm if w or d else 0) - (dm if s or a else 0)) if (w or a or s or d) and not ((w and a)or(s and d)) else ( max( dy - dm, 0 ) if dy > 0 else min( dy + dm, 0 ) )
        if self.o == 2:
            dx = (dx + (dm if a else 0) - (dm if d else 0)) if (a or d) else ( max( dx - dm, 0 ) if dx > 0 else min( dx + dm, 0 ) )
            dy = (dy + (dm if w else 0) - (dm if s else 0)) if (w or s) else ( max( dy - dm, 0 ) if dy > 0 else min( dy + dm, 0 ) )
        if self.o == 1:
            dx = (dx + (dm if s or a else 0) - (dm if w or d else 0)) if (w or a or s or d) and not ((w and a)or(s and d)) else ( max( dx - dm, 0 ) if dx > 0 else min( dx + dm, 0 ) )
            dy = (dy + (dm if w or a else 0) - (dm if s or d else 0)) if (w or a or s or d) and not ((w and d)or(s and a)) else ( max( dy - dm, 0 ) if dy > 0 else min( dy + dm, 0 ) )
        if self.o == 4:
            dx = (dx + (dm if s else 0) - (dm if w else 0)) if (s or w) else ( max( dx - dm, 0 ) if dx > 0 else min( dx + dm, 0 ) )
            dy = (dy + (dm if a else 0) - (dm if d else 0)) if (a or d) else ( max( dy - dm, 0 ) if dy > 0 else min( dy + dm, 0 ) )
        if self.o == 7:
            dx = (dx + (dm if s or d else 0) - (dm if w or a else 0)) if (w or a or s or d) and not ((w and d)or(s and a)) else ( max( dx - dm, 0 ) if dx > 0 else min( dx + dm, 0 ) )
            dy = (dy + (dm if s or a else 0) - (dm if w or d else 0)) if (w or a or s or d) and not ((w and a)or(s and d)) else ( max( dy - dm, 0 ) if dy > 0 else min( dy + dm, 0 ) )
            
        #update the momentum in x and y direction
        x_mom = min(dx,self.maxmom) if dx>0 else max(dx,-self.maxmom)
        y_mom = min(dy,self.maxmom) if dy>0 else max(dy,-self.maxmom)

        #determine hypothesized next x and y coords to prevent walking in walls
        x_hyp = self.x + self.mom2spd( x_mom )
        y_hyp = self.y + self.mom2spd( y_mom )

        #if the current momentum in a direction would put any part of the NPC in a blocked square, the momentum in that direction is instead set to 0
        x_mom = max(0,x_mom) if self.model.isBlocked(x_hyp-16,self.y-16,self.name) or self.model.isBlocked(x_hyp-16,self.y+16,self.name) else x_mom
        x_mom = min(0,x_mom) if self.model.isBlocked(x_hyp+16,self.y-16,self.name) or self.model.isBlocked(x_hyp+16,self.y+16,self.name) else x_mom
        y_mom = max(0,y_mom) if self.model.isBlocked(self.x-16,y_hyp-16,self.name) or self.model.isBlocked(self.x+16,y_hyp-16,self.name) else y_mom
        y_mom = min(0,y_mom) if self.model.isBlocked(self.x-16,y_hyp+16,self.name) or self.model.isBlocked(self.x+16,y_hyp+16,self.name) else y_mom

        return (x_mom,y_mom)

    #move the NPC based on momentum
    def updateCoords(self,x,y,x_mom,y_mom):
        x_spd = self.mom2spd( x_mom )
        y_spd = self.mom2spd( y_mom )
        #update absolute position
        x = x + x_spd
        y = y + y_spd
        return (x,y,x_spd,y_spd)

    #convert momentum to speed
    #the relationship between momentum and speed is sigmoidal. That way, at low speeds acceleration is linear and at higher speeds, acceleration flattens out
    def mom2spd( self,mom ):
        return (1 / (1 + math.exp(-mom)) - 0.5) * 2 * self.speed

    """GETTER METHODS"""

    #Construct the vision inputs
    def getVision(self):
        inputs = []
        for i in range(11):
            (dheat,cheat) = self.V.getVision(self.x_grid,self.y_grid,self.o, 11-i )
            inputs.append(dheat)
            inputs.append(cheat)
        return inputs

    def getLocation(self):
        return (self.x,self.y,self.o)

    def getName(self):
        return self.name

    def getSprite(self):
        return self.sprites[self.o]

    def getBlocking(self):
        return self.blocking

    def canUpdate(self):
        return self.updateable

    def getGenome(self):
        return self.genome

    def getNetwork(self):
        return self.network

    def getCHeat(self):
        return self.c_heat

    def toString(self):
        return "%s @ (%s,%s) facing %s" % (self.name, str(self.x), str(self.y), str(self.o))

