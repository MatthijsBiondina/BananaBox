from PIL import Image

from .Tile import Tile
from entities.FixedEntity import FixedEntity

class GridCreator:
    def __init__(self,model):
        self.model = model

    def buildGrid(self, filename):
        im = Image.open(filename)
        pix = im.load()
        (X,Y) = im.size
        grid = [[Tile(x,y) for y in range(Y)] for x in range(X)]
        for x in range(X):
            for y in range(Y):
                if sum(pix[x,y]) < 100:
                    #print("placing wall at: %s,%s" % (str(x),str(y)))
                    grid[x][y].addEntity('wall')
        return grid

    def addEntities(self,grid):
        for x in range(len(grid)):
            for y in range(len(grid[x])):
                c = grid[x][y].getContents()
                for e in c:
                    if e != 'wall':
                        grid[x][y].remEntity(e)
                
        
        for _,e in self.model.getEntities().items():
            (x,y,_) = e.getLocation()
            (x_grid,y_grid) = self.model.getGridPosition(x,y)
            grid[x_grid][y_grid].addEntity(e.getName())

        return grid
        
