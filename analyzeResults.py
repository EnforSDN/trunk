#Licensed Materials - Property of IBM
#(c) Copyright IBM Corp. 2014, 2014 All Rights Reserved
#US Government Users Restricted Rights - Use, duplication 
#or disclosure restricted by GSA ADP Schedule Contract with 
#IBM Corp.

import shelve
class analyzeResults:
  
    def clear_values(self,d):
      for key, value in d.iteritems():
	if isinstance(value, dict):
	    self.clear_values(d[key])
	else:
	    d[key]=None
      return d

      
    def get_values(self,d, requested_key):
      for key, value in d.iteritems():
	if key == requested_key:
	  yield value
	  continue
	if isinstance(value, dict):
	  for v in self.get_values(value, requested_key):
	    yield v
	    
    def get_keys(self,d):
      for key, value in d.iteritems():	
	if isinstance(value, dict):
	  for k in self.get_keys(value):
	    yield k
	  continue
	yield key
    
    def average(self,gen):
      l = [x for x in gen]
      if len(l) == 0:
	return float('nan')
      if isinstance(l[0], list):
	return [float(sum([x[i] for x in l]))/len([x[i] for x in l]) for i in xrange(len(l[0]))]
      s=0
      for x in l:
	if x!=None:
	  s=s+x 
      #print 's={0}'.format(s)
      return float(s)/len(l) if len(l) > 0 else float('nan')
      #return float(sum(l))/len(l) if len(l) > 0 else float('nan')

    #def maximum(self,gen):
      #l = [x for x in gen]
      #if len(l) == 0:
	#return float('nan')
      #if isinstance(l[0], list):
	#return [float(sum([x[i] for x in l]))/len([x[i] for x in l]) for i in xrange(len(l[0]))]
      #return float(sum(l))/len(l) if len(l) > 0 else float('nan')

      
    def produce2(self,runs, path, func):
      def get_elements(runs, path):
	#print '-----------runs---------------'
	#print(runs)
	for run in runs.values():
	  #print '-----------run---------------'
	  #print(run)
	  aux = run
	  for x in path:
	    #print '-----------path---------------'
	    #print("x: %s, aux: %s" % (x, str(aux)))
	    aux = aux[x]
	  yield aux
      #l = [x for x in get_elements(runs, path)]
      #print 'get_elements={0}'.format(l)
      return func(get_elements(runs, path))
	
    def init_tree(self,tree, initial_value):
      res = {}
      for key, value in tree.iteritems():
	if isinstance(value, dict):
	  res[key] = self.init_tree(value, initial_value)
	  continue
	if isinstance(value, list):
	  res[key] = [initial_value for _ in value]
	  continue
	res[key] = initial_value
      return res
    
    def get_paths(self,tree):      
      for key, value in tree.iteritems():
	aux = [key]
	if isinstance(value, dict):
	  for path in self.get_paths(value):
	    yield aux + path
	  continue
	yield aux
	
    def assign_to_tree(self,tree, path, value):
      aux = tree
      for x in path[:-1]:
	aux = aux[x]
      aux[path[-1]] = value
   
    def fill_tree(self,runs, tree, func):
      #print '-----------tree---------------'
      #print(tree)
      #print '-----------runs---------------'
      #print(runs)

      for path in [path for path in self.get_paths(tree)]:
	#print '-----------path---------------'
	#print(path)
	self.assign_to_tree(tree, path, self.produce2(runs, path, func))
	#print '-----------done---------------'

      return tree
    # ORIGINAL
    #avg_results = init_tree(results.values()[0], -555)
    #fill_tree(results, avg_results, average)
    #print '-----------avg_results---------------'
    #print avg_results
    
    #host_results = {key: value for key, value in avg_results.iteritems() if key.startswith("h")}
    #avg_hosts = init_tree(host_results.values()[0], -555)
    #fill_tree(host_results, avg_hosts, average)
    #print '-----------avg_hosts---------------'
    #print avg_hosts   
    



#if __name__ == '__main__':
  #filename='dbg.out'
  #key='results'
  #my_shelf = shelve.open(filename)
  #globals()[key]=my_shelf[key]
  #my_shelf.close()
  ##print results
  #averageResults(results)
  
  ## create empty average dictionary
  #avg_results={}
  #avg_results['average']=results[1]
  #avg_results=clear_values(avg_results)

  ## create "flat" average dictionary
  #    avg_results = {key: average(get_values(results, key)) for key in get_keys(results)}
  #    print avg_results
  
  ## WORKING VER: 
  #avg_results = init_tree(results.values()[0], -555)
  #fill_tree(results, avg_results, average)
  #print '-----------avg_results---------------'
  #print avg_results
  
  #host_results = {key: value for key, value in avg_results.iteritems() if key.startswith("h")}
  #avg_hosts = init_tree(host_results.values()[0], -555)
  #fill_tree(host_results, avg_hosts, average)
  #print '-----------avg_hosts---------------'
  #print avg_hosts   