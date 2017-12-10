import numpy as np
import matplotlib.pyplot as plt
from synapses import Poisson_synapse

class Neuron(object):
	"""THIS IS A TEMPLATE CLASS ONLY 
	This defines the functionality any neuron type should have:
	- add_synapses
	- step() : what to do every timestep
	- spike():
	"""
	def __init__(self, syn_in=[]):
		super(Neuron, self).__init__()
		self.record = False
		self.name = ''
		# input synapses; always one bg-noise input
		self.syn_in = syn_in + [Poisson_synapse(w=0.30, firing_rate=0.25)]

	def set_record(self, name='', record=True):
		"""Set the 'record-status' of this neuron:
		If Neuron.record is set to True, its potential is stored at each timestep
		This then can be used for plotting. 
		To label plots, it is wise to assign a unique 'name' to the neuron with the
		name-argument
		"""
		self.name = name
		self.record = record
		return

	def add_synapse( self, syn=[] ):
		"""Add synapse(s) to the input of the neuron
		syn 	: either a synapse, or a list of synapses
					syn should be of the 
		"""
		if type(syn) != list:
			syn = [syn]
		self.syn_in += list(syn)
		self.syn_in = list(set(self.syn_in))
		return

	def I_in(self):
		""" Summarizes all input from all synapses or injected currents that are
		Affecting this neuron, and return as one value
		"""
		# By default: Sum the input coming in from each synapse
		get_all_input = np.vectorize( lambda syn: syn.I_out() )
		try:
			return float( np.sum( get_all_input( self.syn_in ) ) )
		except Exception, e:
			print ("ERROR: could not get input from all synapses! \n" + 
				"\t Are all valid synapses from synapses.py, and do they" +
				" implement a valid I_out() function ?")
			raise e

	def get_V(self):
		pass

	def step(self, dt=1.0):
		pass

	def spike(self):
		return False


class LIF_Neuron(Neuron):
	"""Implementation of the Leaky Integrate-and-Fire Neuron"""
	def __init__(self, syn_in=[]):
		super(LIF_Neuron, self).__init__(syn_in)
		

		"""
		...Though the following params make the neuron spike at 30mV, rest at -65mV 
		this is to make the neuron's behavior close to Izh-neurons
		 	Note that the only difference is in the actual values for Vm; 
		through to the scaling constant -- you can compare them!
		"""
		# Behavior params:
		self.tau_m	= 10.0 # effective membrane time constant
		self.tau_r 	= 4.0  # refractory period (ms)
		self.V_rest = -65  # resting potential
		self.th_V 	= -55
		self.dV_s  	= 30 - self.V_rest # delta-V with a spike
		self.S 		= 1.5 # input 'scaling'

		# random initial state:
		# initial refractory period, random int between 0 and 8
		self.t_r = int(np.random.random_integers(0, 8, 1))
		# initial membrane potentiol, random float between th_V and V_rest 
		self.Vm = self.V_rest + np.random.sample(1) * (self.th_V - self.V_rest)
		return

	def get_V(self):
		return self.Vm

	def step(self, dt=1.0):
		# In refractory period; ignore input and do nothing:
		if self.t_r > 0:
			# set/keep Vm at rest, and count down ref period
			self.Vm = self.V_rest
			self.t_r -= dt
			return
		
		# scaled input, so 'responsivenes' matches
		I = self.I_in() * self.S
		#print I
		# Update Vm; the following corresponds to [v' = I + a - bv]
		self.Vm += dt * (I - (self.Vm - self.V_rest) / self.tau_m  )

		# Behavior in a spike:
		# 	Note that adding [dV_s] doesn't have any functionality here:
		# 	it just makes the spikes look pretty
		if self.Vm > self.th_V:
			self.Vm += self.dV_s # spike in the membrane potential
			self.t_r = self.tau_r # enter refractory period for tau_r ms
		return

	def spike(self):
		""" Are we spiking? """
		return self.Vm > self.th_V


class Izh_Neuron(Neuron):
	"""Generic class implementing different types of Izhikevitch-neurons"""
	def __init__(self, syn_in=[], izh_type='A'):
		super(Izh_Neuron, self).__init__(syn_in)

		# parameters, abcd, and s -> scaling of the input
		self.abcd_s = _izh_params[izh_type]
		a,b,c,d, s = self.abcd_s

		# State: V_0 and U_0
		self.V = float( np.random.sample(1) ) * c # anywhere between c and 0
		self.U = b * self.V
		self.spiking = False
		return

	def get_V(self):
		return self.V if not self.spiking  else 30.0

	def step(self, dt=1.0):
		# Unpack parameters:
		a,b,c,d,s = self.abcd_s
		I 	 = self.I_in() * s
		V, U = self.V, self.U

		# update; Izh 2003 rules:
		V += dt * ( 0.04 * V**2 + 5 * V + 140 - U + I )
		U += dt * ( a * ( b * V - U ) )

		# If spike, reset:
		if V >= 30:
			self.spiking = True
			# reset
			self.V = c
			self.U = U + d
			return
		self.spiking = False
		self.V = V; self.U = U

	def spike(self):
		return self.spiking


# params, for different neuron types: a,b,c,d and s-> scaling of the input 
_izh_params = dict(
	A=( 0.02, 0.2, -65, 6, 14),
	## (B) phasic spiking,
	B=( 0.02, 0.25, -65, 6, 0.5),
	## (C) tonic bursting,
	C=( 0.02, 0.25, -50, 2, 15),
	## (D) phasic bursting,
	D=( 0.02, 0.25, -55, 0.05, 0.6),
	## (E) mixed mode,
	E=( 0.02, 0.2, -55, 4, 10),
	## (F) spike freq. adapt,
	F=( 0.01, 0.2, -65, 8, 30),
)
