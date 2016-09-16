from __future__ import print_function
import sys
import copy
import timeit
import fileinput

"""
Torus checkers AI progam, designed to take in a single game position
in the format:
  g w h t
  p turn whoNow
  r position0 position1 etc...
  w position0 position1 etc...

based upon the variable names I have chosen.
Outputs the best move as deemed by its heuristic and decision tree in 
the format:
  m turn whoNow start end
  note; if no move is available or the turnlimit is surpassed start 
  shall be 0 with the end value being indicating the victor or draw
  with new board position after that (only for 8x8 boards)
"""
class Torus:
  redPositions = []
  whitePositions = []
  w = 0
  h = 0
  t = 0
  turn = 0
  whoNow = 0
  time = 0
  maxN = 0
  minN = 0
  """
  method: main
  @param: self

  Description:
  Driver for the torus-checkers AI, calls all subsequent methods.
  """
  def main(self):
    self.parseInput()   #takes input from stdin
    self.printBoard()   #prints a typographical reference of board
    self.imagineGame()  #begins the AI process

  """
  method: parseInput
  @param: self
  

  Description:
  Parses the command line arguments for aformentioned variables in the format
  listed above. Throws an error and exits if anything is out of the ordinary.
  Currently does not support beyond 8x8
  """
  def parseInput(self):
    lineSplit = []
    for i in range(0,4):
      line = sys.stdin.readline()
      lineSplit = line.split()      #breaks the line into components
      if len(lineSplit) < 1:      
        print("Length Error")
        exit()
      if i is 0:                    #defines the width, height, and turn limit
        self.w = int(lineSplit[1])
        self.h = int(lineSplit[2])
        self.t = int(lineSplit[3])
        if self.w is not 8:              #no support for non 8x8 atm
          print("Error: Board size not supported")
          exit()
        if lineSplit[0] is not 'g' or self.w is not self.h or self.t <= 0:
          print("Error on first line")
          exit()
      elif i is 1:                  #defines the players, what turn it is and who's up
        self.turn = int(lineSplit[1])
        self.whoNow = int(lineSplit[2])
        self.maxN = self.whoNow
        if self.maxN is 0:
          self.minN = 1
        else:
          self.minN = 0
        if lineSplit[0] is not 'p' or self.turn < 0 or self.whoNow not in [0,1]:
          print("Error on second line")
          exit()
      elif i is 2:                  #red positions
        j = 0
        for position in lineSplit:
          if position is not 'r' and j is not 1:    #first round it's r second is how many
            if int(position) in self.redPositions or int(position) in self.whitePositions:
              print("Repeat Error")
              exit()
            self.redPositions.append(int(position))
          j += 1
      elif i is 3:                  #white positions
        j = 0
        for position in lineSplit:
          if position is not 'w' and j is not 1:
            if int(position) in self.redPositions or int(position) in self.whitePositions:
              print("Repeat Error")
              exit()
            self.whitePositions.append(int(position))
          j += 1

  """
  method: printBoard
  @param: self

  Description:
  Prints a typographical reference of the board based upon the command line input
  """
  def printBoard(self):
    board = ""
    i = 0
    for j in range(1, 33):
      board += "   "
      if i%2 is 0 and (j-1)%4 is 0:
        board += "   "
      filler = ""
      if j in self.redPositions:
        filler = "r" + str(j) 
        board += filler.ljust(3)
      elif j in self.whitePositions:
        filler = "w" + str(j)
        board += filler.ljust(3)
      else:
        filler = u'\u2588' + u'\u2588' + u'\u2588'
        board += filler
      if j%4 is 0:
        board+= "\n"
        i += 1
    print(board)

  """
  method: imagineGame
  @param: self

  Description:
  Creates the AlphaBeta tree, and calls the findMoves method, and will return the
  final move deemed best by the program
  """
  def imagineGame(self):
    #while(time-timeit.default_timer() < 5):
    #  continue
    parent = Node()
    parent.whitePositions = self.whitePositions
    parent.redPositions = self.redPositions
    parent.turn = self.turn
    parent.whoNow = self.whoNow
    test = self.findMoves(self.whitePositions, self.redPositions, self.turn, self.whoNow)
    if len(test) is 0:
      print("No moves available")
      exit()
    self.time = timeit.default_timer()
    parent.A = self.play(parent,parent.A,parent.B) 
    maxC = -sys.maxint -1
    j = -1
    for i in range(0,len(parent.children)):
      if parent.children[i].alpha > maxC:
        j = i 
        maxC = parent.children[i].alpha
    third = 0
    print("m", self.turn, self.whoNow, end=" ")
    if maxC is 0:
      third = 0
      fourth = self.minN
      print(third,fourth)
    else:
      for i in range(0,len(parent.children[j].move)):
        if i%2 is 0:
          print(parent.children[j].move[i], end=" ")
    print(" ")
      
    
  def play(self, current, A, B):
    if (self.time - timeit.default_timer() > 5 or current.turn >= self.t):
      return self.heuristic(current)
    if (len(self.findMoves(self.whitePositions,self.redPositions,self.turn,self.whoNow)) is 0):
        return self.heuristic(current)
    if(self.draw(current)):
      return 0

    if(self.victory(current)):
      return 1000

    alpha = -sys.maxint
    beta = sys.maxint
    if current.whoNow is self.minN:
      self.generateChildren(current, current.whoNow)
      for child in current.children:
        val = self.play(child, A, min(B, current.beta))
        if val < current.beta:
          beta = val
        if current.A >= current.B:
          return beta
      return beta
    else:
      self.generateChildren(current, current.whoNow)
      for child in current.children:
        val = self.play(child, max(current,max(alpha,A)), B)
        if val > alpha:
          alpha = val
        if B <= val:
          return alpha
      return alpha

  def heuristic(self, current):
    val = 0
    if current.whoNow is 0:
      val += len(current.redPositions)
      val -= len(current.whitePositions)
      for i in current.redPositions:
        if i in range(13,21):
          val += 0.2
    else:
      val -= len(current.redPositions)
      val += len(current.whitePositions)
      for i in current.whitePositions:
        if i in range(13,21):
          val += 0.2


  def draw(self, current):
    x = self.findMoves(current.whitePositions, current.redPositions, current.turn, current.whoNow)
    if len(x) is 0:
      return True
    else: 
      return False

  def victory(self, current):
    if current.whoNow is 0:
      if len(current.whitePositions) is 0:
        return True
      return False
    else:
      if len(current.redPositions) is 0:
        return True
      return False

  def generateChildren(self, current, whoNow):
    if whoNow is 0:
      current.moves = self.findMoves(current.whitePositions, current.redPositions, current.turn, current.whoNow)
      if len(current.moves) is 0:
        return []
      captures = [x for x in current.moves if len(x) is not 2]
      if len(captures) is not 0:
        current.moves = [x for x in current.moves if len(x) is not 2]
      for move in current.moves:
        n = Node()
        n.whitePositions = copy.deepcopy(current.whitePositions)
        n.redPositions = copy.deepcopy(current.redPositions)
        n.turn = current.turn+1
        n.whoNow = (current.whoNow+1)%2
        n.move = move
        
        if len(move) is 2:
          n.redPositions.remove(move[0])
          n.redPositions.append(move[1])
        else:
          i = 0; 
          n.redPositions.remove(move[0])
          for i in range(1, len(move)):
            if i%2 is 1:
              n.whitePositions.remove(move[i])
          n.redPositions.append(move[-1])
        current.children.append(n)
    else:
      current.moves = self.findMoves(current.whitePositions, current.redPositions, current.turn, current.whoNow)
      if len(current.moves) is 0:
        return []
      captures = [x for x in current.moves if len(x) is not 2]
      if len(captures) is not 0:
        current.moves = [x for x in current.moves if len(x) is not 2]
      for move in current.moves:
        n = Node()
        n.whitePositions = copy.deepcopy(current.whitePositions)
        n.redPositions = copy.deepcopy(current.redPositions)
        n.turn = current.turn+1
        n.whoNow = (current.whoNow+1)%2
        
        if len(move) is 2:
          n.whitePositions.remove(move[0])
          n.whitePositions.append(move[1])
        else:
          i = 0; 
          n.whitePositions.remove(move[0])
          for i in range(1, len(move)):
            if i%2 is 1:
              n.redPositions.remove(move[i])
          n.whitePositions.append(move[-1])
        current.children.append(n)


  """
  method: findMoves
  @param: self, whitePositions, redPositions, turn, whoNow
  returns: moves
    An array of arrays containing moves and the start and end positions of that move
    along with what pieces/position of pieces are captured. 
  Description:
  Takes in deep copies of the board as it currently stands and finds a move 
  """
  def findMoves(self, whitePositions, redPositions, turn, whoNow):
    moves = []
    if whoNow is 0: #red
      for piece in redPositions:
        possiblePost = []
        move = []
        now = self.getMoves(whitePositions, redPositions, piece, whoNow)
        if len(now) is not 0:
          for a in now:
            moves.append(a)
    else: #white
      for piece in whitePositions:
        now = self.getMoves(whitePositions, redPositions, piece, whoNow)
        if len(now) is not 0:
          for a in now:
            moves.append(a)
    #print(moves)
    return moves
  
  def getMoves(self, whitePositions, redPositions, piece, whoNow):
    moves = []
    possiblePost = []
    move = []
    captureChances = []
    final = []
    if whoNow is 0: #red
      if piece%8 in range(1,4):     #row is offset by one
        possiblePost.append((piece+4)%32)
        if piece+5 is 32:
          possiblePost.append(32)
        else:
          possiblePost.append((piece+5)%32)
 
      elif piece%8 is 4:            #corner case on the right
        if piece is 28:
          possiblePost.append(32)
        else:
          possiblePost.append((piece+4)%32)
        possiblePost.append((piece+1)%32)

      elif piece%8 is 5:            #corner case on the left
        possiblePost.append((piece+7)%32)
        if piece+4 is 32:
          possiblePost.append(32)
        else:
          possiblePost.append((piece+4)%32)

      elif piece%8 in range(6,9) or piece%8 is 0:   #row is not offset
        possiblePost.append((piece+3)%32)
        possiblePost.append((piece+4)%32)

      else:
        print("Error: Unsupported Size")
        exit()

      possiblePost[:] = [poss for poss in possiblePost if poss not in redPositions]
      captureChances = [poss for poss in possiblePost if poss in whitePositions]
      possiblePost[:] = [poss for poss in possiblePost if poss not in whitePositions]
      for poss in possiblePost:
        move.append([piece,poss])
      for poss in captureChances:
        final = self.canCapture(piece, poss, copy.deepcopy(whitePositions), copy.deepcopy(redPositions), whoNow) 
      if len(move) is not 0:
        for a in move:
          moves.append(a)
      if len(final) is not 0:
        moves.append(final)


    else: #white
      if piece%8 in range(1,4):     #row is offset by one
        if piece-3 is 0:
          possiblePost.append(32)
        else:
          possiblePost.append((piece-3)%32)
        if piece-4 is 0:
          possiblePost.append(32)
        else:
          possiblePost.append((piece-4)%32)

      elif piece%8 is 4:            #corner case on the right
        if piece is 4:
          possiblePost.append(32)
        else:
          possiblePost.append((piece-4)%32)
        possiblePost.append((piece-7)%32)
      elif piece%8 is 5:            #corner case on the left
        possiblePost.append((piece-1)%32)
        possiblePost.append((piece-4)%32)

      elif piece%8 in range(6,9) or piece%8 is 0:   #row is not offset
        possiblePost.append((piece-5)%32)
        possiblePost.append((piece-4)%32)

      else:
        print("Error: Unsupported Size")
        exit()
      
      possiblePost[:] = [poss for poss in possiblePost if poss not in whitePositions]
      captureChances = [poss for poss in possiblePost if poss in redPositions]
      possiblePost[:] = [poss for poss in possiblePost if poss not in redPositions]
      for poss in possiblePost:
        move.append([piece,poss])
      for poss in captureChances:
        final = self.canCapture(piece, poss, copy.deepcopy(whitePositions), copy.deepcopy(redPositions), whoNow) 
      if len(move) is not 0:
        for a in move:
          moves.append(a)
      if len(final) is not 0:
        moves.append(final)
    return moves

  def canCapture(self, piece, poss, whitePositions, redPositions, whoNow):
    if whoNow is 0: #red
      diff = (poss - piece)%32
      x = []
      target = 0

      if piece in [1,9,17,25]:
        if diff is 4:
          if (piece +11) is 32:
            target = 32
          else:
            target = (piece+11)%32
        if diff is 5:
          target = (piece+9)%32

      elif piece in [2, 10, 18, 26, 3, 11, 19, 27]:
        if diff is 4:
          if (piece +7) is 32:
            target = 32
          else:
            target = (piece+7)%32
        if diff is 5:
          if(piece+9) is 32:
            target = 32
          else:
            target = (piece+9)%32

      elif piece in [6, 14, 22, 30, 7, 15, 23, 31]:
        if diff is 3:
          if (piece + 7) is 32:
            target = 32
          else:
            target = (piece+7)%32
        if diff is 4:
          if piece+9 is 32:
            target = 32
          else:
            target = (piece+9)%32

      elif piece in [5, 13, 21, 29]:
        if diff is 4:
          if (piece+9) is 32:
            target = 32
          else:
            target = (piece+9)%32
        if diff is 7:
          if (piece+11) is 32:
            target = 32
          else:
            target = (piece+11)%32

      elif piece in [8, 16, 24, 32]:
        if diff is 3:
          target = (piece+7)%32
        if diff is 4:
          target = (piece+5)%32

      elif piece in [4, 12, 20, 28]:
        if diff is 1:
          target = (piece+5)%32
        if diff is 4:
          target = (piece+7)%32
      
      if target in whitePositions or target in redPositions:
        return []

      x = [piece, poss, target]
      whitePositions.remove(poss)
      redPositions.remove(piece)
      redPositions.append(target)
      y = self.getMoves(whitePositions, redPositions, target, whoNow)
      z = [a for a in y if len(a) is not 2]
      if len(z) is not 0:
        for i in z[0]:
          x.append(i)
        x = list(set(x))
        x.sort()
      return x
    
    else:           #white
      diff = (piece- poss)%32
      x = []
      target = 0

      if piece in [1,9,17,25]:
        if diff is 4:
          if (piece - 5) is 0:
            target = 32
          else:
            target = (piece - 5)%32
        if diff is 3:
          if (piece - 7) is 0:
            target = 32
          else:
            target = (piece - 7)%32

      elif piece in [2, 10, 18, 26, 3, 11, 19, 27]:
        if diff is 4:
          if (piece - 9) is 0:
            target = 32
          else:
            target = (piece - 9)%32
        if diff is 3:
          if (piece - 7) is 0:
            target = 32
          else:
            target = (piece - 7)%32

      elif piece in [6, 14, 22, 30, 7, 15, 23, 31]:
        if diff is 5:
          if (piece - 9) is 0:
            target = 32
          else:
            target = (piece - 9)%32
        if diff is 4:
          if (piece - 7) is 0:
            target = 32
          else:
            target = (piece - 7)%32

      elif piece in [5, 13, 21, 29]:
        if diff is 1:
          if (piece - 5) is 0:
            target = 32
          else:
            target = (piece - 5)%32
        if diff is 4:
          if (piece - 7) is 0:
            target = 32
          else:
            target = (piece - 7)%32

      elif piece in [8, 16, 24, 32]:
        if diff is 4:
          if (piece - 11) is 0:
            target = 32
          else:
            target = (piece - 11)%32
        if diff is 5:
          if (piece - 9) is 0:
            target = 32
          else:
            target = (piece - 9)%32

      elif piece in [4, 12, 20, 28]:
        if diff is 7:
          if (piece - 11) is 0:
            target = 32
          else:
            target = (piece - 11)%32
        if diff is 4:
          if (piece - 9) is 0:
            target = 32
          else:
            target = (piece - 9)%32

      if target in whitePositions or target in redPositions:
        return []
     
      x = [piece, poss, target]
      redPositions.remove(poss)
      whitePositions.remove(piece)
      whitePositions.append(target)
      y = self.getMoves(whitePositions, redPositions, target, whoNow)
      z = [a for a in y if len(a) is not 2]
      if len(z) is not 0:
        for i in z[0]:
          x.append(i)
        x = list(set(x))
        x.sort()
      return x



class Node:
  redPositions = []
  whitePositions = []
  turn = 0
  whoNow = 0
  alpha = -sys.maxint - 1
  beta = sys.maxint
  A = -sys.maxint
  B = sys.maxint
  children = []
  move = []
  moves = []

  def __str__(self):
    return ("redPositions %s\nwhitePositions%s\nmoves %s\n"%(self.redPositions,self.whitePositions,self.moves))

#class AlphaBeta:
  #TODO later
            
play = Torus()
play.main()
