from mesa.space import ContinuousSpace
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import ChartModule
from SimpleContinuousModule import SimpleCanvas
from model import Traffic
from agent import Car, Pedestrian, Light
from data import Data

# You can change this to whatever you want. Make sure to make the different types
# of agents distinguishable
def agent_portrayal(agent):
    if type(agent) is Pedestrian:
        if agent.dir == "up":
            pedest_color = "Blue"
        else:
            pedest_color = "Purple"

    portrayal = {"Shape": "rect" if type(agent) is Car else "circle",
                 "Color": pedest_color if type(agent) is Pedestrian
                 else agent.color if type(agent) is Light
                 else "Pink",
                 "Filled": "true",
                 "w": 3.7*15 if type(agent) is Car else None,
                 "h": 1.7*15 if type(agent) is Car else None,
                 "r": .2*15 if type(agent) is not Car else None}
    return portrayal


# Create a grid of 20 by 20 cells, and display it as 500 by 500 pixels
space = SimpleCanvas(agent_portrayal)

# Create the server, and pass the grid and the graph
server = ModularServer(Traffic,
                       [space],
                       "Traffic Model",
                       {})
