import pygame, sys
from pygame.locals import *
import pygame.freetype # For text
import time
import math
import random

import Rules as R
import TwoPlayerGame as twoPlG    
import AIGame as aiG


WINWIDTH = 950
WINHEIGHT = 650
CAPTION = "GO"
BLACK = (0,0,0) 
WHITE = (255,255,255)
YELLOW = (255,255,0)
LGREY = (156,166,171)
OFFWHITE = (214,210,214)
mySurface = None


def makePygameFont(message, size, colour, xPos, yPos, style):#makes one piece of text
    font = pygame.freetype.Font(style, size) # None = the font style, 20 = the size
    text = font.render(message,colour) # Text is now a tuple, index 0 = surface & index 1 = rect
    textpos = text[1] # textpos is the rectangle
    textpos.centerx = xPos # x position of text
    textpos.centery = yPos # y position of text
    mySurface.blit(text[0],textpos) # Place on the screen the actual text (surface) in the rectangles position

    return textpos

def makePygameRectangle(colour, xPos, yPos, width, height, lineWidth):
    myRect = pygame.Rect(xPos, yPos, width, height)
    pygame.draw.rect(mySurface, colour, myRect, width=lineWidth)
    
    return myRect

def displayMainMenu():
    makePygameRectangle(WHITE, 15, 15, 920, 620, 3)

    makePygameFont("Go", 225, LGREY, 479, 174, 'Byorg.ttf')
    makePygameFont("Go", 225, WHITE, 475, 170, 'Byorg.ttf')
    
    textPlay = makePygameFont("Play Game", 70, WHITE, 475, 340, 'Byorg.ttf')

    text2Player = makePygameFont("2 Players", 70, WHITE, 475, 440, 'Byorg.ttf')

    textRules = makePygameFont("Rules", 70, WHITE, 475, 540, 'Byorg.ttf')

    pygame.draw.circle(mySurface, WHITE, (90,100), 50, width=0)
    pygame.draw.circle(mySurface, WHITE, (90,210), 50, width=3)
    pygame.draw.circle(mySurface, WHITE, (200,210), 50, width=3)
    pygame.draw.circle(mySurface, WHITE, (90,320), 50, width=0)
    pygame.draw.circle(mySurface, WHITE, (860,560), 50, width=0)
    pygame.draw.circle(mySurface, WHITE, (860,450), 50, width=3)

    return textPlay, text2Player, textRules
    
def events(textPlay, text2Player, textRules):
    option = None
    
    for event in pygame.event.get(): 
            if event.type == QUIT:
                pygame.quit() # Cannot be a variable name as its a pygame command
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN: # If mouse is pressed get position of cursor
                pos = pygame.mouse.get_pos()

                if textRules.collidepoint(pos):
                    option = "Rules"

                elif text2Player.collidepoint(pos):
                    option = "2 Player"

                elif textPlay.collidepoint(pos):
                    option = "Play Game"

    return option

pygame.init() # Sets up pygame - runs once
pygame.freetype.init() # For text - runs once
fpsClock = pygame.time.Clock() # Frames/second e.g. 30. - To limit the number of times it wil run the game loop
mySurface = pygame.display.set_mode((WINWIDTH, WINHEIGHT), 0, 32) # Window size, 0, bit colour
pygame.display.set_caption(CAPTION) # Window name

optionClicked = None

while True:
    mySurface.fill(BLACK)
    fpsClock.tick(33)
    
    textPlay, text2Player, textRules = displayMainMenu()
    
    optionClicked = events(textPlay, text2Player, textRules)

    if optionClicked == "Rules":
        optionClicked = R.rulesRunner()

    if optionClicked == "2 Player":
        optionClicked = twoPlG.twoPlayerGameRunner()

    if optionClicked == "Play Game":
        optionClicked = aiG.AIGameRunner()

    pygame.display.update()

    
        









