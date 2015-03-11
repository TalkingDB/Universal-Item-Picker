__author__="Atul Tagra<atul@ignitras.com>"
__date__ ="$6 Oct, 2014 11:18:10 AM$"

from GraphLib import index as gl
import config as c
import socket
import networkx as nx
import sys
import traceback

class explain():
    def __init__(self,graphdblib):
        """
        Constructor recieves graphdblib object as argument
        """
        self.graphdblib = graphdblib
        self.concept_space_name = ''
        
    def commandProcessorHit(self,arg):
        """
        Function to hit command processor socket
        to fetch NER response as GML
        """
        try:
            s = socket.socket()
            s.connect((c.cpUrl, c.cpSocket))
            s.send(arg)
            buf = ''
            while True:
                chunk = s.recv(4096)
                if not chunk:
                    break
                else:
                    buf += chunk
            result = repr(buf)
            return result.strip("'")
        except UnicodeDecodeError:
            print name + ' is a unicode string'
        except Exception as e:
            print e
            print "Exception in user code:"
            print '-'*60
            traceback.print_exc(file=sys.stdout)
            print '-'*60
        
    def checkExplanation(self,name):
        """
        Function to check if node for a particular name already
        present in database or not
        """
        cyp = ('MATCH (d)<-[:token]-()'
            ' MATCH (a)-[*]->(d)'
            ' WHERE a.name = "'+str(self.concept_space_name)+'"'
            ' and d.label = "'+name+'"'
            ' return id(d)')
        res = self.graphdblib.executeQuery(cyp)
        return res
    
    def processExplanation(self,name,concept_space,nodeId):
        """
        Function to create node for Explanation object and connect with parent node
        if already not present in system
        otherwise connect to already present node
        """
        self.concept_space_name = concept_space
        res = self.checkExplanation(name)
        if(len(res) != 0):
            ret = res[0].values[0]
        else:
            glObj = gl.GraphLib()

            gml_string = self.commandProcessorHit(name)

            gml_string = gml_string.replace("&gt;",">")
            glObj.G = glObj.parseGML(gml_string)
            
            # To check the parent element of Explanation graph
            out = {}
            for n, d in glObj.G.in_degree().items():
                if d == 0:
                    out = n
                    
            # To convert comma separated entity to list and also making obtainable for elements in obtainable list
            for n in nx.nodes(glObj.G):
                entity = glObj.G.node[n]['entity']
                entity = (entity).split(',')
                
                intersectionList = list(set(entity).intersection(set(c.obtainableList)))
                if len(intersectionList) > 0:
                    self.makeObtainable(nodeId)

            map = self.graphdblib.jsonToGraph(glObj.jsonOutput())
            ret = map[out]
        
        return ret
    
    def makeObtainable(self,nodeId):
        cyp = ('START n = node(' + str(nodeId) + ')'
            ' SET n.obtainable = "True"')
            
        res = self.graphdblib.executeQuery(cyp)