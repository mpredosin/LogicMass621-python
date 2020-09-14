#!/usr/bin/python3
import pygame
import threading
import sys
import socket
import time
import math

class Rect:

    def __init__(self, x: float, y: float, width: int, height: int):
        self.__x = x
        self.__y = y
        self.__width = width
        self.__height = height
        self.__pyg_rect = pygame.Rect(
            int(self.__x), int(self.__y), self.__width, self.__height)

    def __str__(self):
        return 'x: {} y: {} width: {} height: {}'.format(self.__x, self.__y,
                                                         self.__width, self.__height)

    @property
    def x(self):
        return self.__x

    @x.setter
    def x(self, x):
        self.__x = float(x)
        self.__pyg_rect.x = int(self.__x)

    @property
    def y(self):
        return self.__y

    @y.setter
    def y(self, y):
        self.__y = float(y)
        self.__pyg_rect.y = int(self.__y)

    @property
    def width(self):
        return self.__width

    @property
    def height(self):
        return self.__height

    def colliderect(self, other):
        if self.x+self.width >= other.x and \
                other.x+other.width >= self.x and \
                self.y+self.height >= other.y and \
                other.y+other.height >= self.y:
            return True
    def colliderect(self, other, adjustment):
        x=other.x+adjustment
        y=other.y+adjustment
        width=other.width-adjustment*2
        height=other.height-adjustment*2
        if self.x + self.width >= x and \
                x+width >= self.x and \
                self.y + self.height >= y and \
                y+height >= self.y:
            return True

    def rectintersection(self, other):
        x5 = max(self.x, other.x)
        x6 = min(self.x+self.width, other.x+other.width)
        y5 = max(self.y, other.y)
        y6 = min(self.y+self.height, other.y+other.height)
        if x5 >= x6 or y5 >= y6:
            return Rect(0, 0, 0, 0)
        return Rect(x5, y5, x6-x5, y6-y5)

    def toPygame(self):
        return self.__pyg_rect

class Projectile:

    def __init__(self, xStep: float, yStep: float, rect, player):
        self.__xStep = xStep
        self.__yStep = yStep
        self.__rect = rect
        self.__player = player

    def __str__(self):
        return 'xStep: {} yStep: {} rect: {} player: {}'.format(self.__xStep, self.__yStep,
                                                         self.__rect, self.__player)

    @property
    def xStep(self):
        return self.__xStep
    @xStep.setter
    def xStep(self, xStep):
        self.__xStep = float(xStep)
    @property
    def yStep(self):
        return self.__yStep
    @yStep.setter
    def yStep(self, yStep):
        self.__yStep = float(yStep)
    @property
    def rect(self):
        return self.__rect
    @rect.setter
    def rect(self, rect):
        self.__rect = rect
    @property
    def player(self):
        return self.__player
    @player.setter
    def player(self,rect):
        self.__player = player

    def collideRect(self,other,adjustment):
        if self.player != other:
           return self.rect.colliderect(other.rect,adjustment)
        else:
            return False

def rot_center(image, angle):
    """rotate an image while keeping its center and size"""
    orig_rect = image.get_rect()
    rot_image = pygame.transform.rotate(image, angle)
    rot_rect = orig_rect.copy()
    rot_rect.center = rot_image.get_rect().center
    rot_image = rot_image.subsurface(rot_rect).copy()
    return rot_image

class Tank:
    def __init__(self, rect, angle):
        self.__rect = rect
        self.__angle = angle
        self.__lastFired = 0
        self.__lives = 5

    @property
    def rect(self):
        return self.__rect
    @property
    def angle(self):
        return self.__angle
    @property
    def lastFired(self):
        return self.__lastFired
    @property
    def lives(self):
        return self.__lives
    

    @rect.setter
    def rect(self,rect):
        self.__rect = rect
    @angle.setter
    def angle(self,angle):
        self.__angle = angle
    @lastFired.setter
    def lastFired(self, time):
        self.__lastFired = time
    def reduceLife(self):
        self.__lives -= 1


x = socket.socket()
x.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

hostName = socket.gethostname()
server_IP = socket.gethostbyname(hostName) 
port = 50000

print("Hostname:",hostName, "IP:", server_IP) 

black = (0,0,0)
white = (255,255,255)
red = (255,0,0)

screenWidth = 800
screenHeight = 800
screen = pygame.display.set_mode((screenWidth, screenHeight))

tank = pygame.image.load('tank.png')
tankSize = tank.get_width()

p1Tank = Tank(Rect(screenWidth-tankSize*2,(screenHeight-tankSize)/2,tankSize,tankSize),0)
p2Tank = Tank(Rect(tankSize,(screenHeight-tankSize)/2,tankSize,tankSize),0)

running=True
playing=True
singlePlayer = True

tanks = {}
tanks[0] = tank
tankList = [p1Tank,p2Tank]
tankSpeed = 10

projectileSize=10
projectiles=[]
projectileSpeed=4
reloadSpeed=1

pygame.font.init()
font = pygame.font.Font('freesansbold.ttf', 20)
textP1Lives = font.render(f'Player 1 Lives: {p1Tank.lives}', True, black, white)
textP2Lives = font.render(f'Player 2 Lives: {p2Tank.lives}', True, black, white)
textGameOver = font.render('Game Over', True, black, white)

for i in range(15, 359, 15):
    #print("adding tank", i)
    tanks[i] = rot_center(tank,-i)

if singlePlayer != True:
    server = input('Do you want to start the server?')
    if server.count('y'or'Y'):
        x.bind((hostName,port))
        print("Bound to address ",x.getsockname())
        x.listen(1)
        conn,addr=x.accept()
        thisUser=p1Tank
        otherUser=p2Tank
        pygame.display.set_caption('Player One')
    else:
        server_IP=input("Server IP:")
        x.connect((server_IP,port))
        conn=x
        thisUser=p2Tank
        otherUser=p1Tank
        pygame.display.set_caption('Player Two')
else:
    thisUser = p1Tank
    otherUser = p2Tank


clock=pygame.time.Clock()

def receive():
    global thisUser,otherUser
    while running:
        msg_buffer = b''
        new_msg=True
        while True:

            if (new_msg and len(msg_buffer) < headerSize) or (not new_msg and len(msg_buffer) < headerSize+msglen):
                msg = conn.recv(16)
                msg_buffer += msg
                #print('recv',msg, 'buffer', msg_buffer)

            if new_msg:
                #print(f"new msg len:",msg_buffer[:headerSize].decode())
                msglen=int(msg_buffer[:headerSize])
                new_msg=False

            if len(msg_buffer)-headerSize>=msglen: # full message
                decoded_msg=msg_buffer[headerSize:headerSize+msglen].decode()
                #print('decoded_msg_received',decoded_msg)

                new_msg=True
                msg_buffer=msg_buffer[headerSize+msglen:]
                #print('new buffer',msg_buffer)

def eventLoop():
    global running, thisUser, otherUser, projectiles
    pygame.key.set_repeat(75 , 50)
    pygame.display.init()
    while running:

        event=pygame.event.poll()

        if event.type == pygame.NOEVENT:
            time.sleep(0.01)

        elif event.type == pygame.QUIT:
            # TODO send quit to client
            running = False

        elif event.type == pygame.KEYDOWN:

            if event.key==pygame.K_ESCAPE:
                # TODO send quit to client
                running = False

            if playing: 
                if event.key == pygame.K_w:
                    radians = math.radians(thisUser.angle)
                    thisUser.rect.x = min(max(0,thisUser.rect.x + tankSpeed*math.sin(radians)),screenWidth-thisUser.rect.width)
                    thisUser.rect.y = min(max(0,thisUser.rect.y - tankSpeed*math.cos(radians)),screenHeight-thisUser.rect.height)

                    if singlePlayer != True:
                        msg=f'paddle:{thisUser.x}:{thisUser.y}'.encode()
                        conn.send(msg)

                if event.key == pygame.K_s:
                    radians = math.radians(thisUser.angle)
                    thisUser.rect.x = min(max(0,thisUser.rect.x - tankSpeed*math.sin(radians)),screenWidth-thisUser.rect.width)
                    thisUser.rect.y = min(max(0,thisUser.rect.y + tankSpeed*math.cos(radians)),screenHeight-thisUser.rect.height)
                    if singlePlayer != True:
                        msg=f'paddle:{thisUser.x}:{thisUser.y}'.encode()
                        conn.send(msg)

                if event.key == pygame.K_d:
                    thisUser.angle = (thisUser.angle + 15) % 360
                    if singlePlayer != True:
                        msg=f'paddle:{thisUser.x}:{thisUser.y}'.encode()
                        conn.send(msg)

                if event.key == pygame.K_a:
                    thisUser.angle = (thisUser.angle - 15) % 360
                    if singlePlayer != True:
                        msg=f'paddle:{thisUser.x}:{thisUser.y}'.encode()
                        conn.send(msg)

                if event.key == pygame.K_SPACE:
                    currTime = time.time()
                    if thisUser.lastFired < currTime - reloadSpeed:
                        thisUser.lastFired = currTime
                        radians=math.radians(thisUser.angle)
                        x=thisUser.rect.x+(thisUser.rect.width-projectileSize)/2
                        y=thisUser.rect.y+(thisUser.rect.height-projectileSize)/2
                        #print(math.cos(radians),math.sin(radians))
                        projectiles.append(
                            Projectile(projectileSpeed*math.sin(radians),
                            -projectileSpeed*math.cos(radians),
                            Rect(x,y,projectileSize,projectileSize),thisUser))                
                        if singlePlayer != True:                
                            msg=f'paddle:{thisUser.x}:{thisUser.y}'.encode()
                            conn.send(msg)


def projectile():
    global projectiles
    global radians
    global textP1Lives, textP2Lives
    global playing
    while running:
        #print('projectile thread',len(projectiles))
        for projectile in projectiles[:]:
            if projectile.rect.x >= screenWidth or projectile.rect.x+projectileSize <= 0 or projectile.rect.y+projectileSize <= 0 or projectile.rect.y >= screenHeight:
                projectiles.remove(projectile)
            for tank in tankList:
                if projectile.collideRect(tank,20):
                    p2Tank.reduceLife()
                    textP2Lives = font.render(f'Player 2 Lives: {p2Tank.lives}', True, black, white)
                    projectiles.remove(projectile)
                    if(p2Tank.lives==0) :
                        playing = False
            projectile.rect.x+=projectile.xStep
            projectile.rect.y+=projectile.yStep

        time.sleep(0.01)


def render():
    screen.fill(white)
    screen.blit(tanks[p1Tank.angle],p1Tank.rect.toPygame())
    screen.blit(tanks[p2Tank.angle],p2Tank.rect.toPygame())

    if playing:
        for i in projectiles:
            pygame.draw.rect(screen,red,i.rect.toPygame())
    else:
        screen.blit(textGameOver,((screenWidth-textGameOver.get_width())//2,screenHeight//2))

    screen.blit(textP1Lives,(0,0))
    screen.blit(textP2Lives, (screenWidth-textP2Lives.get_width(),0))
    pygame.display.update()

event_thread = threading.Thread(target=eventLoop)
event_thread.start()

proj_thread = threading.Thread(target=projectile)
proj_thread.start()

if singlePlayer != True:
    recv_thread = threading.Thread(target=receive)
    recv_thread.start()

while running:
    render()

sys.exit()
pygame.quit()