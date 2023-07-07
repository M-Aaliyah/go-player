import pygame, sys
from pygame.locals import *
import pygame.freetype # FOR TEXT
import time
import math
import random
import datetime

WINWIDTH = 950
WINHEIGHT = 650
CAPTION = "GO"
BLACK = (0,0,0) # colours must be in a tuple - r.g.b
BLUE = (0,0,255)
WHITE = (255,255,255)
LGREY = (156,166,171)
OFFWHITE = (214, 210, 214)
clickable = []


def makePygameFont(message, size, colour, xPos, yPos, style):#makes one piece of text
    font = pygame.freetype.Font(style, size) # None = the font style. # 20 = the size
    text = font.render(message,colour) # text is now a tuple. index 0 = surface & index 1 = rect
    textpos = text[1] # textpos is the rectangle
    textpos.centerx = xPos # x position of text.
    textpos.centery = yPos # y position of text
    mySurface.blit(text[0],textpos) # place on the screen the actual text (surface) in the rectangles position

    return textpos

def makePygameRectangle(colour, xPos, yPos, width, height, lineWidth):
    myRect = pygame.Rect(xPos, yPos, width, height)
    pygame.draw.rect(mySurface, colour, myRect, width=lineWidth)
    
    return myRect

def displayRules():
    mySurface.blit(arrow, (25, 12))
    clickable.append(arrow)
    
    mySurface.blit(rules, (30, 50))

def loadImages():
    arrow = pygame.image.load('Arrow.png').convert_alpha()
    arrow = pygame.transform.scale(arrow,(30, 60)) # image, (width, height)
    arrow = pygame.transform.rotate(arrow, 90)

    rules = pygame.image.load('Rules.png').convert_alpha()
    rules = pygame.transform.scale(rules,(890, 570)) # image, (width, height)
        
    return arrow, rules

def events(arrow):
    option = None
    
    for event in pygame.event.get(): 
            if event.type == QUIT:
                pygame.quit() # Cannot be a variable name as its a pygame command
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()

                if arrow.get_rect().collidepoint(pos):
                    option = "Back"

    return option


pygame.init() # sets up pygame. Runs once.
pygame.freetype.init() # FOR TEXT Runs once.
fpsClock = pygame.time.Clock() # Frames/second e.g.30 To limit the number of times it wil run the game loop.
mySurface = pygame.display.set_mode((WINWIDTH, WINHEIGHT), 0, 32) # Window size, 0, bit colour
pygame.display.set_caption(CAPTION) # Window name

arrow, rules = loadImages()

def rulesRunner():
    while True:
        optionClicked = events(arrow)
        mySurface.fill(BLACK)
        fpsClock.tick(33)

        displayRules()

        if optionClicked == "Back":
            break

        pygame.display.update()

    return optionClicked






