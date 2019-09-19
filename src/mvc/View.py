import pygame
import matplotlib.pyplot as plt
import time

from tools.DEBUG import *
from tools.MyThread import MyThread


class View:
    nx = 832
    ny = 32
    size = 24
    node_numbers = True

    def __init__(self, model):
        self.model = model
        self.sett = model.getSettings()
        self.font = pygame.font.SysFont("purisa", 15)
        self.heatmap = plt.get_cmap("magma")
        self.colormap = plt.get_cmap("gist_ncar")
        self.background = pygame.image.load(
            "../res/maps/" + model.getMapName())
        self.layout = self.initNodeLayout()

    def initNodeLayout(self):
        layout = [(self.nx + 4 * 32, self.ny + 15 * 32)]
        for i in range(1, 6):
            layout.append((self.nx + 32 * (i - 1), self.ny))
        for i in range(6, 11):
            layout.append((self.nx + 32 * (i - 6), self.ny + 32))
        for i in range(11, 33):
            layout.append((self.nx + 96 + 32 * ((i - 11) % 2),
                           self.ny + 96 + 32 * int((i - 11) / 2)))
        for i in range(33, 41):
            layout.append((self.nx + 192 + 32 * ((i - 33) % 4),
                           self.ny + 32 * int((i - 33) / 4)))
        for i in range(41, 49):
            layout.append((self.nx + 352 + 32 * ((i - 33) % 4),
                           self.ny + 32 * int((i - 41) / 4)))
        for i in range(49, 57):
            layout.append((self.nx + 32 * ((i - 49) % 2),
                           self.ny + 96 + 32 * int((i - 49) / 2)))
        for i in range(57, 65):
            layout.append((self.nx + 32 * ((i - 57) % 2),
                           self.ny + 320 + 32 * int((i - 57) / 2)))

        for i in range(65, 274):
            layout.append((self.nx + 192 + 32 * int((i - 65) / 14),
                           self.ny + 96 + 32 * int((i - 65) / 14)))
        for i in range(274, 290):
            layout.append((self.nx + 672 + 32 * int((i - 274) %
                                                    3), self.ny + 96 + 32 * int((i - 274) / 3)))
        return layout

    def start(self):
        sett = self.model.getSettings()
        self.gameDisplay = pygame.display.set_mode(
            (int(sett['display_width']), int(sett['display_height'])))
        pygame.display.set_caption(sett['title'])
        self.clock = pygame.time.Clock()

        v_thread = MyThread(1, "ViewThread", self.loop)
        return v_thread

    def loop(self):
        while not self.model.getCrashed():
            self.fillBackground()
            self.fillForeground()
            self.drawNetwork()
            pygame.display.update()
            self.clock.tick(self.sett['frame_rate'])

    def fillBackground(self):
        self.gameDisplay.fill((200, 200, 200))
        self.gameDisplay.blit(self.background, (0, 0))

    def fillForeground(self):
        for name, e in self.model.getEntities().items():
            (x, y, o) = e.getLocation()
            sprite = e.getSprite()
            self.gameDisplay.blit(sprite, (x - 16, y - 16))

    def heat2col(self, heat):
        heat = 0.99 if heat >= 1 else heat
        return [255 * c for c in self.heatmap(heat)[0:3]]

    def drawAxon(self, from_idx, to_idx, heat):
        (xfrom, yfrom) = self.layout[from_idx]
        (xto, yto) = self.layout[to_idx]
        xfrom += 12
        yfrom += 12
        xto += 12
        yto += 12

        pygame.draw.line(self.gameDisplay,
                         self.heat2col(heat),
                         (xfrom, yfrom),
                         (xto, yto),
                         3)

    def drawNode(self, idx, loc, heat):
        (x, y) = loc
        if self.node_numbers:
            label = self.font.render(str(idx), 1, self.heat2col(heat))
            self.gameDisplay.blit(label, (x, y))
        else:
            pygame.draw.rect(self.gameDisplay,
                             self.heat2col(heat),
                             (x, y, 24, 24),
                             0)

    def drawNetwork(self):
        network = self.model.getNetwork()

        connections = self.model.getGenome().getCgenes()
        for c in connections:
            if c.getEnabled():
                self.drawAxon(c.getIn(), c.getOut(),
                              network.getNode(c.getIn()).getActivity())

        nodes = network.getNodes()
        for n in range(len(nodes)):
            self.drawNode(
                nodes[n].getId(), self.layout[nodes[n].getId()], nodes[n].getActivity())
