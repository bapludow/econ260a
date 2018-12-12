from cell import Cell
import matplotlib.pyplot as plt
import scipy.stats as ss
import random as random
import numpy as np
from math import pow
from states import WILD, DEVEL, BURNT, BURNING, NUM_STATES
import parameters as params

class CellConsiderate(Cell) :
    def __init__(self,
                 mean_cost_to_develop,
                 std_cost_to_develop,
                 mean_rent,
                 std_rent,
				 prob_catch_from_neighbor) :

        super(CellConsiderate, self).__init__(mean_cost_to_develop,
                                              std_cost_to_develop,
                                              mean_rent,
                                              std_rent,
											  prob_catch_from_neighbor)

    def estimate_rent(self,
                      horizon,
                      neighbors) :
        
		#copied from cell.py because inputs changed
        num_developed_neighbors = sum([1 for n in neighbors if n.state == DEVEL])
        devel_density = (num_developed_neighbors + 1) / float(len(neighbors) + 1)
        neighbor_density = num_developed_neighbors / float(len(neighbors))
		
		#TODO: compute how adding this cell will imporove the values of the lands around it
        prob_survival = 1 - self.estimate_destruction(neighbors)
        undiscounted_rent = self.neighbor_modulated_rent(neighbor_density)

        #profit for this house
        expected_profit = 0
        for year in range(horizon) :
            expected_profit += undiscounted_rent * pow(prob_survival, year)

        #diffential benefit to neighbors
        #assume neighbors 1) have same rent as me 2) have same neighbor density
        rent_with_this_construction = self.neighbor_modulated_rent(devel_density)
        expected_neighbor_profit = 0
        for year in range(horizon) :
            expected_neighbor_profit += rent_with_this_construction * pow(prob_survival, year)

        differential = expected_neighbor_profit - expected_profit

        #just assume 8 possible neighbors for now
        # if neighbor_density > 0 :
            # print "exp profit: %f, area effect: %f" % (expected_profit, differential * (neighbor_density*8))
        return expected_profit + differential * (neighbor_density*8)


        #Below is just the placeholder, does the same as a regular "Cell"
        # return super(CellConsiderate, self).estimate_rent(horizon,
        #                                                   devel_density,
        #                                                   # neighbor_density)

    def estimate_cost(self,
                      horizon,
                      neighbors) :
        #TODO: compute the odds of destroying your neighbors by putting a house here

        #Below is just the placeholder, does the same as a regular "Cell"
        return super(CellConsiderate, self).estimate_cost(horizon,
                                                          neighbors)

