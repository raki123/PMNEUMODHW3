"""
In this file, you have to define neurons and synapses
NB: they are only included in the simulation when they have been added 
	to the list nodes[] and  the list synapses[] .
NB2: Make sure to construct every object separately; only unique neurons and
		synapses are modeled, and duplicate references are removed.

-  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  -

Note that every networkfile is implicitly preceded by :
>>> from synapses import Neuronal_synapse
>>> from neurons import LIF_Neuron, Izh_Neuron
>>> synapses = [in0, in1] 
>>> nodes = [out0, out1]

So, the input synapses and the output nodes are already listed and accessible

-  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  -

For a cheatsheet of how to define neuron/synapse types and functions, see below
"""

### EXAMPLE 1 :
##define neurons;
#a = Izh_Neuron()
#b = Izh_Neuron(izh_type = 'C')
#
## define a synapse;
#syn_ab = Neuronal_synapse(w = 3.5, pre = a, post = [b])
#
## We want to see the neuron's behavior:
#a.set_record('Neuron A - Izh type A')
#b.set_record('Neuron B - Izh type C')
## and what is happening at the output of interest:
#out0.set_record('Output 0')
#out1.set_record('Output 1')
#
#
## add them to the nodes/synapses
#nodes += [a,b]
#synapses += [syn_ab]
### END OF EXAMPLE 1

## EXAMPLE 2:
#generate 20 Izh neurons:
lyr = []
for i in xrange(20):
	# generate neuron ... with in0 as input and out0 as output
	n = Izh_Neuron( syn_in=[in0] )
	n.set_record(name='', record=False) # name is not important
	s = Neuronal_synapse(w = 2.0,pre=n,post= out0 )
	#add node to lyr:
	lyr += [n]
	synapses += [s]


nodes += lyr
## END OF EXAMPLE 2


"""
Below lists the different types of synapses and neurons that can be defined in
this file, as well as the relevant class methods. 

--------------------------------------------------------------------------------
SYNAPSES 
========
Synapses can be of three types: 
	Neuronal_synapse, transmitting current on a pre-synaptic spike
	Poisson_synapse, abstracting neuronal firing at a certain rate
	Continuous_synapse, mimicking continuously clamped input (for testing)

-  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  -
# Parent class, (TEMPLATE ONLY -- you shouldn't use this one itself)
class Synapse(object)
	__init__(self, w = 0)
		> initialize with a certain weight
	set_record(self, name = '', record = True)
		> set whether the synapse's output current I is recorded (set to false 
			on initialization). With name, you can ID the resulting trace
	
	project( self, post = [] )
		> Use this synapse as input to multiple output nodes at once

-  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  -
# Child classes: Only child-specific implementations documented:
# Neuronal
class Neuronal_synapse(Synapse):
	def __init__(self, w = 0.1, pre = None, post = None):
		> Initialize with weight w,  with one specific presynaptic neuron, 
			and a (list of) postsynaptic neuron(s).
-  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  -
# Poisson:
class Poisson_synapse(Synapse):
	def __init__(self, firing_rate = 0.5, w = 0.1, onset = 0, offset = None)
		> initialize with certain firing rate (spikes/ms), a certain weight,
			onset of stimulation (ms) and offset (if None, it stays on)
-  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  -
class Continuous_synapse(Synapse):
	def __init__(self, w = 0.1, onset = 0, offset = None):
		> initialize with a weight w, and onset/offset as with Poisson

--------------------------------------------------------------------------------
NEURONS 
=======
Neurons can be of two types:
	LIF_Neuron, the Leaky Integrate and Fire neuron
	Izh_Neuron, implementing a variety of Izhikevitch (2003) Neuron-types
-  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  -
# Parent class, (TEMPLATE ONLY -- you shouldn't use this one itself)
class Neuron(object):
	def __init__(self, syn_in = []):
		> Initialize the neuron, possibly with one or several input synapses.
			NB: neurons _always_ have one Poisson_synapse delivering BG-noise
	
	def set_record(self, name = '', record = True)
		> As in Synapse.set_record (but records V not I)

	def add_synapse( self, syn = [] )
		> add one or multiple synapses to the current neuron

-  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  -
# LIF_Neuron
class LIF_Neuron
	--(no LIF-specific methods)

-  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  -
# Izh_Neuron:
class Izh_Neuron(Neuron):
	def __init__(self, syn_in = [], izh_type = 'A'):
		> Initialize as specific Izhikevitch-type. Types A-F are supported.
-  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  -
"""
