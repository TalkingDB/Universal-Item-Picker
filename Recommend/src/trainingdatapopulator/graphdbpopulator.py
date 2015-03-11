__author__="Atul Tagra<atul@ignitras.com>"
__date__ ="$29 Sep, 2014 9:51:27 AM$"

import config as c
import json
import explainInstruction as exp
import populatordb as pd
import sys
import traceback

class GraphDbPopulator():
    def __init__(self,data):
        self.pdObj = pd.populatorDb()
        self.explain = exp.explain(self.pdObj.graphdblib)
        self.keyToBeRemoved = ['parent_id']

    def createConceptSpace(self,data):
        """
        Function to check and create concept space if not already present in database
        """
        self.pdObj.concept_space_name = data
        res = self.pdObj.createNodeWithCheck(data,c.csLabel)
        self.pdObj.graphAddLabel(res,c.csLabel)
        self.conceptSpaceNode = res
        return res
    
    def getConceptSpaceNode(self):
        """
        Function to get concept space node id
        """
        self.pdObj.concept_space_name = config.apiConceptSpace
        res = self.pdObj.createNodeWithCheck(data,c.csLabel)
        self.pdObj.graphAddLabel(res,c.csLabel)
        return res

    def createData(self,data,parent):
        """
        Function to process data list provided in input
        """
        res = ''
        for val in data:
            res = self.processPropertiesDict(val,parent,True)
    
    def processPropertiesDict(self,data,parent,child=False):
        """
        Common function to process properties
        dictionary by creating node with attributes in data and
        passing properties to form relation with current node
        """
        try:
            properties = data.pop('properties', None)
            nodeCheck = self.pdObj.nodeCheck(parent,data['uid'])
#            Check applied for making insertion process resumable
            if(nodeCheck == 'True'):
                print str(data['uid']) +' already present'
                return 'False'
            else:
                newNode, = self.pdObj.createNode(data)
                if(child==True):
                    type = data['type']
                    if type == 'group':
                        par = parent
                        rel = 'contains_group'
                    else:
                        res = self.pdObj.getParentNodeId(data['parent_id'])
                        par = res[0].values[0]
                        if type == 'item':
                            rel = 'says'
                        elif type == 'option_group':
                            rel = 'contains_group'
                        elif type == 'option':
                            rel = 'contains_item'
                else:
                    par = parent
                    rel = 'says'
                    self.pdObj.top_parent_name = data['name']
                self.pdObj.createRelation(par,rel,newNode._id)
                self.processProperties(properties,newNode._id)
                return newNode._id
        except Exception as e:
            print e,data,self.pdObj.top_parent_name
            print "Exception in user code:"
            print '-'*60
            traceback.print_exc(file=sys.stdout)
            print '-'*60
    
    def processProperties(self,prop,parent):
        """
        Function to process properties index of all
        data dictionary elements
        """
        for k,v in prop.iteritems():
            self.createProperty(k,v,parent,'has')
            
    def createProperty(self,key,val,parent,relation):
        """
        Function to create property node and add label c.attributeLabel to it
        """
        dicRel = {}
        if isinstance(val,dict) and len(val['unit']) != '':
            dicRel['unit'] = val['unit']
            dicRel['value'] = val['value']
        elif isinstance(val,list):
            dicRel['unit'] = ''
            dicRel['value'] = val
        else:
            dicRel['unit'] = ''
            dicRel['value'] = str(val)

        res = self.pdObj.createNodeWithCheck(key,c.attributeLabel)
        self.pdObj.createRelation(parent,(relation,dicRel),res)
        self.pdObj.graphAddLabel(res,c.attributeLabel)
    
    def initialize(self):
        """
        Main function needed to be called to start this class processing
        """
        try:
            dataToProcess = json.loads(data)
            if isinstance(dataToProcess,dict):
                data = dataToProcess.pop('data', None)
                resConceptSpace = getConceptSpaceNode()
                if resConceptSpace:
                    res = self.processPropertiesDict(data[0],resConceptSpace,False)
                    # To remove first entry from data which is giving us restaurant details in case of foodweasel
                    if res != 'False':
                        print "Top parent added"
                        data.pop(0)
                        # To add whole data into graph db except for parent node and concept space
                        self.createData(data,res)
                    return "Full data added"
                else:
                    raise ValueError('Concept Space not yet created')
            else:
                raise ValueError('Response should be a dictionary '+type(dataToProcess)+' given')
        except Exception as e:
            print e
            print "Exception in user code:"
            print '-'*60
            traceback.print_exc(file=sys.stdout)
            print '-'*60