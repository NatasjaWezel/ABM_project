from mesa import Agent
from mesa.space import ContinuousSpace
import random


class Road(Agent):
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model)

        self.pos = pos

class Light(Agent):
    def __init__(self, unique_id, model, pos, state):
        super().__init__(unique_id, model)

        self.pos = pos
        self.state = state

    def step(self):
        '''
        This method should move the goat using the `random_move()` method implemented earlier, then conditionally reproduce.
        '''
        self.state = (self.state + 1) % 150




class Pedestrian(Agent):
    def __init__(self, unique_id, model, pos, dir, speed = 1):
        super().__init__(unique_id, model)
        self.pos = pos
        self.dir = dir
        self.speed = speed

        # Liu, 2014 parameters
        self.theta_field = 170  # Degrees
        self.N_directions = 17
        self.R_vision_range = 3 # Meters
        self.desired_speed = 1 # Meters per time step

    def step_new(self):
        """
        stepfunction based on Liu, 2014
        """
        # Choose direction
        direction = self.choose_direction()

        # Calculate distance

        # Check traffic light?

        # Move in that direction
        raise NotImplementedError

    def choose_direction(self):
        """
        Picks the direction with the highest utility
        """
        raise NotImplementedError

    def objects_per_direction(self):
        """
        returns a list of a list of nearest objects
        and a list of nearest pedestrians
        """
        raise NotImplementedError

    def pedestrians_in_field(self):
        """
        returns the number of pedestrians in the field
        """
        raise NotImplementedError

    def step(self):
        '''
        This method should move the Sheep using the `random_move()` method implemented earlier, then conditionally reproduce.
        '''

        # check if there's a traffic light (and adjust speed accordingly)
        changed = 0
        for i in self.model.space.get_neighbors(self.pos, include_center = False, radius = 4):
            if self.check_front() > 0 or isinstance(i,Light) and i.state < 50:
                self.speed = 0
                changed = 1
            elif changed == 0 and self.check_front() == 0 or (isinstance(i, Light) and i.state >= 50 and self.check_front() == 0):
                self.speed = 1

        # take a step
        if self.dir is "up":
            next_pos = (self.pos[0], self.pos[1] + self.speed)
            self.model.space.move_agent(self, next_pos)
        else:
            next_pos = (self.pos[0], self.pos[1] - self.speed)
            self.model.space.move_agent(self, next_pos)

    # this function is in both pedestrian and agent -> more efficient way?
    def check_front(self):
        '''
        Function to see if there is a Pedestrian closeby in front
        '''

        if self.dir == "up":
            direction = 1
        else:
            direction = -1

        # the Pedestrian has a vision range of 1 tile for now (can be changed to its max speed?)
        for i in range(1, 2):
            for agent in self.model.space.get_neighbors((self.pos[0], self.pos[1] + direction * i), radius = 0):
                if isinstance(agent, Car) or isinstance(agent, Pedestrian):
                    return i
        return 0


class Car(Agent):
    def __init__(self, unique_id, model, pos, dir, speed=1, time=0):
        super().__init__(unique_id, model)

        self.pos = pos
        self.dir = dir
        self.speed = speed
        self.time = time

    def step(self):
        '''
        Cars go straight for now.
        '''
        changed = 0
        for i in self.model.space.get_neighbors(self.pos, include_center = False, radius = 2):
        # not only affected by 1 light
            if self.check_front() > 0 or isinstance(i,Light) and i.state > 50:
                # if self.speed > 0:
                self.speed = 0
                changed = 1
            elif changed == 0 and self.check_front() == 0 or (isinstance(i, Light) and i.state <= 50 and self.check_front() == 0):
                # if self.speed < 1:
                self.speed = 1

        # take a step
        if self.dir is "left":
            next_pos = (self.pos[0] - self.speed, self.pos[1])
            self.model.space.move_agent(self, next_pos)
        else:
            next_pos = (self.pos[0] + self.speed, self.pos[1])
            self.model.space.move_agent(self, next_pos)

        self.time += 1


    def check_front(self):
        '''
        Function to see if there is a car closeby in front of a car
        '''

        if self.dir == "right":
            direction = 1
        else:
            direction = -1

        # the car has a vision range of 1 tile for now (can be changed to its max speed?)
        for i in range(1, 2):
            for agent in self.model.space.get_neighbors((self.pos[0] + direction * i, self.pos[1]), radius = 0):
                if isinstance(agent, Car) or isinstance(agent, Pedestrian):
                    return i
        return 0
