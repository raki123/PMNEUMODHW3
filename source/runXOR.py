from network import Network

with open('networkfileXOR.py') as nwsfile:
	nws = nwsfile.read()
counter = 0
for i in range(100):
	net = Network(nws)
	desc, rt = net.simulate()
	#net.make_plots(trace=True, im = True, tmax=rt)
	print "output: %s, reaction time: %s, input patter: %s"%(str(desc), str(rt), str(net.patt_in))
	if desc != sum(net.patt_in,0)%2:
		counter += 1
		print "an error occured. this is error number %s"%str(counter)
	else:
		print "solved correctly"
print "overall %s errors occured"%str(counter)
