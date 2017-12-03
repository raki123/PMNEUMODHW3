import numpy as np

class Synapse(object):
	"""This is a synapse object; it regulates the currents passed on by 
	interconnected neurons
	"""
	def __init__(self, w = 0):
		super(Synapse, self).__init__()
		self.record = False
		self.name = ''

		# current I_out:
		self.w = w

		# short current wave, open-and-close after spike
		self.Iout = 0.0
		self.tau = 1.8 # 1.8 corresponds to the fast time constant of AMPA receptors
		self.spike = False
		return

	def set_record(self, name = '', record = True):
		self.name =  name
		self.record = record
		return

	def time_step(self, t , dt = 1.0):
		return

	def I_out(self):
		return

	def project( self, post = [] ):
		"""Project this synapse to a layer [list] of neurons
		Makes the synapse source [pre] project to multiple neurons at once, 
		using duplicates (not deep copies!) of this synapse
		"""
		if type(post) != list:
			post = [post]

		# Add current synapse to every projected 
		for j in post:
			j.add_synapse(syn = self)
		return 

"""Usable children of the synapse class"""
class Continuous_synapse(Synapse):
	"""Simulates clamped input
	used for testing purposes primarily 
	"""
	def __init__(self, w = 0.1, onset = 0, offset = None):
		super(Continuous_synapse, self).__init__(w)
		
		self.onset = onset
		self.offset = offset
		self.on = False

		return

	def time_step(self, t , dt = 1.0):
		"""Simply determine whether we're on or not:
		"""
		onset = self.onset
		offset = self.offset if self.offset else t+1
		self.on = (t >= onset and t < offset)
		return

	def I_out(self):
		# I_out is really easy; w if on, else 0
		return self.w * self.on


class Neuronal_synapse(Synapse):
	"""Synapse wiring 2 neurons together. When they spike,
	they produce short input: duration governed by tau, by default mimicking AMPA
	"""
	def __init__(self, w = 0.1, pre = None, post = None):
		super(Neuronal_synapse, self).__init__(w)
		self.pre = pre # presynaptic neuron
		self.spike = False
		# optional postsynaptic neuron
		if post:
			self.project(post)

	def time_step(self, t, dt = 1.0):
		self.spike = self.pre.spike() # pre tells you whether it's spiking
		# update 'current flow' accordingly
		self.Iout += dt*(-self.Iout/self.tau) + self.spike
		return

	def I_out(self):
		return self.Iout * self.w


class Poisson_synapse(Synapse):
	"""A Poisson_synapse; it simulates random input to a neuron, with 
	a certain firing rate, an onset, offset and weight
	"""
	def __init__(self, firing_rate = 0.5, w = 0.1, onset = 0, offset = None):
		super(Poisson_synapse, self).__init__(w)
		self.firing_rate = firing_rate # pr spikes per ms
		self.spike = 0 # 0/1
		self.onset = onset
		self.offset = offset
		self.on = False
		return
	
	def time_step(self, t, dt = 1.0):
		# is the stimulus on?
		onset = self.onset
		offset = self.offset if self.offset else t+1
		self.on = (t >= onset and  t < offset)
		# update frequency dep. on onset/offset
		freq = self.firing_rate if self.on else 0.0
		# determine whether spike:	
		self.spike = int( np.random.sample(1)  < (freq * dt)) # random spiking
		# update current accordingly
		self.Iout += dt*(-self.Iout/self.tau) + self.spike
		return

	def I_out(self):
		return self.Iout * self.w * self.on


"""Main code (for testing)
"""
if __name__ == '__main__':
	poiss = Poisson_synapse()
	# define total time and timestep
	T = 800
	dt = 1.0
