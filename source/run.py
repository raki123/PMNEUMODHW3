from network import Network

with open('networkfile.py') as nwsfile:
	nws = nwsfile.read()

net = Network(nws)
for i in range(50):
	desc, rt = net.simulate()
	#net.make_plots(trace=False, im = True, tmax=rt)
	print desc, rt
