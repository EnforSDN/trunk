#Licensed Materials - Property of IBM
#(c) Copyright IBM Corp. 2014, 2014 All Rights Reserved
#US Government Users Restricted Rights - Use, duplication 
#or disclosure restricted by GSA ADP Schedule Contract with 
#IBM Corp.

options = {'emulationTime' : 600, # in sec
           'OFCmd': 'ofctl',
           'topologyName': 'topoTest', 
           'runMode': 'auto-iperf', # auto-iperf / mn-console
           'fw-CPUsamples' : 100 ,
           'statCPUinterval' : 5 ,
           'randomMode' : 'All', # All
           'randomRulesGenerator': 0,
           'randomTrafficMatrixGenerator': 0,
           'randomTopologyGenerator': 0,
           'xAxis': 'UDP/TCP', # Load / TCPUDP
           'probeType' : 'udp', # tcp / ping / udp
           'perfType' : 'iperf', # 'netperf / iperf
           'probTool' : 'iperf', # 'netperf / iperf /'none'
           'perfContraint': 'time', # 'time' , 'data'
           'dataFlowSize': 'medium',
           'topology' : 'Fat-Tree' #'Fat-Tree' / 'Random'
           }
           
dpctlCmd={'header' : 'dpctl add-flow tcp:127.0.0.1:',
       'Delheader' : 'dpctl del-flows tcp:127.0.0.1:',
       'timeout': 'idle_timeout=0,hard_timeout=0',
       'dropAction' : 'actions='
       }

ofctlCmd={'header' : 'ovs-ofctl add-flow ',
       'Delheader' : 'ovs-ofctl del-flows ',
       'dumpPortsheader' : 'ovs-ofctl dump-ports ',
       'timeout': 'idle_timeout=0,hard_timeout=0',
       'dropAction' : 'actions='
       }

              
tcpCol={ 'srcIP':[0,'nw_src'],
	    'srcPort':[2,'nw_dst'],
	    'dstIP':[1,'tp_src'],
	    'dstPort':[3,'tp_dst'],
	    'protocol':[4,'dl_type']
	    }

ruleCol={ 'srcIP':0,
	      'srcPort':1,
	      'dstIP':2,
	      'dstPort':3,
	      'protocol':4
	      }

