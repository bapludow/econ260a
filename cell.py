import matplotlib.pyplot as plt
import scipy.stats as ss
import random as random
import numpy as np
from math import pow
from states import WILD, DEVEL, BURNT, BURNING, NUM_STATES
import parameters as params



class Cell(object) :
    def __init__(self,
                 mean_cost_to_develop,
                 std_cost_to_develop,
                 mean_rent,
                 std_rent,
                 prob_catch_from_neighbor) :
        self.state = WILD
        self.burnable_value = 1
        self.cost_to_develop = np.random.normal(mean_cost_to_develop, std_cost_to_develop)
        self.rent = np.random.normal(mean_rent, std_rent)
        self.prob_catch_from_neighbor = prob_catch_from_neighbor

    def estimate_destruction(self, neighbors) :
        num_developed_neighbors = sum([1 for n in neighbors if n.state == DEVEL])

        #Technically could be burnt or burning, buuuuut meh
        num_wild_neighbors = len(neighbors) - num_developed_neighbors

        # print "num devel: %d, num_wild: %d, prob destruction: %f" % (num_developed_neighbors, num_wild_neighbors, prob_catch_from_neighbor)


        return params.FIRE_START_PROB_DEVEL + (1 - params.FIRE_START_PROB_DEVEL) * self.prob_catch_from_neighbor[num_developed_neighbors]

    def estimate_destruction_old(self, neighbor_density) :
        #TODO: this is a placeholder. Peak at density=.5, zero at density=0 and 1
        #Not realistic, should never be 0
        shifted = neighbor_density - .5
        if shifted < 0 :
            shifted *= -1
        return params.MAX_EST_FIRE_PROB - (shifted * params.MAX_EST_FIRE_PROB/.5)

    def neighbor_modulated_rent(self, neighbor_density) :
	    return self.rent * (1 + 2.5*((-2 * pow((neighbor_density-.75),2))+1.125))
    #    if neighbor_density <= 0.5 :
    #        return self.rent * (1+(2*neighbor_density))
    #    else :
    #        return self.rent * (1+((-2*neighbor_density)+2))

    def estimate_rent(self, horizon, neighbors) : #devel_density, neighbor_density) :

        num_developed_neighbors = sum([1 for n in neighbors if n.state == DEVEL])
        devel_density = (num_developed_neighbors + 1) / float(len(neighbors) + 1)
        neighbor_density = num_developed_neighbors / float(len(neighbors))

        prob_survival = 1 - self.estimate_destruction(neighbors)
        undiscounted_rent = self.neighbor_modulated_rent(neighbor_density)

        expected_profit = 0
        for year in range(horizon) :
            expected_profit += undiscounted_rent * pow(prob_survival, year)

        return expected_profit

    def estimate_cost(self,
                      horizon,
                      neighbors) :
        return self.cost_to_develop


    def update_developed_state(self, cell, neighbors) :
        if cell.state == DEVEL:
            self.state = DEVEL
            return

        if cell.state == BURNT :
            self.state = BURNT
            return

        if cell.state == BURNING:
            self.state = BURNING
            return

        expected_profit = self.estimate_rent(params.TIME_HORIZON,
                                             neighbors)
                                             # devel_density,
                                             # neighbor_density)

        expected_cost = self.estimate_cost(params.TIME_HORIZON,
                                           neighbors)
                                           # devel_density,
                                           # neighbor_density)

        if expected_profit > expected_cost :
            self.state = DEVEL
        else :
            self.state = WILD

        # if cell.state == WILD and num_developed_neighbors > 1 :
        #     self.state = DEVEL
        # else :
            # self.state = cell.state

    def is_burn_because_neighbors(self, n_burning_neighbors, prob_catch) :
        for i in range(n_burning_neighbors) :
            if random.random() < prob_catch :
                return True
        return False

    def update_fire_state(self,
                          cell,
                          neighbors,
                          susceptibility=1.0,
                          no_new_start=False) :

        if cell.state == WILD :
            if not no_new_start and random.random() < params.FIRE_START_PROB_WILD * susceptibility :
                self.state = BURNING
                self.burn()
            else :
                neighbors_burning = sum([1 for n in neighbors if n.state == BURNING])
                catch_fire = self.is_burn_because_neighbors(neighbors_burning,
                                                         susceptibility * params.FIRE_CATCH_PROB_WILD)
                if catch_fire :
                    self.state = BURNING
                    self.burn()
                else :
                    self.state = WILD

        elif cell.state == DEVEL :
            neighbors_devel = sum([1 for n in neighbors if n.state == DEVEL])
            if not no_new_start and \
               random.random() < susceptibility * params.FIRE_START_PROB_DEVEL and \
               neighbors_devel < len(neighbors) :
                self.state = BURNING
                self.burn()
            else :
                neighbors_burning = sum([1 for n in neighbors if n.state == BURNING])
                catch_fire = self.is_burn_because_neighbors(neighbors_burning,
                                                         susceptibility * params.FIRE_CATCH_PROB_DEVEL)
                if catch_fire :
                    self.state = BURNING
                    self.burn()
                else :
                    self.state = DEVEL

        elif cell.state == BURNING :
            self.burnable_value = cell.burnable_value
            self.burn()
            if self.burnable_value <= 0 :
                self.state = BURNT
            else :
                self.state = BURNING

        elif cell.state == BURNT :
            self.state = BURNT

    def burn(self) :
        self.burnable_value -= 1

    def get_state(self) :
        return self.state


if __name__ == "__main__" :
    for i in range(9) :
        neighbors = [Cell(params.MEAN_COST_TO_DEVELOP,
                            params.STD_COST_TO_DEVELOP,
                            params.MEAN_RENT,
                            params.STD_RENT) for k in range(9)]
        for j in range(i) :
            neighbors[j].state = DEVEL
        print "num devel neighbor: %d, prob dest: %f" % (i, neighbors[0].estimate_destruction(neighbors))



#################################################################################################
##All old from when trying to get probabilities analytically. Doing Monte carlo now, see imshow.py
#def p_catch_from_neighbor(num_potential_neighbors) :
#    if num_potential_neighbors != 8 :
#        print "Probability computation for neighborhoods bigger than 8 isn't implemented yet"
#        assert False
#
#    #return data
#    #index is number of developed neighbors
#    prob_catch_from_neighbor = [0]*num_potential_neighbors
#
#    for num_developed_neighbors in range(num_potential_neighbors) : 
#        #Technically could be burnt or burning, buuuuut meh
#        num_wild_neighbors = num_potential_neighbors - num_developed_neighbors
#
#        #compute probability 0..n out of n developed neighbors catches fire
#        devel_binom = ss.binom(num_developed_neighbors, params.FIRE_START_PROB_DEVEL)
#        devel_tuples = []
#        for num_ignited_devel_neighbors in range(num_developed_neighbors+1) :
#            prob = devel_binom.pmf(num_ignited_devel_neighbors)
#            devel_tuples.append((num_ignited_devel_neighbors,
#                                 prob))
#
#        #compute probability 0..n out of n wild neighbors catches fire
#        wild_tuples = []
#        wild_binom = ss.binom(num_wild_neighbors, params.FIRE_START_PROB_WILD)
#        for num_ignited_wild_neighbors in range(num_wild_neighbors+1) :
#            prob = wild_binom.pmf(num_ignited_wild_neighbors)
#            wild_tuples.append((num_ignited_wild_neighbors, prob))
#
#        #combine devel and wild, to get prob of 0..n potential neighbors catching fire
#        total_ignited_tuples = {}
#        for (num_devel, devel_prob) in devel_tuples :
#            for (num_wild, wild_prob) in wild_tuples :
#                total_ignited = num_devel + num_wild
#                if total_ignited in total_ignited_tuples :
#                    total_ignited_tuples[total_ignited] += devel_prob*wild_prob
#                else :
#                    total_ignited_tuples[total_ignited] = devel_prob*wild_prob
#
#        # print total_ignited_tuples
#        catch_from_neighbor = 0
#        for num_ignited in total_ignited_tuples :
#            prob = total_ignited_tuples[num_ignited]
#            catch_from_neighbor += prob * (1 - pow(params.FIRE_CATCH_PROB_DEVEL, num_ignited))
#
#        #16 is number in next "ring"
#        num_frontier = 16
#        frontier_binom = ss.binom(num_frontier, params.FIRE_START_PROB_WILD)
#        frontier_tuples = []
#        for num_ignited in range(num_frontier+1) :
#            prob = frontier_binom.pmf(num_ignited)
#            frontier_tuples.append((num_ignited, prob))
#        #each frontier fire has to catch something in inner ring
#        
#        prob_catch_from_outside_fire
#
#
#        prob_catch_from_neighbor[num_developed_neighbors] = catch_from_neighbor
#
#    return prob_catch_from_neighbor

