#Licensed Materials - Property of IBM
#(c) Copyright IBM Corp. 2014, 2014 All Rights Reserved
#US Government Users Restricted Rights - Use, duplication 
#or disclosure restricted by GSA ADP Schedule Contract with 
#IBM Corp.

#!/usr/bin/python


h=__import__('header') # this is the options, traffic matrix etc...
from setShortestPath_fatree_API import shortestPathFlows_ft
import fattree_API  
from numpy import arange
import pickle
import timeit
import mininet
from mininet.cli import CLI
from mininet.net import Mininet
from mininet.node import Node
from mininet.topo import SingleSwitchTopo
from mininet.log import setLogLevel
from mininet.topo import Topo
from mininet.node import RemoteController
from mininet.node import Controller
from mininet.link import TCLink
import re
import os
import signal
import sys
import subprocess
from select import poll, POLLIN
import time
import smtplib
from math import floor,log10,ceil
import string
import random
import shelve
from analyzeResults import analyzeResults
import shutil

def saveInputs(inputFileName,dirName=None):
  if dirName!=None:
    inputFileName='./{0}/{1}'.format(dirName,inputFileName)
  
  my_shelf=shelve.open(inputFileName,'n')
  generalKeys=['repeats', 'repeat','hostsNum','rulesByrepeat', 'topologyName','trafficMatrixByrepeat','fanout','udpBWs','bwFactor','updPrecentages','topologyType'] # 'switchNums','switchNum',
  if h.options['topology']=='Fat-Tree':
    generalKeys.append('M')
    generalKeys.append('W')
    generalKeys.append('fanout')
    generalKeys.append('fireWallIP')
  
  for key in generalKeys:
    my_shelf[key]=globals()[key]
  my_shelf.close()


def loadInputs(inputFileName,dirName=None):
  if dirName!=None:
    inputFileName='./{0}/{1}'.format(dirName,inputFileName)
  my_shelf=shelve.open(inputFileName)
  print 'my_shelf.keys()={0}'.format(my_shelf.keys())
  generalKeys=['repeats','repeat','hostsNum','rulesByrepeat', 'topologyName','trafficMatrixByrepeat','fanout','udpBWs','bwFactor','updPrecentages','topologyType'] # 'switchNums','switchNum',
  
  for key in generalKeys:
    globals()[key]=my_shelf[key]
  
  if topologyType=='Fat-Tree':
    for key in ['M','W','fanout','fireWallIP']:
      globals()[key]=my_shelf[key]
    
  my_shelf.close()

def saveResults(outputFileName,hostsNum=0,keys=None,dirName=None):
  if dirName!=None:
    outputFileName='./{0}/{1}'.format(dirName,outputFileName)
  
  my_shelf=shelve.open(outputFileName,'n')
  saveKeys=[]
  if keys==None:
    simulationKeys=['avgResults','maxResults','minResults']
    generalKeys=['repeats','switchNums', 'repeat','hostsNum','switchNum','rulesByrepeat', 'topologyName','trafficMatrixByrepeat','updPrecentages'] 
  else:
    simulationKeys=[]
    generalKeys=keys
    
  for simType in simulationTypes:
    for simulationKey in simulationKeys:
      saveKeys.append('{0}_{1}'.format(simType.lower(),simulationKey))
  
  for key in generalKeys:
    my_shelf[key]=globals()[key]
      
  for key in saveKeys:
    if hostsNum==0:
      my_shelf[key]=globals()[key]
    else:
      my_shelf[key]=globals()[key][hostsNum]
    
  my_shelf.close()


def assignResults(results):
  "get repeatalbe results and generate avg, min, max"
  aR=analyzeResults()
  avg_results = aR.init_tree(results.values()[0], -555)
  aR.fill_tree(results, avg_results, aR.average)
  
  max_results = aR.init_tree(results.values()[0], -555)
  aR.fill_tree(results, max_results, max)
  
  min_results = aR.init_tree(results.values()[0], -555)
  aR.fill_tree(results, min_results, min)
  del aR, results
  return  avg_results,min_results,max_results

def random_split(items, size):
  sample = set(random.sample(items, size))
  protocols=[0 for x in items]
  
  for x in items:
    if x in sample:
      protocols[x-1]='UDP'
    if x not in sample:
      protocols[x-1]='TCP'
  return protocols
  
  
def TrafficMatrixUDPTCPGenerator(hosts,UDPPrecentages,generationType,onlyElephant=0):
  "generate random/determentstic traffic matrix according to generationType for UDP/TCP mixed precentage traffic"
  "tcp: ['tcp',dataSize]	 ; udp: ['udp',dataSize,transmitBW constraint (if 0 without constraint)]"
  "dataSize for DC: "
  "'mice':query traffic (mice 2KB to 20KB in size). Use till 32KB according to DeTail paper"
  "'medium': delay sensitive short messages (100KB to 1MB)"
  "'elephant': throughput sensitive long flows (1MB to 100MB)"

  
  trafficMatrix={} # index of the host (not of the hTrafficMatrixUDPTCPGenerator(hosts,UDPPrecentages,onlyElephant=0,generationType):osts python list !), i.e. (1,3,['tcp']): h1(client) ->(tcp)-> h3(server). 3rd tuple is protocol; supproted: 'tcp' ['udp',udp bandwidth]
  protocols=['tcp','udp']
  print 'UDPPrecentages={0}'.format(UDPPrecentages)
  if onlyElephant==1:
    dataSizes=['elephant'] # exlude 'mice' since data to trasmit in iperf <128KB incur very high bandwidth report...
  else:
    dataSizes=['medium','elephant'] # exlude 'mice' since data to trasmit in iperf <128KB incur very high bandwidth report...
  
  destination=[0 for h in range(0,hosts/2,1)]
  for h in range(1,hosts/2,1):
    if generationType == 'detementstic':
      dst=hosts/2+h
    else:
      raise RuntimeError ('Unknown generationType:{0}'.format(generationType))
    destination[h]=dst
    
  udpBW=0 # PalceHolder for acctual udpBW detemined across simulation
  i=0
  for UDPPrecentage in UDPPrecentages:
    trafficMatrixtmp=[]
    protocols=random_split(range(1,hosts/2,1), (UDPPrecentage*((hosts/2)-1))/100)
    for h in range(1,hosts/2,1):
      protocol=protocols[h-1]
      dataSize=dataSizes[random.randrange(0, len(dataSizes), 1)]
      dst=destination[h]
      if protocol=='udp':
	udpBW=str(udpBW)+"M"
	trafficMatrixtmp.append((h,dst,[protocol,dataSize,udpBW]))
      else:
	trafficMatrixtmp.append((h,dst,[protocol,dataSize]))
    trafficMatrix[i]=trafficMatrixtmp
    i=i+1
  return trafficMatrix

  
  
  
  

def randomTrafficMatrixGenerator(hosts,onlyUDP=0,onlyElephant=0):
  "generate random traffic matrix"
  "tcp: ['tcp',dataSize]	 ; udp: ['udp',dataSize,transmitBW constraint (if 0 without constraint)]"
  "dataSize for DC: "
  "'mice':query traffic (mice 2KB to 20KB in size). Use till 32KB according to DeTail paper"
  "'medium': delay sensitive short messages (100KB to 1MB)"
  "'elephant': throughput sensitive long flows (1MB to 100MB)"


  trafficMatrix=[] # index of the host (not of the hosts python list !), i.e. (1,3,['tcp']): h1(client) ->(tcp)-> h3(server). 3rd tuple is protocol; supproted: 'tcp' ['udp',udp bandwidth]
  
  if onlyUDP==1:
    protocols=['udp']
  else:
    protocols=['tcp','udp']
  
  if onlyElephant==1:
    dataSizes=['elephant'] # exlude 'mice' since data to trasmit in iperf <128KB incur very high bandwidth report...
  else:
    dataSizes=['medium','elephant'] # exlude 'mice' since data to trasmit in iperf <128KB incur very high bandwidth report...

  udpBWRange=[1,100] # in MB
  for h in range(1,hosts,1):
    dst=random.randrange(1, hosts, 1)
    if dst==h:
      dst=(dst+random.randrange(1, hosts/2, 1))%hosts
    if dst==0:
      dst=dst+1
    protocol=protocols[random.randrange(0, len(protocols), 1)]
    dataSize=dataSizes[random.randrange(0, len(dataSizes), 1)]
    if protocol=='udp':
      udpBW=str(random.randrange(udpBWRange[0],udpBWRange[1], 1))+"M"
      trafficMatrix.append((h,dst,[protocol,dataSize,udpBW]))
    else:
      trafficMatrix.append((h,dst,[protocol,dataSize]))
  return trafficMatrix

def determinsticTrafficMatrixGenerator(hosts,onlyUDP=0,onlyElephant=0):
  "generate random traffic matrix"
  "tcp: ['tcp',dataSize]	 ; udp: ['udp',dataSize,transmitBW constraint (if 0 without constraint)]"
  "dataSize for DC: "
  "'mice':query traffic (mice 2KB to 20KB in size). Use till 32KB according to DeTail paper"
  "'medium': delay sensitive short messages (100KB to 1MB)"
  "'elephant': throughput sensitive long flows (1MB to 100MB)"
  ' connect: i -> h/2+i'
  trafficMatrix=[] # index of the host (not of the hosts python list !), i.e. (1,3,['tcp']): h1(client) ->(tcp)-> h3(server). 3rd tuple is protocol; supproted: 'tcp' ['udp',udp bandwidth]
  
  if onlyUDP==1:
    protocols=['udp']
  else:
    protocols=['tcp','udp']
  
  if onlyElephant==1:
    dataSizes=['elephant'] # exlude 'mice' since data to trasmit in iperf <128KB incur very high bandwidth report...
  else:
    dataSizes=['medium','elephant'] # exlude 'mice' since data to trasmit in iperf <128KB incur very high bandwidth report...

  udpBWRange=[1,100] # in MB
  for h in range(1,hosts/2,1):
    dst=hosts/2+h
    protocol=protocols[random.randrange(0, len(protocols), 1)]
    dataSize=dataSizes[random.randrange(0, len(dataSizes), 1)]
    if protocol=='udp':
      udpBW=str(random.randrange(udpBWRange[0],udpBWRange[1], 1))+"M"
      trafficMatrix.append((h,dst,[protocol,dataSize,udpBW]))
    else:
      trafficMatrix.append((h,dst,[protocol,dataSize]))
  return trafficMatrix
  
def setAllowRules(h,curAllowRules,protocolMode=2):
  allowRules = curAllowRules
  if protocolMode==1:
    protocolList=['udp']
  elif protocolMode==2:
    protocolList=['ip']
  else:
    protocolList=['tcp','udp']

  for host in h:
    ip='10.0.0.{0}'.format(host)
    for protocol in protocolList:
      allowRules.append([ip,'*', '*', '*', protocol])
  return allowRules
  
  
def randomRulesGenerator(h,mode,onlyUDP=0):
  # define random rules for srcIP-based and protocol flows (all rest are wild-card)
  denyRules=[]
  allowRules=[]
  processRules=[]
  randomChunks=[]

  if mode=='random':
    randomChunks=randomChunk(range(h),3)
  else:
    hosts=[]
    for i in range(h):
      hosts.append(i)
    if mode=='allDeny':
      randomChunks.append(hosts)
      randomChunks.append([])
      randomChunks.append([])
    elif mode=='allAllow':
      randomChunks.append([])
      randomChunks.append(hosts)
      randomChunks.append([])
    elif mode=='allProcess':
      randomChunks.append([])
      randomChunks.append([])
      randomChunks.append(hosts)
    else:
      raise RuntimeError('Unknown mode:{0}'.format(mode))
    
  if onlyUDP==1:
    protocolList=['udp']
  elif onlyUDP==2:
    protocolList=['ip']
  else:
    protocolList=['tcp','udp']

  for protocol in protocolList:
    for g in range(3):
      for host in randomChunks[g]:
	ip='10.0.0.{0}'.format(host+1)
	if g==0:
	  denyRules.append([ip,'*', '*', '*', protocol])
	elif g==1:
	  allowRules.append([ip,'*', '*', '*', protocol])
	elif g==2:
	  processRules.append([ip,'*', '*', '*', protocol])
	  
  return [denyRules,allowRules,processRules]
  
def randomChunk(xs, n):
    ys = list(xs)
    random.shuffle(ys)
    ylen = len(ys)
    size = int(ylen / n)
    chunks = [ys[0+size*i : size*(i+1)] for i in xrange(n)]
    leftover = ylen - size*n
    edge = size*n
    for i in xrange(leftover):
            chunks[i%n].append(ys[edge+i])
    return chunks

def kill_iperf():
   # kill iperf till no process exists ...
   print '*** Start killing iperf'
   stderr=''
   while len(stderr)==0:
    p = subprocess.Popen('sudo killall -9 iperf', shell=True, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    (stdout, stderr) = p.communicate() 
    print stdout
    print stderr
    if stderr!='':
      print stderr
   p = subprocess.Popen('sudo killall -9 netperf', shell=True, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
   p = subprocess.Popen('sudo killall -9 netserver', shell=True, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
  
      
def signal_handler(signal,frame):
    "Killall iperf when ctrl+C entered"
    print 'KeyboardInterrupt - killall iperf'
    kill_iperf() 

    sys.exit(0)

def chunks( l, n ):
    "Divide list l into chunks of size n - thanks Stackoverflow"
    return [ l[ i: i + n ] for i in range( 0, len( l ), n ) ]

def magnitude(x):
  return int(floor(log10(x)))
    
def printConvert(v):
  "v is in mega, convert it to visible number for printing"
  v=v*1e6
  oom=magnitude(v)
  if oom>=3 and oom<6:
    return [v/1e3,'K']
  elif oom>=6 and oom<9:
    return [v/1e6,'M']
  elif oom>=9:
    return [v/1e9,'G']
  elif oom<3:
    return [v,'']
    
def convertToMega(BWsStr,perfType=h.options['perfType']):
  "convert BWsStr to value in M."
  B=[];
  
  for BW in BWsStr:
    if perfType=='iperf':
      v=re.findall(r'(\d+\.?\d*) (\w?)',BW)
      if len(v)==1:
	value=v[0][0]
	oom=v[0][1]   # order of magnitude 
	if oom=='K':
	  B.append(float(value)/1000)
	elif oom=='M':
	  B.append(float(value))
	elif oom=='G':
	  B.append(float(value)*1000)
	elif oom=='':
	  B.append(float(value)/1e6)
	else:
	  raise error ("Unknown order of magnitude")
    elif perfType=='netperf':
      B.append(float(BW)/1e6)
    else: 
      raise RuntimeError ('Unknown perfType')

  return B 
  
def convertToMegaNetPerf(BWsStr,oom):
  "convert BWsStr to value in M."
  B=[];
  for value in BWsStr:
      if oom=='10^3':
	B.append(float(value)/1000)
      elif oom=='10^6':
	B.append(float(value))
      elif oom=='10^9':
	B.append(float(value)*1000)
      elif oom=='':
	B.append(float(value)/1e6)
      else:
	raise error ("Unknown order of magnitude")
  return B 
  

def convertTomili(BWsStr):
  "convert BWsStr to value in milisec."
  B=[];
  
  for BW in BWsStr:
    v=re.findall(r'(\d+\.?\d*) (\w?)',BW)
    if len(v)==1:
      value=v[0][0]
      oom=v[0][1]   # order of magnitude 
      if oom=='u':
	B.append(float(value)/1000)
      elif oom=='m':
	B.append(float(value))
      elif oom=='':
	B.append(float(1e3*value))
      else:
	raise error ("Unknown order of magnitude")
  return B 

    
    
def readOutputFile(node,filename,probeType,perfType='iperf',bwLimit=None,simName=None):
    "re on the iperf outputs to catch data and bw; return avg bw and total transmitted data"
     #client%s-%s-%s.txt` ;' % (server.IP() , client.name,simName,h.options['fwMode'])  
    if perfType=='none':
      return -1,-1,'nan','nan'
    content_file = open(filename, 'r')
    txt = content_file.read()
    
    if probeType == 'tcp' or probeType == 'udp':
      if perfType == 'iperf':
	BWsRE= re.findall(r'(\d+\.?\d* \w?)bits/sec',txt)
	BWs =convertToMega(BWsRE)
      elif perfType == 'netperf':
	BWsRE= re.findall(r'[0-9]+\.?[0-9]*\s+[0-9]+\.?[0-9]*\s+[0-9]+\.?[0-9]*\s+[0-9]+\.?[0-9]*\s+([0-9]+\.?[0-9]*)\s+\n',txt)
	units= re.findall(r'\s+(10\^\d*)bits/sec\s*\n',txt)
	if len(BWsRE)==0:
	  BWs=[0]
	else:
	  BWs =convertToMegaNetPerf(BWsRE,units[0])
      else: 
	raise RuntimeError ('Unknown perfType')
      Bws_below100=[]
      if bwLimit!=None:
	Bws_below100=[x for x in BWs if x<1.1*bwLimit]
      else:
	Bws_below100=BWs
      if len(Bws_below100)>0:
	BWAvg=sum(Bws_below100)/len(Bws_below100)
	if perfType=='iperf':
	  DatasStr= re.findall(r'(\d+\.?\d* \w?)Bytes',txt)
	elif perfType=='netperf':
	  DatasStr= re.findall(r'[0-9]+\s+[0-9]+\s+([0-9]+)*\s+[0-9]+\.?[0-9]*\s+[0-9]+\.?[0-9]*\s+\n',txt)
	else: 
	  raise RuntimeError ('Unknown perfType')

	Datas=convertToMega(DatasStr,perfType)
	DataSum=sum(Datas)
	if BWAvg!=0:
	  BWAvgStr=printConvert(BWAvg)
	  DataSumStr=printConvert(DataSum)
	else:
	  BWAvgStr=['0','']
	  DataSumStr=['0','']
      else:
	BWAvg=None 
	DataSum=None 
	BWAvgStr= [None,'']
	DataSumStr= [None,'']

    elif probeType == 'ping':
      BWsRE= re.findall(r'time=(\d+\.?\d* \w?)s',txt)
      Bws_below100 =convertTomili(BWsRE)
      if len(Bws_below100)>0:
	BWAvg=sum(Bws_below100)/len(Bws_below100)
	BWAvgStr=[BWAvg,'m']
      else:
	BWAvg=None 
	BWAvgStr= [None,'']
      DataSumStr= [None,'']
      DataSum=None 
    elif probeType=='UDPRR':
        BWsRE= re.findall(r'[0-9]+\s+[0-9]+\s+[0-9]+\s+[0-9]+\s+[0-9]+\.?[0-9]*\s+([0-9]+\.?[0-9]*)\s+\n',txt)
	BWAvg = 1e3/float(BWsRE[0]) # in milli seconds
	BWAvgStr=[BWAvg,'m']
	DataSumStr= [None,'']
	DataSum=None 
	
    return BWAvg, DataSum, BWAvgStr, DataSumStr

  
def startTCPServer(host,perfType=h.options['perfType']):
    "start host as iperf server"
    if perfType=='none':
      return
    elif perfType=='iperf':
      fileName = 'outTCPServer-{0}.txt'.format(host.name)
      cmd="iperf -s >  {0} &".format(fileName)
    elif perfType=='netperf':
      cmd="netserver -D &"
      fileName=''
    else: 
      raise RuntimeError ('Unknown perfType')
    
    print ( '*** Host %s will be start as a TCP server' % host.name )
    print "cmd={0}".format(cmd)
    out=host.cmd(cmd)
    return fileName
  
  
def startUDPServer(host,perfType=h.options['perfType']):
    "start host as iperf server"
    if perfType=='none':
      return
    elif perfType=='iperf':
      fileName = 'outTCPServer-{0}.txt'.format(host.name)
      cmd="iperf -s -u > {0} &".format(fileName)
      
    elif perfType=='netperf':
      cmd="netserver -D &"
    else: 
      raise RuntimeError ('Unknown perfType')
    
    print ( '*** Host %s will be start as a UDP server' % host.name )
    print "cmd={0}".format(cmd)
    host.cmd( cmd )
    return fileName	
  
def chooseBW(bwType):
  # bw flows distribution in DC according to DCTCP paper
  #bw=''
  if bwType=='mice':
    # query traffic (mice 2KB to 20KB in size). Use till 32KB according to DeTail paper
    bw=[30,2,'K'] # high-low . low
  elif bwType=='medium':
    # delay sensitive short messages (100KB to 1MB)
    bw=[900,100,'K'] # high-low . low
  elif bwType=='elephant':
    # throughput sensitive long flows (1MB to 100MB)
    bw=[99,1,'M'] # high-low . low
  else:
    raise RuntimeError ('Unknown bwType')

  return bw

  
  
def startProbeClient( client, server,data,probeType,seconds,simName=None,perfType=h.options['perfType']):
    "start host as client of server. sends iperf continuously "
    if perfType=='none':
      return
    filename = 'client-{3}probe-{0}-{1}-{2}.txt'.format(client.name,simName,h.options['fwMode'],probeType)
    if probeType == 'tcp' or probeType == 'udp' :
      if perfType=='iperf':
	
	if probeType == 'udp':
	  cmd = 'iperf -c %s  -u -n 5120K > %s' % (server.IP() ,filename)
	elif probeType =='tcp':
	  cmd = 'iperf -c %s  -n 512K > %s' % (server.IP() ,filename)
	else:
	  raise RuntimeError ('Unknown probeType type: {0}'.format(probeType))
	
      elif perfType=='netperf':
	cmd='netperf -H %s -l %s > %s '% (server.IP() ,seconds, filename)  
      else: 
	raise RuntimeError ('Unknown perfType')
    elif probeType == 'ping':
      cmd='ping {0} -c 100 > {1}'.format(server.IP() ,filename)
    elif probeType=='UDPRR':
      cmd='netperf -H %s -t UDP_RR > %s '% (server.IP(), filename)  
  
    print ( '*** Host %s  will be %s-Probe client of: %s with flow of: %s-%s %sB' %  (client.name,probeType,server.name,data[1],data[1]+data[0],data[2]))
    print "cmd={0}".format(cmd)
    client.cmd( cmd )
    return filename
  
  
def startTCPClient( client, server,data,seconds,simName=None):
    "start host as client of server. sends iperf continuously "
    #print data
    #wait = raw_input("PRESS ENTER TO CONTINUE ...") 
    filename = 'client-{0}-{1}-{2}.txt'.format(client.name,simName,h.options['fwMode'])
    if h.options['perfType']=='iperf':
      if h.options['perfContraint']==  'time':
	cmd='iperf -c %s -t %s > %s &' % (server.IP() ,seconds ,filename) # by time
      elif h.options['perfContraint']==  'data':
	cmd='iperf -c %s -n %s%s > %s &' % (server.IP() ,data[0],data[2] ,filename) # by data
      
    elif h.options['perfType']=='netperf':
      if h.options['perfContraint']==  'time':
	cmd='netperf -H %s -l %s > %s &'% (server.IP() ,seconds, filename)  
      elif h.options['perfContraint']==  'data':
	cmd='netperf -H %s -- -m %s%s > %s &'% (server.IP() ,data[0],data[2], filename)  
    else: 
      raise RuntimeError ('Unknown perfType')

    print ( '*** Host %s  will be TCP client of: %s with flow of: %s-%s %sB' %  (client.name,server.name,data[1],data[1]+data[0],data[2]))
    print "cmd={0}".format(cmd)
    client.cmd( cmd )
    return filename
    
    
def startUDPClient( client, server,data,bw,seconds,simName=None):
    "start host as client of server. sends iperf continuously "
    filename = 'client-{0}-{1}-{2}.txt'.format(client.name,simName,h.options['fwMode'])
    bwNum=re.findall(r'(\d+)',bw)
    if h.options['perfType']=='iperf':
      if h.options['perfContraint']==  'time':
	cmd='iperf -c %s -u -t %s > %s &' % (server.IP() ,seconds ,filename) # by time
      elif h.options['perfContraint']==  'data':
	cmd='iperf -c %s -u -n %s%s > %s &' % (server.IP(),data[0],data[2] ,filename) # by data
      
    elif h.options['perfType']=='netperf':
      
      if h.options['perfContraint']==  'time':
	cmd='netperf -H %s -l %s -t UDP_RR >> %s &'% (server.IP() ,seconds, filename)  
      elif h.options['perfContraint']==  'data':
	cmd='netperf -H %s -t UDP_RR -- -m %s%s > %s &'% (server.IP() ,data[0],data[2], filename) 
    else: 
      raise RuntimeError ('Unknown perfType')
    
    print ( '*** Host %s  will be UDP client of: %s with flow of: %s-%s %sB and bandwidth of %sbit/sec' %  (client.name,server.name,data[1],data[1]+data[0],data[2],bw))
    print "cmd={0}".format(cmd)
    client.cmd( cmd )
    return filename
    
      

def getSegmentsSentOut(host):
    netstatOut=host.cmd('netstat -s | grep send') 
    return int(re.findall(r'(\d+) segments',netstatOut)[0])
		

def collectSwitchStat(switches):
  # collect switch statistics by dump-ports
  finalMsg=''
  for s in switches:
	msg = str(s) + ": 	\n"
	for i in range(len(s.intfs)):
	  if str(s.intfs[i])!='lo':
	    switch=re.findall(r'(s\d+)-',str(s.intfs[i]))
	    port=re.findall(r'-eth(\d+)',str(s.intfs[i]))
	    dumpPortscmdStr="{0}{1} {2}".format(h.ofctlCmd['dumpPortsheader'],switch[0],port[0])
	    p = subprocess.Popen(dumpPortscmdStr, shell=True, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	    (stdout, stderr) = p.communicate() 
	    msg = msg + stdout
	finalMsg = finalMsg + msg
  return finalMsg

  
def enforsdn_eval( t,n,topologyName,seconds,dropQueue=0,dirName=None):
    "iperf clients -> servers accroding to trafficMatrix in header.py"
    # Create network and identify subnets
    topo=t
    net=n
    repeat = 0
    resultsByload={}
    fw=net.get("fw")
    numofPackets={}
    numofPackets['Process']=0
    numofPackets['Allow']=0
    numofPackets['Deny']=0
    hosts = net.hosts
    hostsNames=[]
    switchesNames=[]
    
    for i in xrange(len(hosts)):
      hostsNames.append(hosts[i].name)
        
    switches=net.switches
    for i in xrange(len(switches)):
      switchesNames.append(switches[i].name)
        
    links = {}
    linksbw={}
    
    for s in net.switches +net.hosts:
	linksbw[str(s)]={}
	links[str(s)]={}
	for i in range(len(s.intfs)):
		if s.intfs[i].link:
			n, tmp = str(s.intfs[i].link.intf1).split("-")
			bw = s.intfs[i].link.intf1.params['bw']
			bw=100
			if n==str(s):
				n, tmp = str(s.intfs[i].link.intf2).split("-")
				bw = s.intfs[i].link.intf1.params['bw']
			links[str(s)][str(n)]=str(i)
			linksbw[str(s)][str(n)]=str(bw)
	
    totalRules=len(h.denyRules)+len(h.allowRules)+len(h.processRules)
    
    flowsEnforcedRulesByFW=[ 0 for x in range(len(hosts)-1) ] 
    for client,server,protocol in h.trafficMatrix:
      flowsEnforcedRulesByFW[client-1]=1
    
    fw= net.get("fw")
    lenSwitch=len(net.switches)
    fwMode=h.options['fwMode']
    outputFileName = 'setShortestPath.in'
    my_shelf=shelve.open(outputFileName,'n')
    keys=['hostsNames','switchesNames','links','fwMode','lenSwitch']
    
    for key in keys:
      my_shelf[key]=locals()[key]

    if h.options['topology']=='Fat-Tree':
      globalkeys=['M','W','fanout','fireWallIP']
      for key in globalkeys:
	my_shelf[key]=globals()[key]
	
    my_shelf.close()

    topology = ''.join([topologyName,'-forRunning.txt'])
    setRoute = shortestPathFlows_ft(topology, False)

    setRoute.setDefaultFlowsFromFW()
    segments_sent_out_initial={}
    OFRules={}
    OFRules['Process']=0
    OFRules['Deny']=0
    OFRules['Allow']=0
    
    if h.options['fwMode']=='normal':

      for rule in h.rules['Process']:
	includeFw=1
	numofOFcmds=setRoute.setDefaultFlowsToFW(rule[0],includeFw,priority=10)
	OFRules['Process'] = OFRules['Process'] + numofOFcmds
      OFRules['Process'] = OFRules['Process']*2
      
      for rule in h.rules['Deny']:
	includeFw=0
	numofOFcmds=setRoute.setDefaultFlowsToFW(rule[0],includeFw,priority=10)
	OFRules['Deny'] = OFRules['Deny'] + numofOFcmds
      OFRules['Deny'] = OFRules['Deny']*2
      
      for rule in h.rules['Allow']:
	includeFw=1
	numofOFcmds=setRoute.setDefaultFlowsToFW(rule[0],includeFw,priority=10)
	OFRules['Allow'] = OFRules['Allow'] + numofOFcmds
      OFRules['Allow'] = OFRules['Allow']*2
      
    elif h.options['fwMode']=='advanced':

      for rule in h.rules['Process']:
	includeFw=1
	numofOFcmds=setRoute.setDefaultFlowsToFW(rule[0],includeFw,priority=10)
	OFRules['Process'] = OFRules['Process'] + numofOFcmds
      OFRules['Process'] = OFRules['Process']*2
      
      for rule in h.rules['Allow']:
	numofOFcmds = setRoute.setDirectFlow(rule[0])
	OFRules['Allow'] = OFRules['Allow'] + numofOFcmds
      
      for rule in h.rules['Deny']:
	OFRules['Deny'] = OFRules['Deny'] + 1
      
    elif h.options['fwMode']=='none':

      for rule in h.rules['Allow']:
	numofOFcmds = setRoute.setDirectFlow(rule[0])
	OFRules['Allow'] = OFRules['Allow'] + numofOFcmds

      for rule in h.rules['Process']:
	numofOFcmds = setRoute.setDirectFlow(rule[0])
	OFRules['Process'] = OFRules['Process'] + numofOFcmds

      for rule in h.rules['Deny']:
	OFRules['Deny'] = OFRules['Deny'] + 1
	
    else:
      raise RuntimeError('unknown fwType:{0}'.format(h.options['fwMode']))

    if h.options['runMode']=='mn-console':
      seconds=18000
    
    if h.options['xAxis']=='Load':
      runOver=udpBWs
    elif h.options['xAxis']=='UDP/TCP':
      runOver=[0]

    for u in runOver:
      results={}
      serversHostIndx=[]
      clientsHostIndx=[]
      fileNames={}
      clientsfileNames={}
      
      if h.options['xAxis']=='Load':
	udpBW = u
      elif h.options['xAxis']=='UDP/TCP':
	udpBW = udpBWs[0]

      trafficMatrix = h.trafficMatrix
      if udpBW>0:
	# Start iperf servers and clients
	print '*** start UDP connections'
	
	# generate network load congestion 
	for client,server,protocol in trafficMatrix:
	  skip=0
	  clientsHostIndx.append(client-1)
	  serversHostIndx.append(server-1)
	  if protocol[0] == 'probe-wo-fw' or protocol[0] == 'probe-fw' : # this is the tcp probes
	    skip = 1

	  if h.options['fwMode']=='none':
	    #and if flow is dropped:
	    for denyRule in h.denyRules:
	      if( (denyRule[0]=="10.0.0."+str(client) or denyRule[0]=="*") and (denyRule[1]=='*' or denyRule[1]=="10.0.0."+str(server)) ):
		skip=1
	  if skip==1:
	    continue	
	  
	  for denyRule in h.denyRules:
	    if( h.options['fwMode']=='none' and (denyRule[0]=="10.0.0."+str(client) or denyRule[0]=="*") and (denyRule[1]=='*' or denyRule[1]=="10.0.0."+str(server)) ):
	      raise RuntimeError ('Starting Denied flow in None Firewall mode!')
	  

	  data=chooseBW(protocol[1])
	  
	  if protocol[0].lower()=='tcp':
	    print '*** start TCP: client: {0} & server: {1}'.format(client,server-1)
	    startTCPServer(hosts[server-1])
	    if topologyType=='Fat-Tree':
	      netstatOut=hosts[client].cmd('netstat -s | grep send') 
	      segments_sent_out_initial[client]= getSegmentsSentOut(hosts[client])
	      clientsfileNames[client]=startTCPClient( hosts[client], hosts[server-1],data,seconds,simName=dirName)
	    
	  elif protocol[0].lower()=='udp':
	    print '*** start UDP: client: {0} & server: {1}'.format(client,server-1)
	    startUDPServer(hosts[server-1])
	    if 1: #len(udpBWs)>1: # load simulations....
	      udpBW_str=str(udpBW)+'M'
	      if topologyType=='Fat-Tree':
		segments_sent_out_initial[client]= getSegmentsSentOut(hosts[client])
		clientsfileNames[client]=startUDPClient( hosts[client], hosts[server-1],data,udpBW_str,seconds,simName=dirName)
	  else:
	    raise error (["Unknown protocol in trafficMatrix:",[client,server,protocol]])
      
      f=open('./'+resultsFileName, 'w+')
      if h.options['runMode']!='mn-console':
	print '*** Run for {0} seconds'.format(10) 
	time.sleep(10)
      
      tcpprobeClients={}
      for client,server,protocol in trafficMatrix:
	if (protocol[0] == 'probe-fw' and probeRule =='probe-fw') or (protocol[0] == 'probe-wo-fw' and probeRule =='probe-wo-fw') : # this is the tcp probes  
	  print 'connect {0} to {1}'.format(hosts[client-1],hosts[server-1])
	  if h.options['runMode']!='mn-console':
	    if h.options['probeType']=='UDPRR':
	      startTCPServer(hosts[server-1],perfType='netperf')
	    elif h.options['probeType']=='udp':
	      fileNames[server-1]=startUDPServer(hosts[server-1],perfType=h.options['probTool'])
	    elif h.options['probeType']=='tcp':
	      fileNames[server-1]=startTCPServer(hosts[server-1],perfType=h.options['probTool'])
		
	    time.sleep(30)
	    data=chooseBW(protocol[1])
	    probeTime = 100 
	    print 'start probe client: {0}'.format(h.options['probeType'])
	    if h.options['probeType']=='udp':
	      if topologyType=='Fat-Tree':
		fileNames[client-1]=startProbeClient( hosts[client], hosts[server-1],data,h.options['probeType'],probeTime,simName=dirName,perfType=h.options['probTool']) 
	    else:
	      if topologyType=='Fat-Tree':
		fileNames[client-1]=startProbeClient( hosts[client], hosts[server-1],data,h.options['probeType'],probeTime,simName=dirName,perfType=h.options['probTool']) 
      
	    tcpprobeClients[client-1] = protocol[0]
	  else:
	    CLI(net)
	
      stat=''
      time.sleep(seconds*1.2)
      
      for client,server,protocol in trafficMatrix:
	hostName=hosts[client-1].name
	netstatOut=hosts[client-1].cmd('netstat -s') 
	retransmited=re.findall(r'(\d+) segments retransmited',netstatOut)
	if  client-1 in tcpprobeClients and tcpprobeClients[client-1] ==  'probe-wo-fw' :         
	  filename=fileNames[client-1]
	  readOutputFile(hostName,filename,h.options['probeType'],perfType=h.options['probTool'],simName=dirName)

	  if probeType == 'ping':
	    filename=fileNames[client-1]
	  else:
	    filename=fileNames[server-1]
	    
	  bw, data, bwStr, dataStr = readOutputFile(hostName,filename,h.options['probeType'],perfType=h.options['probTool'],simName=dirName)
	  results['{0}-probe-wo-fw'.format(h.options['probeType'])]={'BW': bw , 'Data': data , 'retransmited': int(retransmited[0])} # bw in Mbit/sec ; data in MBytes ; segments retransmitted
	  #print '{1}-probe-wo-fw: bw={0}'.format(bwStr,h.options['probeType'])
	elif client-1 in tcpprobeClients and tcpprobeClients[client-1] ==  'probe-fw':
	  
	  filename=fileNames[client-1]
	  readOutputFile(hostName,filename,h.options['probeType'],perfType=h.options['probTool'],simName=dirName)
	  
	  if probeType == 'ping':
	    filename=fileNames[client-1]
	  else:
	    filename=fileNames[server-1]
	    
	  bw, data, bwStr, dataStr = readOutputFile(hostName,filename,h.options['probeType'],perfType=h.options['probTool'],simName=dirName)
	  results['{0}-probe-fw'.format(h.options['probeType'])]={'BW': bw , 'Data': data , 'retransmited': int(retransmited[0])} # bw in Mbit/sec ; data in MBytes ; segments retransmitted
	  #print '{1}-probe-fw: bw={0}'.format(bwStr,h.options['probeType'])
	
	else:
	  try:
	    filename=clientsfileNames[client]
	    bw, data, bwStr, dataStr = readOutputFile(hostName,filename,h.options['probeType'],perfType=h.options['perfType'],simName=dirName)
	    segments_sent_out=getSegmentsSentOut(hosts[client-1]) - segments_sent_out_initial[client]
	    ruleType=findRule(client)

	    if h.options['fwMode']=='advanced' and (ruleType=='Deny' or ruleType=='Allow'):
	      numofPackets[ruleType]=numofPackets[ruleType] + 1
	    else:
	      numofPackets[ruleType]=numofPackets[ruleType]+segments_sent_out
	    
	  except:
	    pass
	  
      #os.popen('echo mininet |sudo -S rm client*.txt setShortestPath.in -f')
      os.popen('sudo rm client*.txt setShortestPath.in -f')
      
      for host in hosts:
	  print '*********** Killing host:{0} ***********'.format(host)
	  host.cmd( 'kill -9 %while' )
	  host.cmd( 'kill -9 %iptables' )
      kill_iperf()
      
      results['numofPackets']=numofPackets
      results['OFRules']=OFRules
      results['numHosts']=len(hosts)
      resultsByload[u]=results
      sleepingTime=seconds
      
      if h.options['xAxis']!='UDP/TCP':
	print '************** Clean-up for {0} seconds ***********'.format(sleepingTime)
	time.sleep(sleepingTime)

    #os.popen('echo mininet |sudo -S rm *.txt -f')
    #os.popen('echo mininet |sudo -S rm *.out -f')
    os.popen('sudo rm *.txt -f')
    os.popen('sudo rm *.out -f')

    f.close()
    return resultsByload
    # end elif h.options['runMode']=='auto-iperf' #


if __name__ == '__main__':
    signal.signal(signal.SIGINT,signal_handler)
    startTime=time.time()
    os.popen('sudo mn -c')
    kill_iperf()
    #os.popen('echo mininet |sudo -S rm client*.txt -f')
    os.popen('sudo rm client*.txt -f')
    simTime=300 
    setLogLevel( 'info' )
    #setLogLevel( 'debug' )
    
    
    if len(sys.argv)==2:
      repeatsConf=1
      print '{0}'.format(h.options['topology'])
      if h.options['topology']=='Fat-Tree':
	M=[4,4]
	W=[4,4]
	fanout = 2  
	fanoutConf = fanout
	hostsNum=1
	switchNums=[5] # artificial

	for i in range(len(M)):
	  print 'hostNum({0})*M[{1}]'.format(hostsNum,i)
	  hostsNum=hostsNum*M[i]
	hostsNum=hostsNum*fanout
	print 'hostsNum={0}'.format(hostsNum)
	fireWallIP="10.1.1.{0}".format(hostsNum/2)
	print 'fireWallIP={0}'.format(fireWallIP)
      else:
	raise RuntimeError('Unknown h.options[''topology'']={0}'.format(h.options['topology']))
    
    if h.options['xAxis']=='Load':
      #global udpBWs
      udpBWsConf=arange(0,0.25,0.05) 
      updPrecentages=[0] # artificial
      print 'udpBWsConf={0}'.format(udpBWsConf)
    elif h.options['xAxis']=='UDP/TCP':
      udpBWsConf = [0.01]
      updPrecentages= arange(0,101,10) 
      
      
    filename="".join([h.options['topologyName'],'-forRunning.txt'])

    outputPostfix=re.findall(r'(\w+).',sys.argv[1])[0] 
    simulationTypes=['none','normal','advanced']
    probeTypes=['ping','tcp'] 
    if len(sys.argv)==7:
      runSimulation=1
    elif len(sys.argv)==2:
      runSimulation=0
    else:
      error('Invalid arguments: enforsdn_eval.py <configurationFilename> - for generating inputs or enforsdn_eval.py <configurationFilename> <simulationType> <probeType> - for simulations')

    advanced_results={}
    advanced_avgResults={}
    advanced_maxResults={}
    advanced_minResults={}

    normal_avgResults={}
    normal_maxResults={}
    normal_minResults={}
    normal_results={}

    none_avgResults={}
    none_maxResults={}
    none_minResults={}
    none_results={}
    
    rulesByrepeat={}
    trafficMatrixByrepeat={}
    
    
    # produce topologies, trafficMatrix and rules
    if runSimulation:
      loadInputs(sys.argv[1],dirName=outputPostfix)
      h.options['topology']=topologyType
      print '*** Loading {0} configurations ***'.format(repeats)

      simulationTypes=[sys.argv[2]]
      probeTypes=[sys.argv[3]]
      dropQNum=int(sys.argv[4])
      updPrecentage = int(sys.argv[5])
      probeRule=[sys.argv[6]][0]
    else:
      repeats = repeatsConf
      udpBWs=None
      bwFactor=None
      print '*** Generate {0} configurations ***'.format(repeats)
      directory = './'+outputPostfix
      if not os.path.exists(directory):
	os.makedirs(directory)
      else:
	raise RuntimeError ('folder {0} already exists, remove before generating'.format(outputPostfix))
      
      f=open('./{0}/runCmds'.format(outputPostfix), 'w+')
      cmds=[]
      dropQueue=0
      for repeat in range(1,repeats+1):
	if h.options['xAxis']=='Load':
	  if (h.options['randomTrafficMatrixGenerator'] or h.options['randomMode']=='All'):
	    trafficMatrixByrepeat[repeat]=determinsticTrafficMatrixGenerator(hostsNum,onlyUDP=1,onlyElephant=1)
	  else:
	    trafficMatrixByrepeat[repeat]=h.trafficMatrix
	elif h.options['xAxis']=='UDP/TCP':
	  generationType='detementstic' #'random'
	  trafficMatrixByrepeat[repeat]=TrafficMatrixUDPTCPGenerator(hostsNum,updPrecentages,generationType,onlyElephant=0)
	else:
	  raise RuntimeError ('unknown xAxis option = {0}'.format(h.options['xAxis']))
	# choose randomally two client<->server connections for: tcp without fw ('accept') and tcp with fw ('Process' - no rule needed)
	
	tcpProbeWOFWPairInd=random.randint(0, len(trafficMatrixByrepeat[repeat][0])-1)
	tcpProbeFWPairInd = tcpProbeWOFWPairInd
	while tcpProbeFWPairInd == tcpProbeWOFWPairInd:
	  tcpProbeFWPairInd=random.randint(0, len(trafficMatrixByrepeat[repeat][0])-1)
	i=0
	for u in updPrecentages:
	  trafficMatrixByrepeat[repeat][i][tcpProbeWOFWPairInd][2][0]='probe-wo-fw'
	  trafficMatrixByrepeat[repeat][i][tcpProbeWOFWPairInd][2][1]='mice' 
	  trafficMatrixByrepeat[repeat][i][tcpProbeFWPairInd][2][0]='probe-fw'
	  trafficMatrixByrepeat[repeat][i][tcpProbeFWPairInd][2][1]='mice' 
	  i=i+1
	

	if (h.options['randomRulesGenerator'] or h.options['randomMode']=='All'):
	  [denyRules,allowRules,processRules]=randomRulesGenerator(hostsNum/2,'random',onlyUDP=2) # ***'allDeny' ; 'allAllow' ; 'allProcess' ; 'random'
	  allowRules=setAllowRules(range((hostsNum/2)+1,hostsNum+1),allowRules)
	  
	  for j in [tcpProbeWOFWPairInd]:
	    host=trafficMatrixByrepeat[repeat][0][j][0]
	    ip='10.0.0.{0}'.format(host)
	    proto = 'ip'
	    allowRules.append([ip,'*', '*', '*', proto])

	  for j in [tcpProbeFWPairInd]:
	    host=trafficMatrixByrepeat[repeat][0][j][0]
	    ip='10.0.0.{0}'.format(host)
	    proto = 'ip'
	    processRules.append([ip,'*', '*', '*', proto])

	  
	  rulesByrepeat[repeat] = {'Deny':denyRules, 'Allow' : allowRules, 'Process': processRules}
	  
	  del denyRules, allowRules, processRules

	topologyName=re.findall(r'(\w+).',sys.argv[1])[0]+str(hostsNum)+"-topology" 
	if h.options['topology']=='Fat-Tree':
	  fattree_API.topoCreator(M,W,fanout, "FW", fireWallIP )
	  destination='{0}-forRunning.py'.format(topologyName)
	  shutil.move('generated.py' , destination)
	
	# move topology file to its directory
	source='{0}-forRunning.py'.format(topologyName)
	destination='./{0}/{1}'.format(outputPostfix,source)
	shutil.move(source , destination)
	topologyType = h.options['topology']
	saveInputs(sys.argv[1],dirName=outputPostfix) 
	
	for probeType in probeTypes:
	  for simType in simulationTypes:
	    for updPrecentage in range(len(updPrecentages)):
	      for probeRule in ['probe-fw','probe-wo-fw']:
		#cmd = 'echo mininet | sudo -S python {0} {1} {2} {3} {4} {5} {6}'.format(sys.argv[0],sys.argv[1],simType,probeType,-1,updPrecentage,probeRule)
		cmd = 'python {0} {1} {2} {3} {4} {5} {6}'.format(sys.argv[0],sys.argv[1],simType,probeType,-1,updPrecentage,probeRule)
		cmds.append(cmd)
		f.write(cmd+'\n')  
	os.popen('chmod +x ./{0}/runCmds'.format(outputPostfix))
  
    if runSimulation:
      # run simulations
      for simulationType in simulationTypes:
	for probeType in probeTypes:
	  for repeat in range(1,repeats+1):
	    os.popen('sudo mn -c')
	    resultsFileName='results-loads-{0}-{1}-{2}-{3}-{4}-RAW.out'.format(simulationType,probeType,outputPostfix,updPrecentage,probeRule)
	    os.popen('rm {0} -f'.format(resultsFileName))

	    # load repeat configurations
	    if (h.options['randomRulesGenerator'] or h.options['randomMode']=='All'):
	      #del h.rules, h.denyRules, h.allowRules, h.processRules
	      h.rules = rulesByrepeat[repeat]
	      h.denyRules = h.rules['Deny']
	      h.allowRules = h.rules['Allow']
	      h.processRules = h.rules['Process']
	    
	    if (h.options['randomTrafficMatrixGenerator'] or h.options['randomMode']=='All'):
	      #del h.trafficMatrix
	      h.trafficMatrix=trafficMatrixByrepeat[repeat][updPrecentage]
	      
	    if (h.options['randomTopologyGenerator'] or h.options['randomMode']=='All'):
	      topologyName=re.findall(r'(\w+).',sys.argv[1])[0]+str(hostsNum)+"-topology" 
	    elif h.options['randomTopologyGenerator']==0: 	      
	      pass
	    else:
	      raise Warning ('check topologyName... {0}'.format(topologyName))
	    
	    topologyNameRun='./'+outputPostfix+'/'+topologyName+'-forRunning' 
	    topologyNameRun_tmp="".join([topologyName,simulationType,probeType])
	    # copy + simulationType 
	    shutil.copy("".join([topologyNameRun,'.py']),"".join([topologyNameRun_tmp,'.py']))
	    print 'import {0}'.format(topologyNameRun_tmp)
	    t=__import__(topologyNameRun_tmp)
	    os.remove("".join([topologyNameRun_tmp,'.py']))
	    baseBW = (float(t.hostsLinksBW)/float(hostsNum))
	    udpBWs=[x*baseBW for x in udpBWsConf]
	    
	    if simulationType != 'none':
	      fw= t.net.get("fw")
	    else:
	      pass 

	    h.options['fwMode']=simulationType
	    h.options['probeType']=probeType
	    if simulationType=='normal':
	      normal_results[repeat]=enforsdn_eval( t.myTopo(),t.net,topologyName,seconds=simTime,dropQueue=dropQNum,dirName=outputPostfix)
	    elif simulationType=='advanced':
	      advanced_results[repeat]=enforsdn_eval( t.myTopo(),t.net,topologyName,seconds=simTime,dropQueue=dropQNum,dirName=outputPostfix)
	    elif simulationType=='none':
	      none_results[repeat]=enforsdn_eval( t.myTopo(),t.net,topologyName,seconds=simTime,dropQueue=dropQNum,dirName=outputPostfix)
	    else:
	      raise RuntimeError ('UnKnown simulation Type: {0}'.format(simulationType))
	    time.sleep(30)  

	    outputFileName='output-loads-{0}-{1}-{2}-{3}-{4}-RAW.out'.format(simulationType,outputPostfix,h.options['probeType'],updPrecentage,probeRule)
	    saveResults(outputFileName,keys=['normal_results','advanced_results','none_results'],dirName=outputPostfix)
	    
	    print '*** Total simulation time={0} ***'.format(time.time()-startTime)
	    print '************** Stoping MiniNet ***********'
	    t.net.stop()
	    kill_iperf()
	    dropQNum=dropQNum+2
      if 0:
	if h.options['xAxis']=='Load':
	  
	  if 'normal' in simulationTypes:
	    normal_host_results={}
	    (normal_avgResults,normal_minResults,normal_maxResults)=assignResults(normal_results)
	    for k in normal_avgResults.keys():
	      normal_host_results[k] = {key: value for key, value in normal_avgResults[k].iteritems() if key.startswith("h")}
	      (normal_avgResults[k],normal_minResults[k],normal_maxResults[k])=assignResults(normal_host_results[k])
	  
	  if 'advanced' in simulationTypes:
	    advanced_host_results={}
	    (advanced_avgResults,advanced_minResults,advanced_maxResults)=assignResults(advanced_results)
	    for k in advanced_avgResults.keys():
	      advanced_host_results[k] = {key: value for key, value in advanced_avgResults[k].iteritems() if key.startswith("h")}
	      (advanced_avgResults[k],advanced_minResults[k],advanced_maxResults[k])=assignResults(advanced_host_results[k])

	  if 'none' in simulationTypes:
	    none_host_results={}
	    (none_avgResults,none_minResults,none_maxResults)=assignResults(none_results)
	    for k in none_avgResults.keys():
	      none_host_results[k] = {key: value for key, value in none_avgResults[k].iteritems() if key.startswith("h")}
	      (none_avgResults[k],none_minResults[k],none_maxResults[k])=assignResults(none_host_results[k])
	
	  outputFileName='output-loads-{0}-{1}.out'.format(simulationType,outputPostfix)
	  saveResults(outputFileName,dirName=outputPostfix)

	  
	      
	elif h.options['xAxis']=='Hosts':

	  # save results by hostNum #
	  if 'advanced' in simulationTypes:
	    (advanced_avgResults[hostsNum],advanced_minResults[hostsNum],advanced_maxResults[hostsNum])=assignResults(advanced_results)
	    advanced_host_results = {key: value for key, value in advanced_avgResults[hostsNum].iteritems() if key.startswith("h")}

	    (advanced_avgResults[hostsNum]['hostsAvg'],advanced_minResults[hostsNum]['hostsAvg'],advanced_maxResults[hostsNum]['hostsAvg'])=assignResults(advanced_host_results)
	  if 'normal' in simulationTypes:
	    (normal_avgResults[hostsNum],normal_minResults[hostsNum],normal_maxResults[hostsNum])=assignResults(normal_results)
	    normal_host_results = {key: value for key, value in normal_avgResults[hostsNum].iteritems() if key.startswith("h")}
	    (normal_avgResults[hostsNum]['hostsAvg'],normal_minResults[hostsNum]['hostsAvg'],normal_maxResults[hostsNum]['hostsAvg'])=assignResults(normal_host_results)
	  if 'none' in simulationTypes:
	    (none_avgResults[hostsNum],none_minResults[hostsNum],none_maxResults[hostsNum])=assignResults(none_results)
	    none_host_results = {key: value for key, value in none_avgResults[hostsNum].iteritems() if key.startswith("h")}
	    (none_avgResults[hostsNum]['hostsAvg'],none_minResults[hostsNum]['hostsAvg'],none_maxResults[hostsNum]['hostsAvg'])=assignResults(none_host_results)

	  outputFileName='output-hosts-{0}-{1}.out'.format(hostsNum,outputPostfix)
	  saveResults(outputFileName,hostsNum=hostsNum,dirName=outputPostfix)

  