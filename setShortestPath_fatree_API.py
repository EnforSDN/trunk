#Licensed Materials - Property of IBM
#(c) Copyright IBM Corp. 2014, 2014 All Rights Reserved
#US Government Users Restricted Rights - Use, duplication 
#or disclosure restricted by GSA ADP Schedule Contract with 
#IBM Corp.

import sys
import os
import string
import getopt
import networkx as nx
import socket
import netaddr
import shelve
import time
import re
from fattree_API import topoCreator
# Based on the topology created by netEdit (in which a fw is connected using two interfaces to s1), creates a set or forwarding rules so all the traffic sent from host x to host y traverse the fw
# Additional rule can bypass the default rule and sent the data directly between host x and host y
# fw mac address is 00:11:11:11:11:11

class shortestPathFlows_ft:
    def __init__(self, topology, l):
        self.l = l
	self.loadInputs('setShortestPath.in',generalKeys=['hostsNames','switchesNames','links','fwMode','lenSwitch','M','W','fanout','fireWallIP'],dirName=None)
	print 'call topoCreator: M={0} W={1} fanout={2} fireWallIP={3}'.format(M,W,fanout,fireWallIP)
	self.ft=topoCreator(M,W,fanout, "FW", fireWallIP)
    def loadInputs(self,inputFileName,generalKeys=None,dirName=None):
      if dirName!=None:
	inputFileName='./{0}/{1}'.format(dirName,inputFileName)
      my_shelf=shelve.open(inputFileName)

      for key in generalKeys:
	globals()[key]=my_shelf[key]

      my_shelf.close()

    
    def execCmd(self, cmd):
      pass
    
    def setArp(self):
      pass
    
    def setDefaultFlows(self, priority=10):
      self.ft.setDefaultFlows()
      
    def setDirectFlows(self):
      self.ft.setDirectFlows()
    
    def setFlows(self,sip, dip, protocol, src_port, dst_port, priority=30):
      self.ft.setFlows(sip,dip,protocol,src_port,dst_port,priority) #define new flows
      
    
    def dropFlows(self,sip, dip, protocol, src_port, dst_port, priority=30):
      self.ft.dropFlows(sip,dip,protocol=protocol,src_port=src_port,dst_port=dst_port,priority=priority) #drop flows
      
    def delFlows(self,sip, dip, protocol, src_port=0, dst_port=0):
      pass
    
    
    def setDefaultFlowsFromFW(self):
      self.ft.setDefaultFlowsFromFW()
      
    def setDefaultFlowsToFW(self, srcip,includeFw,priority=10):
      numofOFcmds=self.ft.setDefaultFlowsToFW(srcip,includeFw,priority=10)
      return numofOFcmds

      
    def setDirectFlow(self, srcip):
      numofOFcmds=self.ft.setFlow(srcip) # setFlows
      return numofOFcmds
    
    def flush(self):
      pass

#def parseCmd(data,f,conn):
    #close = 0 
    #usage="[-h] [-f] -c add|del|setdirectflows|killSocket -s <src address> -d <dst address> -p tcp|udp|icmp [--sport <source port>] [--dport <source port>] -a accept|drop\n"
    #try:
        #opts, args = getopt.getopt(string.split(data),"hfxc:s:d:p:a:", ['sport=', 'dport='])
    #except getopt.GetoptError:
        #conn.send(usage)
        #return 0

    ## default parameters
    #cmd=""
    #sip=""
    #dip=""
    #sport=0
    #dport=0
    #protocol=""
    #action="accept"
    #flush=False
    
    #try:
        #for opt, arg in opts:
            #if opt == '-h':
                #conn.send(usage)
                #return 0
            #elif opt == '-f':
                #flush=True
            #elif opt == '-c':
                #cmd=arg
            #elif opt== '-s':
                #sip = str(netaddr.IPAddress(arg))
            #elif opt== '-d':
                #dip=str(netaddr.IPAddress(arg))
            #elif opt== '-p':
                #protocol=arg
            #elif opt== '--sport':
                #sport=string.atoi(arg)
            #elif opt== '--dport':
                #sport=string.atoi(arg)
            #elif opt== '-a':
                #action=arg
    #except:
        #conn.send(usage)
        #return 0

    #if flush==True:
        #f.flush()
        #return 0

    #if sip=="" or dip=="" or action not in ("accept", "drop") or protocol not in ("icmp", "tcp", "udp") or cmd not in ("add", "del","setdirectflows","killSocket"):
        #print "msg isn`t llegal"
        #conn.send(usage)
        #return 0

    #if cmd == "add":
        #if action=="accept":
            #f.setFlows(sip, dip, protocol, sport, dport)
        #else:  # drop
            #f.dropFlows(sip, dip, protocol, sport, dport)
    #elif cmd=="del":
        #f.delFlows(sip, dip, protocol, sport, dport)
    #elif cmd=="setdirectflows":
	#f.setDirectFlows()
    #elif cmd=="killSocket":
      #close = 1
    #return close
        
    

#def server(f, tcp_port):
    #TCP_IP="0.0.0.0"
    #s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #s.bind((TCP_IP, tcp_port))
    #s.listen(1)
    #close = 0
    #conn, addr = s.accept()
    #print 'Connection address:', addr
    #cmd=''
    #nextcmd=''
    #try:
      #while not close:
	  #data = conn.recv(50)
	  #if not data:
	      #break
	  #print "received data:", data
	  
	  #if string.find(data,'\n')!=-1:
	    #s=re.findall('(.*)\n(.*)',data)
	    #cmd="".join([cmd,s[0][0]])
	    #if s[0][1]!=None:
	      #nextcmd=s[0][1]
	    #close = parseCmd(cmd, f, conn)
	    #cmd=nextcmd
	  #else:
	    #cmd="".join([cmd,data])
	    
    #except KeyboardInterrupt:
      #conn.close()

    #conn.close()
    #return 0


#def printUsage(name):
    #print 'Usage: %s [-h] [-l] [-t] <topology file>' % name
    #print "-h\t\tprint this usage"
    #print "-t <topology file>\t\tTopology file as it created by netEdit -t"
    #print "-l \t\tList commands and exit"
    
#def main(argv):

    #try:
        #opts, args = getopt.getopt(argv[1:],"hlt:p:f:")
    #except getopt.GetoptError:
        #printUsage(argv[0])
	#sys.exit(2)
    
    #l=False
    #topology=""
    #tcp_port=2222
    #fwType = 0
    #for opt, arg in opts:
        #if opt == '-h':
            #printUsage(argv[0])
            #sys.exit()
        #elif opt== '-t':
            #topology = arg
        #elif opt== '-l':
            #l = True
        #elif opt== '-p':
            #tcp_port = string.atoi(arg)
	#elif opt == '-f':
	  #fwType= arg
    
    #if topology=="":
        #printUsage(argv[0])
        #sys.exit()
        

    #f = shortestPathFlows(topology, l)
    #if fwType != 0 and fwType == 'none':
      #f.setDirectFlows()
    #elif fwType == 0:
      #f.setDefaultFlows(priority=2)
      #server(f, tcp_port)
    #else:
      #print 'Unknown fwType: {0}'.format(fwType)
      #sys.exit()
    #return 0
