import numpy as np
import matplotlib.pyplot as plt

import synapses
from neurons import Izh_Neuron, LIF_Neuron


def two_neurons():
    """
    Define 2 neurons, give them input, and see how they behave:
    """
    # construct 2 neurons with default settings:
    nrn1 = Izh_Neuron()
    nrn2 = LIF_Neuron()

    # define an input:
    clamp = synapses.Continuous_synapse(w = .75, onset = 200, offset = 650)
    # connect the input to the neurons:
    nrn1.add_synapse(clamp)
    nrn2.add_synapse(clamp)

    # managing Time, and temporal resolution of the simulation:    
    T = 800  # ms
    dt = 1.0 # ms
    ntsteps = int(T // dt)

    # init arrays for recording synapses and neurons:
    Ii = np.zeros(( 1, ntsteps )) # 1 input x T/dt time-steps
    Vv = np.zeros(( 2, ntsteps )) # 2 neurons x T/dt time-steps
    # run the model, for each timestep

    # define total time and timestep
    idx = 0
    for idx,t in enumerate( np.linspace(start=0, stop=T, num=ntsteps) ):
        # update synapse, and store I_out()
        clamp.time_step(t, dt)
        Ii[0, idx] = clamp.I_out()
        
        # update neurons
        nrn1.step(dt)
        nrn2.step(dt)

        # Store V's
        Vv[0, idx] = nrn1.get_V()
        Vv[1, idx] = nrn2.get_V()
        idx+=1

    plt.plot(Vv.T) # .T transpose, plots 2 lines in 1 command once
    # OR:
    # plt.plot(Ii.T)
    plt.show()
    return

def two_neurons_poiss():
    # ... your code goes here ...
    return

def izh_tester(izh_type = 'A'):
        # construct 2 neurons with default settings:
    nrn = Izh_Neuron(izh_type=izh_type)

    # define an input:
    clamp = synapses.Continuous_synapse(w = 0.8, onset = 200, offset = 650)
    # connect the input to the neurons
    nrn.add_synapse(clamp)

    # managing Time, and temporal resolution of the simulation:    
    T = 800  # ms
    dt = 1.0 # ms
    ntsteps = int(T // dt)

    # init arrays for recording synapses and neurons:
    Ii = np.zeros(( 1, ntsteps )) # 1 input x T/dt time-steps
    Vv = np.zeros(( 1, ntsteps )) # 1 neurons x T/dt time-steps
    # run the model, for each timestep

    # define total time and timestep
    idx = 0
    for idx,t in enumerate( np.linspace(start=0, stop=T, num=ntsteps) ):
        # update synapse, and store I_out()
        clamp.time_step(t, dt)
        Ii[0, idx] = clamp.I_out()
        
        # update neuron
        nrn.step(dt)

        # Store V's
        Vv[0, idx] = nrn.get_V()
        idx+=1

    plt.plot(Vv.T)
    # OR:
    # plt.plot(Ii.T)
    plt.show()
    return


def connecting_neurons():
    # define total time and timestep
    T = 800
    dt = 1.0
    ntsteps = int(T // dt)

    
    # construct 2 neurons:
    nrn1 = Izh_Neuron()
    nrn2 = LIF_Neuron()


    # construct clamped input, to inject current
    poiss = synapses.Poisson_synapse(
        firing_rate = 0.40, w = 0.45, onset = 200, offset = 650)
    
    # wiring:
    nrn1.add_synapse(poiss)
    n1n2 = synapses.Neuronal_synapse(pre = nrn1, w = 3.0)
    nrn2.add_synapse(n1n2)
    
    # init arrays for recording:
    Ii = np.zeros(( 2, ntsteps)) # 2 inputs
    Vv = np.zeros(( 2, ntsteps)) # 2 neurons
    
    idx = 0
    for t in np.linspace(start=0, stop=T, num=ntsteps):
        # update synapse, and store I_out()
        poiss.time_step(t, dt)
        n1n2.time_step(t, dt)

        Ii[0, idx] = poiss.I_out()
        Ii[1, idx] = n1n2.I_out()
        
        # update neurons
        nrn1.step(dt)
        nrn2.step(dt)

        # Store V's
        Vv[0, idx] = nrn1.get_V()
        Vv[1, idx] = nrn2.get_V()
        idx+=1

    plt.plot(Vv.T) # .T transpose so we can plot 2 lines at once
    # OR:
    # plt.plot(Ii.T)
    plt.show()
    return


if __name__ == '__main__':
    two_neurons()
    # izh_tester()
    # two_neurons_poiss()
    # connecting_neurons()