import pygame, sys
from pygame.locals import *
import pygame.freetype 
import time
import math
import random


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
BEIGE = (214,165,45)
LGREEN = (161,235,175)
YELLOW = (214,165,45)
EMPTY, B, W = '.', 'B', 'W'

# Board is 570x570, each grid square is 95x95, grid to edge is 47.5


class Board():
    def __init__(self):
        self._width = 6
        self._height = 6
        self._boardFull = False # Used 
        self._turn = 0 # The game starts with the first player's turn - BLACK, which is indicated by 0. WHITE's turn is indicated by 1
        self._passCount = 0
        self._p1PassCount = 0
        self._p2PassCount = 0
        self._passed = False
        self._resigned = False
        self._passes = [] # A list to hold whether or not a player has passed at the end of each turn

        self._points = self.initialisePoints() # GRAPH with the info for every point on the board - node objects (from node graph class)
        self._groups = [] # List of all the stone groups on the board

        self._p1PlacedStone = False
        self._p2PlacedStone = False
        self._p1LastNode = None # For implementing the Ko rule, we need to know the last node each player placed a stone on to prevent a repeat
        self._p2LastNode = None 
        self._p1Captures = 0 # Holds the number of captures of the opponent's stones each player has made during the game and is displayed
        self._p2Captures = 0
        self._validSuicideNode = None # Holds the valid suicide node for the current turn - i.e. allowed if it results in immediate capture of the opponent's stone/s

        self.updateStoneNeighbours()

    def addP1Captures(self, c1): # Used to add to BLACK's capture's score when WHITE's stone/s are captured
        self._p1Captures += c1

    def addP2Captures(self, c2): # Used to add to WHITE's capture's score when BLACK's stone/s are captured
        self._p2Captures += c2

    def getP1Captures(self):
        return self._p1Captures

    def getP2Captures(self):
        return self._p2Captures
   
    def getWidth(self):
        return self._width

    def getHeight(self):
        return self._height

    def getGroups(self):
        return self._groups

    def getPassed(self):
        return self._passed

    def addPasses(self, newPass): # Adds to the passes list each turn whether or not the player has passed
        self._passes.append(newPass)

    def getResigned(self):
        return self._resigned
   
    def initialisePoints(self): # Creates a full graph (array) of all the Node objects (points on the board) and 
        points = []             # sets the window coords for when a stone is placed in a point (node)
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

    def getPoints(self):
        return self._points

    def getBoardFull(self):
        return self._boardFull

    def setBoardFull(self, newState):
        self._boardFull = newState

    def getTurn(self):
        return self._turn

    def getP1PlacedStone(self):
        return self._p1PlacedStone

    def getP2PlacedStone(self):
        return self._p2PlacedStone

    def setP1PlacedStone(self, newState):
        self._p1PlacedStone = newState

    def setP2PlacedStone(self, newState):
        self._p2PlacedStone = newState

    def getP1LastNode(self):
        return self._p1LastNode

    def getP2LastNode(self):
        return self._p2LastNode

    def setP1LastNode(self, newNode):
        self._p1LastNode = newNode

    def setP2LastNode(self, newNode):
        self._p2LastNode = newNode

    def setValidSuicideNode(self, newNode):
        self._validSuicideNode = newNode

    def getValidSuicideNode(self):
        return self._validSuicideNode
       
    def displayWindow(self): # Draws and displays the empty board, player information, and resign and play buttons onto mySurface
        mySurface.blit(arrow, (25, 12))

        makePygameRectangle(LGREY, 32, 52, 570, 570, 3)
        mySurface.blit(boardImage, (30, 50))

        makePygameRectangle(LGREY, 632, 52, 290, 80, 3)
        makePygameRectangle(WHITE, 630, 50, 290, 80, 3)
        pygame.draw.line(mySurface, WHITE, (630,75), (920,75), 3)
        makePygameFont("Player 1 -> B", 25, WHITE, 775, 62.5, 'Byorg.ttf')
        makePygameFont("Captures: "+str(self._p1Captures), 20, WHITE, 775, 102.5, 'Byorg.ttf')

        makePygameRectangle(LGREY, 632, 147, 290, 80, 3)
        makePygameRectangle(WHITE, 630, 145, 290, 80, 0)
        pygame.draw.line(mySurface, BLACK, (630,170), (920,170), 3)
        makePygameFont("Player 2 -> W", 25, BLACK, 775, 157.5, 'Byorg.ttf')
        makePygameFont("Captures: "+str(self._p2Captures), 20, BLACK, 775, 197.5, 'Byorg.ttf')

        passRect = makePygameRectangle(LGREY, 630, 255, 137.5, 80, 0)
        passRectL = makePygameRectangle(WHITE, 630, 255, 137.5, 80, 2)
        resignRect = makePygameRectangle(DGREY, 782.5, 255, 137.5, 80, 0)
        resignRectL = makePygameRectangle(WHITE, 782.5, 255, 137.5, 80, 2)
        makePygameFont("PASS", 25, WHITE, 698.75, 295, 'Byorg.ttf')
        makePygameFont("RESIGN", 25, WHITE, 851.25, 295, 'Byorg.ttf')

        if self._turn == 0:
            makePygameFont("Player 1's turn ...", 25, LGREY, 317, 27, 'Byorg.ttf')
            makePygameFont("Player 1's turn ...", 25, WHITE, 315, 25, 'Byorg.ttf')
        else:
            makePygameFont("Player 2's turn ...", 25, LGREY, 317, 27, 'Byorg.ttf')
            makePygameFont("Player 2's turn ...", 25, WHITE, 315, 25, 'Byorg.ttf')

        self.displayStones() # The board must continuosly display the stones on the board

        return passRect, resignRect

    def displayStones(self): # Displays the correct colour stones onto the nodes whose state in the graph are not EMPTY
        for row in range(self._height):    # Loops through all the board node objects in my graph - self._points,
            for col in range(self._width): # and blits them to mySurface if its state isn't empty
                state = self._points[row][col].getState()
               
                if state != EMPTY:
                    x, y = self._points[row][col].getCoords()
                   
                    if state == B:
                        bRect = blackStone.get_rect()
                        bRect.center = (x, y)
                        mySurface.blit(blackStone, bRect)
                    else:
                        wRect = whiteStone.get_rect()
                        wRect.center = (x, y)
                        mySurface.blit(whiteStone, wRect)

    def updateStoneNeighbours(self): # Adds the up, down, left, and right immediate neighbours to each of the graph's stone's neighbours list
        for r in range(self._width):
            for c in range(self._height):
                node = self._points[r][c]
                node.resetNeighbours()
               
                if r != 0: # No up neighbour if in top row
                    node.addNeighbour(self._points[r-1][c])

                if r != self._height-1: # No down neighbour if in bottom row
                    node.addNeighbour(self._points[r+1][c])
               
                if c != 0: # No left neighbour if in leftmost col
                    node.addNeighbour(self._points[r][c-1])

                if c != self._width-1: # No right neighbour if in rightmost col
                    node.addNeighbour(self._points[r][c+1])
           
    def placeStone(self, node): # This changes the state of a node on the board via the graph to hold the counter (colour)
        if self._turn == 0:
            state = B
            self.setP1PlacedStone(True)
            self.setP1LastNode(node) # Used for the Ko rule to determine the last node each player played on
        else:
            state = W
            self.setP2PlacedStone(True)
            self.setP2LastNode(node) # Used for the Ko rule to determine the last node each player played on
   
        node.setState(state)

        self.updateBoard() # Every a stone is placed, we want to update the connections, group, and liberties of every stone (reset all too)  

        self.printTextBoard() # Displays a board as text in the terminal for testing
       
        self._turn += 1 
        if self._turn == 2:
            self._turn = 0
           
        print(len(self._groups)) # TEST

        for g in self._groups:
            print("grp: ",len(g)) # TEST

    def updateStoneConnections(self):  # Goes in placeStone - this updates ALL connections of a stone after a move is made (and node.group if needed)
        for row in range(self._width): # Connections can be BEYOND IMMEDIATE neighbours i.e. for a group (chain of stones)
            for col in range(self._height):
                node = self._points[row][col]
                node.resetConnections() # Clears all previous stone connections for the current node as they will change after a move is made

                # This checks the next stone in each direction and appends it to the current stone's connections if it is the same colour
                # The methods stop when the stone they are checking is not the same colour as the stone object in board.points[row][col] or EMPTY
                if node.getState() != EMPTY:
                    self.checkUpConnections(node, row, col) # Checks for same-colour nodes above the current node and adds them to connections
                    self.checkDownConnections(node, row, col) # Checks for same-colour nodes below the current node and adds them to connections
                    self.checkLeftConnections(node, row, col) # Checks for same-colour nodes left of the current node and adds them to connections
                    self.checkRightConnections(node, row, col) # Checks for same-colour nodes right of the current node and adds them to connections

    def checkUpConnections(self, node, r, c):
        if r != 0: # If the node is on the top row, it will have NO up connections
            r -= 1 # Start checking with the stone in the row ABOVE the 'node', i.e. sooner row in graph array
            up = True
           
            while up and r >= 0 and r < self._height: # The top row [0] is the last stone we compare to
                nodeToCheck = self._points[r][c] # The node we are checking the origional 'node' against

                if nodeToCheck.getState() != EMPTY and nodeToCheck.getState() == node.getState(): # This means there is a node connection - a group (but the actual groups will be assigned later)
                    node.addConnection(nodeToCheck)
                    r -= 1

                else:
                    up = False # If there isn't the same stone up, then the connection/chain in this direction has ended and the while loop stops

    def checkDownConnections(self, node, r, c):
        if r != 5: # If the node is on the bottom row, it will have NO down connections
            r += 1 # Start checking with the stone in the row BELOW the 'node', i.e. later row in graph array
            down = True
           
            while down and r < self._height and r >= 0: # The bottom row [5] is the last stone we compare to
                nodeToCheck = self._points[r][c] # The node we are checking the origional 'node' against

                if nodeToCheck.getState() != EMPTY and nodeToCheck.getState() == node.getState(): # This means there is a node connection
                    node.addConnection(nodeToCheck)                                               
                    r += 1

                else:
                    down = False # If there isn't the same stone down, then the connection/chain in this direction has ended and the while loop stops
                   
    def checkLeftConnections(self, node, r, c):
        if c != 0: # If the node is in the leftmost column, it will have NO left connections
            c -= 1 # Start checking with the stone in the column to the left the 'node', i.e. sooner col in graph array
            left = True

            while left and c >= 0 and c < self._width: # The leftmost col [0] is the last stone we compare to
                nodeToCheck = self._points[r][c] # The node we are checking the origional 'node' against

                if nodeToCheck.getState() != EMPTY and nodeToCheck.getState() == node.getState(): # This means there is a node connection
                    node.addConnection(nodeToCheck)
                    c -= 1

                else:
                    left = False # If there isn't the same stone left, then the connection/chain in this direction has ended and the while loop stops
       
    def checkRightConnections(self, node, r, c):
        if c != 5: # If the node is in the rightmost column, it will have NO right connections
            c += 1 # Start checking with the stone in the column to the right the 'node', i.e. later col in graph array
            right = True

            while right and c < self._height and c >= 0 : # The rightmost col [5] is the last stone we compare to
                nodeToCheck = self._points[r][c] # The node we are checking the origional 'node' against

                if nodeToCheck.getState() != EMPTY and nodeToCheck.getState() == node.getState(): # This means there is a node connection
                    node.addConnection(nodeToCheck)
                    c += 1

                else:
                    right = False # If there isn't the same stone right, then the connection/chain in this direction has ended and the while loop stops

    def updateStoneGroups(self): # Used to go through all the board nodes and create new groups if chains exist
        self._groups = []
       
        for row in range(self._height):
            for col in range(self._width):
                node = self._points[row][col]
                state = node.getState()
                g = [] # Potentially used to create a new group
                existing = False # Initially, the current stone is not known to exist in the a group which has been previously created - we check this below

                if len(node.getConnections()) == 0:
                    node.setGroup(-1) # The stone's node (point from graph) has no connections so it is a lone stone, i.e. -1 (changed to show it has been checked for a group)

                else: # The stone's node has other same-colour connections so it is part of a group we need to create/add to
                    for group in range(len(self._groups)):        # Loops through the existing groups
                        for n in range(len(self._groups[group])): # then loops through each node in each existing group
                            if node in self._groups[group][n].getConnections(): # Checks if the current node has a connection to any of the nodes in an existing group
                                existing = True

                                if node not in self._groups[group]: # We first need to ensure we are not adding a connected stone which has already been added into a group
                                    self._groups[group].append(node) # If the connected stone is not already in a group, we add and assign it the group which it is connected to (by any node)
                                    node.setGroup(group)

                    if not existing: # There is no existing groups with the current node so create a new one incl all its connections
                        node.setGroup(len(self._groups)) # Creating a new group - the new group num will be the length of the list as group nums start at 0
                        g.append(node) # Adding the current node to the new group

                        for n in node.getConnections(): # Adding all the found connections nodes to the new group and assigning them a group number
                            n.setGroup(len(self._groups))
                            g.append(n)

                        self._groups.append(g) # Adding the new group to the full list of board groups (chains)

    def resetStoneLiberties(self): # This function resets the liberties list for every node on the board as it changes each turn
        for row in range(self._height):
            for col in range(self._width):
                self._points[row][col].resetLiberties()
           
    def updateGroupStoneLiberties(self): # Goes through each group on the board and updates the liberties list of all the nodes in a group
        self.resetStoneLiberties()       # If a stone is in a group, the stone's liberties will be the same as the liberties of all the stones in that group
        liberties = []

        for group in range(len(self._groups)):        # For each node in each group we check their immediate neighbours
            for n in range(len(self._groups[group])): # and if any are EMPTY (their state) then we can add this to the stone's liberties
                node = self._groups[group][n]
                neighbours = node.getNeighbours()

                for neighbour in neighbours:
                    if neighbour.getState() == EMPTY and neighbour not in liberties: # EMPTY neighbours (liberties) of a groups' stones may cross over
                        liberties.append(neighbour)                                  # so we must check if it already exists in the liberties list

            print("libs", len(liberties)) # TEST
           
            for groupNode in self._groups[group]: # For each of the stones in a group, their liberties are set to the list of node objects found above (liberties)
                groupNode.setLiberties(liberties)
                print("groupNode libs: ", len(groupNode.getLiberties())) # TEST

            liberties = []
                 
    def updateLoneStoneLiberties(self): # Checks the liberties (EMPTY adjacent spaces) for each lone stone node in our board graph using the direct neighbours (max 4)
        for row in range(self._height):
            for col in range(self._width):
                node = self._points[row][col]
                liberties = []

                if node.getGroup() == -1:
                    for n in node.getNeighbours():
                        if n.getState() == EMPTY:
                            liberties.append(n)

                    node.setLiberties(liberties)
   
    def koRule(self): # Saves the last node object placed-on by each player and sets it to an invalid node to play on next, to prevent a consecutive/repeat of a board state
        if self._p1PlacedStone:
            node = self._p1LastNode
            node.setValidPoint(False)

            self.setP1PlacedStone(False)
           
        elif self._p2PlacedStone:
            node = self._p2LastNode
            node.setValidPoint(False)

            self.setP2PlacedStone(False)

    def suicideRule(self, node): # The player cannot place a stone if it results in it getting captured immediately
        suicide = False          # but it is allowed if it results in immediate capture of the opponent's stone/s
        groupCapture = False
        stoneCapture = False

        if self._turn == 0:
            state = B
        else:
            state = W

        # Checking for a potential self capture of a group of stones
        for group in self._groups:
            emptyNextNeighbour = False
            liberties = group[0].getLiberties()

            if len(liberties) == 1 and node in liberties: # If the group has one liberty left which is the node we want to place at then it's a capture
                if state == group[0].getState(): # If the state of the group which would be captured is the same as the node then suicide

                    for l in liberties[0].getNeighbours():
                        if l.getState() == EMPTY:
                            emptyNextNeighbour = True
               
                    if not emptyNextNeighbour:
                        suicide = True

                else:
                    groupCapture = True # It's not a suicide if it will result in the immediate capture of an opponent's chain

        emptyNeighbour = False

        # Checking for a potential stone capture if a stone on the board has the node chosen to place in as it's last liberty
        for row in range(self._height):
            for col in range(self._width):
                toCheck = self._points[row][col]
                liberties = toCheck.getLiberties()
               
                if toCheck.getGroup() == -1 or toCheck.getGroup() == None and toCheck.getState() != EMPTY: # If the nodeToCheck is a lone stone
                    if len(liberties) == 1 and node in liberties and toCheck.getState() == state: # If the current stone has one liberty and it is the node the player wants to place in and the stone's state is the same as the current player
                        for neighbour in liberties[0].getNeighbours(): # If the stone's last liberty has a neighbour that is empty then the stone will not be captured 
                            if neighbour.getState() == EMPTY:
                                emptyNeighbour = True

                        if not emptyNeighbour:
                            suicide = True
                            print("running single capture") # TEST

                    elif len(liberties) == 1 and node in liberties and toCheck.getState() != state: # If the stone has one liberty left and the node the player wants to move into is the last liberty then the stone in the current group will be captured
                        stoneCapture = True

        # Checking for a potential self capture when placing into the lone space the player wants to play in
        opponentStateNeighbours = 0

        for n in node.getNeighbours():
            if n.getState() != state and n.getState() != EMPTY:
                opponentStateNeighbours += 1

        if opponentStateNeighbours == len(node.getNeighbours()) and not groupCapture and not stoneCapture: # If the node HAS all opponent-player stones as it's neighbours then playing in this node WOULD be an immediate suicide  
            suicide = True                                                                                 # Checking whether there is the same amount of opponentStoneNeighbours as the actual stone's neighbours accounts for all cases
            print("running self capture") # TEST

        return suicide

    def removeDeadStonesC(self): # Checks the chains to see if they are captured and removes them unless an immediate capture has taken place
        if self._turn == 0:
            state = B
        else:
            state = W
       
        remove = []
       
        # First we check if the groups (chains of stones) have any liberties left, if not, it has been captured by the opposing player
        for group in self._groups:
            print("group libs removal: ", len(group[0].getLiberties())) # TEST
            if len(group[0].getLiberties()) == 0 and group[0].getState() != state: # NOTE: you cannot self-capture so this prevents that (part of the suicide rule)
                if group[0].getState() == B:
                    print("adding to W capts",len(group)) # TEST
                    self._p2Captures += len(group) # Adds to WHITE's captures the number of stones in the group

                else:
                    print("adding to B capts",len(group)) # TEST
                    self._p1Captures += len(group) # Adds to BLACK's captures the number of stones in the group

                for node in group: # Resets all the attributes of the nodes in the group after the stones in it have been captured
                    node.setState(EMPTY)
                    node.resetAll()
               
                remove.append(self._groups.index(group)) # Adds the group which has been captured to the remove list to be popped later on
       
        if len(remove) > 1: # This prevents a capture of the current player stones if the move has just caused an immediate capture of the opponent    
            newGroups = []

            for i in range(len(self._groups)): # If 
                if i not in remove:
                    newGroups.append(self._groups[i])

            self._groups = newGroups
           
        else:
            for i in remove:
                if self._groups[i] != state:
                    print("removing group: ",i ) # TEST
                    self._groups.pop(i)

    def removeDeadStonesL(self): # Checks if the remaining lone stones have no librties left and remove these
        for row in range(self._height):
            for col in range(self._width):
                node = self._points[row][col]
               
                if node.getState() != EMPTY and node.getGroup() == -1: # If the stone is a lone stone 
                    if len(node.getLiberties()) == 0 and node != self._validSuicideNode: # If the node has no liberties left and does not result in a self capture
                        if node.getState() == B: # Add a capture point to the opposite player's turn
                            print("adding to W capts 1") # TEST
                            self._p2Captures += 1
                        else:
                            print("adding to B capts 1") # TEST
                            self._p1Captures += 1
                   
                        node.setState(EMPTY)
                        node.resetAll()
                        print("removing", node) # TEST

    def updateBoard(self): # Every time a stone is placed, we want to update the connections, group, and liberties of every stone
        self.updateStoneNeighbours() # Adds the up, down, left, and right immediate neighbours to each of the graph's stone's neighbours list
        self.updateStoneConnections() # Updates all the connections of each stone after a move is made 
        self.updateStoneGroups() # Used to go through all the board nodes and create new groups if chains exist
        self.updateGroupStoneLiberties() # Goes through each group on the board and updates the liberties list of all the nodes in a group
        self.updateLoneStoneLiberties() # Checks the liberties for each lone stone node in the board graph using the direct neighbours and updates its liberties list
        self.removeDeadStonesC() # Checks the chains to see if they are captured and removes them unless an immediate capture has taken place
        self.removeDeadStonesL() # Checks if the remaining lone stones have no librties left and remove these
        self.koRule() # Saves the last node object placed-on by each player and sets it to an invalid node to play on next, to prevent a consecutive/repeat of a board state

    def printTextBoard(self): # TEST - simple text display of the board's nodes' state
        b = []

        for i in range(self._width): # Loops through the full board graph and gets a list of all the states
            for j in range(self._height):
                node = self._points[i][j]
                b.append(node.getState() + " L" + str(len(node.getLiberties())))
            print(b)
            b = []

    def passedUpdate(self):
        print('running passedUpdate') # TEST
        if self._turn == 0:
            self._passes.append(B)
            self._p2Captures += 1
            makePygameFont("< BLACK gave away a point to WHITE for passing >", 20, WHITE, 708, 26, 'Byorg.ttf')
        else:
            self._passes.append(W)
            self._p1Captures += 1
            makePygameFont("< WHITE gave away a point to BLACK for passing >!", 20, WHITE, 708, 26, 'Byorg.ttf')

        if (self._passes[len(self._passes)-1] == B and self._passes[len(self._passes)-2] == W) or (self._passes[len(self._passes)-1] == W and self._passes[len(self._passes)-2] == B): # Checks the last two pass states in the passes array (B, W, or EMPTY) and if they are equal (consecutive) then the game should end
            self._passed = True

        self._turn += 1 # If a player passes, the other player can now play a move again
        if self._turn == 2:
            self._turn = 0

        self.updateBoard()
        self.displayStones()
        pygame.display.update() 
        pygame.time.wait(600)
       
    def resignedUpdate(self): 
        self._resigned = True

    def gameOver(self):       # Runs when either two consecutive passes or a resign has been made 
        winner = self.score() # It displays the winner for the users

        if winner == B:
            makePygameRectangle(BLACK, 60, 150, 830, 350, 0)
            makePygameRectangle(LGREEN, 60, 150, 830, 350, 4)
            makePygameFont("PLAYER 1 BLACK WINS!", 60, WHITE, 475, 325, 'Byorg.ttf')

        elif winner == W:
            makePygameRectangle(WHITE, 60, 150, 830, 350, 0)
            makePygameRectangle(LGREEN, 60, 150, 830, 350, 4)
            makePygameFont("PLAYER 2 WHITE WINS!", 60, BLACK, 475, 325, 'Byorg.ttf')
           
        else:
            makePygameRectangle(BLACK, 60, 150, 415, 350, 0)
            makePygameRectangle(WHITE, 475, 150, 415, 350, 0)
            makePygameRectangle(LGREEN, 60, 150, 830, 350, 4)
            makePygameFont("DRAW!", 60, LGREEN, 475, 325, 'Byorg.ttf')

    def score(self): # Determines the winner of the game by finding total area each player occupies on the board together with their total captures & returns it
        p1Score = 0
        p2Score = 0
        winner = None
       
        for r in range(self._height):
            for c in range(self._width):
                node = self._points[r][c]

                if node.getState() != EMPTY:
                    if node.getState() == B:
                        p1Score += 1
                    else:
                        p2Score += 1

        p1Score += self._p1Captures
        p2Score += self._p2Captures

        if p1Score > p2Score:
            winner = B
        elif p2Score > p1Score:
            winner = W

        return winner

       
class Node: # GRAPH data structure - node object class
    def __init__(self, x, y):
        self._x, self._y = x, y # Window position coords
        self._state = EMPTY
        self._validPoint = True
        self._neighbours = [] # IMMEDIATE neighbours (4 per stone max) - up, down, left, right
        self._connections = [] # ALL connections of a stone, potentially BEYOND IMMEDIATE neighbours i.e. a group
        self._group = None # Default None if not checked for a group. I will separately create a new group with all stones in a list if needed in updateGroups
        self._liberties = [] 

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

    def addConnection(self, newNode): # Used by board class updateStoneConnections() for each stone after a move is made
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

    def resetAll(self): # Used to reset all the attributes of a board node to the default values when its stone is removed from the board
        self._connections.clear()
        self._validPoint = True
        self._group = None
        

def makePygameFont(message, size, colour, xPos, yPos, style):# Makes one piece of text
    font = pygame.freetype.Font(style, size) # None = the font style. # 20 = the size
    text = font.render(message,colour) # text is now a tuple. index 0 = surface & index 1 = rect
    textpos = text[1] # textpos is the rectangle
    textpos.centerx = xPos # x position of text.
    textpos.centery = yPos # y position of text
    mySurface.blit(text[0],textpos) # place on the screen the actual text (surface) in the rectangles position

    return textpos

def makePygameRectangle(colour, xPos, yPos, width, height, w):
    myRect = pygame.Rect(xPos, yPos, width, height)
    pygame.draw.rect(mySurface, colour, myRect, width=w)

    return myRect

def loadImages():
    arrow = pygame.image.load('Arrow.png').convert_alpha()
    arrow = pygame.transform.scale(arrow,(30, 60)) # Image, (Width, Height)
    arrow = pygame.transform.rotate(arrow, 90)

    boardImage = pygame.image.load('Go board 6x6.png').convert_alpha()
    boardImage = pygame.transform.scale(boardImage, (570, 570))

    blackStone = pygame.image.load('Black stone.png').convert_alpha()
    blackStone = pygame.transform.scale(blackStone, (85, 85))

    whiteStone = pygame.image.load('White stone.png').convert_alpha()
    whiteStone = pygame.transform.scale(whiteStone, (85, 85))

    return arrow, boardImage, blackStone, whiteStone

def events(arrow, passRect, resignRect):
    option = False # No option selected yet so the default is False
    valid = False
    node = False # No node has been clicked on yet so the default is False as we have no node object
    pos = pygame.mouse.get_pos() # Defines mouse position on window

    if pos[0] > 30 and pos[0] < 600 and pos[1] > 50 and pos[1] < 620:
        displayMousePointer(pos)
   
    for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit() 
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if arrow.get_rect().collidepoint(pos):
                    option = "Back"

                elif passRect.collidepoint(pos):
                    option = "Pass Update"

                elif resignRect.collidepoint(pos):
                    option = "Resign Update"

                else:
                    valid, node = checkNodeClicked(pos)
                    option = "Play Move"

    return option, valid, node

def playMove(valid, node): # Calls the function to place the stone selected by the current player and if the node selected is invalid (e.g. suicide) then it will call the function to display an error message for the suer
    if valid and node.getState() == EMPTY:
        if node.getValidPoint() and not board.suicideRule(node) and node != board.getP1LastNode() and node != board.getP2LastNode():
            print("VALID PLACE") # TEST
            board.setValidSuicideNode(node)
            board.placeStone(node)
            board.addPasses(EMPTY)
        else:
            valid = False
            displayErrorMessage() # Displays an eror message if a game rule has been broken, e.g. Ko rule or Suicide rule
       
def checkNodeClicked(mousePos): # Loops through the nodes in my board graph and checks which has been clicked on using the coordinates
    for r in range(board.getWidth()):
        for c in range(board.getHeight()):
            node = board.getPoints()[r][c]
            x, y = node.getCoords()

            if mousePos[0] >= x-15 and mousePos[0] <= x+15 and mousePos[1] >= y-15 and mousePos[1] <= y+15:
                return True, node # As soon as the clicked node is found, no more iterations of the for loop are needed

    return False, False # Not a valid node selection or no node has been selected         

def displayMousePointer(mousePos): # Displays an input indicator for the player if they are hovering over a valid node on the board
    for i in range(board.getWidth()):
        for j in range(board.getHeight()):
            x, y = board.getPoints()[i][j].getCoords()

            if mousePos[0] >= x-15 and mousePos[0] <= x+15 and mousePos[1] >= y-15 and mousePos[1] <= y+15 and board.getPoints()[i][j].getState() == EMPTY:
                pygame.draw.circle(mySurface, LGREEN, mousePos, 15, width=2)

def displayErrorMessage():
    makePygameRectangle(WHITE, 200, 260, 200, 100, 0)
    makePygameRectangle(BLUE, 200, 260, 200, 100, 4)
    makePygameFont("INVALID MOVE", 30, BLUE, 300, 310, 'Byorg.ttf')
    pygame.display.update()
    time.sleep(2)
               

pygame.init() 
pygame.freetype.init() 
fpsClock = pygame.time.Clock() 
mySurface = pygame.display.set_mode((WINWIDTH, WINHEIGHT), 0, 32) 
pygame.display.set_caption(CAPTION) 

arrow, boardImage, blackStone, whiteStone = loadImages()


def twoPlayerGameRunner():
    global board
    board = Board()

    while True:
        mySurface.fill(BLACK)
        fpsClock.tick(33)
        passRect, resignRect = board.displayWindow()
   
        optionClicked, validCheck, node = events(arrow, passRect, resignRect)

        if optionClicked == "Back":
            break

        elif optionClicked == "Pass Update":
            board.passedUpdate()

        elif optionClicked == "Resign Update":
            board.resignedUpdate()

        elif optionClicked == "Play Move":
            playMove(validCheck, node)

        if board.getPassed() or board.getResigned(): # If two consecutive passes have been made of a player has resigned then the game is over
            board.gameOver()
            pygame.display.update()
            pygame.time.wait(3000)
            break

        pygame.display.update()

    return optionClicked
