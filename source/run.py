from network import Network

with open('networkfile.py') as nwsfile:
	nws = nwsfile.read()

for i in range(10):
	net = Network(nws)
	desc, rt = net.simulate()
	#net.make_plots(trace=False, im = True, tmax=rt)
	print desc, rt
