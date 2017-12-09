# our neuron model, and our synapses model
import neurons
import synapses

#utils
import numpy as np
import matplotlib.pyplot as plt
import sys
import itertools
from random import randint

# the following ensures every network spec will know the neuron/synapse types
# and knows the fixed input synapses and output nodes
_network_spec_header = """
from synapses import Neuronal_synapse, Continuous_synapse, Poisson_synapse
from neurons import LIF_Neuron, Izh_Neuron
synapses = [in0, in1]
nodes = [out0, out1]
"""

class Network(object):
	"""This contains a bunch of neurons and synapses, and should eventually 
	result in a perceptual descision
	"""
	def __init__(self, network_spec="", T=5000, dt=1.0, rand_input=False):
		super(Network, self).__init__()
		"""
		Code for the network architecture:
		1. Set input synapses
		2. Set output neurons
		3. Set further, unknown network specification
		"""
		########## 1. input synapses / one is stimulated, other isn't ##########
		# Input pattern:
		self.patt_in = np.array( [randint(0,1), randint(0,1)] )

                print self.patt_in
		## perceptual descision making: does the input match the output?
		if rand_input:
			np.random.shuffle( self.patt_in )

		# store which was the input:
		self.which_in = np.where(self.patt_in==1)[0]

		# Set inputs:
		in_f = 0.75 * self.patt_in
		in0 = synapses.Poisson_synapse(
			firing_rate = in_f[0], w=0.5, onset=300)
		in1 = synapses.Poisson_synapse(
			firing_rate = in_f[1], w=0.5, onset=300)
		
		########### 2. output neurons: fixed, unconnected LIF neurons ##########
		out0 = neurons.LIF_Neuron()
		out1 = neurons.LIF_Neuron()

		###### 3. Read in further network architecture specified by user #######
		### Compile network specification
		try:
			cnwspec = compile(_network_spec_header + network_spec,
				u'<string>', u'exec')
		except Exception, e:	
			print "!!!Failed to COMPILE network_spec!!!"
			raise e
		### ... and evaluate it:
		try:
			exec cnwspec in locals()
		except Exception, e:
			print "!!!!Failed to EXECUTE network_spec!!!"
			raise e

		### Store unique nodes/synapses in the class
		# set() gets rid of doubles:
		self.nodes = list(set(nodes))
		# sort them by name:
		self.nodes = sorted(self.nodes, key = lambda x: x.name) 
		# this collects all known synapses:
		self.synapses = self.list_network_synapses(self.nodes, synapses)

		"""
		Code to run the network. Step-functions, check output spikes, etc.
		"""
		# function to tstep all neurons/synapses at once (for self.time_step) :
		self.all_syn_step = np.vectorize(
			lambda syn, t, dt: syn.time_step(t, dt) )
		self.all_nrn_step = np.vectorize(
			lambda nrn, dt: nrn.step(dt) )
		# does the output spike?
		self.get_out_spikes = lambda : (out0.spike(), out1.spike())
		self.outspikes = []

		"""
		Code for recording(s): 
		>>> extract and list which neurons and synapses are recorded, 
			store those for later use
		>>> Set up functions to record from those
		>>> Notify user (of nr of recordings)
		"""
		### Extract those neurons which is recorded:
		# Function to determine all recorded objects
		get_recording = np.vectorize( lambda obj: obj.record)
		# Get their indices
		recv_idx = np.where(get_recording(self.nodes))[0]
		reci_idx = np.where(get_recording(self.synapses))[0]

		# and store them in separate lists:
		self.rec_nrns = np.array( self.nodes 	)[recv_idx] 
		self.rec_syns = np.array( self.synapses )[reci_idx]

		### Set up functions that record from them:
		getI = lambda syn : syn.I_out()
		getV = lambda nrn : nrn.get_V()
		self.get_Is = np.vectorize( getI )
		self.get_Vs = np.vectorize( getV )

		### notify user how many nodes/synapses are recorded:
		if len(recv_idx) > 0:
			print "#recorded Neurons : ", self.get_Vs(self.rec_nrns).shape[0]

		if len(reci_idx) > 0:
			print "#recorded Synapses: ", self.get_Is(self.rec_syns).shape[0]

		return

	def list_network_synapses(self, nodes, known_synapses = [] ):
		""" This functions lists all unique synapses in the network. 
		This lists all unique synapses connected to 'nodes'. Passing
		additional 'known_synapses' is particularily useful when synapses exist 
		independently from nodes (e.g. for testing purposes...)
			Main purpose for this function is to ensure all synapses in the 
		network are actually included in the simulation, including the hidden
		BG-noise synapses that come with each neuron.
		"""
		# how to get all synapses from nodes:
		get_all_syn = np.vectorize( lambda n_s: n_s.syn_in )
		# Nodes encode synapses as lists: 'itertools.chain' welds them together:
		node_syns = list(itertools.chain.from_iterable( get_all_syn(nodes) ))
		# list all synapses found + known synapses
		all_synapses = node_syns + known_synapses 
		# filter duplicates and return
		return list( set(all_synapses) )
		
	def time_step(self, t, dt, idx):
		""" Simulate a time_step in the model
		1. update all synapses in the network
		2. update all nodes in the network
		3. Record nodes and synapses where requested
		4. Update #output spikes, (to check output frequency > threshold)
		"""
		# update synapses:
		self.all_syn_step(self.synapses, t, dt)
		# update neurons:
		self.all_nrn_step(self.nodes, dt)

		# Record V or I where requested
		if len(self.rec_nrns) > 0:
			self.Vv[:,idx] = self.get_Vs(self.rec_nrns)
		if len(self.rec_syns) > 0:
			self.Ii[:,idx] = self.get_Is(self.rec_syns)
		# update spike_output
		if len(self.outspikes) >= (300 * dt):
			self.outspikes = self.outspikes[1:]
		self.outspikes.append( self.get_out_spikes() )
		return

	def simulate(self, T=5000, dt=1.0):
		"""Simulate one trial with the current network.
		1. set out recording-traces
		2. Run through timesteps until descision_made or time > T
		3. return result
		"""
		# T should be higher than 300, that is when stim-onset is.
		if T < 300:
			print "WARNING: T < 300ms, corrected to 300ms"
			T = 300
		self.T = T; 
		self.dt = dt

		### 1. set out traces for neurons to be recorded
		self.Vv = np.zeros(( self.rec_nrns.shape[0], int(T//dt)))
		self.Ii = np.zeros(( self.rec_syns.shape[0], int(T//dt)))

		### 2. Run through timesteps:
		# 'progess bar'
		pb_width = T//100
		init_pbar = "[>{}]".format(" "*(pb_width))
		sys.stdout.write(init_pbar)
		sys.stdout.flush()
		sys.stdout.write("\b" * (pb_width+1))
		# /progress bar

		self.descision_made = None
		idx = 0
		for t in np.arange(0, T, dt):
			# update network:
			self.time_step(t,dt, idx)
			
			# updat 'progress bar'
			if t % 100 == 0:
				sys.stdout.write("\b->")
				sys.stdout.flush()
			
			# check descision made, if so, stop
			if idx > 300:
				self.check_descision_made(t, dt)
			if self.descision_made:
				break
			idx += 1

		# ...end of the progress bar
		sys.stdout.write("\n")

		# check for descisions:
		if self.descision_made == None:
			self.descision_made = (None, t)
		return self.descision_made

	def check_descision_made(self, t, dt, f_thres = 0.10 ):
		# descision when > 0.1 spikes/ms, i.e. 10ms ISI
		spike_traces = zip(*self.outspikes)
		nspikes = sum(spike_traces[0]), sum(spike_traces[1])
		if nspikes[0] > (f_thres * 300*dt): # if n spikes in this timespan > 200Hz
			self.descision_made = ( 0, t )
		elif nspikes[1] > (f_thres * 300*dt):
			self.descision_made = ( 1, t )
		return

	def make_plots(self, trace=True, im=False, tmax=None):
		"""Plot traces of recorded neurons and synapses"""

		tmax = self.T if tmax == None else tmax
		tmax = int(tmax)
		tt = np.linspace(0, tmax, tmax*self.dt)

		if trace:
			getname = lambda obj : obj.name
			get_all_names = np.vectorize( getname)
			if len(self.rec_nrns) > 0:
				x = np.tile(tt, (self.Vv.shape[0],1 ) )
				plt.plot(x.T, self.Vv[:,:tt.shape[0]].T )
				plt.legend(get_all_names(self.rec_nrns))
				plt.show()
			# plot I
			if len(self.rec_syns) > 0:
				x = np.tile(tt, (self.Ii.shape[0],1 ) )
				plt.plot(x.T, self.Ii[:,:tt.shape[0]].T )
				plt.legend(get_all_names(self.rec_syns))
				plt.show()				
		if im:
			if len(self.rec_nrns) > 0:
				plt.imshow(self.Vv[:,:tmax], 
							interpolation='none', aspect='auto')
				plt.show()
			if len(self.rec_syns) > 0:
				plt.imshow(self.Ii[:,:tmax], 
							interpolation='none', aspect='auto')
				plt.show()
		return


if __name__ == '__main__':
	"""This code reads the network_spec file, and runs it (once)
	"""
	# reading the networkfile:
	with open('networkfile.py') as nwsfile:
		nws = nwsfile.read()
	# generate a Network-object
	net = Network(nws)

	# generate a Network-object with it, and run it
	desc, rt = net.simulate()
	net.make_plots(trace=True, im=False, tmax=rt)
