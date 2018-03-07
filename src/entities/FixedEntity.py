import pygame

class FixedEntity():
    def __init__(self,name,x,y,P_block, hp):
        self.name = name
        self.x = x
        self.y = y
        self.pb = P_block
        self.max_hp = hp
        self.hp = hp

    def damage(self,amount):
        self.hp = max(0,self.hp-amount)

    def heal(self,amount):
        self.hp = min(self.max_hp, self.hp+amount)

    def getPblock(self):
        return self.pb

    def toString(self):
        return "%s @ (%s,%s)" % (self.name, str(self.x), str(self.y))
