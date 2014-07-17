#Licensed Materials - Property of IBM
#(c) Copyright IBM Corp. 2014, 2014 All Rights Reserved
#US Government Users Restricted Rights - Use, duplication 
#or disclosure restricted by GSA ADP Schedule Contract with 
#IBM Corp.

import math
import subprocess
import json
import os
import time
import copy

class Node(object):
    '''node creation.'''

    def __init__(self, firewall,M_,W_, type_ = None, tuple_= None ):
        self.type = type_
        self.tupleDigits =[]
        self.port_counter=0
        self.parents = []
        self.children = []
        self.hosts = [] #------
        self.dpid=""
        if (tuple_ != None):
            for i in range(len(tuple_)):
                self.tupleDigits.append(tuple_[i])
        self.d_=0
        self.M=M_
        self.W=W_
        self.H=len(M_)
        self.fireWall=firewall
        
    def insrtDPID(self, dpid):          #identify the switches equivalent to MAC
        self.dpid= self.dpid+ str(dpid)  
    
    def __str__(self):
        out_str = ''
        out_str+=self.type
        if self.type=='h':
            out_str+=str(self.number)
        else:
            for i in range(self.H+1):
                out_str+=str(self.tupleDigits[i])
        if out_str==self.fireWall:       #overwrite a host to be a firewall
            out_str='fw'
        return out_str
    
    def __repr__(self):
        return str(self.d_)
        
    def getTuple(self):                 #get the tuple ID
        return self.tupleDigits
    
    def getLevel(self):                 #get the level of the switch
        return self.tupleDigits[0]
    
    def isEquale(self, tuple_ ,level):  #Check if equal
        for i in range(1,self.H-level):
            if tuple_[i] != self.tupleDigits[i]:
                return False
        for i in range(self.H-level+1,self.H+1):
            if tuple_[i] != self.tupleDigits[i]:
                return False
        return True
    
    def addParent(self,parent):
        self.parents.append(parent)
        
    def getParents(self):
        return self.parents
    
    def addChildren(self,children):
        self.children.append(children)
        
    def getChildren(self):
        return self.children
    
    def changeType(self,type_):
        self.type= type_
        
    def addXCord(self, cordX_):
        self.cordX= cordX_
    
    def addYCord(self, cordY_):
        self.cordY= cordY_ 
        
    def addNumber(self, number_):
        self.number= number_
        
    def hostNumber(self):
        out_str = ''
        out_str+=self.type       
        out_str+=str(self.number)
        return out_str
    
    def addHostRef(self, port, hosttuple):
        if port not in self.hosts:
            self.hosts.append([]) 
        self.hosts[port].append(hosttuple)

    def getHostRef(self, port):
        return self.hosts[port]

    def calcD(self):
        self.d_=0
        for l in range(0,self.H+1):         #sigma from 1 to H
            tempMul=1
            for i in range(0,l):            #PI multiply from 1 to l-1
                tempMul*= self.M[i]
            self.d_+= self.tupleDigits[self.H-l]*tempMul
        return self.d_       
     
         
    def calcG(self, d):
        l=self.tupleDigits[0]       #extract level
        tempMul=1
        for k in range(0,l):        #PI multiply from 1 to l
            tempMul*=self.W[k]
        if l>0 :
            g=int((d+1)/tempMul)%(self.W[l])+self.M[l-1]+1   #by formula (7) and up port reference added **d+1**
        else :
            g=int((d+1)/tempMul)%(self.W[l])
        return g
    
       
        
class topoCreator(object):
    
    def __init__(self,mList,wList,fanout_,fw="FW",ip="10.1.1.1", rCtrler=False, rCtrlerIP="127.0.0.1", fldir="/home/openflow/floodlight"):
        self.fwType=fw
        self.M=[]
        self.W=[]
        self.W=[1]+wList
        self.M=[fanout_]+mList
        self.fireWall=ip
        self.fwIP=ip
        self.rCntrler=rCtrler
        self.rCtrlerIP=rCtrlerIP
        self.fldir=fldir
        if (fw !=None ):
            self.fwhostNum = self.fwIP.rsplit(".",1)
            self.fireWall='h'+self.fwhostNum[1]            #define which host is the firewall
        self.H=len(self.M)
        self.incindex=0
        self.TUPLE_SIZE = 100
        self.SPACE_SIZE = 10
        self.VERTICAL_SPACE_SIZE = 200
        self.HORIZON_REF = 100
        self.t=[0 for x in range(self.H+1)]

        self.codeStrings()      #define constant strings                                     #createGenFile
        self.openLogs()         #open rules file                                             #createGenFile
        self.createGenerated()  #open generated file                                         #createGenFile                                     
        self.tupleBuild()       #build all tuples with recursion
        self.manageableList()   #create a managable list
        self.createFamily()     #add each tuple parents and children, handles ports
        [hostsNum,switchesNum]=self.writeToFile()      #code generator core                                        #createGenFile
        self.connectEntities()  #define connections between entities                        #createGenFile
        self.jsonHndler()
        self.initFunctions()    #initial phats
        self.closeLogs()        #close logs file 
        self.closeGenFile()     #close Generated.py file                                                               #createGenFile
	self.hostsNum=hostsNum
	self.switchesNum=switchesNum
        
    def openLogs(self):         #open file
        os.popen('sudo rm logs -f')
        self.bf = open('logs','w+')
        
    def closeLogs(self):        #close file
        self.bf.close()   
        
    def incI(self):             #unique number to each flow name
        self.incindex =  self.incindex+1
        return str(self.incindex)
        
    def createGenerated(self,fileName_="generated"):    #create generated file
        self.fileName=fileName_
        os.popen('sudo rm {0}.{1} -f'.format(self.fileName,'py'))
        self.f = open(self.fileName + ".py",'w')
        self.f.write(self.pre_code)
     
    def execute(self, cmd):     #execute cmd of the open VSwitch
        if (self.rCntrler == False):
            openflag=False
            p = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            if self.bf.closed:                  #check if closed
                self.bf = open('logs','a+')
                openflag=True
            self.bf.write(cmd+"\n")
            if openflag==True:
                self.bf.close()

    def executeRC(self, cmd, exedelete=False):  #execute cmd of the controller
        if (self.rCntrler != False):
            openflag=False
            if (exedelete==False):
                cmd="curl -d '{"+cmd+"}' http://"+self.rCtrlerIP+":8080/wm/staticflowentrypusher/json"
            else:
                cmd="curl -X DELETE -d '{\"name\":\""+cmd+"\"}' http://"+self.rCtrlerIP+":8080/wm/staticflowentrypusher/json"
            p = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            if self.bf.closed:
                self.bf = open('logs','a+')
                openflag=True
            self.bf.write(cmd+"\n")
            if openflag==True:
                self.bf.close()

        
##define string to print in file:
#pre code
    def codeStrings(self):  #part of the generated file
        self.pre_code = "# Usage: sudo pythonexmpale.py\n\
\n\
from mininet.topo import Topo\n\
from mininet.net import Mininet\n\
from mininet.node import CPULimitedHost\n\
from mininet.node import RemoteController\n\
from mininet.node import Controller\n\
from mininet.link import TCLink\n\
from mininet.cli import CLI\n\
import string\n\
import os\n\
\n\
class myTopo(Topo):\n\
\tdef __init__(self, **opts):\n\
\t\tTopo.__init__(self, **opts)\n"

#post code        
        self.post_code = "\ndef noneController(a):\n\
\treturn None\n\
\n"

        self.post_codeNoFL = "net = Mininet(topo=myTopo(), link=TCLink, autoSetMacs=True, controller=noneController, listenPort=6634)\n"
        self.post_codeFL = "net = Mininet(topo=myTopo(), link=TCLink, autoSetMacs=True, controller=RemoteController, listenPort=6634)\n"

        self.string_aux1 = "fw.cmd(\"sysctl net.ipv4.ip_forward=1\")\n\
fw.cmd(\"sysctl net.ipv4.conf.all.send_redirects=0\")\n\
fw.cmd(\"sysctl net.ipv4.conf.all.rp_filter=2\")\n\
fw.cmd(\" sudo echo 0 > /proc/sys/net/ipv4/conf/fw-eth0/send_redirects \")\n\
fw.cmd(\" sudo echo 2 > /proc/sys/net/ipv4/conf/fw-eth0/rp_filter \")\n\
fw.cmd(\"ip route flush all\")\n\
fw.cmd(\"ip route add default dev fw-eth0\")\n"


        self.string_aux2 = "for i in net.hosts:\n\
\ti=str(i)\n\
\th=net.get(i)\n\
\tfor dst in net.hosts:\n\
\t\tdst=str(dst)\n\
\t\tif dst==\"fw\":\n\
\t\t\tcontinue\n\
\t\tif dst==i:\n\
\t\t\tcontinue\n\
\t\tn=dst[1:]\n\
\t\th.cmd(\"arp -s 10.0.0.%s 00:00:00:00:00:%02x\" % (n, string.atoi(n)))\n\
#net.interact()\n"

    def tupleBuild(self):   #build the tuple by calculation
        self.r = []
        for h in range (0, self.H+1):
            self.recursion(0,h,0)
            
    def recursion(self,i, l, tcount):
        m = []
        if tcount==0:
            self.t[i]=l
            self.recursion(i+1, l, tcount+1)      
        elif tcount==self.H:
            L= self.M[self.H-i] if l==0 else self.W[self.H-i]
            for j in range (0, L):
                self.t[i]= j
                m.append( Node(self.fireWall,self.M,self.W,'s',self.t) )
            self.r.append(m)

        else:       
            if i<(self.H-l+1) and tcount<(self.H-l+1):
                for j in range (0, self.M[self.H-i]):
                    self.t[i]=j
                    self.recursion(i+1, l, tcount+1)
            else:
                if i==(self.H-l+1) and tcount==(self.H-l+1):
                    i=self.H
                for j in range (0, self.W[self.H-i]):
                    self.t[i]=j
                    self.recursion(i-1, l, tcount+1)      
     
    def manageableList(self):   #creating a managable list

        lst_aux = []
        for i in range(len(self.r)):
            for j in range(len(self.r[i])):
                lst_aux.append(self.r[i][j]) 
        self.tuple = []
        for i in range(self.H+1):
            m = []
            self.tuple.append(m)    
        for j in range(len(lst_aux)):
            self.tuple[lst_aux[j].getLevel()].append(lst_aux[j])
        

    def createFamily(self):                             #connects the topology
        for l in range(self.H):                         #for each layer
            for i in range(len(self.tuple[l])):         #for each entity in layer
                for j in range(len(self.tuple[l+1])):   #for each upper entity
                    if self.tuple[l][i].isEquale(self.tuple[l+1][j].getTuple() ,l):     #if makes the parents rule
                        self.tuple[l][i].addParent(self.tuple[l+1][j])                  # add a parent will add the current as a children of it
                        self.tuple[l+1][j].addChildren(self.tuple[l][i])
                        
        for l in range(1,self.H+1):
            for i in range(len(self.tuple[l])):
                if l==1 :

                    for dm in range(self.M[l-1]):
                        self.tuple[l][i].addHostRef(dm, self.tuple[l][i].getChildren()[dm])
                if l>1 :
                    for dm in range(self.M[l-1]):
                        for dmc in range(self.M[l-2]):
                            for d in self.tuple[l][i].getChildren()[dm].getHostRef(dmc):
                                self.tuple[l][i].addHostRef(dm, d)
                                
#find maximum layer
    def writeToFile(self):          #write to generated.py file
        maxLayer=0
        hostsNum=0
        switchesNum=0
        for l in range(self.H+1):
            maxLayer = len(self.tuple[l]) if len(self.tuple[l])> maxLayer else maxLayer
        self.gifLineSize = (maxLayer-1) * (self.TUPLE_SIZE+self.SPACE_SIZE) + self.TUPLE_SIZE

        currentYcord = self.VERTICAL_SPACE_SIZE * (self.H+1)         
        for l in range(self.H+1):
            layerEntitiesSize = len(self.tuple[l])
            currentLineSize = (layerEntitiesSize-1) * (self.TUPLE_SIZE+self.SPACE_SIZE) + self.TUPLE_SIZE
            spaceFromBorder = (self.gifLineSize - currentLineSize)/2

            for i in range(len(self.tuple[l])):

                self.tuple[l][i].addXCord( self.HORIZON_REF + spaceFromBorder + i*(self.TUPLE_SIZE+self.SPACE_SIZE) )
                self.tuple[l][i].addYCord( currentYcord - l*self.VERTICAL_SPACE_SIZE )
                if l==0:
                    self.tuple[l][i].changeType('h')
                    self.tuple[l][i].addNumber(i+1)
                    if str(self.tuple[0][i])=="fw":
                        ipstr= str(self.fwIP)
                    else:
                        ipstr= "10.0.0."+str(i+1)   
                    self.f.write("\t\t" +str(self.tuple[l][i])+"=self.addHost('"+str(self.tuple[l][i])+"',ip='"+ ipstr+"')" + "  # (x=" + str(self.tuple[l][i].cordX) + ",y=" + str(self.tuple[l][i].cordY)+")\n")
                    hostsNum=hostsNum+1
                else:
                    self.f.write("\t\t" +str(self.tuple[l][i])+"=self.addSwitch('"+str(self.tuple[l][i])+"')" + "  # (x=" + str(self.tuple[l][i].cordX) + ",y=" + str(self.tuple[l][i].cordY)+")\n")
		    switchesNum = switchesNum + 1
	return [hostsNum,switchesNum]


    def connectEntities(self):      #define connections between entities             
        for l in range(self.H):
            for i in range(len(self.tuple[l])):
                    for j in range(len( self.tuple[l][i].getParents() )):
			module=str(self.tuple[l][i])
			if module[0]=='h' or module=='fw': # host or fw
			  bw=1
			else:
			  bw=10
                        self.f.write( "\t\tself.addLink(" + str(self.tuple[l][i]) + "," + str(self.tuple[l][i].getParents()[j]) + ",bw=" + str(bw) + ")\n" )           
        self.f.write(self.post_code)
        if (self.rCntrler!=False):
            self.f.write("#")
        self.f.write(self.post_codeNoFL)
        if (self.rCntrler==False):
            self.f.write("#")
        self.f.write(self.post_codeFL)
        mark=""
        if self.fwType!="FW":
            mark="#"
        self.f.write( mark+"fw = net.get(\"" +"fw"+"\")\n" )
        self.f.write("net.start()\n")
        if self.fwType!="FW":
            self.f.write("\"\"\"\n")
        self.f.write("fw.cmd(\"ifconfig fw-eth0 down\")\n")
        self.f.write( "fw.cmd(\"ifconfig fw-eth0 hw ether 00:11:11:11:11:11 "+str(self.fwIP) + " up\")\n" )
        self.f.write(self.string_aux1)
        if self.fwType!="FW":
            self.f.write("\"\"\"\n")        
        self.f.write(self.string_aux2)
        self.f.write("hostsLinksBW="+str(bw))
    def closeGenFile(self):     #close file
        self.f.close()
    
    def jsonHndler(self):       #parse the json file to get the DPID of the switches
        if os.path.exists('json'):
            os.remove('json')
        cmd = "curl http://"+self.rCtrlerIP+":8080/wm/core/controller/switches/json >> "+os.getcwd()+"/json;"
        p = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        time.sleep(0.5)#wait for the file to be written
        if (os.path.getsize('json') <= 3):  #check if the file not empty
            return
        json_data=open('json')
        data = json.load(json_data)
        json_data.close()  
        
        snum =self.numOfSW()
                 
        for sn in range(snum):                          #parse the json file and build list
            for l in range(1,self.H+1):                 #for each layer
                for i in range(len(self.tuple[l])):     #for each entity in layer
                    if (str(self.tuple[l][i])== str(data[sn]["ports"][0]["name"]).rsplit("-",1)[0]):
                        self.tuple[l][i].insrtDPID(data[sn]["dpid"])

    def defineFlows(self,pathi, inports, outports, fwType, priority=2): #define the flows
        for i in range(len(pathi)):
            for j in range(len(pathi)):
                for s in range(len(pathi[i][j])):
                    last=len(pathi[i][j])
                    if s!=0 and s!=last-1 and i!=j:
                        if str(pathi[i][j][s])!="fw":
                            beforefw=""
                            beforefwFL=""
                            strsrcip= "10.0.0." +str(pathi[i][j][0].calcD()+1)
                            strdstip="10.0.0." + str(pathi[i][j][last-1].calcD()+1)
                            if ((s+1)!=(last-1) and str(pathi[i][j][s+1])=="fw"):  
                                beforefw="mod_dl_dst:00:11:11:11:11:11,"
                                beforefwFL=beforefwFL+"set-dst-mac=00:11:11:11:11:11,"
                            self.execute("sudo ovs-ofctl add-flow " +str(pathi[i][j][s])+" in_port="+str(inports[i][j][s-1]) + ",ip,nw_src="+ strsrcip+ ",nw_dst="+strdstip +",priority="+str(priority) + ",actions="+beforefw+"output:"+str(outports[i][j][s]))
                            self.executeRC("\"switch\": \"" +str(pathi[i][j][s].dpid)+"\", \"name\":\"add-flow-"+self.incI()+"\", \"ether-type\":\"0x0800\", \"priority\":\""+str(priority)+"\", \"src-ip\":\"10.0.0."+ str(pathi[i][j][0].calcD()+1)+"\", \"dst-ip\":\"10.0.0."+ str(pathi[i][j][last-1].calcD()+1)+"\", \"ingress-port\":\""+str(inports[i][j][s-1])+"\", \"active\":\"true\", \"actions\":\""+beforefwFL+"output="+str(outports[i][j][s])+"\"")
                            self.executeRC("\"switch\": \"" +str(pathi[i][j][s].dpid)+"\", \"name\":\"add-flow-"+self.incI()+"\", \"ether-type\":\"0x0806\", \"priority\":\""+str(priority)+"\", \"src-ip\":\"10.0.0."+ str(pathi[i][j][0].calcD()+1)+"\", \"dst-ip\":\"10.0.0."+ str(pathi[i][j][last-1].calcD()+1)+"\", \"ingress-port\":\""+str(inports[i][j][s-1])+"\", \"active\":\"true\", \"actions\":\""+beforefwFL+"output="+str(outports[i][j][s])+"\"")
                                          
    def calcPath(self,sip, dip,inports=[],outports=[]):     #calculate the path of the routes
        l=0
        down=0
        iport=99
        oport=99
        path=[]
    
        if sip==dip:
            path.append(sip)
            return path
    
        while sip != dip:
            if l>0:
                path.append(sip)
            if l==0 :
                path.append(sip)
                t = sip.getParents()[sip.calcG(dip.calcD())]
                if down==0:
                    oport = sip.calcG(dip.calcD())
                    outports.append(oport)
                    iport = t.getChildren().index(sip)
                    inports.append(iport+1)
                sip=t
                l=l+1
            else:
                t=sip
                for dm in range(self.M[l-1]):
                    if dip in sip.getHostRef(dm):
                        oport = dm+1
                        outports.append(oport)
                        t = sip.getChildren()[dm]
                        for up in range(self.W[l-1]):
                            if t.getParents()[up]==sip:
                                if l==1:
                                    iport=up
                                else:
                                    iport = up+self.M[l-2]+1 

                                inports.append(iport)
                        l=l-1
                        down=1
                sip=t    
                if down==0:
                    oport =sip.calcG(dip.calcD())
                    outports.append(oport)
                    t = sip.getParents()[sip.calcG(dip.calcD())-self.M[l-1]-1]
                    iport = t.getChildren().index(sip)+1
                    inports.append(iport)
                    sip=t
                    l=l+1
        
        path.append(dip) 
        return path

#class functions(object):
    def initFunctions(self):        #initialize the routing and paths
        self.inports=[[0 for x in xrange(len(self.tuple[0]))] for x in xrange(len(self.tuple[0]))] 
        self.outports=[[0 for x in xrange(len(self.tuple[0]))] for x in xrange(len(self.tuple[0]))] 
        self.pathi=[[0 for x in xrange(len(self.tuple[0]))] for x in xrange(len(self.tuple[0]))] 
        self.path=[[[] for x in xrange(len(self.tuple[0]))] for x in xrange(len(self.tuple[0]))] 
	self.pathi_direct=[[0 for x in xrange(len(self.tuple[0]))] for x in xrange(len(self.tuple[0]))] 
        self.path_direct=[[[] for x in xrange(len(self.tuple[0]))] for x in xrange(len(self.tuple[0]))] 

        
        self.pathLen=[[0 for x in xrange(len(self.tuple[0]))] for x in xrange(len(self.tuple[0]))] 
        self.dpath=[[[] for x in xrange(len(self.tuple[0]))] for x in xrange(len(self.tuple[0]))] 
        inportstmp=[]
        outportstmp=[]
        
        for isip in range(len(self.tuple[0])):
            sip=self.tuple[0][isip]
            for idip in range(len(self.tuple[0])):
                dip=self.tuple[0][idip]
                del inportstmp[:]
                del outportstmp[:]
                self.pathi_direct[isip][idip]=list(self.calcPath(sip, dip,inportstmp,outportstmp))
                if self.fwType!=None:   #firewall disabled
		  p1=self.calcPath(sip, self.ipToTuple(self.fwIP),inportstmp,outportstmp)
		  if len(p1)!=0:
		      p1.pop()
		  p2=self.calcPath(self.ipToTuple(self.fwIP), dip,inportstmp,outportstmp)
		  self.pathi[isip][idip]=list(p1+p2)
		else:
		  self.pathi=self.pathi_direct

                self.inports[isip][idip]=list(inportstmp)
                self.outports[isip][idip]=list(outportstmp)
                self.pathLen[isip][idip]=len(self.pathi[isip][idip])
                
                for t in self.pathi[isip][idip]: #make the tuple node to be shown as a string
                    self.path[isip][idip].append(str(t))
                for t in self.pathi_direct[isip][idip]: #make the tuple node to be shown as a string
                    self.path_direct[isip][idip].append(str(t))
        
        self.defineFlows(self.pathi, self.inports, self.outports, self.fwType, priority=2)
        self.dpath=copy.deepcopy(self.path)
        
    def setDefaultFlows(self,priority=2): 
        self.defineFlows(self.pathi, self.inports, self.outports, self.fwType, priority)
    def printIndex(self):       #print the topology entities
        for i in range(len(self.tuple[0])):
            if str(self.tuple[0][i])=="fw":
                ipstr= str(self.fwIP)
            else:
                ipstr= "10.0.0."+str(i+1)
            print str(self.tuple[0][i])+": "+ipstr
          
        snum=1
        for l in range(1,self.H+1):                          #for each layer
            for i in range(len(self.tuple[l])):       #for each entity in layer
                print "s"+str(snum)+": "+str(self.tuple[l][i])
                snum=snum+1

    
    def setFlows(self,sip,dip,protocol=None,src_port=0,dst_port=0,priority=30): #define new flows
        s = self.ipToHostNum(sip) 
        d = self.ipToHostNum(dip)
        self.dpath[s][d]=copy.deepcopy(self.path[s][d])
        for i in range(1, len(self.path[s][d])-1):
            if str(self.path[s][d][i])!="fw":
                someStr = "sudo ovs-ofctl add-flow "+str(self.path[s][d][i])+" in_port="+str(self.inports[s][d][i-1]) +",ip"
                someStrFL=""
                if (protocol != None):
                    someStr += ","+str(protocol)
                    someStrFL += ", \"protocol\": \""+str(protocol)+"\""
                someStr += ",nw_src="+str(sip)+",nw_dst="+str(dip)
                someStrFL += ", \"src-ip\":\""+ str(sip)+"\", \"dst-ip\":\""+ str(dip)+"\""
                if (src_port>0):
                    someStr += ",tp_src="+str(src_port)
                    someStrFL += ", \"src-port\":\""+str(src_port)+"\""
                if (dst_port>0):
                    someStr += ",tp_dst="+str(dst_port)
                    someStrFL += ", \"dst-port\":\""+str(dst_port)+"\""
                beforefw=""
                beforefwFL=""               
                if (i+1)!=(len(self.path[s][d])-1) and str(self.path[s][d][i+1])=="fw":
                    beforefw+="mod_dl_dst:00:11:11:11:11:11,"     
                    beforefwFL+="set-dst-mac=00:11:11:11:11:11,"         #TODO complete    
                someStr += ",priority="+str(priority)+",actions="+beforefw+"output:"+str(self.outports[s][d][i])
                someStrFL +=", \"priority\":\""+str(priority)+"\", \"active\":\"true\", \"actions\":\""+beforefwFL+"output="+str(self.outports[s][d][i])+"\""
                if (self.rCntrler == False):
                    self.execute(someStr)
                else:
                    someStrFL1="\"switch\":\"" +str(self.pathi[s][d][i].dpid)+"\", \"name\":\"set-flow-"+self.incI()+ "\", \"ingress-port\":\""+str(self.inports[s][d][i-1]) +"\""+someStrFL+", \"ether-type\":\"0x0800\""
                    self.executeRC(someStrFL1)
                    someStrFL2="\"switch\":\"" +str(self.pathi[s][d][i].dpid)+"\", \"name\":\"set-flow-"+self.incI()+ "\", \"ingress-port\":\""+str(self.inports[s][d][i-1]) +"\""+someStrFL+", \"ether-type\":\"0x0806\""
                    self.executeRC(someStrFL2)
            
    def setFlow(self,sip,src_port=0,dst_port=0,protocol='ip',priority=30): #define direct route for src ip to all dstips
        s = self.ipToHostNum(sip) 
        numofOFcmds = 0
        firstdst = 1
	for idip in range(len(self.path_direct[s])):
	  hostd=self.tuple[0][idip]
	  dip=self.HostNumToip(idip+1)
	  d = idip
	  for i in range(1, len(self.path_direct[s][d])-1):
	      if str(self.path_direct[s][d][i])!="fw":
		  someStr = "sudo ovs-ofctl add-flow "+str(self.path_direct[s][d][i])+" in_port="+str(self.inports[s][d][i-1]) +",ip"
		  someStrFL=""
		  if (protocol != None):
		      someStr += ","+str(protocol)
		      someStrFL += ", \"protocol\": \""+str(protocol)+"\""
		  someStr += ",nw_src="+str(sip)+",nw_dst="+str(dip)
		  someStrFL += ", \"src-ip\":\""+ str(sip)+"\", \"dst-ip\":\""+ str(dip)+"\""
		  if (src_port>0):
		      someStr += ",tp_src="+str(src_port)
		      someStrFL += ", \"src-port\":\""+str(src_port)+"\""
		  if (dst_port>0):
		      someStr += ",tp_dst="+str(dst_port)
		      someStrFL += ", \"dst-port\":\""+str(dst_port)+"\""
		  beforefw=""
		  beforefwFL=""               
		  if (i+1)!=(len(self.path_direct[s][d])-1) and str(self.path_direct[s][d][i+1])=="fw":
		      beforefw+="mod_dl_dst:00:11:11:11:11:11,"     
		      beforefwFL+="set-dst-mac=00:11:11:11:11:11,"         #TODO complete    
		  someStr += ",priority="+str(priority)+",actions="+beforefw+"output:"+str(self.outports[s][d][i])
		  someStrFL +=", \"priority\":\""+str(priority)+"\", \"active\":\"true\", \"actions\":\""+beforefwFL+"output="+str(self.outports[s][d][i])+"\""
		  if (self.rCntrler == False):
		      self.execute(someStr)
		      if firstdst:
			numofOFcmds = numofOFcmds + 1
		  else:
		      someStrFL1="\"switch\":\"" +str(self.pathi_direct[s][d][i].dpid)+"\", \"name\":\"set-flow-"+self.incI()+ "\", \"ingress-port\":\""+str(self.inports[s][d][i-1]) +"\""+someStrFL+", \"ether-type\":\"0x0800\""
		      self.executeRC(someStrFL1)
		      someStrFL2="\"switch\":\"" +str(self.pathi_direct[s][d][i].dpid)+"\", \"name\":\"set-flow-"+self.incI()+ "\", \"ingress-port\":\""+str(self.inports[s][d][i-1]) +"\""+someStrFL+", \"ether-type\":\"0x0806\""
		      self.executeRC(someStrFL2)
		      if firstdst:
			numofOFcmds = numofOFcmds + 1
	  firstdst = 0
	return numofOFcmds
      
    def setDefaultFlowsFromFW(self,protocol='ip',src_port=0,dst_port=0,priority=30): #define direct route for src ip to all dstips
        
        for si in range(len(self.path_direct)):
	  for di in range(len(self.path_direct)):
	    sip=self.path_direct[si][di][0]
	    if sip=="fw":
	      s = si
	      d = di
	      dip = self.HostNumToip(d+1)
	      for i in range(1, len(self.path_direct[s][d])-1):
		  if str(self.path[s][d][i])!="fw":
		      someStr = "sudo ovs-ofctl add-flow "+str(self.path[s][d][i])+" in_port="+str(self.inports[s][d][i-1]) +",ip"
		      someStrFL=""
		      if (protocol != None):
			  someStr += ","+str(protocol)
			  someStrFL += ", \"protocol\": \""+str(protocol)+"\""
		      someStr += ",nw_dst="+str(dip)
		      someStrFL += ", \"dst-ip\":\""+ str(dip)+"\""
		      if (src_port>0):
			  someStr += ",tp_src="+str(src_port)
			  someStrFL += ", \"src-port\":\""+str(src_port)+"\""
		      if (dst_port>0):
			  someStr += ",tp_dst="+str(dst_port)
			  someStrFL += ", \"dst-port\":\""+str(dst_port)+"\""
		      beforefw=""
		      beforefwFL=""               
		      if (i+1)!=(len(self.path[s][d])-1) and str(self.path[s][d][i+1])=="fw":
			  beforefw+="mod_dl_dst:00:11:11:11:11:11,"     
			  beforefwFL+="set-dst-mac=00:11:11:11:11:11,"         #TODO complete    
		      someStr += ",priority="+str(priority)+",actions="+beforefw+"output:"+str(self.outports[s][d][i])
		      someStrFL +=", \"priority\":\""+str(priority)+"\", \"active\":\"true\", \"actions\":\""+beforefwFL+"output="+str(self.outports[s][d][i])+"\""
		      if (self.rCntrler == False):
			  self.execute(someStr)
		      else:
			  someStrFL1="\"switch\":\"" +str(self.pathi[s][d][i].dpid)+"\", \"name\":\"set-flow-"+self.incI()+ "\", \"ingress-port\":\""+str(self.inports[s][d][i-1]) +"\""+someStrFL+", \"ether-type\":\"0x0800\""
			  self.executeRC(someStrFL1)
			  someStrFL2="\"switch\":\"" +str(self.pathi[s][d][i].dpid)+"\", \"name\":\"set-flow-"+self.incI()+ "\", \"ingress-port\":\""+str(self.inports[s][d][i-1]) +"\""+someStrFL+", \"ether-type\":\"0x0806\""
			  self.executeRC(someStrFL2)


    def setDefaultFlowsToFW(self,sip,includeFw,protocol='ip',src_port=0,dst_port=0,priority=30): #define direct route for src ip to all dstips
	numofOFcmds=0
	s = self.ipToHostNum(sip)
	reachFW = 0
	for di in range(len(self.path_direct[s])):
	  if self.path_direct[s][di][len(self.path_direct[s][di])-1]=='fw':
	    dip= self.HostNumToip(di)
	    d = di 
	    for i in range(1, len(self.path_direct[s][d])-1):
		if str(self.path[s][d][i])!="fw":
		    someStr = "sudo ovs-ofctl add-flow "+str(self.path[s][d][i])+" in_port="+str(self.inports[s][d][i-1]) +",ip"
		    someStrFL=""
		    if (protocol != None):
			someStr += ","+str(protocol)
			someStrFL += ", \"protocol\": \""+str(protocol)+"\""
		    someStr += ",nw_src="+str(sip)
		    someStrFL += ", \"src-ip\":\""+ str(sip)
		    if (src_port>0):
			someStr += ",tp_src="+str(src_port)
			someStrFL += ", \"src-port\":\""+str(src_port)+"\""
		    if (dst_port>0):
			someStr += ",tp_dst="+str(dst_port)
			someStrFL += ", \"dst-port\":\""+str(dst_port)+"\""
		    beforefw=""
		    beforefwFL=""               
		    if str(self.path[s][d][i+1])=="fw":
			if includeFw:
			  beforefw+="mod_dl_dst:00:11:11:11:11:11,"     
			  beforefwFL+="set-dst-mac=00:11:11:11:11:11,"         
			  reachFW=1
			else:
			  break
		    someStr += ",priority="+str(priority)+",actions="+beforefw+"output:"+str(self.outports[s][d][i])
		    someStrFL +=", \"priority\":\""+str(priority)+"\", \"active\":\"true\", \"actions\":\""+beforefwFL+"output="+str(self.outports[s][d][i])+"\""
		    if (self.rCntrler == False):
			self.execute(someStr)
			numofOFcmds=numofOFcmds+1
			if reachFW:
			  break
		    else:
			someStrFL1="\"switch\":\"" +str(self.pathi[s][d][i].dpid)+"\", \"name\":\"set-flow-"+self.incI()+ "\", \"ingress-port\":\""+str(self.inports[s][d][i-1]) +"\""+someStrFL+", \"ether-type\":\"0x0800\""
			self.executeRC(someStrFL1)
			someStrFL2="\"switch\":\"" +str(self.pathi[s][d][i].dpid)+"\", \"name\":\"set-flow-"+self.incI()+ "\", \"ingress-port\":\""+str(self.inports[s][d][i-1]) +"\""+someStrFL+", \"ether-type\":\"0x0806\""
			self.executeRC(someStrFL2)
			numofOFcmds=numofOFcmds+1
	return numofOFcmds

            
    def dropFlows(self,sip,dip,protocol=None,src_port=0,dst_port=0,priority=30): #drop flows
        s = self.ipToHostNum(sip) 
        d = self.ipToHostNum(dip)
        someStr = "sudo ovs-ofctl add-flow "+str(self.path[s][d][1])+" in_port="+str(self.inports[s][d][0])+",ip"
        someStrFL="\"switch\":\"" +str(self.pathi[s][d][1].dpid)+"\", \"name\":\"drop-flow-"+self.incI()+"\""
        if (protocol != None):
            someStr += ","+str(protocol)
            someStrFL += ", \"protocol\":\""+str(protocol)+"\""
        someStr += ",nw_src="+str(sip)+",nw_dst="+str(dip)
        someStrFL += ", \"src-ip\":\""+ str(sip)+"\", \"dst-ip\":\""+ str(dip)+"\""
        if (src_port>0):
                someStr += ",tp_src="+str(src_port)
                someStrFL += ", \"src-port\":\""+str(src_port)+"\""
        if (dst_port>0):
                someStr += ",tp_dst="+str(dst_port)
                someStrFL += ", \"dst-port\":\""+str(dst_port)+"\""
        someStr +=",priority="+str(priority)+",actions=drop"
        someStrFL +=", \"priority\":\""+str(priority)+"\", \"active\":\"true\""
        if (self.rCntrler == False):
            self.execute(someStr)
        else:
            self.executeRC(someStrFL)            

        

    def delFlows(self,sip,dip,protocol=None,src_port=0,dst_port=0):     #delete flows
        s = self.ipToHostNum(sip) 
        d = self.ipToHostNum(dip)
        valueslist = []
        for i in range(1, len(self.path[s][d])-1):
            if str(self.path[s][d][i])!="fw":
                someStr = "sudo ovs-ofctl del-flows "+str(self.path[s][d][i])+" ip,in_port="+str(self.inports[s][d][i-1])
                valueslist.append("\"src-ip\":\""+ str(sip))
                valueslist.append("\"dst-ip\":\""+ str(dip))
                if (protocol != None):
                    someStr += ","+str(protocol)
                    valueslist.append("\"protocol\":\""+str(protocol)+"\"")
                someStr += ",nw_src="+str(sip)+",nw_dst="+str(dip)
                if (src_port>0):
                    someStr += ",tp_src="+str(src_port)
                    valueslist.append("\"src-port\":\""+str(src_port)+"\"")
                if (dst_port>0):
                    someStr += ",tp_dst="+str(dst_port)
                    valueslist.append("\"dst-port\":\""+str(dst_port)+"\"")
                if (self.rCntrler == False):
                    self.execute(someStr)
                else:
                    with open('logs') as logfile:
                        for line in logfile:
                            if all(value in line for value in valueslist):
                                se = line.partition("\"name\":\"")[2].partition("\"")[0]
                                self.executeRC(se,exedelete=True)      
                
    def setArp(self,optionalSwitch=None):           #set arp of the flows                                                     
        if (optionalSwitch==None):
            for l in range(1,self.H+1):
                for i in range(len(self.tuple[l])):
                    someStr = "sudo ovs-ofctl add-flow "+str(self.tuple[l][i])+" arp,actions=all"
                    self.execute(someStr)
        else:
            someStr = "sudo ovs-ofctl add-flow "+str(optionalSwitch)+" arp,actions=all"
            self.execute(someStr)
                
    def isFirewall(self):                           #check if this is the firewall
        if (self.fwType == "FW"):
            return True
        else:
            return False
        
    def ipToTuple(self,ip):                         #translate ip to tuple
        hostNum = ip.rsplit(".",1)
        return self.tuple[0][int(hostNum[1])-1]
    
    def ipToHostNum(self,ip):                       #translate ip to host number
        hostNum = ip.rsplit(".",1)
        return int(hostNum[1])-1

    def HostNumToip(self,h):                       #translate ip to host number
	return ''.join(["10.0.0.",str(h)])

    
    def numOfSW(self):                                  #calculate the number of switches
        snum=0                                          
        for l in range(1,self.H+1):                     #for each layer
            for i in range(len(self.tuple[l])):         #for each entity in layer
                snum=snum+1
        return snum
    
    def drawTopo(self):                             #draw the topology MUST have "netEdit.py" in the directory!
        cmd = "sudo python netEdit.py -g -c " + self.fileName + ".py " + self.fileName
        p = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        
