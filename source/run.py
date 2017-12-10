from network import Network

with open('networkfile.py') as nwsfile:
	nws = nwsfile.read()
counter = 0
for i in range(100):
	net = Network(nws)
	desc, rt = net.simulate()
	#net.make_plots(trace=True, im = True, tmax=rt)
	print desc, rt, net.patt_in
	if desc != sum(net.patt_in,0)%2:
		counter += 1
		print counter
print counter
