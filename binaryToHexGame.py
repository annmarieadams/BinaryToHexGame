import random, pygame, sys, random
from pygame.locals import *

FPS = 20
WINDOWWIDTH = 510
WINDOWHEIGHT = 850
BOXSIZE = 55
GAPSIZE = 5
COLUMNS = 8
TOPBOX = 680
MARGIN = int((WINDOWWIDTH - (COLUMNS * (BOXSIZE + GAPSIZE))) / 2)  # x margin between first and last boxes
DEFEATCONS = {'0':'0000' , '1': '0001', '2':'0010', '3':'0011', '4':'0100', '5':'0101', '6':'0110', '7': '0111', '8':'1000',
              '9':'1001', 'A': '1010', 'B':'1011', 'C':'1100', 'D':'1101', 'E':'1110', 'F':'1111'}
KEYBOARDCONTROLS = (K_1, K_2, K_3, K_4, K_5, K_6, K_7, K_8)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
boxes = []
enemies = []


class Box:

    def __init__(self, x, y, state):
        self.x = x  
        self.y = y 
        self.state = state  # contains a 0 or 1


class Enemy:

    def __init__(self, hexNum, belongsTo, defeated, defeatCon1, defeatCon2, x, y):
        self.hexNum = hexNum
        self.belongsTo = belongsTo  # index of the box
        self.defeated = defeated  # contains a bool if defeated or not
        self.defeatCon1 = defeatCon1  # the first 4 binary numbers needed to defeat
        self.defeatCon2 = defeatCon2  # the last 4 binary numbers needed to defeat
        self.x = x
        self.y = y


def main():
    timeToWait = 4000
    gameOver = False
    global FPSCLOCK, DISPLAYSURF
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    clock = pygame.time.Clock()
    timeElapsed = 0
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    mousex = 0
    mousey = 0
    score = 0
    pygame.display.set_caption('Binary to Hex Game')
    iconImg = pygame.image.load('assets/icon.png')
    pygame.display.set_icon(iconImg)
    while True:  # main game loop
        if gameOver == False:
            timeElapsed += clock.tick()
            DISPLAYSURF.fill(WHITE)
            showScore(int(score / 2))
            drawBoxes()
            drawTextOnBoxes()
            keyboardPressed = False
            mouseClicked = False
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == MOUSEMOTION:
                    mousex, mousey = event.pos
                elif event.type == MOUSEBUTTONUP:
                    mousex, mousey = event.pos
                    mouseClicked = True
                elif event.type == KEYDOWN:
                    if event.key in KEYBOARDCONTROLS:
                        keyboardPressed = True
                        saveEvent = KEYBOARDCONTROLS.index(event.key)                
            if timeElapsed >= timeToWait:
                myEnemy = generateEnemy()
                enemies.append(myEnemy)
                timeToWait -= 10
                timeElapsed = 0
            for enemy in enemies:
                animateEnemy(enemy)
                if enemy.defeated == True:
                    score += 1
                    enemies.remove(enemy)
                    if not pygame.mixer.get_busy(): 
                        soundObj = pygame.mixer.Sound('assets/blip.wav')
                        soundObj.play()
                gameOver = checkIfLoss(enemy)
            boxClickedIndex = getBoxAtPixel(mousex, mousey)
            if boxClickedIndex != None and mouseClicked:
                changeNumber(boxClickedIndex)
                mouseClicked = False
            if keyboardPressed == True:
                changeNumber(saveEvent)
                keyboardPressed = False
            checkWinCon()
        else:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == KEYDOWN:
                    if event.key == K_RETURN:
                        score = 0
                        gameOver = False
                        for enemy in enemies:
                            enemies.remove(enemy)
                        for box in boxes:
                            box.state = 0       
        pygame.display.update()
        FPSCLOCK.tick(FPS)


def drawBoxes():  # for drawing the default boxes the game starts with
    boxSep = 0
    for i in range(COLUMNS):
        pygame.draw.rect(DISPLAYSURF, BLACK, (MARGIN + boxSep, TOPBOX, BOXSIZE, BOXSIZE), 3)
        newBox = Box(MARGIN + boxSep, TOPBOX, 0)
        boxes.append(newBox)  # xy coords
        boxSep += BOXSIZE + GAPSIZE
    return


def drawTextOnBoxes():
    for i in range(COLUMNS):
        fontObj = pygame.font.Font('freesansbold.ttf', 32)
        textSurfaceObj = fontObj.render(str(boxes[i].state), True, BLACK)
        textRectObj = textSurfaceObj.get_rect()
        textRectObj.center = (boxes[i].x + int(BOXSIZE / 2), boxes[i].y + int(BOXSIZE / 2)) 
        DISPLAYSURF.blit(textSurfaceObj, textRectObj)  # blit the number onto the middle of the box 
    return     

        
def getBoxAtPixel(x, y):  # get the box that the user clicked on, return the index in the list of boxes
    for index, box in enumerate(boxes):
            boxRect = pygame.Rect(box.x, box.y, BOXSIZE, BOXSIZE)
            if boxRect.collidepoint(x, y):
                return index
    return None


def changeNumber(boxIndex):  # change the number displayed when user clicks the box
    fontObj = pygame.font.Font('freesansbold.ttf', 32)
    pygame.draw.rect(DISPLAYSURF, WHITE, (boxes[boxIndex].x + 3, boxes[boxIndex].y + 3, BOXSIZE - 6, BOXSIZE - 6))  # Make sure border isn't changed
    if (boxes[boxIndex].state):
        boxes[boxIndex].state = 0
    else:
        boxes[boxIndex].state = 1
    textSurfaceObj = fontObj.render(str(boxes[boxIndex].state), True, BLACK)
    textRectObj = textSurfaceObj.get_rect()
    textRectObj.center = (boxes[boxIndex].x + int(BOXSIZE / 2), boxes[boxIndex].y + int(BOXSIZE / 2))
    DISPLAYSURF.blit(textSurfaceObj, textRectObj)     

    
def generateEnemy(): 
    hexNum1, binaryNum1 = random.choice(list(DEFEATCONS.items()))
    hexNum2, binaryNum2 = random.choice(list(DEFEATCONS.items()))
    belongsTo = random.randint(0, 7)
    newEnemy = Enemy(hexNum1 + hexNum2, belongsTo, False, binaryNum1, binaryNum2, boxes[belongsTo].x, 0)
    enemies.append(newEnemy)
    return newEnemy


def animateEnemy(enemy):
    enemyImg = pygame.image.load('assets/enemy.png')
    DISPLAYSURF.blit(enemyImg, (enemy.x, enemy.y))
    fontObj = pygame.font.Font('freesansbold.ttf', 12)
    if enemy.hexNum[0] != '0':
        textSurfaceObj = fontObj.render(enemy.hexNum, True, BLACK)
    else:
        textSurfaceObj = fontObj.render(enemy.hexNum[1], True, BLACK)
    textRectObj = textSurfaceObj.get_rect()
    textRectObj.center = (enemy.x + 25, enemy.y + 25)
    DISPLAYSURF.blit(textSurfaceObj, textRectObj)
    enemy.y += 1
    return


def checkWinCon():
    currentBin1 = ''
    currentBin2 = ''
    defeated = False
    for i in range(4):
        currentBin1 += str(boxes[i].state)
        currentBin2 += str(boxes[i + 4].state)
    for enemy in enemies:
        if enemy.defeatCon1 == currentBin1 and enemy.defeatCon2 == currentBin2:
            enemy.defeated = True

    
def checkIfLoss(enemy):
    if enemy.y + 50 >= TOPBOX:
        for i in range(len(enemies)):
            del(enemies[0])
        soundObj = pygame.mixer.Sound('assets/lose.wav')
        soundObj.play()
        fontObj = pygame.font.Font('freesansbold.ttf', 55)
        textSurfaceObj = fontObj.render('GAME OVER', True, BLACK)
        textRectObj = textSurfaceObj.get_rect()
        textRectObj.center = (200, 150)
        DISPLAYSURF.blit(textSurfaceObj, textRectObj)
        fontObj = pygame.font.Font('freesansbold.ttf', 30)
        textSurfaceObj = fontObj.render('Press Enter to play again', True, BLACK)
        textRectObj = textSurfaceObj.get_rect()
        textRectObj.center = (250, 200)
        DISPLAYSURF.blit(textSurfaceObj, textRectObj)
        
        return True
    return False


def showScore(score):
    fontObj = pygame.font.Font('freesansbold.ttf', 20)
    textSurfaceObj = fontObj.render('Score: ' + str(score), True, BLACK)
    textRectObj = textSurfaceObj.get_rect()
    textRectObj.center = (450, 820)
    DISPLAYSURF.blit(textSurfaceObj, textRectObj)
    
  
if __name__ == '__main__':
    main()
    
