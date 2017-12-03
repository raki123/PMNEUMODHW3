import numpy as np
from scipy.stats import gaussian_kde
import matplotlib.pyplot as plt
import csv

# our network class:
import network

class Network_simulator(object):
	"""This class  defines ways to run multiple networks with the same 
	'spec-file' and turn them into readable results. Primarily, it allows:
	-	to generate density plots of simulated RTs and decisions
	-	to write such results to a csv file, one row per trial with the response
	made and the simulated RT
	-	to read results from previous simulations and generate the density plots
	again
	"""
	def __init__(self, nwspec="", T=2000, dt=1.0):
		"""The constructor:
		- nwspec is the network_specification_file
		- T is the simulated time.
		- dt is the timesteps taken
		"""
		# init 'object'
		super(Network_simulator, self).__init__()
		self.nwspec = nwspec
		self.T = T
		self.dt = dt
		# results field is intially empty
		self.results = []

	def simulate(self, n_iter=10, trial_trace=False, 
						trial_im=False, rug_plot=True):
		"""Run the network n_iter times, and store the results
		- n_iter: number of iterations, int > 0
		- trial_trace: bool; should traceplots of the trial be generated?
		- trial_im: bool; should spike image plots be generated?
		- rug_plot: should we generate a rug-plot (w/ density lines) of the 
		current results?
		"""
		
		# Run the specified amount of iterations:
		for it in xrange(n_iter):
			# setup network with the nwspec:
			net = network.Network(network_spec=self.nwspec)
			# get desc, rt from simulation
			desc, rt = net.simulate(T=self.T, dt=self.dt )
			
			# transform desc into None,True,False for correctness
			if desc is not None:
				# Compare result to net.which_in
				self.results.append( (desc==net.which_in, rt) )
			else:
				self.results.append( (None, rt) )
			print self.results[-1]

			# plotting:
			if trial_trace or trial_im:
				net.make_plots(trace=trial_trace, im=trial_im, tmax=rt + 1)

		# summary results
		if rug_plot:
			self.make_rug_plot(res_choice = True)
		return

	def make_rug_plot(self, res_choice = None):
		"""Generate a rug-plot, plotting the resulting RTs of 
		either all responses, or correct/incorrect selectively
		- res_choice: 
			True for correct responses 
			False for incorrect responses
			None for both responses 
		"""
		
		if res_choice is None:
			res_choice = [True, False]
			plt.subplot(121)
		else:
			res_choice = [res_choice]
			plt.subplot(111)

		# plot results for chosen res_choice
		none_res = filter(lambda x: x[0] is None, self.results)
		descT = filter(lambda x: x[0] == True, self.results)
		descF = filter(lambda x: x[0] == False, self.results)

		# get range of the values, for xlim()
		vals = []
		if descT: vals += zip(*descT)[1]
		if descF: vals += zip(*descF)[1]
		min_,max_ = (min(vals)-5.5, max(vals)+5.5 )
		# vals = zip(*descT)[1] +  zip(*descF)[1]
		if True in res_choice:
			if descT:
				ax = plt.gca()
				rts = zip(*descT)[1]
				ax.hold(True)
				if len(rts) > 2:
					kernel = gaussian_kde(rts)
					base = np.linspace(min_,max_, 100)
					ax.plot(base, kernel(base), lw=1.5, color='b')
				ax.plot(rts, np.zeros(len(rts)), 'b|', ms=20)
				ax.set_xlim( min_,max_ )
				ax.hold(False)

			print "Correct descisions: {:.2f}%".format(float(len(descT)) / 
													  len(self.results)*100)
		if False in res_choice:
			if descF:
				if len(res_choice) == 2:
					ax = plt.subplot(122)
				else:
					ax = plt.gca()
				rts = zip(*descF)[1]
				ax.hold(True)
				if len(rts) > 2:
					kernel = gaussian_kde(rts)
					base = np.linspace(min_,max_, 100)
					ax.plot(base, kernel(base), lw=1.5, color='r')
				ax.plot(rts, np.zeros(len(rts)), 'r|', ms=20)
				ax.set_xlim( min_,max_ )
				ax.hold(False)
			print "Incorrect descisions: {:.2f}%".format(float(len(descF)) / 
														  len(self.results) * 100)
		
		print "No descision made: {:.2f}%".format(float(len(none_res)) / 
												len(self.results)*100)
		plt.show()
		return

	def write_res(self, fname):
		with open(fname,'w') as f:
			writer = csv.writer(f)
			# write header?
			for desc,rt in self.results:
				if desc is not None:
					writer.writerow( [bool(desc), rt] )
				else:
					writer.writerow( ["NoResp", rt] )
		return

	def read_res(self,fname):
		with open(fname, 'r') as f:
			reader = csv.reader(f)
			for row in reader:
				desc,rt = row
				# print desc, rt
				# self.results.append( (None,rt) )
				if desc not in ['True', 'False']:
					self.results.append( (None, rt) )
				else:
					self.results.append( (desc=='True', float(rt)) )
		return



"""Main (for testing)
"""
if __name__ == '__main__':
	# look up your "networkfile" -- you may change this filename if you wish
	with open('networkfile.py') as nwsfile:
		nws = nwsfile.read()

	# Generate a network, based on this network-specification
	simulator = Network_simulator(nws)

	# run a bunch of simulatons:
	simulator.simulate(n_iter=5, trial_im=False, 
						trial_trace=False, rug_plot=True)

	# print the results:
	print simulator.results

	# write the results to a file: 
	simulator.write_res('temp_results.csv')
	
	# # Read the results from a file:
	# create new network simulator object
	sim2 = Network_simulator()
	# read the file:
	sim2.read_res('temp_results.csv')
	# use it to create a nice plot:
	sim2.make_rug_plot(res_choice=True)

