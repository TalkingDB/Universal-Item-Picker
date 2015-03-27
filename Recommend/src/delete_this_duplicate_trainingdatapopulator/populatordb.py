__author__="Atul Tagra<atul@ignitras.com>"
__date__ ="$6 Oct, 2014 11:51:16 AM$"

from app import *
from py2neo import neo4j, rel
from database import graphdb
import sys
import traceback

Config = Config()

class populatorDb():
    def __init__(self):
        db_url = str(Config.get('Database')['neo4j_path'])
        self.dbObj = neo4j.GraphDatabaseService(db_url)
        self.graphdblib = graphdb.GraphDB(self.dbObj)
        self.concept_space_name = ''
        self.top_parent_name = ''

    def createNode(self,data):
        """
        Function to create node of given dictionary
        """
        outdict = {}
        for k, v in data.iteritems():
            if k == 'name':
                outdict[k.lower()] = v.lower()
            else:
                outdict[k.lower()] = v
        return self.dbObj.create(data)
    
    def createRelation(self,start,relation,end):
        """
        Function to create relation betweeen parent node and child with relation value provided
        """
        return self.dbObj.create(rel(self.dbObj.node(start),relation,self.dbObj.node(end)))
    
    def graphAddLabel(self,nodeId,label):
        """
        Function to add label on given node id
        """
        self.dbObj.node(nodeId).add_labels(label)
        
    def clearDatabase(self):
        """
        Function to clear database
        """
        self.dbObj.clear()
    
    def getParentNodeId(self,val):
        """
        Function to get parent node id in given concept space
        """
        try:
            if(self.concept_space_name != '' and self.top_parent_name != ''):
                cyp = ('Match (a)-[:says]-(b)'
                    'MATCH (b)-[*]->(c)' 
                    'WHERE a.name = "'+str(self.concept_space_name)+'"'
                    ' and b.name = "'+str(self.top_parent_name)+'"'
                    ' and c.uid = "'+str(val)+'"'
                    'return id(c)')
                res = self.graphdblib.executeQuery(cyp)
                return res
            else:
                raise ValueError('Either concept space of top parent name is blank')
        except Exception as e:
            print e
            print "Exception in user code:"
            print '-'*60
            traceback.print_exc(file=sys.stdout)
            print '-'*60
            
    def createNodeWithCheck(self,key,label):
        """
        Function to create node with check if it is already present in system
        or not
        """
        checkDict = {
        'key':'name',
        'value':key
        }
        res = self.graphdblib.checkIfNodeExists(label,checkDict)
        if not res:
            crn, = self.createNode({"name":key})
            ret = crn._id
        else:
            ret = res[0]._id
        
        return ret
    
    def createNodeWithRelation(self,data,parent,relation):
        """
        Function to create node with relation
        """
        ret, = self.createNode(data)
        self.createRelation(parent,relation,ret._id)

        return ret
    
    def nodeCheck(self,parent,uid):
        """
        Function to check if node already exists
        
        @rtype: boolean
        @return: True when node already exists and False in case if it doesn't exist
        """
        try:
            if(parent != ''):
                cyp = 'START n = node(%d) MATCH (n)-[]->(a) WHERE a.uid = "%s" RETURN count(a)' % (parent,uid)
                res = self.graphdblib.executeQuery(cyp)
                if res[0].values[0] > 0:
                    return 'True'
                else:
                    return 'False'
            else:
                raise ValueError('parent cannot be blank')
        except Exception as e:
            print e
            print "Exception in user code:"
            print '-'*60
            traceback.print_exc(file=sys.stdout)
            print '-'*60