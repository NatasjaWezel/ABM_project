from server import server
from mesa import Model
from model import Traffic

from data import Data

import matplotlib.pyplot as plt

print("Do you want to launch the server for visualization? (Type yes/no)")
choiche = input()

if choiche == "yes":
    # launch at default port
    server.port = 8522
    server.launch()
else:
    print("How many steps?")
    steps = int(input())
    print("Okay then, running your model now...")
    model = Traffic()
    data = model.run_model(steps)

    simulation_info = model.datacollector.get_model_vars_dataframe()
    data.write_info(simulation_info)
    
    print("Terminated normally! Have fun with your data ;-)")
