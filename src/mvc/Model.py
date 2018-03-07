import numpy as np
import time
import random

from .Controller         import *
from .View               import *
from tools.DEBUG         import *
from grid.GridCreator    import *
from tools.MyThread      import *
from genetics.Genome     import *
from genetics.Evolution  import *
from network.Brain       import *
from network.Vision      import *
from entities.NPC        import *
from entities.PC         import *
from entities.Consumable import *

import os

class Model:
    grid = []
    manual = False
    print_fps = True
    print_score = False
    gen_idx = 0

    map_name = "02.jpg"
    
    def __init__(self,maxframes):
        self.settings   = self.initSettings()
        self.sim_frames = int(self.settings['sim_frames'])
        self.controller = Controller(self)
        self.view       = View(self)
        self.crashed    = False
        self.grid       = self.initGrid()
        self.keys       = {}
        self.reader     = GenomeReader(self)

        self.evolution  = Evolution(self)
        self.evolution.loadGenomes('../res/genomes',1000)
        
        self.entities   = {'food':Consumable('food',400,300,'Food',0.5,self),
                           'player':NPC('player',400,220,2,10,10,'PC',1,self.reader.makeGenome('../res/genomes/000000.dna'),self)}
        self.grid       = self.addEntities2Grid()
        
        self.score = 0
        self.maxframes = 0


        self.startThreads()
        
        
    """INITIALIZATION"""
        
    def initSettings(self):
        settings = {}
        with open('../res/settings.txt','r') as f:
            for line in f:
                if len(line)>1 and not line[0]=='#':
                    line_data = (line.rstrip()).split("=")
                    line_data = [(d.rstrip()).lstrip() for d in line_data]
                    settings[line_data[0]] = line_data[1] if not line_data[1].isdigit() else float(line_data[1])
        return settings

    def initGrid(self):
        self.builder = GridCreator(self)
        grid = self.builder.buildGrid("../res/grids/" + self.map_name)
        return grid

    def addEntities2Grid(self):
        return self.builder.addEntities( self.grid )

    def loadGenome(self):
        reader = GenomeReader(self)
        genome = reader.makeGenome('../res/genomes/000000.dna')
        return genome

    def loadNetwork(self,genome):
        return Brain(genome)

    def startThreads(self):
        c_thread = self.controller.start()
        v_thread = self.view.start()
        m_thread = MyThread( 3, "ModelThread", self.loop )
        c_thread.start()
        v_thread.start()
        m_thread.start()
        c_thread.join()
        v_thread.join()
        m_thread.join()

    def reset(self):
        (self.gen_idx,genome) = self.evolution.getNextGenome()
        self.entities   = {'food':Consumable('food',400,300,'Food',0.5,self),
                           'player':NPC('player',400,220,2,10,10,'PC',1,genome,self)}
        self.grid       = self.addEntities2Grid()
        self.keys       = {}
        self.genome     = self.loadGenome()
        self.network    = self.loadNetwork(self.genome)
        self.score = 0
    
    """GAME LOOP"""

    def loop(self):
        start_time = time.time()
        last_frame_time = time.time()
        tmp = 0
        epoch = 0
        stop = False
        while not self.crashed:
            epoch += 1
            if epoch % 10 == 0:
                self.settings = self.initSettings()
                self.sim_frames = int(self.settings['sim_frames'])
            self.reset()
            c_frame = 0
            stopped = 0
            while not self.crashed and c_frame < self.sim_frames:
                tmp += 1
                c_frame += 1
                last_frame_time = self.sleep(last_frame_time)
                for _,e in self.entities.items():
                    if e.canUpdate():
                        (oldx,oldy,newx,newy) = e.update()
                        #update position in the grid
                        if oldx != newx or oldy != newy:
                            stopped = 0
                            self.grid[oldx][oldy].remEntity(e.getName())
                            self.grid[newx][newy].addEntity(e.getName())
                            if self.grid[newx][newy].contains('food'):
                                self.grid[newx][newy].remEntity('food')
                                self.spawnFood()
                                self.score += 1
                                if self.print_score:
                                    print("Score: " + str(self.score), end='\r')
                        else:
                            stopped += 1

                if tmp % 100 == 0:
                    if self.print_fps:
                        print("Running @ %.2f fps" % ( float(tmp) / (time.time() - start_time) ), end='\r')
                    start_time = time.time()
                    tmp = 0
                if stopped >= 300:
                    self.score -= 1
                    stopped = 0
                    break
            self.evolution.reportFitness(self.gen_idx,self.score+1.)
            c_frame = 0
        
        

    def sleep(self,last_frame_time):
        sleep_time = 1./self.settings['game_FPS'] - (time.time() - last_frame_time)
        if sleep_time > 0:
            time.sleep(sleep_time)
        return last_frame_time + 1./self.settings['game_FPS']

    def spawnFood(self):
        (x,y) = (random.randint(0,23),random.randint(0,19))
        while self.isBlocked(x*32+16,y*32+16):
            #print( str(x) + "," + str(y) )
            (x,y) = (random.randint(0,23),random.randint(0,19))
        self.entities['food'] = Consumable('food',x*32+16,y*32+16,'Food',0.5,self)
        self.grid[x][y].addEntity('food')

    """GETTER METHODS"""

    def isBlocked(self,x,y,name=None):
        (x_grid,y_grid) = self.getGridPosition(x,y)
        tile = self.grid[x_grid][y_grid]
        if tile.isEmpty():
            return False
        else:
            contents = [n for n in tile.getContents() if (n=='wall' or self.entities[n].getBlocking())]
            if name == None and len(contents)>0:
                return True
            else:
                return not len( [n for n in contents if n != name] )==0

    def getSettings(self):
        return self.settings

    def getCrashed(self):
        return self.crashed

    def getKey(self,key):
        try:
            return self.keys[key]
        except KeyError:
            return False
    def getEntities(self):
        return self.entities

    def getGridPosition(self,x,y):
        return ( int((x)/32), int((y)/32))

    def getGrid(self):
        return self.grid

    def getGenome(self,name='player'):
        return self.entities[name].getGenome()

    def getNetwork(self,name='player'):
        return self.entities[name].getNetwork()

    def getMapName(self):
        return self.map_name

    def getScore(self):
        return self.score

    """SETTER METHODS"""
    def setCrashed(self, boolean):
        self.crashed = boolean

    def setKey(self, key, boolean):
        self.keys[key] = boolean
