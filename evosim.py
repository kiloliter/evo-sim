import math
import random
import copy
import unittest
import pickle

import pygame
from pygame.locals import *
import pygame.gfxdraw

worldWidth = 600
worldHeight = 600
sidebarWidth = 200

eyeCount = 4
numberOfCreatures = 100
hiddenLayerNeuronCount = 7 # number of neurons in the hidden layers
hiddenLayerCount = 1 #number of hidden layers

numberOfFood = 400
mutationRate = .005
foodDropDelay = 10
energyFromFood = 10 # the amount of energy to give a creature every time it eats
creatureRotateSpeed = .02 # how fast a creature can rotate
creatureMoveSpeed = 2 # how fast the creature moves forward
costOfLiving = .02 # the amount of energy to subtract from creature every frame
infancyLength = 60 # the amount of time a creature sits still when first born

random.seed(1)

class neuron:
    def __init__(self, previousLayer):
        self.input_list = []
        self.inputWeightList = []
        self.inputLayer = previousLayer
        self.threshold = 1
        self.activated = 0
        i = 0
        if self.inputLayer != 0:
            while i < len(self.inputLayer.neurons):
                self.inputWeightList.append(random.random())
                i = i + 1
    def update(self):
        if self.inputLayer == 0:
            return
        total = 0
        i = 0
        while i < len(self.inputLayer.neurons):
            total = total + self.inputLayer.neurons[i].activated * self.inputWeightList[i]
            i = i + 1
        if total >= self.threshold:
            self.activated = 1
        else:
            self.activated = 0
    def randomize(self):
        i = 0
        while i < len(self.inputWeightList):
            self.inputWeightList[i] = random.random()
            i = i + 1        
        self.threshold = random.random() * 3
    def mutate(self):
        for i in self.inputWeightList:
            if random.random() > .9:
                i = i + random.random() - .5
        if random.random() > .9:
            self.threshold = self.threshold + (random.random() - .5)

class NeuronLayer:
    def __init__(self, neuronCount, previousLayer):
        self.neurons = []
        i = 0
        while i < neuronCount:
            self.neurons.append(neuron(previousLayer))
            i = i + 1
    def update(self):
        for i in self.neurons:
            i.update()
    def randomize(self):
        for i in self.neurons:
            i.randomize()
    def mutate(self):
        for i in self.neurons:
            i.mutate()        

class Food:
    def __init__(self):
        self.randomize()
    def draw(self):
        pygame.gfxdraw.aacircle(s, self.x + sidebarWidth, self.y, 5, (0, 200, 0))
    def randomize(self):
        self.x = random.randrange(worldWidth)
        self.y = random.randrange(worldHeight)
    
class Creature:
    def __init__(self):
        self.energy = 5.0
        self.reproductionTimer = 0
        self.neurons = []
        self.r = 127
        self.g = 127
        self.b = 127
        self.infancy = 0
        self.neurons.append(NeuronLayer(eyeCount + 1, 0)) # create the input layer
        # create hidden neuron layers
        i = 0
        while i < hiddenLayerCount:
            self.neurons.append(NeuronLayer(hiddenLayerNeuronCount, self.neurons[i]))
            i = i + 1
        self.neurons.append(NeuronLayer(5, self.neurons[hiddenLayerCount])) # create output layer
        self.rotation = 0
        self.randomize()
        self.x = random.randrange(worldWidth)
        self.y = random.randrange(worldHeight)
        self.rotation = random.random() * 2
        self.eatenCount = 0
        self.reproductionTimer = random.randrange(260)
    def randomize(self):
        for i in self.neurons[1:]:
                i.randomize()
    def mutate(self):
        for i in self.neurons[1:]:
            i.mutate()
        if random.random() < .7:
            self.r = self.r + random.randrange(30) - 15
        if random.random() < .7:
            self.g = self.g + random.randrange(30) - 15
        if random.random() < .7:
            self.b = self.b + random.randrange(30) - 15
        if self.r > 255:
            self.r = 255
        if self.r < 0:
            self.r = 0
        if self.g > 255:
            self.g = 255
        if self.g < 0:
            self.g = 0
        if self.b > 255:
            self.b = 255
        if self.b < 0:
            self.b = 0            

    def draw(self):
        pygame.gfxdraw.filled_circle(s, int(self.x + .5) + sidebarWidth, int(self.y + .5), 5, (self.r, self.g, self.b))
        pygame.gfxdraw.line(s, int(self.x + .5) + sidebarWidth, int(self.y + .5), int(self.x + math.sin(self.rotation * math.pi) * 5 + .5) + sidebarWidth, int(self.y + math.cos(self.rotation * math.pi) * 5 + .5), (255, 255, 255))

    def update(self):
        if self.infancy > 0:
            self.infancy -= 1
            return
        self.readInput()
        for i in self.neurons[1:]:
            i.update()
        self.checkForCancer()
        self.actOnOutput()
        self.isTouchingFood()
        self.resetInputs()
        self.subtractEnergy()
        # random mutation
        if random.random() < mutationRate:
            self.mutate()

    def subtractEnergy(self):
        self.energy = self.energy - costOfLiving
        
    def readInput(self):
        # look around, and send what we see around us to the input neurons

        # this is to keep them all from dying of cancer if there's no food
        if len(foodList) == 0:
            self.neurons[0].neurons[0].activated = 1
            return

        # figure out which food is closest, and turn on the correct input neuron
        i = 0
        closest = 0
        closestDistance = 1000
        while i < len (foodList):
            if math.hypot(self.x - foodList[i].x, self.y - foodList[i].y) < closestDistance:
                closestDistance = math.hypot(self.x - foodList[i].x, self.y - foodList[i].y)
                closest = i
            i = i + 1
        temp = 0
        if foodList[closest].y - self.y == 0:
            self.y = self.y + .1
        else:
            temp = (self.rotation - (math.atan((foodList[closest].x - self.x) / (foodList[closest].y - self.y)) / math.pi)) / (2 / float(eyeCount))
        if foodList[closest].y < self.y:
            temp = temp - eyeCount / 2
        if temp < 0:
            temp = temp + eyeCount
        if temp >= eyeCount:
            temp = temp - eyeCount
        self.neurons[0].neurons[int(temp)].activated = 1

        # energy level
        if self.energy > 30:
            temp = 30
        else:
            temp = self.energy
        self.neurons[0].neurons[eyeCount].activated = temp / 30.0
        
    def checkForCancer(self):
        # death by cancer
        if self.neurons[hiddenLayerCount + 1].neurons[3].activated != 1:
            self.energy = -1
        
    def actOnOutput(self):
        # see if we should rotate
        if self.neurons[hiddenLayerCount + 1].neurons[1].activated == 1:
            self.rotation = self.rotation - creatureRotateSpeed
            if self.rotation < 0:
                self.rotation = self.rotation + 2
        if self.neurons[hiddenLayerCount + 1].neurons[2].activated == 1:
            self.rotation = self.rotation + creatureRotateSpeed
            if self.rotation > 2:
                self.rotation = self.rotation - 2
        # see if we should move forward
        if self.neurons[hiddenLayerCount + 1].neurons[0].activated == 1:
            self.x = self.x + math.sin(self.rotation * math.pi) * 2
            self.y = self.y + math.cos(self.rotation * math.pi) * 2

        # see if we should make a baby
        if self.neurons[hiddenLayerCount + 1].neurons[4].activated == 1:
            self.energy = self.energy / 2
            creatureList.append(copy.deepcopy(self))
            creatureList[len(creatureList) - 1].infancy = infancyLength
            
    def resetInputs(self):
        # reset all input neurons to zero
        for i in self.neurons[0].neurons:
            i.activated = 0
            
    def isTouchingFood(self):
        # check if we can eat
        i = 0
        while i < len (foodList):
            if math.hypot(self.x - foodList[i].x, self.y - foodList[i].y) < 10:
                del foodList[i]
                self.eatenCount = self.eatenCount + 1
                self.energy = self.energy + energyFromFood
            i = i + 1
            
    def sexualReproduction(self, parent):
        # Randomly take genes from both parents and create a new creature.
        global creatureList
        which = self
        if random.random() > .5:
            which = parent
        whichAmount = random.randrange(20)
        whichCounter = 0
        self.energy = self.energy / 2
        creatureList.append(copy.deepcopy(self))
        creatureList[len(creatureList) - 1].infancy = infancyLength
        for a in range(1, len(creatureList[len(creatureList) - 1].neurons) - 1):
            for b in range(len(creatureList[len(creatureList) - 1].neurons[a].neurons) - 1):
                creatureList[len(creatureList) - 1].neurons[a].neurons[b].threshold = which.neurons[a].neurons[b].threshold
                for c in range(len(creatureList[len(creatureList) - 1].neurons[a].neurons[b].inputWeightList) - 1):
                    creatureList[len(creatureList) - 1].neurons[a].neurons[b].inputWeightList = which.neurons[a].neurons[b].inputWeightList
                    if whichCounter > whichAmount:
                        whichCounter = 0
                        whichAmount = random.randrange(20)
                        if random.random() > .5:
                            which = parent
                        else:
                            which = self
                
creatureList = []
foodList = []

class TestNeuron(unittest.TestCase):

    def setUp(self):
        self.neuronLayerTest = NeuronLayer(2, 0)
        self.neuron_test = neuron(self.neuronLayerTest)
        self.neuron_test.inputWeightList[0] = 1
        self.neuron_test.inputWeightList[1] = 0
        self.neuronLayerTest.neurons[0].activated = 1

    def testUpdateWithThreshold(self):
        self.neuron_test.inputWeightList[1] = 1
        self.neuron_test.threshold = 2.1
        self.neuronLayerTest.neurons[1].activated = 1
        self.neuron_test.update()
        self.assertEqual(self.neuron_test.activated, 0)
        self.neuron_test.threshold = 1.4
        self.neuron_test.update()
        self.assertEqual(self.neuron_test.activated, 1)

    def testSetup(self):
        self.assertEqual(self.neuron_test.activated, 0)

class TestCreature(unittest.TestCase):

    def setUp(self):
        self.creature_test = Creature()
        self.creature_test.x = 0
        self.creature_test.y = 0
        self.creature_test.rotation = 0
        foodList.append(Food())

    def tearDown(self):
        global foodList
        foodList = []

    def testInfancy(self):
        self.creature_test.infancy = 10
        self.creature_test.update()
        self.assertEqual(self.creature_test.infancy, 9)

    def testEating(self):
        foodList[0].x = 0
        foodList[0].y = 0
        self.assertEqual(self.creature_test.eatenCount, 0)
        a = self.creature_test.energy
        self.creature_test.isTouchingFood()
        self.assertEqual(len(foodList), 0)
        self.assertEqual(self.creature_test.eatenCount, 1)
        self.assertEqual(self.creature_test.energy, a + energyFromFood)
        foodList.append(Food())

    def testNotEating(self):
        foodList[0].x = 200
        foodList[0].y = 200
        self.creature_test.isTouchingFood()
        self.assertEqual(foodList[0].x, 200)
        self.assertEqual(foodList[0].y, 200)

    def testRotateClockwise(self):
        self.creature_test.neurons[hiddenLayerCount + 1].neurons[2].activated = 1
        self.creature_test.actOnOutput()
        self.assertEqual(self.creature_test.rotation, creatureRotateSpeed)
        self.creature_test.neurons[hiddenLayerCount + 1].neurons[2].activated = 0

    def testRotateCounterClockwise(self):
        self.creature_test.neurons[hiddenLayerCount + 1].neurons[1].activated = 1
        self.creature_test.actOnOutput()
        self.assertEqual(self.creature_test.rotation, 2 - creatureRotateSpeed)
        self.creature_test.neurons[hiddenLayerCount + 1].neurons[1].activated = 0

    def testMoveForwardRotated(self):
        self.creature_test.neurons[hiddenLayerCount + 1].neurons[0].activated = 1
        self.creature_test.neurons[hiddenLayerCount + 1].neurons[1].activated = 1
        self.creature_test.actOnOutput()
        self.assertEqual(int(self.creature_test.x + .5), 0)
        self.assertEqual(int(self.creature_test.y + .5), creatureMoveSpeed)

    def testInput(self):
        self.creature_test.x = 50
        self.creature_test.y = 50
        foodList[0].x = 0
        foodList[0].y = 0
        self.creature_test.infancy = 0
        self.creature_test.rotate = 0
        self.creature_test.readInput()
        self.assertEqual(self.creature_test.neurons[0].neurons[0].activated, 0)
        self.assertEqual(self.creature_test.neurons[0].neurons[1].activated, 1)
        self.assertEqual(self.creature_test.neurons[0].neurons[2].activated, 0)
        self.assertEqual(self.creature_test.neurons[0].neurons[3].activated, 0)
        self.creature_test.resetInputs()
        self.creature_test.x = 50
        self.creature_test.y = 50
        foodList[0].x = 100
        foodList[0].y = 100
        self.creature_test.rotate = 0
        self.creature_test.readInput()
        self.assertEqual(self.creature_test.neurons[0].neurons[0].activated, 0)
        self.assertEqual(self.creature_test.neurons[0].neurons[1].activated, 0)
        self.assertEqual(self.creature_test.neurons[0].neurons[2].activated, 0)
        self.assertEqual(self.creature_test.neurons[0].neurons[3].activated, 1)

    def testEnergyUse(self):
        a = self.creature_test.energy
        foodList = []
        self.creature_test.subtractEnergy()
        self.assertEqual(self.creature_test.energy, a - costOfLiving)

    def testEnergyMeter(self):
        self.creature_test.energy = 15
        self.creature_test.infancy = 0
        self.creature_test.readInput()
        self.assertEqual(self.creature_test.neurons[0].neurons[4].activated, .5)
        
    def testReproduction(self):
        self.creature_test.neurons[hiddenLayerCount + 1].neurons[4].activated = 1
        self.creature_test.actOnOutput()
        self.assertEqual(len(creatureList), 1)
        self.creature_test.neurons[hiddenLayerCount + 1].neurons[4].activated = 0

class TestNeuronLayer(unittest.TestCase):

    def setUp(self):
        self.layerTest = NeuronLayer(4, 0)

    # Make sure that a neuron layer gets initialized the way it's supposed to.
    def testInit(self):
        self.assertEqual(len(self.layerTest.neurons), 4)

    # Make sure that a second neuron layer gets initialized the way it's supposed to.
    def testInitSecondLayer(self):
        layerTest2 = NeuronLayer(10, self.layerTest)
        self.assertEqual(len(layerTest2.neurons), 10)
        self.assertEqual(layerTest2.neurons[0].inputLayer, self.layerTest)
        
class Game:
    def mainLoop(self):
        cursorPosition = 0
        global mutationRate
        global foodDropDelay
        global creatureList
        global foodList
        foodDropCounter = 0
        while 1:
            frameCounter = pygame.time.get_ticks()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                if event.type == MOUSEBUTTONDOWN:
                    foodList.append(Food())
                    foodList[len(foodList) - 1].x = event.pos[0] - sidebarWidth
                    foodList[len(foodList) - 1].y = event.pos[1]
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                    if event.unicode == 's':
                        # save
                        file = open('save', 'w')
                        pickle.dump(creatureList,file)
                        file.close()
                    if event.unicode == 'l':
                        # load
                        unpicklefile = open('save', 'r')
                        creatureList = pickle.load(unpicklefile)
                        unpicklefile.close()
                                    
                    if event.key == pygame.K_DOWN and cursorPosition != 2:
                        cursorPosition += 1
                    if event.key == pygame.K_UP and cursorPosition != 0:
                        cursorPosition -= 1
                    if cursorPosition == 0:
                        # food amount
                        if event.key == pygame.K_LEFT:
                            if len(foodList) != 0:
                                del foodList[0]
                        elif event.key == pygame.K_RIGHT:
                                foodList.append(Food())
                        elif event.key == pygame.K_PAGEUP:
                            if len(foodList) > 10:
                                for i in range(0, 10):
                                    del foodList[0]
                        elif event.key == pygame.K_PAGEDOWN:
                            for i in range(0, 10):
                                foodList.append(Food())

                    if cursorPosition == 1:
                        # mutation rate
                        if event.key == pygame.K_LEFT:
                            if mutationRate != 0:
                                mutationRate -= .0001
                        elif event.key == pygame.K_RIGHT:
                            if mutationRate != 1000:
                                mutationRate += .0001
                        elif event.key == pygame.K_PAGEUP:
                            if mutationRate > .001:
                                mutationRate -= .001
                        elif event.key == pygame.K_PAGEDOWN:
                            if mutationRate != 1000:
                                mutationRate += .001

                    if cursorPosition == 2:
                        # food drop
                        if event.key == pygame.K_LEFT:
                            if foodDropDelay != 0:
                                foodDropDelay -= 1
                        elif event.key == pygame.K_RIGHT:
                                foodDropDelay += 1
                        elif event.key == pygame.K_PAGEUP:
                            if foodDropDelay > 10:
                                foodDropDelay -= 10
                        elif event.key == pygame.K_PAGEDOWN:
                                foodDropDelay += 10
                        
            s.fill((0, 0, 0))

            # check for dead creatures and remove them
            i = 0
            while i < len(creatureList):
                if creatureList[i].energy <= 1:
                    del creatureList[i]
                    continue
                i = i + 1
                
            # drop food on the creatures
            if foodDropCounter >= foodDropDelay:
                foodList.append(Food())
                foodDropCounter = 0
            else:
                foodDropCounter += 1

            # draw pictures
            for i in creatureList:
                i.update()
                i.draw()
            for i in foodList:
                i.draw()
            screen.blit(s, (0, 0))

            # draw text on the side of the screen
            screen.fill((0, 0, 0), (0, 0, sidebarWidth, worldHeight))
            fg = 250, 240, 230
            bg = 5, 5, 5
            font = pygame.font.Font(None, 18)

            text = "creature count: " + str(len(creatureList))
            ren = font.render(text, 0, fg, bg)
            size = font.size(text)
            screen.blit(ren, (sidebarWidth - size[0] - 15, 10))

            if cursorPosition == 0:
                fg = 0, 0, 0
                bg = 255, 255, 255
            else:
                bg = 0, 0, 0
                fg = 255, 255, 255                    
            text = "food count: " + str(len(foodList))
            ren = font.render(text, 0, fg, bg)
            size = font.size(text)
            screen.blit(ren, (sidebarWidth - size[0] - 15, 30))
            
            if cursorPosition == 1:
                fg = 0, 0, 0
                bg = 255, 255, 255
            else:
                bg = 0, 0, 0
                fg = 255, 255, 255 
            text = "mutation rate: " + str(mutationRate * 100) + "%"
            ren = font.render(text, 0, fg, bg)
            size = font.size(text)
            screen.blit(ren, (sidebarWidth - size[0] - 15, 50))

            if cursorPosition == 2:
                fg = 0, 0, 0
                bg = 255, 255, 255
            else:
                bg = 0, 0, 0
                fg = 255, 255, 255 
            text = "food drop delay: " + str(foodDropDelay)
            ren = font.render(text, 0, fg, bg)
            size = font.size(text)
            screen.blit(ren, (sidebarWidth - size[0] - 15, 70))
            
            pygame.display.flip()

i = 0
while i < numberOfCreatures:
    creatureList.append(Creature())
    x = creatureList[len(creatureList) - 1].x
    y = creatureList[len(creatureList) - 1].y
    rotation = creatureList[len(creatureList) - 1].rotation
    creatureList[len(creatureList) - 1].update()
    if creatureList[len(creatureList) - 1].energy < 3 or x == creatureList[len(creatureList) - 1].x or y == creatureList[len(creatureList) - 1].y or rotation == creatureList[len(creatureList) - 1].rotation:
        del creatureList[len(creatureList) - 1]
    else:
        i = i + 1

foodList = []
i = 0
while i < numberOfFood:
    foodList.append(Food())
    i = i + 1

gameInstance = Game()

pygame.init()
screen = pygame.display.set_mode((worldWidth + sidebarWidth,worldHeight))
s = pygame.Surface(screen.get_size(), pygame.SRCALPHA, 32)
pygame.key.set_repeat(500,15)
pygame.display.set_caption("evolution simulator")
gameInstance.mainLoop()
    
pygame.quit()
