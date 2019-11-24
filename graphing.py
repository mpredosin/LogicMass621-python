#!/usr/bin/python

import pygame, math

black = [0, 0, 0]
white = [255, 255, 255]

step = 15

screenWidth = 800
screenHeight = 800

graphWidth = 50
graphHeight = 50

graphCenterX = 0
graphCenterY = 0

sx= screenWidth / float(graphWidth)
sy= screenHeight / float(graphHeight)

interval = 1 / sx

MinX = -graphWidth / 2 + graphCenterX
MaxX = graphWidth / 2 + graphCenterX
MinY = -graphHeight/2 + graphCenterY
MaxY = graphHeight/2 + graphCenterY

print("MinX",MinX,"MaxX",MaxX,"MinY",MinY,"MaxY",MaxY)

def tran(x,y):

    # translate
    x = x - graphCenterX
    y = y - graphCenterY
    
    # scale
    x = x * sx
    y = y * sy

    # transform to screen coordinates
    x = screenWidth/2 + x
    y = screenHeight/2 - y
    
    return x,y

pygame.init()
pygame.font.init()
pygame.display.set_caption('Graph')

font = pygame.font.Font('freesansbold.ttf', 20)
screen = pygame.display.set_mode((screenWidth, screenHeight))

textX = font.render('X', True, black, white)
textY = font.render('Y', True, black, white)

textXWidth = textX.get_width() / sx

def compute_y(x):
   return (x * x*2/3) + 20
    
def render():

    global MinX
    global MaxX
    global MinY
    global MaxY

    MinX = -graphWidth / 2 + graphCenterX
    MaxX = graphWidth / 2 + graphCenterX
    MinY = -graphHeight/2 + graphCenterY
    MaxY = graphHeight/2 + graphCenterY

    # x label
    screen.blit(textX, tran(MaxX - textXWidth,0))
    # y label
    screen.blit(textY, tran(0,MaxY))

    # x-axis
    pygame.draw.line(screen,black, tran(MinX,0), tran(MaxX,0),1)
    # y-axis
    pygame.draw.line(screen,black, tran(0,MinY),tran(0,MaxY),1)

    x = MinX
    y = compute_y(x)
    x2 = x
    y2 = y
        
    while x < MaxX:
        y = compute_y(x)
        pygame.draw.line(screen,black, tran(x2,y2) , tran(x,y) ,1)
        x2 = x
        y2 = y
        x = x + interval

running = True
while running:
    event = pygame.event.wait();
    if event.type == pygame.QUIT:
        running = False
    elif event.type == pygame.KEYDOWN:
        if event.key == pygame.K_DOWN:
            graphCenterY = graphCenterY - graphHeight/step
        if event.key == pygame.K_UP:
                graphCenterY = graphCenterY + graphHeight/step
        if event.key == pygame.K_LEFT:
            graphCenterX = graphCenterX - graphWidth/step
        if event.key == pygame.K_RIGHT:
                graphCenterX = graphCenterX + graphWidth/step
        print("MinX",MinX,"MaxX",MaxX,"MinY",MinY,"MaxY",MaxY)

    # clear screen to white
    screen.fill(white)
    render()
    pygame.display.update()
