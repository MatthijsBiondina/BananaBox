import pygame
import time

from tools.DEBUG import *
from tools.MyThread import MyThread

class Controller:
    def __init__(self, model):
        self.model = model
        self.settings = model.getSettings()
        
    def start(self):
        dprt(self,"Starting Controller")
        c_thread = MyThread( 2, "ControlThread", self.loop)
        return c_thread

    def loop(self):
        last_frame_time = time.time()
        while not self.model.getCrashed():
            last_frame_time = self.sleep(last_frame_time)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.model.setCrashed(True)
                if event.type == pygame.KEYDOWN:
                    self.model.setKey(event.key,True)
                    #print( event.key )
                if event.type == pygame.KEYUP:
                    self.model.setKey(event.key,False)
            pygame.event.pump()
            
    def sleep(self,last_frame_time):
        sleep_time = 1./self.settings['game_FPS'] - (time.time() - last_frame_time)
        if sleep_time > 0:
            time.sleep(sleep_time)
        return last_frame_time + 1./self.settings['game_FPS']
