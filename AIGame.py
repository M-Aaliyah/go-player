import pygame, sys                                  
from pygame.locals import *                         
import pygame.freetype 
import time
import math
import random

import TwoPlayerGame as tpg


WINWIDTH = 950
WINHEIGHT = 650
CAPTION = "GO"
BLACK = (0,0,0) 
RED = (255,0,0)
BLUE = (0,0,255)
WHITE = (255,255,255)
OFFWHITE = (214,210,214)
LGREY = (156,166,171)
DGREY = (71,76,78)
LGREEN = (161,235,175)
YELLOW = (214,165,45)
EMPTY, B, W = '.', 'B', 'W'

# p2 is the AI player - W
# AI move weightings are assigned by how many stones the AI will capture or save from capture


class AIBoard(tpg.Board): # Inheritance - AIBoard is a subclass of superclass Board
    def __init__(self):
        super(AIBoard, self).__init__() # Calls the superclass Board's constructor
        
        self._moveStack = AIMoveStack(self._width*self._height) # Instantiation of the stack to hold the possible moves for the AI
        self._AIToggleDisplay = False
        self._toggleCount = 0 

    def getToggleCount(self):
        return self._toggleCount

    def setToggleCount(self, newToggleCount): 
        self._toggleCount = newToggleCount

    def displayWindow(self): # Draws and displays the empty board, player information, resign and play buttons onto mySurface
                             # Overrides superclass Board's displayWindow method
        mySurface.blit(arrow, (25, 12))

        tpg.makePygameRectangle(LGREY, 32, 52, 570, 570, 3)
        mySurface.blit(boardImage, (30, 50))

        tpg.makePygameRectangle(LGREY, 632, 52, 290, 80, 3)
        tpg.makePygameRectangle(WHITE, 630, 50, 290, 80, 3)
        pygame.draw.line(mySurface, WHITE, (630,75), (920,75), 3)
        tpg.makePygameFont("You -> B", 25, WHITE, 775, 62.5, 'Byorg.ttf')
        tpg.makePygameFont("Captures: "+str(self._p1Captures), 20, WHITE, 775, 102.5, 'Byorg.ttf')

        tpg.makePygameRectangle(LGREY, 632, 147, 290, 80, 3)
        tpg.makePygameRectangle(WHITE, 630, 145, 290, 80, 0)
        pygame.draw.line(mySurface, BLACK, (630,170), (920,170), 3)
        tpg.makePygameFont("AI -> W", 25, BLACK, 775, 157.5, 'Byorg.ttf')
        tpg.makePygameFont("Captures: "+str(self._p2Captures), 20, BLACK, 775, 197.5, 'Byorg.ttf')

        toggleRect = None
        toggleRectL = None

        passRect = tpg.makePygameRectangle(LGREY, 630, 255, 137.5, 80, 0)
        passRectL = tpg.makePygameRectangle(WHITE, 630, 255, 137.5, 80, 2)
        resignRect = tpg.makePygameRectangle(DGREY, 782.5, 255, 137.5, 80, 0)
        resignRectL = tpg.makePygameRectangle(WHITE, 782.5, 255, 137.5, 80, 2)
        tpg.makePygameFont("PASS", 25, WHITE, 698.75, 295, 'Byorg.ttf')
        tpg.makePygameFont("RESIGN", 25, WHITE, 851.25, 295, 'Byorg.ttf')

        if self._turn == 0:
            tpg.makePygameFont("Your turn ...", 25, LGREY, 317, 27, 'Byorg.ttf')
            tpg.makePygameFont("Your turn ...", 25, WHITE, 315, 25, 'Byorg.ttf')
        else:
            tpg.makePygameFont("AI's turn ...", 25, LGREY, 317, 27, 'Byorg.ttf')
            tpg.makePygameFont("AI's turn ...", 25, WHITE, 315, 25, 'Byorg.ttf')

        toggleRect = tpg.makePygameRectangle(YELLOW, 632, 363, 290, 80, 0) 
        toggleRectL = tpg.makePygameRectangle(WHITE, 632, 363, 290, 80, 2) 
        tpg.makePygameFont("TOGGLE AI", 25, WHITE, 777, 403, 'Byorg.ttf')

        self.displayStones() # The window must continuosly display the stones on the board

        return passRect, resignRect, toggleRect

    def initialisePoints(self): # Creates a full graph (array) of all the Node objects (points on the board) and sets the window coords for when a stone is placed in a point (node)
        points = []
        row = []
        xCoord = 77.5
        yCoord = 97.5
        p = []

        for r in range(self._width):
            for c in range(self._height):
                newPoint = Node(xCoord, yCoord)
                row.append(newPoint)
                xCoord += 95
            points.append(row)
            xCoord = 77.5
            yCoord += 95
            row = []
           
        return points

    def displayAIToggle(self): # Shows the AI weightings for each node when the toggle on the display is pressed
        for r in range(self._height):
            for c in range(self._width):
                node = self._points[r][c]
                weight = node.getAIWeighting()
                x, y = node.getCoords()
                tpg.makePygameFont(str(weight), 20, WHITE, x, y, 'Byorg.ttf')
   
    def AIMakeMove(self): # Determines the best possible move the AI can make by using methods like checkCapture, checkDefend, etc
        pygame.display.flip() # Need to update the display before the delay so that player's stone is placed on the board first
        pygame.time.wait(900) # Short time delay so that gameplay isn't too hard for the player to follow
       
        self.resetNodeAIWeightings() # Reset the node weightings before the AI determines the new weightings
        self._moveStack.reset() # Reset the moveStack before the AI determines a new move
       
        moveNode = None
        done = False
        checkNode = None # Used in the loop for the current node (top node from the move stack)
        maxWeighting = 0 
        maxNode = None

        self.checkAIAvoid() # Finds the nodes on the board that are invalid (suicide, breaks the Ko Rule, or already occupied) for the AI to move in and assigns its AI weighting to -1
        self.checkAIStoneCapture() # Finds the nodes on the board with 1 lib and so allow the AI to capture a stone and assigns it a weighting of 1
        self.checkAILongTermStoneCapture() # Finds the nodes on the board with 2 libs and so allow the AI to capture in the long-term and assigns a weighting of 0.5
        self.checkAIChainCapture() # Finds the nodes on the board which allow the AI to capture a chain and assigns its weighting as the number of stones in the chain that would be captured
        self.checkAIStoneDefend() # Finds the nodes on the board which allow the AI to defend their stone (1/2 libs left) and assigns a weighting the num of stones which would be saved from capture/future capture
        self.checkAIChainDefend() # Finds the nodes on the board which allow the AI to defend their chain and assigns its weighting as the number of stones which would be saved from capture
        self.checkAIDefault() # Finds the remaining nodes on the board that are valid to move into and assigns them the default 0 weighting
            
        print("moves stack: ", self._moveStack.size()) # TEST

        if not self._moveStack.isEmpty(): # Only runs if there are nodes in the stack 
            while not done: # Goes through all the nodes in the AI move stack and determines the highest weighted node
                checkNode = self._moveStack.peek() 
                checkNodeWeight = checkNode.getAIWeighting()
               
                if checkNodeWeight >= maxWeighting: # Sets the maximum weighting and node to the current node popped from the stack if it has a greater value than the previously stored node
                    maxWeighting = checkNodeWeight
                    maxNode = checkNode

                self._moveStack.pop()

                if self._moveStack.isEmpty():
                    done = True # We have gone through all the moves in the stack to find the node with the greatest weight

            if maxNode != None: # There is a valid node for the AI to move in (with the biggest reward for the AI)
                if maxNode.getAIWeighting() == 0: # If the maximum node weighting is 0 (default random), the AI can find a valid default node near the opponent's stone/s to make gameplay more challenging
                    nearOpponentNode = self.findNodeNearOpponent()

                    if nearOpponentNode != None: # If there is a valid default node found to be near the opponents' stone/s this will become the node the AI will move to
                        maxNode = nearOpponentNode
                       
                moveNode = maxNode
                moveNode.setAIWeighting(100) # Implies that the AI will definitely move on this node
                self.placeStone(moveNode) # The AI places a stone on the moveNode which has the greatest weighting
                AIboard.addPasses(EMPTY)
               
        else: # The AI will pass if there are no available valid nodes to move on (this also gives away a capture point to the opponent)
            print("running pass ai") # TEST
            self.makeAIPass()

    def resetNodeAIWeightings(self): # Resets all AI move weightings for all the nodes in the board graph before the AI determines a new move
        for r in range(self._height):
            for c in range(self._width):
                self._points[r][c].resetAIWeighting()

    def checkAIAvoid(self): # Finds the nodes on the board which the AI will never move in and assigns a weighting of -1
        print("RUNNING checkAIAvoid") # TEST
        for r in range(self._height):
            for c in range(self._width):
                valid = False
                nodeToCheck = self._points[r][c]

                if nodeToCheck.getState() == EMPTY and nodeToCheck.getValidPoint() and not self.suicideRule(nodeToCheck) and nodeToCheck != self._p1LastNode and nodeToCheck != self._p2LastNode: # If the node is invalid (Breaks ko rule, sucide) then assign it a weighting opd -1
                    valid = True

                if not valid: # The node currently being looked has its AI weighting set to -1 (invalid) if it is not empty, is a suicide node, and breaks the Ko rule
                    nodeToCheck.setAIWeighting(-1)

    def checkAIStoneCapture(self): # Finds the nodes on the board with 1 lib and so allow the AI to capture a stone and assigns a weighting of 1
        print("RUNNING checkAIStoneCapture") # TEST
        for r in range(self._height):
            for c in range(self._width):
                nodeToCheck = self._points[r][c]
                liberties = nodeToCheck.getLiberties()

                if nodeToCheck.getState() != EMPTY and nodeToCheck != None and len(liberties) != 0: # If the stone is present at this node has at least one liberty left
                    lastLib = liberties[0] 

                    if nodeToCheck.getState() == B and len(liberties) == 1 and lastLib.getValidPoint() and not self.suicideRule(lastLib) and lastLib != self._p1LastNode and lastLib != self._p2LastNode:
                        lastLib.setAIWeighting(1) # Placing a stone in the last liberty of this opponent's stone will allow the AI to capture 1 stone (nodeToCheck)
                        self._moveStack.push(lastLib)

    def checkAILongTermStoneCapture(self): # Finds the nodes on the board with 2 libs and so allow the AI to capture in the long-term and assigns a weighting of 0.5
        print("RUNNING checkAILongTermStoneCapture") # TEST
        for r in range(self._height):
            for c in range(self._width):
                nodeToCheck = self._points[r][c]
                liberties = nodeToCheck.getLiberties()

                if nodeToCheck.getState() != EMPTY and nodeToCheck != None and len(liberties) == 2: # If a stone is present at this node and it has two liberties left
                    secLib = liberties[1]
                    lastLib = liberties[0]

                    if nodeToCheck.getState() == B and secLib.getValidPoint() and not self.suicideRule(secLib) and secLib != self._p1LastNode and secLib != self._p2LastNode:
                        secLib.setAIWeighting(0.5) # Placing a stone in the last liberty of this opponent's stone will allow the AI to capture 1 stone (nodeToCheck)
                        self._moveStack.push(lastLib)

                    if nodeToCheck.getState() == B and lastLib.getValidPoint() and not self.suicideRule(lastLib) and lastLib != self._p1LastNode and lastLib != self._p2LastNode:
                        secLib.setAIWeighting(0.5) 
                        self._moveStack.push(lastLib)
       
    def checkAIChainCapture(self): # Finds the nodes on the board which allow the AI to capture a chain and assigns its weighting as the number of stones in the chain that would be captured
        print("RUNNING checkAIChainCapture") # TEST
        for group in self._groups:
            nodeToCheck = group[0]
            liberties = nodeToCheck.getLiberties()

            if len(liberties) != 0:
                lastLib = liberties[0]

                if nodeToCheck.getState() == B and len(liberties) == 1 and lastLib.getValidPoint() and not self.suicideRule(lastLib) and lastLib != self._p1LastNode and lastLib != self._p2LastNode: # If there is player chain and it has one liberty left 
                    lastLib.setAIWeighting(len(group)) # Placing a stone in the last liberty of this opponent's group will allow the AI to capture the num of stones in this group of stones (chain)
                    self._moveStack.push(lastLib)
   
    def checkAIStoneDefend(self): # Finds the nodes on the board which allow the AI to defend their stone (1/2 libs left) and assigns a weighting the num of stones which would be saved from capture/future capture
        print("RUNNING checkAIStoneDefend") # TEST
        for r in range(self._height):
            for c in range(self._width):
                nodeToCheck = self._points[r][c]
                liberties = nodeToCheck.getLiberties()

                if nodeToCheck.getState() != EMPTY and nodeToCheck.getState() != None:
                    if len(liberties) == 1: # Defending of AI stone with 1 lib left
                        lastLib = liberties[0]
                       
                        if nodeToCheck.getState() == W and lastLib.getValidPoint() and not self.suicideRule(lastLib) and lastLib != self._p1LastNode and lastLib != self._p2LastNode: # Defending a stone with one lib left
                            lastLib.setAIWeighting(1) # Placing a stone in the last liberty of the AI's stone will allow the AI to defend 1 of their own stones (nodeToCheck)
                            self._moveStack.push(lastLib)
                           
                    elif len(liberties) == 2: # Defending of AI stone with 2 libs left - given less priority than defending from a stone which can immediately be captured (1 lib)
                        lastLib = liberties [0]
                        secLib = liberties[1]
                       
                        if nodeToCheck.getState() == W and secLib.getValidPoint() and not self.suicideRule(secLib) and secLib != self._p1LastNode and secLib != self._p2LastNode: # Defending a stone with two libs left
                            secLib.setAIWeighting(0.5) # Placing a stone in the last liberty of the AI's stone will allow the AI to defend 1 of their own stones (nodeToCheck) in future
                            self._moveStack.push(secLib)

                        if nodeToCheck.getState() == W and lastLib.getValidPoint() and not self.suicideRule(lastLib) and lastLib != self._p1LastNode and lastLib != self._p2LastNode:
                            lastLib.setAIWeighting(0.5)
                            self._moveStack.push(lastLib)

    def checkAIChainDefend(self): # Finds the nodes on the board which allow the AI to defend their chain and assigns its weighting as the number of stones which would be saved from capture
        print("RUNNING checkAIChainDefend") # TEST
        for group in self._groups:
            nodeToCheck = group[0]
            liberties = nodeToCheck.getLiberties()

            if len(liberties) == 1:
                lastLib = liberties[0]

                if nodeToCheck.getState() == W and lastLib.getValidPoint() and not self.suicideRule(lastLib) and lastLib != self._p1LastNode and lastLib != self._p2LastNode:
                    lastLib.setAIWeighting(len(group)) # Placing a stone in the last liberty of this AI group will allow the AI to capture the num of stones in this group of stones (chain)
                    self._moveStack.push(lastLib)
       
    def checkAIDefault(self): # Finds the remaining nodes on the board that are valid to move into and assigns them the default 0 weighting
        print("RUNNING checkAIDefault") # TEST
        for r in range(self._height):
            for c in range(self._width):
                nodeToCheck = self._points[r][c]

                if nodeToCheck.getAIWeighting() == None and nodeToCheck.getState() == EMPTY and not self.suicideRule(nodeToCheck) and nodeToCheck != self._p1LastNode and nodeToCheck != self._p2LastNode: # This means it has not been set as a node to avoid (-1) and hasn't been assigned as any other weighted nodes to move in
                    nodeToCheck.setAIWeighting(0) # This node is a valid random node to place in if no other nodes are avilable for the AI to gain a higher capture score - weighting (0)
                    self._moveStack.push(nodeToCheck)

    def findNodeNearOpponent(self): # Tries to find valid nodes that are adjacent to the opponent's stones on the board and sets their weighting to 1
        nodesNearOpponent = []
       
        for r in range(self._height):
            for c in range(self._width):
                node = self._points[r][c]
                neighbours = node.getNeighbours()
                opponentNeighbour = False
               
                if node.getAIWeighting() == 0: # If the node we are looking at is a valid and empty space
                    for n in neighbours: # Loops through the current node's neighbours (4)
                        if n.getState() == B: # If the node has a neighbour which is the opponents' stone (state = B) then this is a good node for the AI to play in
                            opponentNeighbour = True

                if opponentNeighbour:
                    nodesNearOpponent.append(node)

        for node in nodesNearOpponent: # Defult nodes that are near an opponent are assigned a heigher weighting than regular default nodes as placing near the opponent is a better game strategy
            node.setAIWeighting(1)
   
        try: # Exception handling - there would be an index error if we try to access the first index of an empty list
            return nodesNearOpponent[0] # Tries to return the first node that is found to be near the opponents' stone/s

        except:
            return None # Returns nothing if there are no nodes near the opponent otherwise there would be an index error if no objects exist in this array        
               
    def makeAIPass(self): # Only used if there are no valid default (random) board moves left that the AI can make
        self.passedUpdate()

    def gameOver(self): # Overrides superclass Board's gameOver method to display extra AI text
        winner = self.score()

        if winner == B:
            tpg.makePygameRectangle(BLACK, 60, 150, 830, 350, 0)
            tpg.makePygameRectangle(LGREEN, 60, 150, 830, 350, 4)
            tpg.makePygameFont("YOU WIN!", 60, WHITE, 475, 325, 'Byorg.ttf')

        elif winner == W:
            tpg.makePygameRectangle(WHITE, 60, 150, 830, 350, 0)
            tpg.makePygameRectangle(LGREEN, 60, 150, 830, 350, 4)
            tpg.makePygameFont("AI WINS!", 60, BLACK, 475, 325, 'Byorg.ttf')
           
        else:
            tpg.makePygameRectangle(BLACK, 60, 150, 415, 350, 0)
            tpg.makePygameRectangle(WHITE, 475, 150, 415, 350, 0)
            tpg.makePygameRectangle(LGREEN, 60, 150, 830, 350, 4)
            tpg.makePygameFont("DRAW!", 60, LGREEN, 475, 325, 'Byorg.ttf')
       

class Node: # GRAPH data structure - node object class
    def __init__(self, x, y):
        self._x, self._y = x, y # Window position coords
        self._state = EMPTY
        self._validPoint = True
        self._neighbours = [] # IMMEDIATE neighbours (4 per stone max) - up, down, left, right
        self._connections = [] # ALL connections of a stone, potentially BEYOND IMMEDIATE neighbours i.e. a group
        self._group = None # Default None if not checked for a group. I will separately create a new group with all stones in a list if needed in updateGroups
        self._liberties = [] # Holds the liberties each node has left. If it is part of a group (chain) , all the nodes in that group will have the same liberties.
        self._AIWeighting = None # Used by the AI to determine the best possible move

    def getCoords(self):
        return self._x, self._y

    def getState(self):
        return self._state

    def setState(self, newState):
        self._state = newState

    def getValidPoint(self):
        return self._validPoint

    def setValidPoint(self, state):
        self._validPoint = state
   
    def getNeighbours(self):
        return self._neighbours

    def addNeighbour(self, newNode):
        self._neighbours.append(newNode)

    def resetNeighbours(self):
        self._neighbours.clear()

    def getConnections(self):
        return self._connections

    def addConnection(self, newNode): # Used by board class' updateStoneConnections for each stone after a move is made
        self._connections.append(newNode)

    def resetConnections(self):
        self._connections.clear()

    def getGroup(self):
        return self._group
   
    def setGroup(self, newGroup):
        self._group = newGroup

    def getLiberties(self):
        return self._liberties

    def resetLiberties(self):
        self._liberties.clear()
       
    def setLiberties(self, newLiberties):
        self._liberties = newLiberties

    def resetAll(self):
        self._connections.clear()
        self._validPoint = True
        self._group = None

    def setAIWeighting(self, weight):
        self._AIWeighting = weight

    def getAIWeighting(self):
        return self._AIWeighting

    def resetAIWeighting(self):
        self._AIWeighting = None
       

class AIMoveStack: # Will hold all the possible nodes that the AI can move in
    def __init__(self, maxItems):
        self._items = [] # Array to hold all the valid possible moves the AI can make
        self._front = -1 # Points to the front of the queue
        self._maxSize = maxItems # Remains the same for all AI Move Stack's created as there are a fixed num of nodes of the board
        self._currentSize = 0

    def size(self):
        return len(self._items)
       
    def push(self, item): # Adds an item to the front
        if not self.isFull():
            self._front = self._front + 1
            self._currentSize = self._currentSize + 1
            self._items.append(item)
        else:
            print("Stack is full.")

    def pop(self): # Removes and returns the item from the front
        itemToReturn = None
       
        if not self.isEmpty():
            itemToReturn = self._items[self._front]
            self._front = self._front - 1
            self._currentSize = self._currentSize - 1
            self._items.pop()
        else:
            print("Stack is empty.")

        return itemToReturn

    def peek(self): # Returns the front item in the stack without removing it
        if not self.isEmpty():
            item = self._items[self._front]
            return item

    def isEmpty(self): # Indicates if the queue is empty
        if self._currentSize == 0:
            return True
        else:
            return False

    def isFull(self): # Indicates if the queue is full
        if self._currentSize == self._maxSize:
            return True
        else:
            return False

    def reset(self): 
        self._items.clear()
        self._front = -1
        self._currentSize = 0

    def getItems(self):
        return self._items

def checkNodeClicked(mousePos): # Loops through the nodes in my board graph and checks which has been clicked on using the coordinates
    for r in range(AIboard.getWidth()):
        for c in range(AIboard.getHeight()):
            node = AIboard.getPoints()[r][c]
            x, y = node.getCoords()

            if mousePos[0] >= x-15 and mousePos[0] <= x+15 and mousePos[1] >= y-15 and mousePos[1] <= y+15:
                return True, node # As soon as the clicked node is found, no more iterations of the for loop are needed
    return False, False # Not a valid node selection or no node has been selected 

def displayMousePointer(mousePos): # Displays the input indicator on the board node 
    for i in range(AIboard.getWidth()):
        for j in range(AIboard.getHeight()):
            x, y = AIboard.getPoints()[i][j].getCoords()
            
            if mousePos[0] >= x-15 and mousePos[0] <= x+15 and mousePos[1] >= y-15 and mousePos[1] <= y+15 and AIboard.getPoints()[i][j].getState() == EMPTY:
                pygame.draw.circle(mySurface, LGREEN, mousePos, 15, width=2)

def events(arrow, passRect, resignRect, toggleRect):
    option = False # No option selected so the default is False
    valid = False # Initially no valid node has been selected by the player
    node = False  # No node has been clicked on yet so the default is False as we have no node object
    pos = pygame.mouse.get_pos() # Defines mouse position on window
    
    if pos[0] > 30 and pos[0] < 600 and pos[1] > 50 and pos[1] < 620:
        displayMousePointer(pos)

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit() 
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN: # Checking if the user clicks on any game window buttons
            print("Clicked") # TEST
            if arrow.get_rect().collidepoint(pos):
                option = "Back"

            if passRect.collidepoint(pos):
                print('Passed') # TEST
                option = "Pass Update"

            if resignRect.collidepoint(pos):
                option = "Resign Update"

            if toggleRect != None and toggleRect.collidepoint(pos):
                print("Pressed toggle") # TEST
                option = "Set Toggle"

            if AIboard.getTurn() == 0: # A node that has been clicked only needs to be returned if it is the player's turn
               valid, node = checkNodeClicked(pos)
                   
    return option, valid, node

def playMove(valid, node): # Calls the function that places the stone selected by the current player (if it is not valid an error message will be displayed) or runs the AI make move function 
    if AIboard.getTurn() == 0: # If not ai's turn
        if valid and node.getState() == EMPTY and node.getValidPoint() and not AIboard.suicideRule(node) and node != AIboard.getP1LastNode() and node != AIboard.getP2LastNode(): # It the node the player has selected is valid (ko rule, not a sucide and not already occupied by a stone)
            print("VALID PLACE") # TEST
            AIboard.setValidSuicideNode(node)
            AIboard.placeStone(node)
            AIboard.addPasses(EMPTY)

        elif node != False:
            if not node.getValidPoint() or node.getState() != EMPTY or node == AIboard.getP1LastNode() or node == AIboard.getP2LastNode() or AIboard.suicideRule(node): # If the node is invalid to move in 
                valid = False
                tpg.displayErrorMessage()
            
    else: # If it's the AI's turn
        print("AI's Turn") # TEST
        AIboard.AIMakeMove()
        

pygame.init() 
pygame.freetype.init() 
fpsClock = pygame.time.Clock() # Frames/second e.g.30 To limit the number of times it wil run the game loop.
mySurface = pygame.display.set_mode((WINWIDTH, WINHEIGHT), 0, 32) # Window size, 0, bit colour
pygame.display.set_caption(CAPTION) 

arrow, boardImage, blackStone, whiteStone = tpg.loadImages()

def AIGameRunner():
    global AIboard
    AIboard = AIBoard()

    while True:
        mySurface.fill(BLACK)
        fpsClock.tick(33)
        passRect, resignRect, toggleRect = AIboard.displayWindow()
        optionClicked, validCheck, node = events(arrow, passRect, resignRect, toggleRect)

        if optionClicked == "Back":
            break

        elif optionClicked == "Pass Update":
            AIboard.passedUpdate()
    
        elif optionClicked == "Resign Update":
            AIboard.resignedUpdate()

        elif optionClicked == "Set Toggle": 
            AIboard.setToggleCount(99)
            
        playMove(validCheck, node)
       
        if AIboard.getToggleCount() > 0:
            AIboard.displayAIToggle()
        AIboard.setToggleCount(AIboard.getToggleCount()-1)
        
        if AIboard.getPassed() or AIboard.getResigned(): # If two consecutive passes or a resign has been made the game is over
            AIboard.gameOver()
            pygame.display.update()
            pygame.time.wait(5000)
            break

        pygame.display.update()

    return optionClicked
