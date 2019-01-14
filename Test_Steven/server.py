from mesa.space import ContinuousSpace
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import ChartModule
from mesa.visualization.modules import CanvasGrid
from SimpleContinuousModule import SimpleCanvas
from model import Traffic
from agent import Car, Pedestrian, Road, Light

# You can change this to whatever you want. Make sure to make the different types
# of agents distinguishable
def agent_portrayal(agent):
    if type(agent) is Light:
        if agent.state < 50:
            current_color = "Red"
        elif agent.state < 100:
            current_color = "Green"
        else:
            current_color = "Orange"

    portrayal = {"Shape": "rect" if type(agent) is Road else "circle",

                 "Color": "Blue" if type(agent) is Pedestrian 
                 else "Black" if type(agent) is Road 
                 else "Blue" if type(agent) is Light 
                 else "Pink",

                 "Filled": "true",
                 "Layer": 0 if type(agent) is Road else 1,
                 "w": 1,
                 "h": 1,
                 "r": 10}
    return portrayal

# Create a grid of 20 by 20 cells, and display it as 500 by 500 pixels
space = SimpleCanvas(agent_portrayal, 750, 750)

# Create the server, and pass the grid and the graph
server = ModularServer(Traffic,
                       [space],
                       "Traffic Model",
                       {})
