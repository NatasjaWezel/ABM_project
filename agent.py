from mesa import Agent
from mesa import space
from mesa.space import ContinuousSpace
import random
import math
import numpy as np

from light import Light

class Pedestrian(Agent):
    def __init__(self, unique_id, model, pos, dir, speed = 1, time=0):
        super().__init__(unique_id, model)
        self.pos = pos
        self.dir = dir
        self.speed = speed
        self.time = time

        # Liu, 2014 parameters
        self.vision_angle = 170  # Degrees
        self.N = 16 # Should be >= 2!
        self.R_vision_range = 3 # Meters
        self.des_speed = 1 # Meters per time step
        self.pre_pos = pos
        self.speed_free = 1 #normal distribution of N(1.34, 0.342)
        self.peds_in_vision = None # list of pedestrians in vision field

        # Set direction in degrees
        if self.dir == "up":
            self.direction = 270
        elif self.dir == "down":
            self.direction = 90
        else:
            raise ValueError("invalid direction, choose 'up' or 'down'")

        # TODO: assign target point randomly (preference to right side?)
        self.target_point = (10,0)

        # Weights (for equation 1)
        # What is We' for equation 7??
        self.Ek_w = 1
        self.Ok_w = 1
        self.Pk_w = 1
        self.Ak_w = 1
        self.Ik_w = 1

    def step_new(self):
        """
        stepfunction based on Liu, 2014
        """
        # Check traffic light and decide to move or not
        # Returns True if light is red
        # Move if not red (TODO: decide what to do with orange)
        if self.traffic_red() is False:
            # TODO: decide what their choice is if on midsection or on middle of the road. Move to the spot where there is space?

            # Get list of pedestrians in the vision field
            self.peds_in_vision = self.pedestrians_in_field(self.vision_angle, self.R_vision_range)
            # Set desired_speed with number of pedestrians in vision field as input
            self.des_speed = self.desired_speed(len(self.peds_in_vision))

            # Choose direction
            theta_chosen = self.choose_direction()
            self.direction = theta_chosen

            # TODO: DELETE THESE VARIABLES
            theta_chosen = 90
            available_speed = 3

            # Choose speed (TODO: or delete?)
            chosen_speed = min(available_speed, self.des_speed)
            # Get new position
            next_pos = self.new_pos(chosen_speed, theta_chosen)

            # Update previous position
            self.pre_pos = self.pos
            # Move to new position
            # self.model.space.move_agent(self, next_pos)

            # # Finalize this step
            # self.time += 1


    def desired_speed(self, n_agents_in_cone, gamma=1.913, max_density=5.4):
        #Parameters: Normal speed
        # TODO: Only works for vision angle of 170 degrees for now
        print('self', self.vision_angle)
        if self.vision_angle == 170:
            # cone_area_170 = 13.3517
            # agent_area: pi*(0.4**2) = 0.5027
            # dens = agent_area/cone_area
            dens = 0.0376
        else:
            # TODO: remove hardcoding?
            raise ValueError('Code only works for 170 degrees vision range for now')

        # Calculate cone density 
        # TODO: DELETE THIS HACK AND FIX DIVIDE BY ZERO ERROR CORRECTLY
        if n_agents_in_cone <= 0:
            n_agents_in_cone = 1

        cone_density = n_agents_in_cone * dens
        # Calculate the desired speed (see eq. 8)
        des_speed = self.speed_free*(1 - np.exp(-gamma*((1/cone_density)-(1/max_density))))

        # Check if speed is not negative?
        if des_speed >= 0:
            return des_speed
        else:
            # TODO: set a default speed?
            return 0


    def choose_direction(self):
        """
        Picks the direction with the highest utility
        """
        # Loop over the possible directions
        # TODO: Check if utility function doesn't return a negative value
        max_util = [-1, None]
        pos_directions = self.possible_directions()        
        for direction in pos_directions:
            # Calculate utility
            util = self.calc_utility(direction)
            # Check if this utility is higher than the previous
            if util > max_util[0]:
                max_util = [util, direction]

        # Return direction
        return max_util[1]


    def possible_directions(self):
        """
        TODO: THIS ONE STILL INCLUDES END BOUNDARIES OF VISION RANGE
        """

        # Calculate the lower angle and the upper angle
        lower_angle = self.direction - (self.vision_angle / 2)
        upper_angle = self.direction + (self.vision_angle / 2)

        # Get list of possible directions
        theta_N = self.vision_angle/(self.N)
        pos_directions = []
        for i in range(self.N+1):
            pos_directions.append(lower_angle+i*theta_N)

        return pos_directions


    def calc_utility(self, direction):
        """
        Calculate the utility (equation 1 for now. Whats omega_e' in eq. 7?)
        """

        # TODO: Something is still going wrong with the direction? I think in pedestrian_intersection. Checked pos_directions and that seems okay (see notebook pedestians_tryout_parts)
        # List of pedestrians in that direction
        peds_in_dir = self.pedestrian_intersection(self.peds_in_vision, direction, .7)

        # Get closest pedestrian in this directions
        if len(peds_in_dir) > 0:
            # min_distance, min_pedestrian.pos
            closest_ped = self.closest_pedestrian(peds_in_dir)
            # print('closest:', closest_ped)
        # If no pedestrians in view, closest_ped is set at vision range
        else:
            closest_ped = [self.R_vision_range, None]
        
        # Distance to road 'wall'
        # TODO: IMPLEMENT: Check if wall is within vision range and get the distance to it and coordinates
        # If no pedestrians in view, closest_ped is set at vision range
        closest_wall = [self.R_vision_range, None]

        # Determine possible new position
        chosen_velocity = min(self.des_speed, closest_ped[0], closest_wall[0])
        next_pos = self.new_pos(chosen_velocity, direction)

        # Calculate distance to target point
        target_dist = self.model.space.get_distance(next_pos, self.target_point)

        # # Calculate factors
        # Ek = 1 - (Dk_target - self.R_vision_range - Rk_step)/(2*Rk_step)
        # Ok = None
        # Pk = None
        # Ak = None
        # Ik = None

        # raise NotImplementedError

        # # Using equation 1 for now:
        # return self.Ek_w * Ek + self.Ok_w * Ok + \
        #         self.Pk_w * Pk + self.Ak_w * Ak + \
        #         self.Ik_w * Ik
        # TODO: DELETE AND RETURN CORRECT UTILITY
        return 1


    def new_pos(self, chosen_velocity, theta_chosen):
        """
        TODO: CHECK FUNCTION IF SENDS CORRECT NEW POSITION"""
        new_pos = (self.pos[0] + chosen_velocity*np.cos(math.radians(theta_chosen)), self.pos[1]+chosen_velocity*np.sin(math.radians(theta_chosen)))
        return new_pos


    # TODO: DELETE I think
    # def update_angle(self):
    #     """
    #     Updates the angle to the new direction
    #     """
    #     # Find the current heading
    #     if (self.pos != self.pre_pos):

    #         # Get heading
    #         deltapos = self.model.space.get_heading(self.pos, self.pre_pos)
    #         # If the heading has a non-zero angle
    #         if (deltapos[0] != 0):
    #             # Calculate new angle
    #             cur_angle = math.degrees(math.atan((deltapos[1] / deltapos[0])))
    #             self.direction = cur_angle
    #         # If angle is zero, set the direction according to 'up' or 'down'
    #         else:
    #             if(self.dir == "up"):
    #                 self.direction = 90
    #             elif(self.dir == "down"):
    #                 self.direction = 270


    def pedestrians_in_field(self, vision_angle, vis_range):
        """
        returns the number of pedestrians in the field
        """
        # Calculate the lower angle and the upper angle
        lower_angle = self.direction - (vision_angle / 2)
        upper_angle = self.direction + (vision_angle / 2)

        # Change the current points to an np array for simplicity
        p0 = np.array(self.pos)

        # Convert to radians for angle calcuation
        # math.radians(180*3.5)%(2*math.pi) (TODO: useful or no?)
        u_rads = math.radians(upper_angle)
        l_rads = math.radians(lower_angle)
        # Calculate the end angles
        dx1 = math.cos(l_rads) * vis_range
        dy1 = math.sin(l_rads) * vis_range
        dx2 = math.cos(u_rads) * vis_range
        dy2 = math.sin(u_rads) * vis_range

        # Calculate the points
        p1 = np.array([p0[0] + dx1, p0[1] + dy1])
        p2 = np.array([p0[0] + dx2, p0[1] + dy2])
        # Calculate the vectors
        v1 = p1-p0
        v2 = p2-p1

        # Get the current neighbors
        neighbours = self.model.space.get_neighbors(self.pos, include_center=False, radius=vis_range)
        cone_neigh = []
        # Loop to find if neighbor is within the cone
        for neigh in neighbours:
            v3 = np.array(neigh.pos) - p0
            # Append object to cone_neigh if its within vision cone
            if (np.cross(v1, v3) * np.cross(v1, v2) >= 0 and np.cross(v2, v3) * np.cross(v2, v1) >= 0 and type(neigh) == Pedestrian):
                cone_neigh.append(neigh)

        return cone_neigh

    def pedestrian_intersection(self, conal_neighbours, angle, offset):
        """This fucntion will check the map for intersections from the given angle and the offset
        and return a list of neighbours that match those crieria
        Conal_neighbours: the objects within the vision field
        Angle: the direction k
        Offset: 1.5*radius_of_pedestrian to both sides of the direction line
        TODO: So this code give us the pedestrians in a certain direction right?
        TODO: CHECK CODE FOR DIFFERENT SITUATIONS
        """
        # calculate the linear formula for the line
        m = math.tan(math.radians(angle))
        b = self.pos[1] - (m*self.pos[0])

        # calcuate the y offset of the range of lines
        b_offset = offset/math.cos(angle)

        # calcuate the new intersection points based off the offset of the line
        b_top = b+b_offset
        b_bot = b-b_offset

        neighbours = conal_neighbours
        inter_neighbors = []
        for neigh in neighbours:
            if ((neigh.pos[1] - ((m*neigh.pos[0])+b_top)) <= 0 and (neigh.pos[1] - ((m*neigh.pos[0])+b_bot)) >= 0):
                inter_neighbors.append(neigh)

        # TODO: debug statement. This function only works for pedestrians going down? (i.e. 90 degree direction?)
        # TODO: Check for going up and directions other than 90 and 270
        # Prints the position, dir and direction of the current agent and the positions of the agents it sees
        # print('ped_intersect', self.pos, self.dir, self.direction, 'sees:', [neigh.pos for neigh in inter_neighbors])

        return inter_neighbors

    def closest_ped_on_line(self, m, b, neighbours):
        """
        This would find the closest pedestrian to a path given a subset of pedestrians
        TODO: CHECK CODE FOR DIFFERENT SITUATIONS
        """
        min_distance = abs((m*neighbours[0].pos[0])-neighbours[0].pos[1]+b)/math.sqrt((m**2) + 1)
        min_pedestrian = neighbours[0]
        for i in range(1, len(inter_neigh)):
            cur_distance = abs((m * neighbours[i].pos[0]) - neighbours[i].pos[1] + b) / math.sqrt((m ** 2) + 1)
            #if math.sqrt((self.pos[0]-inter_neigh[i].pos[0])**2+(self.pos[1]-inter_neigh[i].pos[1])**2) < min_distance:
            if cur_distance < min_distance:
                min_pedestrian = neighbours[i]
                min_distance = cur_distance
            elif cur_distance == min_distance:
                if self.model.space.get_distance(self.pos, min_pedestrian.pos) > self.model.space.get_distance(self.pos, neighbours.pos):
                    min_pedestrian = neighbours[i]
                    min_distance = cur_distance

        return min_distance, min_pedestrian

    def closest_pedestrian(self, inter_neigh):
        """
        This is used to find the closest pedestrian of a given included list of neighbours
        TODO: CHECK CODE FOR DIFFERENT SITUATIONS
        Returns distance to and the position of the closest pedestrian
        """
        min_distance = self.model.space.get_distance(self.pos, inter_neigh[0].pos)
        #min_distance = math.sqrt((self.pos[0]-inter_neigh[0].pos[0])**2+(self.pos[1]-inter_neigh[0].pos[1])**2)
        min_pedestrian = inter_neigh[0]
        for i in range(1, len(inter_neigh)):
            #if math.sqrt((self.pos[0]-inter_neigh[i].pos[0])**2+(self.pos[1]-inter_neigh[i].pos[1])**2) < min_distance:
            cur_distance = self.model.space.get_distance(self.pos, inter_neigh[i].pos)
            if cur_distance < min_distance:
                min_pedestrian = inter_neigh[i]
                min_distance = cur_distance

        return min_distance, min_pedestrian.pos


    def traffic_red(self):
        """
        Returns true if light is red
        """
        # Check if agent is in front of the traffic light (correct_side=True)
        # TODO: Add light for midsection (and add midsection)
        correct_side = False
        if self.dir == "up":
            own_light = 2
            if self.pos[1] > int(self.model.space.y_max/2 + 2):
                correct_side = True
        else:
            own_light = 6
            if self.pos[1] < int(self.model.space.y_max/2 - 2):
                correct_side = True

        # Iterate over all the agents
        for i in self.model.space.get_neighbors(self.pos, include_center = False, radius = 4):
            # If the agent is a light, which is red or orange, which is your own light and you're in front of the light
            if (isinstance(i,Light) and (i.state < 50 or i.state > 100) and i.light_id == own_light and correct_side == True):
                return True

        return False


    def step(self):
        '''
        This method should move the Sheep using the `random_move()` method implemented earlier, then conditionally reproduce.
        '''

        # check if there's a traffic light (and adjust speed accordingly)
        changed = 0
        correct_side = False
        if self.dir == "up":
            own_light = 6
            if self.pos[1] > int(self.model.space.y_max/2 + 2 ):
                correct_side = True
        else:
            own_light = 3
            if self.pos[1] < int(self.model.space.y_max/2 - 2):
                correct_side = True

        # very inefficient code right here if we notice if the run time is too long

        for i in self.model.space.get_neighbors(self.pos, include_center = False, radius = 2):
            if self.check_front() > 0 or (isinstance(i,Light) and (i.state < 50 or i.state > 100) and i.light_id == own_light and correct_side == True):
                self.speed = 0
                changed = 1
            elif (changed == 0 and self.check_front() == 0) or (changed == 0 and self.check_front() == 0 and correct_side == False):
                self.speed = 1


        # take a step
        if self.dir is "up":
            next_pos = (self.pos[0], self.pos[1] - self.speed)
            self.pre_pos = self.pos
            self.model.space.move_agent(self, next_pos)
        else:
            next_pos = (self.pos[0], self.pos[1] + self.speed)
            self.pre_pos = self.pos
            self.model.space.move_agent(self, next_pos)

        # TODO has to be moved to new step function
        self.time += 1
        # DELETE
        self.step_new()

    # this function is in both pedestrian and agent -> more efficient way?
    def check_front(self):
        '''
        Function to see if there is a Pedestrian closeby in front
        '''

        if self.dir == "up":
            direction = -1
        else:
            direction = 1

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
        correct_side = False
        if self.dir == "right":
            own_light = 1
            if self.pos[0] < int(self.model.space.x_max/2 - 2):
                correct_side = True
        else:
            own_light = 2
            if self.pos[0] > int(self.model.space.x_max/2 + 2):
                correct_side = True

        # very inefficient code right here if we notice if the run time is too long

        for i in self.model.space.get_neighbors(self.pos, include_center = False, radius = 4):
        # not only affected by 1 light
            if changed == 0 and (self.check_front() > 0 or (isinstance(i,Light) and (i.state < 50 or i.state > 100) and i.light_id == own_light and correct_side == True)):
                self.speed = 0
                break

            elif (changed == 0 and self.check_front() == 0) or (changed == 0 and self.check_front() == 0 and correct_side == False):
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
