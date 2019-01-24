from mesa import Agent
from mesa import space
from mesa.space import ContinuousSpace
import random
import math
import numpy as np

class Light(Agent):
    def __init__(self, unique_id, model, pos, state, light_id):
        super().__init__(unique_id, model)

        self.pos = pos
        self.state = state
        self.light_id = light_id
        self.stateSlow = 0

    def step(self):
        '''
        Update the state of the light.
        '''
        self.stateSlow = (self.stateSlow + 1) % 3
        if self.stateSlow == 0:
            self.state = (self.state + 1) % 405

        # self.state = (self.state + 1) % 405

# simultaneous strategy
# 3 & 4 are the same
# 5 & 6 are the same
