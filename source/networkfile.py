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
### XOR Solving network
# the input synapses gathered in a list to make indexing possible
inp = [in0, in1]

# a layer of neurons which should each detect if one of the inputs is zero or one
# the neuron at index i,j should fire if the input with index i is equal to j
catchsingle = [[LIF_Neuron(), LIF_Neuron()],[LIF_Neuron(), LIF_Neuron()]]

# a layer of neurons which should detect one of the possible input pairs
# the neuron at index i,j should fire if the input is equal to i,j
catchdouble = [[LIF_Neuron(), LIF_Neuron()],[LIF_Neuron(), LIF_Neuron()]]

#catchdouble = [[Izh_Neuron(), Izh_Neuron()],[Izh_Neuron(), Izh_Neuron()]]
# the output synapses gathered in a list to make indexing possible
outp = [out0, out1]

for i in [(0,0),(0,1),(1,0),(1,1)]:
	# debug statement to see how well the single input recognition works
	# catchsingle[i[0]][i[1]].set_record(name='c'+str(i), record = True)

	if i[1] == 0:
		# as far as i know there isnt a possibility to say if you do not get any input current then fire otherwise do not fire
		# instead when detecting a zero as input one can give the neuron some input current which is always present (or rather present when there is a stimulus)
		# this input current is then decreased by inhibiting neural connections if a one is present as input
		c = Poisson_synapse(firing_rate=0.75, w = 2.0, onset = 300)
		catchsingle[i[0]][i[1]].add_synapse([c])
		synapses.append(c)

	
	for x in xrange(50):
		n = Izh_Neuron( syn_in=[inp[i[0]]] )
		# add neurons which excite neurons responsible for detecting ones as input if they find a one 
		# or if the neuron is responsible for detecting a zero as input it receives an inhibiting signal from this neuron
		# this is handled by the sign of the weight of the neural synapse created here
		s = Neuronal_synapse(w = 1.0 * (-1)**(i[1]+1),pre=n,post= catchsingle[i[0]][i[1]] )
		nodes += [n]
		synapses += [s]

		# debug statement to see when the neurons are firing and what the output current is
		#if i == 1:
		#	n.set_record(name='spiking'+str(i), record=True) # name is not important
		#	s.set_record(name = 'outp_current'+str(i), record = True)

	# if we know which single digits are present we can derive which digit is present overall
	# if we know the first digit is a 0 the whole input can only be 0,0 or 0,1 -> add synapses which excite the corresponding neurons
	# furthermore if we know the first digit is a 0 the whole input can not be 1,0 or 1,1 -> add synapses which inhibit the corresponding neurons
	if i[0] == 0:
		s = Neuronal_synapse(w = 10.0, pre = catchsingle[i[0]][i[1]], post = catchdouble[i[1]][0])
		synapses += [s]
		s = Neuronal_synapse(w = 10.0, pre = catchsingle[i[0]][i[1]], post = catchdouble[i[1]][1])
		synapses += [s]
		s = Neuronal_synapse(w = -15.0, pre = catchsingle[i[0]][i[1]], post = catchdouble[1-i[1]][0])
		synapses += [s]
		s = Neuronal_synapse(w = -15.0, pre = catchsingle[i[0]][i[1]], post = catchdouble[1-i[1]][1])
		synapses += [s]
	if i[0] == 1:
		s = Neuronal_synapse(w = 10.0, pre = catchsingle[i[0]][i[1]], post = catchdouble[0][i[1]])
		synapses += [s]
		s = Neuronal_synapse(w = 10.0, pre = catchsingle[i[0]][i[1]], post = catchdouble[1][i[1]])
		synapses += [s]
		s = Neuronal_synapse(w = -15.0, pre = catchsingle[i[0]][i[1]], post = catchdouble[0][1-i[1]])
		synapses += [s]
		s = Neuronal_synapse(w = -15.0, pre = catchsingle[i[0]][i[1]], post = catchdouble[1][1-i[1]])
		synapses += [s]

# connect neurons which recongnize the different inputs to the corresponding outputs 0,0 to 0, 1,1 to 0 etc.
for i in [(0,0),(0,1),(1,0),(1,1)]:
	s = Neuronal_synapse(w = 10.0, pre = catchdouble[i[0]][i[1]], post = outp[(i[0] + i[1])%2])
	synapses += [s]
	# s = Neuronal_synapse(w = -3.0, pre = catchdouble[i[0]][i[1]], post = outp[(i[0] + i[1]+1)%2])
	# synapses += [s]

	# debug statement to see how well input detection is working
	# catchdouble[i[0]][i[1]].set_record(name=str(i), record = True)

# suppress random current reaching the output neurons by inhibiting before stimulus onset
for i in [0,1]:
	c = Poisson_synapse(w = -2.0, onset = 0, offset = 300)
	outp[i].add_synapse([c])
	synapses.append(c)

# add all neurons which were not added before
nodes += sum(catchsingle, [])
nodes += sum(catchdouble, [])

# debug statement showing how well the decision making process works overall/how close a decision was
# out0.set_record(name='out0', record=True)
# out1.set_record(name='out1', record=True)


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
