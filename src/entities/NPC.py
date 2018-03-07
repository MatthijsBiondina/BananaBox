import pygame
import math
import numpy as np
from network.Vision import *
from network.Brain  import *

class NPC():
    blocking = True
    updateable = True
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
        
    def damage(self,amount):
        self.hp = max(0,self.hp-amount)

    def heal(self,amount):
        self.hp = min(self.max_hp, self.hp+amount)

    def update(self):
        self.queryNetwork()

        (self.x_mom, self.y_mom)    = self.updateMoment(self.x_mom, self.y_mom)
        (self.x,self.y,x_spd,y_spd) = self.updateCoords(self.x,self.y,self.x_mom,self.y_mom)
        self.o                      = self.determineOrientation(x_spd,y_spd)

        old_x_grid = self.x_grid
        old_y_grid = self.y_grid
        (self.x_grid,self.y_grid) = self.model.getGridPosition(self.x,self.y)
        return (old_x_grid,old_y_grid,self.x_grid,self.y_grid)

    """NETWORK METHODS"""

    def queryNetwork(self):
        net_input = [0]*64
        vis_input = self.getVision()
        for i in range(10,32):
            net_input[i] = vis_input[i-10]
        output = self.network.query(net_input)
        self.controls(output)
        

    def controls(self,output):
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
    
    def determineOrientation(self,dx,dy):
        o = self.o
        if (self.keys['w'] or self.keys['a'] or self.keys['s'] or self.keys['d']) and not (dx == 0 and dy == 0):
            if dx > 2*abs(dy):        o = 6
            elif -dx > 2*abs(dy):     o = 4
            elif dy > 2*abs(dx):      o = 2
            elif -dy > 2*abs(dx):     o = 8
            elif dx >= 0 and dy >= 0: o = 3
            elif dx <= 0 and dy >= 0: o = 1
            elif dx <= 0 and dy <= 0: o = 7
            elif dx >= 0 and dy <= 0: o = 9
        return o

    def updateMoment(self,x_mom,y_mom):
        w = self.keys['w']
        a = self.keys['a']
        s = self.keys['s']
        d = self.keys['d']
        dx = x_mom
        dy = y_mom
        dm = self.d_mom

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
            
        
    

        
        #if   x_mom > 0: x_mom = max(0,min( self.maxmom, x_mom + (self.d_mom if keys['d'] and not keys['a'] else -self.d_mom)))
        #elif x_mom < 0: x_mom = min(0,max(-self.maxmom, x_mom - (self.d_mom if keys['a'] and not keys['d'] else -self.d_mom)))
        #else:           x_mom = x_mom + (self.d_mom if keys['d'] else 0) - (self.d_mom if keys['a'] else 0)

        #if   y_mom > 0: y_mom = max(0,min( self.maxmom, y_mom + (self.d_mom if keys['s'] and not keys['w'] else -self.d_mom)))
        #elif y_mom < 0: y_mom = min(0,max(-self.maxmom, y_mom - (self.d_mom if keys['w'] and not keys['s'] else -self.d_mom)))
        #else:           y_mom = y_mom + (self.d_mom if keys['s'] else 0) - (self.d_mom if keys['w'] else 0)

        x_mom = min(dx,self.maxmom) if dx>0 else max(dx,-self.maxmom)
        y_mom = min(dy,self.maxmom) if dy>0 else max(dy,-self.maxmom)

        #determine hypothesized next x and y coords to prevent walking in walls
        x_hyp = self.x + self.mom2spd( x_mom )
        y_hyp = self.y + self.mom2spd( y_mom )

        #you can't walk through walls:
        x_mom = max(0,x_mom) if self.model.isBlocked(x_hyp-16,self.y-16,self.name) or self.model.isBlocked(x_hyp-16,self.y+16,self.name) else x_mom
        x_mom = min(0,x_mom) if self.model.isBlocked(x_hyp+16,self.y-16,self.name) or self.model.isBlocked(x_hyp+16,self.y+16,self.name) else x_mom
        y_mom = max(0,y_mom) if self.model.isBlocked(self.x-16,y_hyp-16,self.name) or self.model.isBlocked(self.x+16,y_hyp-16,self.name) else y_mom
        y_mom = min(0,y_mom) if self.model.isBlocked(self.x-16,y_hyp+16,self.name) or self.model.isBlocked(self.x+16,y_hyp+16,self.name) else y_mom

        return (x_mom,y_mom)

    def updateCoords(self,x,y,x_mom,y_mom):
        x_spd = self.mom2spd( x_mom )
        y_spd = self.mom2spd( y_mom )
        #update absolute position
        x = x + x_spd
        y = y + y_spd
        return (x,y,x_spd,y_spd)

    def mom2spd( self,mom ):
        return (1 / (1 + math.exp(-mom)) - 0.5) * 2 * self.speed

    """GETTER METHODS"""

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

