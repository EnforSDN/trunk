# Usage: sudo pythonexmpale.py

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import CPULimitedHost
from mininet.node import RemoteController
from mininet.node import Controller
from mininet.link import TCLink
from mininet.cli import CLI
import string
import os

class myTopo(Topo):
	def __init__(self, **opts):
		Topo.__init__(self, **opts)
		h1=self.addHost('h1',ip='10.0.0.1')  # (x=100,y=800)
		h2=self.addHost('h2',ip='10.0.0.2')  # (x=210,y=800)
		h3=self.addHost('h3',ip='10.0.0.3')  # (x=320,y=800)
		h4=self.addHost('h4',ip='10.0.0.4')  # (x=430,y=800)
		h5=self.addHost('h5',ip='10.0.0.5')  # (x=540,y=800)
		h6=self.addHost('h6',ip='10.0.0.6')  # (x=650,y=800)
		h7=self.addHost('h7',ip='10.0.0.7')  # (x=760,y=800)
		h8=self.addHost('h8',ip='10.0.0.8')  # (x=870,y=800)
		h9=self.addHost('h9',ip='10.0.0.9')  # (x=980,y=800)
		h10=self.addHost('h10',ip='10.0.0.10')  # (x=1090,y=800)
		h11=self.addHost('h11',ip='10.0.0.11')  # (x=1200,y=800)
		h12=self.addHost('h12',ip='10.0.0.12')  # (x=1310,y=800)
		h13=self.addHost('h13',ip='10.0.0.13')  # (x=1420,y=800)
		h14=self.addHost('h14',ip='10.0.0.14')  # (x=1530,y=800)
		h15=self.addHost('h15',ip='10.0.0.15')  # (x=1640,y=800)
		fw=self.addHost('fw',ip='10.1.1.16')  # (x=1750,y=800)
		h17=self.addHost('h17',ip='10.0.0.17')  # (x=1860,y=800)
		h18=self.addHost('h18',ip='10.0.0.18')  # (x=1970,y=800)
		h19=self.addHost('h19',ip='10.0.0.19')  # (x=2080,y=800)
		h20=self.addHost('h20',ip='10.0.0.20')  # (x=2190,y=800)
		h21=self.addHost('h21',ip='10.0.0.21')  # (x=2300,y=800)
		h22=self.addHost('h22',ip='10.0.0.22')  # (x=2410,y=800)
		h23=self.addHost('h23',ip='10.0.0.23')  # (x=2520,y=800)
		h24=self.addHost('h24',ip='10.0.0.24')  # (x=2630,y=800)
		h25=self.addHost('h25',ip='10.0.0.25')  # (x=2740,y=800)
		h26=self.addHost('h26',ip='10.0.0.26')  # (x=2850,y=800)
		h27=self.addHost('h27',ip='10.0.0.27')  # (x=2960,y=800)
		h28=self.addHost('h28',ip='10.0.0.28')  # (x=3070,y=800)
		h29=self.addHost('h29',ip='10.0.0.29')  # (x=3180,y=800)
		h30=self.addHost('h30',ip='10.0.0.30')  # (x=3290,y=800)
		h31=self.addHost('h31',ip='10.0.0.31')  # (x=3400,y=800)
		h32=self.addHost('h32',ip='10.0.0.32')  # (x=3510,y=800)
		s1000=self.addSwitch('s1000')  # (x=980,y=600)
		s1010=self.addSwitch('s1010')  # (x=1090,y=600)
		s1020=self.addSwitch('s1020')  # (x=1200,y=600)
		s1030=self.addSwitch('s1030')  # (x=1310,y=600)
		s1100=self.addSwitch('s1100')  # (x=1420,y=600)
		s1110=self.addSwitch('s1110')  # (x=1530,y=600)
		s1120=self.addSwitch('s1120')  # (x=1640,y=600)
		s1130=self.addSwitch('s1130')  # (x=1750,y=600)
		s1200=self.addSwitch('s1200')  # (x=1860,y=600)
		s1210=self.addSwitch('s1210')  # (x=1970,y=600)
		s1220=self.addSwitch('s1220')  # (x=2080,y=600)
		s1230=self.addSwitch('s1230')  # (x=2190,y=600)
		s1300=self.addSwitch('s1300')  # (x=2300,y=600)
		s1310=self.addSwitch('s1310')  # (x=2410,y=600)
		s1320=self.addSwitch('s1320')  # (x=2520,y=600)
		s1330=self.addSwitch('s1330')  # (x=2630,y=600)
		s2000=self.addSwitch('s2000')  # (x=980,y=400)
		s2010=self.addSwitch('s2010')  # (x=1090,y=400)
		s2020=self.addSwitch('s2020')  # (x=1200,y=400)
		s2030=self.addSwitch('s2030')  # (x=1310,y=400)
		s2100=self.addSwitch('s2100')  # (x=1420,y=400)
		s2110=self.addSwitch('s2110')  # (x=1530,y=400)
		s2120=self.addSwitch('s2120')  # (x=1640,y=400)
		s2130=self.addSwitch('s2130')  # (x=1750,y=400)
		s2200=self.addSwitch('s2200')  # (x=1860,y=400)
		s2210=self.addSwitch('s2210')  # (x=1970,y=400)
		s2220=self.addSwitch('s2220')  # (x=2080,y=400)
		s2230=self.addSwitch('s2230')  # (x=2190,y=400)
		s2300=self.addSwitch('s2300')  # (x=2300,y=400)
		s2310=self.addSwitch('s2310')  # (x=2410,y=400)
		s2320=self.addSwitch('s2320')  # (x=2520,y=400)
		s2330=self.addSwitch('s2330')  # (x=2630,y=400)
		s3000=self.addSwitch('s3000')  # (x=980,y=200)
		s3100=self.addSwitch('s3100')  # (x=1090,y=200)
		s3200=self.addSwitch('s3200')  # (x=1200,y=200)
		s3300=self.addSwitch('s3300')  # (x=1310,y=200)
		s3010=self.addSwitch('s3010')  # (x=1420,y=200)
		s3110=self.addSwitch('s3110')  # (x=1530,y=200)
		s3210=self.addSwitch('s3210')  # (x=1640,y=200)
		s3310=self.addSwitch('s3310')  # (x=1750,y=200)
		s3020=self.addSwitch('s3020')  # (x=1860,y=200)
		s3120=self.addSwitch('s3120')  # (x=1970,y=200)
		s3220=self.addSwitch('s3220')  # (x=2080,y=200)
		s3320=self.addSwitch('s3320')  # (x=2190,y=200)
		s3030=self.addSwitch('s3030')  # (x=2300,y=200)
		s3130=self.addSwitch('s3130')  # (x=2410,y=200)
		s3230=self.addSwitch('s3230')  # (x=2520,y=200)
		s3330=self.addSwitch('s3330')  # (x=2630,y=200)
		self.addLink(h1,s1000,bw=1)
		self.addLink(h2,s1000,bw=1)
		self.addLink(h3,s1010,bw=1)
		self.addLink(h4,s1010,bw=1)
		self.addLink(h5,s1020,bw=1)
		self.addLink(h6,s1020,bw=1)
		self.addLink(h7,s1030,bw=1)
		self.addLink(h8,s1030,bw=1)
		self.addLink(h9,s1100,bw=1)
		self.addLink(h10,s1100,bw=1)
		self.addLink(h11,s1110,bw=1)
		self.addLink(h12,s1110,bw=1)
		self.addLink(h13,s1120,bw=1)
		self.addLink(h14,s1120,bw=1)
		self.addLink(h15,s1130,bw=1)
		self.addLink(fw,s1130,bw=1)
		self.addLink(h17,s1200,bw=1)
		self.addLink(h18,s1200,bw=1)
		self.addLink(h19,s1210,bw=1)
		self.addLink(h20,s1210,bw=1)
		self.addLink(h21,s1220,bw=1)
		self.addLink(h22,s1220,bw=1)
		self.addLink(h23,s1230,bw=1)
		self.addLink(h24,s1230,bw=1)
		self.addLink(h25,s1300,bw=1)
		self.addLink(h26,s1300,bw=1)
		self.addLink(h27,s1310,bw=1)
		self.addLink(h28,s1310,bw=1)
		self.addLink(h29,s1320,bw=1)
		self.addLink(h30,s1320,bw=1)
		self.addLink(h31,s1330,bw=1)
		self.addLink(h32,s1330,bw=1)
		self.addLink(s1000,s2000,bw=10)
		self.addLink(s1000,s2010,bw=10)
		self.addLink(s1000,s2020,bw=10)
		self.addLink(s1000,s2030,bw=10)
		self.addLink(s1010,s2000,bw=10)
		self.addLink(s1010,s2010,bw=10)
		self.addLink(s1010,s2020,bw=10)
		self.addLink(s1010,s2030,bw=10)
		self.addLink(s1020,s2000,bw=10)
		self.addLink(s1020,s2010,bw=10)
		self.addLink(s1020,s2020,bw=10)
		self.addLink(s1020,s2030,bw=10)
		self.addLink(s1030,s2000,bw=10)
		self.addLink(s1030,s2010,bw=10)
		self.addLink(s1030,s2020,bw=10)
		self.addLink(s1030,s2030,bw=10)
		self.addLink(s1100,s2100,bw=10)
		self.addLink(s1100,s2110,bw=10)
		self.addLink(s1100,s2120,bw=10)
		self.addLink(s1100,s2130,bw=10)
		self.addLink(s1110,s2100,bw=10)
		self.addLink(s1110,s2110,bw=10)
		self.addLink(s1110,s2120,bw=10)
		self.addLink(s1110,s2130,bw=10)
		self.addLink(s1120,s2100,bw=10)
		self.addLink(s1120,s2110,bw=10)
		self.addLink(s1120,s2120,bw=10)
		self.addLink(s1120,s2130,bw=10)
		self.addLink(s1130,s2100,bw=10)
		self.addLink(s1130,s2110,bw=10)
		self.addLink(s1130,s2120,bw=10)
		self.addLink(s1130,s2130,bw=10)
		self.addLink(s1200,s2200,bw=10)
		self.addLink(s1200,s2210,bw=10)
		self.addLink(s1200,s2220,bw=10)
		self.addLink(s1200,s2230,bw=10)
		self.addLink(s1210,s2200,bw=10)
		self.addLink(s1210,s2210,bw=10)
		self.addLink(s1210,s2220,bw=10)
		self.addLink(s1210,s2230,bw=10)
		self.addLink(s1220,s2200,bw=10)
		self.addLink(s1220,s2210,bw=10)
		self.addLink(s1220,s2220,bw=10)
		self.addLink(s1220,s2230,bw=10)
		self.addLink(s1230,s2200,bw=10)
		self.addLink(s1230,s2210,bw=10)
		self.addLink(s1230,s2220,bw=10)
		self.addLink(s1230,s2230,bw=10)
		self.addLink(s1300,s2300,bw=10)
		self.addLink(s1300,s2310,bw=10)
		self.addLink(s1300,s2320,bw=10)
		self.addLink(s1300,s2330,bw=10)
		self.addLink(s1310,s2300,bw=10)
		self.addLink(s1310,s2310,bw=10)
		self.addLink(s1310,s2320,bw=10)
		self.addLink(s1310,s2330,bw=10)
		self.addLink(s1320,s2300,bw=10)
		self.addLink(s1320,s2310,bw=10)
		self.addLink(s1320,s2320,bw=10)
		self.addLink(s1320,s2330,bw=10)
		self.addLink(s1330,s2300,bw=10)
		self.addLink(s1330,s2310,bw=10)
		self.addLink(s1330,s2320,bw=10)
		self.addLink(s1330,s2330,bw=10)
		self.addLink(s2000,s3000,bw=10)
		self.addLink(s2000,s3100,bw=10)
		self.addLink(s2000,s3200,bw=10)
		self.addLink(s2000,s3300,bw=10)
		self.addLink(s2010,s3010,bw=10)
		self.addLink(s2010,s3110,bw=10)
		self.addLink(s2010,s3210,bw=10)
		self.addLink(s2010,s3310,bw=10)
		self.addLink(s2020,s3020,bw=10)
		self.addLink(s2020,s3120,bw=10)
		self.addLink(s2020,s3220,bw=10)
		self.addLink(s2020,s3320,bw=10)
		self.addLink(s2030,s3030,bw=10)
		self.addLink(s2030,s3130,bw=10)
		self.addLink(s2030,s3230,bw=10)
		self.addLink(s2030,s3330,bw=10)
		self.addLink(s2100,s3000,bw=10)
		self.addLink(s2100,s3100,bw=10)
		self.addLink(s2100,s3200,bw=10)
		self.addLink(s2100,s3300,bw=10)
		self.addLink(s2110,s3010,bw=10)
		self.addLink(s2110,s3110,bw=10)
		self.addLink(s2110,s3210,bw=10)
		self.addLink(s2110,s3310,bw=10)
		self.addLink(s2120,s3020,bw=10)
		self.addLink(s2120,s3120,bw=10)
		self.addLink(s2120,s3220,bw=10)
		self.addLink(s2120,s3320,bw=10)
		self.addLink(s2130,s3030,bw=10)
		self.addLink(s2130,s3130,bw=10)
		self.addLink(s2130,s3230,bw=10)
		self.addLink(s2130,s3330,bw=10)
		self.addLink(s2200,s3000,bw=10)
		self.addLink(s2200,s3100,bw=10)
		self.addLink(s2200,s3200,bw=10)
		self.addLink(s2200,s3300,bw=10)
		self.addLink(s2210,s3010,bw=10)
		self.addLink(s2210,s3110,bw=10)
		self.addLink(s2210,s3210,bw=10)
		self.addLink(s2210,s3310,bw=10)
		self.addLink(s2220,s3020,bw=10)
		self.addLink(s2220,s3120,bw=10)
		self.addLink(s2220,s3220,bw=10)
		self.addLink(s2220,s3320,bw=10)
		self.addLink(s2230,s3030,bw=10)
		self.addLink(s2230,s3130,bw=10)
		self.addLink(s2230,s3230,bw=10)
		self.addLink(s2230,s3330,bw=10)
		self.addLink(s2300,s3000,bw=10)
		self.addLink(s2300,s3100,bw=10)
		self.addLink(s2300,s3200,bw=10)
		self.addLink(s2300,s3300,bw=10)
		self.addLink(s2310,s3010,bw=10)
		self.addLink(s2310,s3110,bw=10)
		self.addLink(s2310,s3210,bw=10)
		self.addLink(s2310,s3310,bw=10)
		self.addLink(s2320,s3020,bw=10)
		self.addLink(s2320,s3120,bw=10)
		self.addLink(s2320,s3220,bw=10)
		self.addLink(s2320,s3320,bw=10)
		self.addLink(s2330,s3030,bw=10)
		self.addLink(s2330,s3130,bw=10)
		self.addLink(s2330,s3230,bw=10)
		self.addLink(s2330,s3330,bw=10)

def noneController(a):
	return None

net = Mininet(topo=myTopo(), link=TCLink, autoSetMacs=True, controller=noneController, listenPort=6634)
#net = Mininet(topo=myTopo(), link=TCLink, autoSetMacs=True, controller=RemoteController, listenPort=6634)
fw = net.get("fw")
net.start()
fw.cmd("ifconfig fw-eth0 down")
fw.cmd("ifconfig fw-eth0 hw ether 00:11:11:11:11:11 10.1.1.16 up")
fw.cmd("sysctl net.ipv4.ip_forward=1")
fw.cmd("sysctl net.ipv4.conf.all.send_redirects=0")
fw.cmd("sysctl net.ipv4.conf.all.rp_filter=2")
fw.cmd(" sudo echo 0 > /proc/sys/net/ipv4/conf/fw-eth0/send_redirects ")
fw.cmd(" sudo echo 2 > /proc/sys/net/ipv4/conf/fw-eth0/rp_filter ")
fw.cmd("ip route flush all")
fw.cmd("ip route add default dev fw-eth0")
for i in net.hosts:
	i=str(i)
	h=net.get(i)
	for dst in net.hosts:
		dst=str(dst)
		if dst=="fw":
			continue
		if dst==i:
			continue
		n=dst[1:]
		h.cmd("arp -s 10.0.0.%s 00:00:00:00:00:%02x" % (n, string.atoi(n)))
#net.interact()
hostsLinksBW=10