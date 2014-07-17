#Licensed Materials - Property of IBM
#(c) Copyright IBM Corp. 2014, 2014 All Rights Reserved
#US Government Users Restricted Rights - Use, duplication 
#or disclosure restricted by GSA ADP Schedule Contract with 
#IBM Corp.

import shelve
import matplotlib.pyplot as plt
from analyzeResults import analyzeResults
import numpy as np
import sys
from analyzeResults import analyzeResults
import re
import math

def plotGraph(x,xlabel,ylabel,title,fname,*args):
  ""
  "Supported formats: emf, eps, jpeg, jpg, pdf, png, ps, raw, rgba, svg, svgz, tif, tiff."
  #if dirName!=None:
  fig_ratio =0.45
  logMode=0
  dirName = './'+outputPostfix+'/'
  xinch=3
  yinch=0.2*xinch
  figType='png'
  maxY=0
  minY=1e100
  LS=['bo','rs','gh','c+','mx','kD','yv','r<','b>']
  figname='{2}{0}.{1}'.format(fname,figType,dirName)
  if args[0]=='Normal' or args[0]=='Concise' or args[0]=='Concise1' or args[0]=='Concise2' or args[0]=='Normal-log' or args[0]=='Dic':
    if args[0]=='Normal' or args[0]=='Normal-log':
      LS=['g-v','k-.s','b--o','r:^','k-.>','g-D','y-v','r-<','b->']
      if args[0]=='Normal-log':
	logMode=1
    elif args[0]=='Concise':
      LS=['b--o','c:+','k-.s','g-D','y-v','r-<','b->']
    elif args[0]=='Concise1':
      LS=['g-v','r:^','k-.s','b--o','k-.>','g-D','y-v','r-<','b->']
    elif args[0]=='Concise2':
      LS=['k-.s','b--o','k-.>','g-D','y-v','r-<','b->']
    elif args[0]=='Dic':
      LSDIC={}
      LSDIC['No-FW'] = ['b-.o',12,6,3]
      LSDIC['Accept: Reg-FW'] = ['r:>']
      LSDIC['Accept: eSDN-FW'] = ['g-->']
      LSDIC['Process: Reg-FW'] = ['r:^']
      LSDIC['Process: eSDN-FW'] = ['g--^']
    
    for i in range(1,len(args),2):
      if args[0]=='Dic':
	if len(LSDIC[args[i+1]])==1:
	  markersizeV=10
	  linewidthV=3
	  mewV=2
	else:
	  markersizeV=LSDIC[args[i+1]][1]
	  linewidthV=LSDIC[args[i+1]][2]
	  mewV=LSDIC[args[i+1]][3]
	  
	
	plt.plot(x, args[i], LSDIC[args[i+1]][0],label=args[i+1],markersize=markersizeV,linewidth=linewidthV,mew=mewV)
	if len(args)==3:
	  plt.legend(fontsize=12)
	elif len(args)==5:
	  plt.legend(loc=4,fontsize=16)
	elif len(args)==9:
	  plt.legend(loc=4,fontsize=16)
	elif len(args)==13:
	  plt.legend(loc=10, fontsize=16,ncol=2)
	else:
	  plt.legend(loc=4, fontsize=16)

      else:
	plt.plot(x, args[i], LS[(i-1)/2],label=args[i+1],markersize=8)
	if len(args)==3:
	  plt.legend(fontsize=12)
	elif len(args)==5:
	  plt.legend(loc=4,fontsize=16)
	elif len(args)==9:
	  plt.legend(loc=4,fontsize=16)
	elif len(args)==13:
	  plt.legend(loc=10, fontsize=16,ncol=2)
	else:
	  plt.legend(loc=7, fontsize=16)

      maxY=max(max(args[i]),maxY)
      
      minYtmp=min(args[i])
      if not isinstance(minYtmp, float):
	minYtmp=minYtmp[0]
      minY=min(minYtmp,minY)
    
  elif args[0]=='Error':
    if len(args)%4!=0: # include type (args[0])
      raise Exception ("Error: Not a tripled num of input to errorPlotGraph - {0} args".format(len(args)))

    for i in range(1,len(args),3):
      lineStyle=LS[i/3]
      dminimum = np.array([ abs(args[i][j]-args[i+1][j]) for j in xrange(len(args[i]))])
      dmaximum = np.array([ abs(args[i][j]-args[i+2][j]) for j in xrange(len(args[i]))])
      plt.errorbar(x, args[i],yerr=np.vstack((dminimum,dmaximum)),marker=lineStyle[1],mfc=lineStyle[0], mec=lineStyle[0], ms=6, mew=2,capsize=6,linewidth=2,fmt=lineStyle[1])
    
  else:
    raise Exception ("Error: Unknown plot type: {0}".format(args[0]))
  plt.xlim([0, max(x)*1.1])
  
  
  plt.xlabel(xlabel, fontsize=18)
  plt.ylabel(ylabel, fontsize=18,multialignment='center')
  plt.title(title, fontsize=20)
  
  x_percentage = [str(xx)+'%' for xx in x ]
  plt.xticks(x,x_percentage, fontsize=14)
  plt.yticks(fontsize=14)

  if logMode:
    plt.yscale('log')    
    plt.axes().set_aspect(float(max(x)-min(x)) / float(math.log(maxY[0])-math.log(minY)) * 0.2)
  else:
    plt.ylim([0, maxY[0]*1.1])
    minY=0 # required for new yLim
    if float(maxY[0]-minY)!=0:
      plt.axes().set_aspect(float(max(x)-min(x)) / float(maxY[0]-minY) * fig_ratio)

  plt.tight_layout()
  plt.savefig(figname,format=figType)
  plt.savefig('{2}{0}.{1}'.format(fname,'eps',dirName),format='eps')
  plt.close()

def loadResults_LoadRAW(inputFileName,probeType,probeRule,keys=None):
  # load RAW data for Load x-Axis (single simTYpe ONLY). e.g., 'normal_results','advanced_results','none_results'
  my_shelf=shelve.open(inputFileName)
  RAWKeys=keys 
  for key in RAWKeys:
    if key in my_shelf.keys():
      globals()[key]=my_shelf[key]
      simType=re.findall('(\w+)_',key)
      x= eval ('len({0}_results)'.format(simType[0]))    
      if x>0:
	tmp_host_results={}
	exec ('(tmp_avgResults,tmp_minResults,tmp_maxResults)=assignResults({0}_results)'.format(simType[0]))
	loads=[key for key in sorted(tmp_avgResults.keys())]
	if probeRule=='probe-fw':
	  val=[tmp_avgResults[key]['{0}-probe-fw'.format(probeType)]['BW'] for key in sorted(tmp_avgResults.keys())]
	elif probeRule=='probe-wo-fw':
	  val=[tmp_avgResults[key]['{0}-probe-wo-fw'.format(probeType)]['BW'] for key in sorted(tmp_avgResults.keys())] 

  my_shelf.close()
  return val
  


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



if __name__ == '__main__':
  global outputPostfix
  probeRules=['probe-fw','probe-wo-fw']
  if len(sys.argv)!=4:
    sys.exit('Usage: {0} inputData-filename xAxisMode[Load/Hosts/TCPUDP] probeType[tcp/ping]'.format(sys.argv[0]))
  else:
    outputFileName=sys.argv[1] 
    xAxis=sys.argv[2]  
    probeType = sys.argv[3] # 'ping' / 'tcp'
    
    if probeType=='tcp' or probeType=='udp':
      xAxisTitle='TCP Session Throughput \n[Mbit/sec]'
    elif probeType=='ping':
      xAxisTitle='TCP Session RTT [ms]'
    else:
      raise RuntimeError ('Unknown probeType:{0}'.format(probeType))
  
  if xAxis=='TCPUDP': 
    outputPostfix=sys.argv[1] 
    loads=[]
    x=range(0,11)
    simType='normal'
    tcpprobewofwbw_normal=[]
    tcpprobefwbw_normal=[]
    for udpIndex in x:
      
      for probeRule in probeRules:
	outputFileName='./{1}/output-loads-{0}-{1}-{2}-{3}-{4}-RAW.out'.format(simType,outputPostfix,probeType,udpIndex,probeRule)
	val = loadResults_LoadRAW(outputFileName,probeType,probeRule,keys=['normal_results'])
	if probeRule=='probe-fw':
	  tcpprobefwbw_normal.append(val)
	elif probeRule=='probe-wo-fw':
	  tcpprobewofwbw_normal.append(val)
      loads.append(udpIndex)
    
    simType='advanced'
    tcpprobewofwbw_advanced=[]
    tcpprobefwbw_advanced=[]
    for udpIndex in x:
      for probeRule in probeRules:
	outputFileName='./{1}/output-loads-{0}-{1}-{2}-{3}-{4}-RAW.out'.format(simType,outputPostfix,probeType,udpIndex,probeRule)
	val = loadResults_LoadRAW(outputFileName,probeType,probeRule,keys=['advanced_results'])
	if probeRule=='probe-fw':
	  tcpprobefwbw_advanced.append(val)
	elif probeRule=='probe-wo-fw':
	  tcpprobewofwbw_advanced.append(val)

    simType='none'
    tcpprobewofwbw_none=[]
    tcpprobefwbw_none=[]
    for udpIndex in x:
      for probeRule in probeRules:
	outputFileName='./{1}/output-loads-{0}-{1}-{2}-{3}-{4}-RAW.out'.format(simType,outputPostfix,probeType,udpIndex,probeRule)
	val = loadResults_LoadRAW(outputFileName,probeType,probeRule,keys=['none_results'])
	if probeRule=='probe-fw':
	  tcpprobefwbw_none.append(val)
	elif probeRule=='probe-wo-fw':
	  tcpprobewofwbw_none.append(val)

  titleDic={'tcp':'Throughput','ping':'Round Trip Time (RTT)'}
  x=[(100*load)/(len(loads)-1) for load in loads]

  if probeType=='tcp':
    plotGraph(x,'Percentage of UDP connections',xAxisTitle,titleDic[probeType]+' vs. Offered Load ','Compare-All-New-'+probeType,'Dic',tcpprobewofwbw_none,'No-FW',tcpprobewofwbw_normal,'Accept: Reg-FW',tcpprobewofwbw_advanced,'Accept: eSDN-FW',tcpprobefwbw_normal,'Process: Reg-FW',tcpprobefwbw_advanced,'Process: eSDN-FW')
    plotGraph(x,'Percentage of UDP connections',xAxisTitle,titleDic[probeType]+' vs. Offered Load ','Compare-AllNormal-New-'+probeType,'Dic',tcpprobewofwbw_normal,'Accept: Reg-FW',tcpprobefwbw_normal,'Process: Reg-FW')
  elif probeType=='ping':
    plotGraph(x,'Percentage of UDP connections',xAxisTitle,titleDic[probeType]+' vs. Offered Load ','Compare-All-New-'+probeType,'Dic',tcpprobewofwbw_none,'No-FW',tcpprobewofwbw_normal,'Accept: Reg-FW',tcpprobewofwbw_advanced,'Accept: eSDN-FW',tcpprobefwbw_normal,'Process: Reg-FW',tcpprobefwbw_advanced,'Process: eSDN-FW')
    plotGraph(x,'Percentage of UDP connections',xAxisTitle,titleDic[probeType]+' vs. Offered Load ','Compare-AllbutNormal-New'+probeType,'Dic',tcpprobewofwbw_none,'No-FW',tcpprobewofwbw_advanced,'Accept: eSDN-FW',tcpprobefwbw_none,'Process: eSDN-FW')
    
