__author__="Atul Tagra<atul@ignitras.com>"
__date__ ="$15 Nov, 2014 9:09:04 PM$"

import config as c

class obtainableChecker():   
    def __init__(self, data):
        self.n = []
        self.result = self.checkValidity(data)
    
    def checkValidity(self,data):
        temp = data
        ret = []
        nodeCounter = 0
        for node in temp['nodes']:
            if node['type'] == 'hypergraph' and node['command'] == 'CommandNet>AlongWith':
                ret.append(self.checkRelation(temp, nodeCounter))
            nodeCounter += 1
                
        #Check is applied to differentiate between instruction having 'with' in it and not
        if len(ret):
            for x in ret:
                if x:
                    return 'True'
            return 'False'
        else:
            return 'True'
    
    def checkRelation(self, data, source):
        valid = False
        self.getLeafNodes(data, source)
        for node in self.n:
            entity = (node['entity']).split(',')
            #Check applied for making soda items obtainable if exist in obtainableList
            intersectionList = list(set(entity).intersection(set(c.obtainableList)))
            if len(intersectionList) > 0:
                valid = True
        
        return valid
        
    def getLeafNodes(self, data, source):
        for rel in data['links']:
            if rel['source'] == source:
                if 'param' in rel and rel['param'] == 'subject':
                    #nodeToCheck.append(rel['target'])
                    nodeIndex = rel['target']
                    nodeType = data['nodes'][nodeIndex]['type']
                    if nodeType == 'hypergraph':
                        self.getLeafNodes(data, nodeIndex)
                    elif nodeType == 'token':
                        self.n.append(data['nodes'][nodeIndex])