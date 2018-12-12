from math import floor
from cell_grid import CellGrid
import os
import parameters as params
from states import NUM_STATES, WILD, DEVEL, BURNING, BURNT
import random
from itertools import product 

def simulate_neighbor_destruction(num_potential_neighbors) :
    dim = 3
    if num_potential_neighbors != 8 :
        assert False

    filename = "prob_destruction_%f_%f_%f_%f_%d" % (params.FIRE_START_PROB_DEVEL,
                                                    params.FIRE_CATCH_PROB_DEVEL,
                                                    params.FIRE_START_PROB_WILD,
                                                    params.FIRE_CATCH_PROB_WILD,
                                                    num_potential_neighbors)
    if os.path.exists(filename) :
        chance_destruction = [0]*(num_potential_neighbors+1)
        with open(filename) as fin :
            for line in fin.readlines() :
                splt = line.strip().split(',')
                num_devel_neighbors = int(splt[0])
                prob_dest = float(splt[1])
                chance_destruction[num_devel_neighbors] = prob_dest

        return chance_destruction

    print "Running simulations to estimate destruction of center cell in neighborhood"

    chance_destruction = []
    num_simulations = 10000
    for num_devel_neighbors in range(num_potential_neighbors+1) :
        print "Simulating number develeoped neighbors = %d" % num_devel_neighbors
        times_burned = 0
        all_neighbors = list(product(range(1,dim+1), range(1,dim+1)))
        for simulation in range(num_simulations) :
            cells = CellGrid(dim+1, dim+1)
            cells.set_state(dim/2+1, dim/2+1, DEVEL)
            for (row,col) in random.sample(all_neighbors, num_devel_neighbors) :
                cells.set_state(row, col, DEVEL)

            while True :
                cells.update_fire_state(susceptibility=1,
                                        no_new_start=False)
                if cells.state_counts[BURNING] == 0 :
                    break
            if cells.get_state(dim/2+1, dim/2+1) == BURNT :
                times_burned += 1

        chance_destruction.append(float(times_burned) / num_simulations)

    with open(filename, 'w') as fout :
        print "Saving file '%s' with probabilties to remember for next time" % filename
        for (i,prob) in enumerate(chance_destruction) :
            fout.write("%d,%f\n" % (i,prob))

    return chance_destruction


def main() :
    root = "C:/Users/BAP/Documents/Econ - Nat'l Resources/Final Project/econ_260a-master/output_test"
    #root = "C:/Users/BAP/Documents/Econ - Nat'l Resources/Final Project/econ_260a-master/output_test_coop"

    if not os.path.exists(root) :
        os.mkdir(root)
    else :
        for listing in os.listdir(root) :
            fullpath = os.path.join(root, listing)
            if os.path.isfile(fullpath):
                os.unlink(fullpath)


    num_rows = 25
    num_cols = 100
    chance_destruction_lookup = simulate_neighbor_destruction(8)
    cells = CellGrid(num_rows,
                     num_cols,
                     chance_destruction_lookup)
    time_steps = 10

    outputfile = os.path.join(root, "log.txt")
    with open(outputfile, 'w') as fout :
        fout.write("%s\n" % "Time,Developed,Wild,Fires Started,Burn Iterations,Total Burnt")
        for time_step in range(time_steps) :

            name = "devel_%d" % (time_step)
            filename = os.path.join(root, "%s.png" % name)

            #render current state
            cells.display(filename)

            #decide to build or not
            num_developed = cells.update_developed_state()

            #See if anything catches fire
            burn_iteration = 0
            fire_susceptibility = random.uniform(.5,1.5)
            num_fires_started = 0
            while True :
                #random walk starting from the current susceptibility
                fire_susceptibility += random.uniform(-.1-burn_iteration/float(20),.1)
                cells.update_fire_state(susceptibility=fire_susceptibility,
                                        no_new_start=burn_iteration > 0)
                if cells.state_counts[BURNING] > 0 :
                    if burn_iteration == 0 :
                        num_fires_started = cells.state_counts[BURNING]

                    burn_name = "%s_burn_%d" % (name, burn_iteration)
                    filename = os.path.join(root, "%s.png" % burn_name)
                    cells.display(filename)
                else :
                    break

                burn_iteration += 1

            fout.write("%d,%d,%d,%d,%d,%d\n" % (time_step,
                                             cells.state_counts[DEVEL],
                                             cells.state_counts[WILD],
                                             num_fires_started,
                                             burn_iteration,
                                             cells.state_counts[BURNT]))

if __name__ == "__main__" :
    main()


    # once initialized to DEVEL or WILD, a cell only can transition to burning/burned or not
    # ie nothign goes WILD to DEVEL
    # how do things go from WILD to devel
    # probabilisticaly?
    # or depending on neighbors?
    # if that ineq is true, always turn to develped?
    # or if conditions are met, then there is a chance to become DEVEL
