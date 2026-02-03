import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import matplotlib.animation as animation
import math as math
from matplotlib.backend_bases import MouseButton
import Cell

figure, axes = plt.subplots()
axes.set_aspect( 1 )
#axes.set_axis_off()
plt.xlim(0, 20)
plt.ylim(0, 20)
plt.title( 'Drosophila Embryonic Midgut' )

class dynamics:
    def __init__(self, xF, yF, xV, yV):
        self.xF=xF
        self.yF=yF
        self.xV=xV
        self.yV=yV
        pass

class circle:
    def __init__(self,x,y,radius,colour,dynamics):
        self.X = x
        self.Y = y
        self.Radius = radius
        self.colour = colour
        self.dynamics = dynamics
        self.actor = mpatches.Ellipse(xy=(self.X,self.Y), width = self.Radius*2, height = self.Radius*2, fill = True, facecolor = self.colour)

class list_of_circle:
    def __init__(self):
        self.circles_List=[] 
    
    def __getitem__(self,index):
        return self.circles_List[index]
    
    def AddCircle(self,Circle):
        self.circles_List.append(Circle)

circles=list_of_circle()
circles.AddCircle(circle(5,5,2,'blue',dynamics(1,-1,0,0)))
circles.AddCircle(circle(10,11,3,'red',dynamics(0,-1,-0.05,0)))

object_density = 1.5
fluid_density = 1
delay=10 #pause in ms
drag_coefficient = 0.5
increment=1/delay

x = 5
for c in circles:
    axes.add_artist(c.actor)

def checkEdges(circle):
    if (circle.X < circle.Radius):
        circle.X = circle.Radius; #Prevent from leaving the canvas from the left side
        circle.dynamics.xV *= -1
    elif (circle.X > 20-circle.Radius):
        circle.X = 20 - circle.Radius
        circle.dynamics.xV *= -1

    if (circle.Y - circle.Radius < 0):
        circle.Y = circle.Radius
        circle.dynamics.yV *= -1
    elif (circle.Y + circle.Radius > 20):
        circle.Y = 20 - circle.Radius
        circle.dynamics.yV *= -1

def animate(i):
    ArtistList=[]
    for circle in circles:
        circlearea = math.pi * circle.Radius**2
        circlemass = circlearea * object_density
        circlexaccelation = circle.dynamics.xF/circlemass
        circleyaccelation = circle.dynamics.yF/circlemass
        circle.dynamics.xV += circlexaccelation*increment
        circle.dynamics.yV += circleyaccelation*increment

        circle.X += circle.dynamics.xV
        circle.Y += circle.dynamics.yV

        checkEdges(circle)
        circle.actor.center=[circle.X,circle.Y]
        ArtistList.append(circle.actor)





    #probably need integration/differential equations to deal with drag oscilations
    #leave for now
    """circle1xdrag = 0.5 * fluid_density * circle1area * drag_coefficient * round(circle1.dynamics.xV,1) ** 2
    if circle1.dynamics.xV > 0:
        circle1.dynamics.xF -= circle1xdrag
    elif circle1.dynamics.xV < 0:
        circle1.dynamics.xF += circle1xdrag"""
    #circle1xaccelation = (circle1.dynamics.xF-circle1xdrag)/circle1mass


    
    return ArtistList


ani = animation.FuncAnimation(figure, animate, frames=1000, interval=delay, blit=True)

plt.show()