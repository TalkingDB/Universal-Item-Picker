# -*- coding: utf-8 -*-
# -*- coding: latin-1 -*-
__author__="Atul Tagra<atul@ignitras.com>"
__date__ ="$4 Nov, 2014 9:09:04 PM$"


import csv
import sys
import json
import traceback
import glob
import config as c
import socket
import time

class csvCreator():
    def __init__(self):    
        """
        Constructor function to initialize global variables
        """               
        #Global objects
        self.nodesWriter = ''
        self.relationWriter = ''
        self.alreadyNER = {}
        self.totalNer = 0
        self.alreadyNERList = []
        
        #Universal Nodes data
        self.universalNodes = c.universalNodes
        self.exceptionNodes = [] # Get exception nodes for universal nodes
        self.universalRow = {}
        
        #Main function call
        self.coreCreator()
    
#     @profile        
    def createFiles(self):
        """
        Function to Initialize files in write mode and write first row
        
        Output: int count (number of default entry rows)
        """
        #Initialize file in write mode        
        f1 = open(c.nodeFileName, 'wt')
        f2 = open(c.relationFileName, 'wt')
        f3 = open(c.logFileName, 'wt')
        
        try:
            self.nodesWriter = csv.writer(f1,delimiter='\t')
            self.relationWriter = csv.writer(f2,delimiter='\t')
            self.logWriter = csv.writer(f3,delimiter='\t')
            
            #Create first rows for logs and nodes csv
            self.logWriter.writerow( ('Restaurant Id', 'Items', 'Timetaken') )
            self.nodesWriter.writerow( ('name', 'l:label', 'uid', 'type', 'obtainable', 'command', 'label', 'entity:string_array') )
            self.nodesWriter.writerow( (c.apiConceptSpace, 'ConceptSpace', '', '', '', '', '', '') )
            count = 1
            
            #Create universal nodes in nodes csv
            for n in self.universalNodes:
                self.nodesWriter.writerow( (n, 'Universal', '', '', '', '', '', '') )
                self.universalRow[n] = count
                count += 1
                
            #Create first row in rels csv    
            self.relationWriter.writerow( ('start', 'end', 'type', 'unit', 'value', 'param') )
            
            return count
        except Exception as e:
            print e
    
#     @profile     
    def coreCreator(self):
        """
        Function to create nodes and relations for flat data
        Process properties
        Process NER data
                
        Output: log
        """
        try:
            print("Process Started at ",time.ctime(time.time()))
            
            #Get count of already entered nodes
            count = self.createFiles()
            
            #Get all JSON files of restaurant from config path
            restaurants = glob.glob(c.pathToFiles)
            
            #Restaurant file iterator
            for restaurant in restaurants:
                f = open(restaurant,'r')
                data = json.loads(f.read())
                
                #Output for maintaining logs
                startTime = int(round(time.time() * 1000))
                print "Restaurant ID being processed:",data['unique_value']
                
                #Variables which need to be refreshed for each restaurant
                parentIdCount = {}
                countItem = 0
                
                #Flat data iterator
                for resData in data['data']:
                    
                    #Variable declaration
                    rel = 'says'
                    parent = 0
                    label = ''
                    unit = ''
                    value = ''
                    obtainable = ''
                    name = str((resData['name']).encode('utf8'))
                    name = name.lower()
                    nodeType = resData['type']
                    
                    #Variables initialization for response received from doNER call
                    nodesNER = []
                    relNER = []
                    tokenNode = ''
                    
                    #List to have row id of parent_id in resData which will be used to create relation
                    parentIdCount[(resData['uid']).encode('ascii')] = count
                    
                    #Create first relation for restaurant with concept space
                    if nodeType == 'parent_group':
                        rel = 'says'
                    else:
                        parent = parentIdCount[(resData['parent_id']).encode('ascii')]
                        
                        #Conditional checks for possible node types
                        if nodeType == 'group':
                            rel = 'contains_group'
                        elif nodeType == 'item':
                            countItem += 1
                            rel = 'says'
                            #Commented because not running separate script for NER
                            #label = 'NER_elegible'
                            obtainable = 'True'
                            try:
                                obtainableRet,nodesNER,relNER,tokenNode = self.doNER(name,count)
                            except:
                                print '-'*60
                                traceback.print_exc(file=sys.stdout)
                                print '-'*60
                        elif nodeType == 'option':
                            countItem += 1
                            rel = 'contains_item'
                            #Commented because not running separate script for NER
                            #label = 'NER_elegible'
                            try:
                                obtainableRet,nodesNER,relNER,tokenNode = self.doNER(name,count)
                                if obtainableRet == 'True':
                                    obtainable = 'True'
                            except:
                                print '-'*60
                                traceback.print_exc(file=sys.stdout)
                                print '-'*60
                        elif nodeType == 'option_group':
                            rel = 'contains_group'

                    try:
                        self.nodesWriter.writerow( (name, label, resData['uid'], nodeType, obtainable, '', '', '') )
                    except:
                        self.nodesWriter.writerow( ('', label, resData['uid'], nodeType, obtainable, '', '', '') )
                        print (name).encode('utf8')
                        
                    #Call to function for creating has relation with universal nodes
                    self.processProperties(resData['properties'], count)
                    
                    #Check applied to avoid self relation
                    if parent <> count:
                        self.relationWriter.writerow( (parent, count, rel, unit, value, '') )
                    
                    #Create relation of item with token node with relation token 
                    #if tokenNode not blank
                    if tokenNode:
                        self.relationWriter.writerow( (count, tokenNode, 'token', '', '', '') )
                    
                    count += 1
                    
                    #If nodesNER list is not empty add NER nodes and its relation
                    if nodesNER:
                        for row in nodesNER:
                            self.nodesWriter.writerow(row)
                            count += 1
                        
                        for relRow in relNER:
                            self.relationWriter.writerow( relRow )
                
                #Output for maintaining logs
                endTime = int(round(time.time() * 1000))
                print "Items and options in restaurant", countItem
                timeTaken = (endTime - startTime)/1000
                print "Time taken to insert restaurant", timeTaken, "\n"
                self.logWriter.writerow( (data['unique_value'], countItem, timeTaken) )
            
            #Output for maintaining logs
            print "Number of Nodes in Restaurant:", count
            print "Restaurants:", len(restaurants)
            print "Total NER nodes:", self.totalNer
            #Provide list of currently not present universal nodes
            print json.dumps(self.exceptionNodes)
            print("Process Completed at ",time.ctime(time.time()))
            
        except Exception as e:
            print e
            print "Exception in user code:"
            print '-'*60
            traceback.print_exc(file=sys.stdout)
            print '-'*60
        pass
    
#     @profile 
    def processProperties(self,properties,count):
        """
        Function to process properties and write a list of exceptioNodes if 
        found any
                
        Input : dict properties
                int count of node in nodes.csv
        """
        #Variable declaration
        rel = 'has'
        
        #Properties iterator
        for k,v in properties.iteritems():
            #Add relation with already present nodes or else add them to exceptionNodes list
            if k in self.universalNodes:
                universal = self.universalRow[k]
                if isinstance(v,dict):
                    unit = v['unit']
                    value = v['value']
                else:
                    unit = ''
                    value = v
                
                try:
                    self.relationWriter.writerow( (count, universal, rel, unit, value, '') )
                except:
                    self.relationWriter.writerow( (count, universal, rel, unit, str(value.encode('utf8')), ''))
            else:
                if k not in self.exceptionNodes:
                    self.exceptionNodes.append(k)
    
#     @profile 
    def doNER(self,name,parentNode):
        """
        Function to Attach Token nodes with NER elegible nodes
        Checks if data already present in alreadyNERList and send CP socket request
        if not already present
                
        Input : string name
                string parentNode which is row count in nodes.csv
        
        Output: tuple
            (makeObtainable,nodesNER,relationNER,tokenNode)
        """
        #print name
        count = parentNode
        nodesNER = []
        relationNER = []
        #Check applied for name not blank #2624
        if name:
            #Check if name already in alreadyNERList
            if name not in self.alreadyNERList:
                #Counter for output log
                self.totalNer += 1
                
                #Fetch data from CP socket
                nerData = json.loads(self.commandProcessorHit(name))

                #Variable Declaration
                label = ''    
                makeObtainable = 'False'
                nodeList = []
                
                #CP output nodes iterator
                for node in nerData['nodes']:
                    #Convert entity comma separated to list (old requirement)
                    entity = (node['entity']).split(',')
    
                    #Check applied for making soda items obtainable if exist in obtainableList
                    intersectionList = list(set(entity).intersection(set(c.obtainableList)))
                    if len(intersectionList) > 0:
                        makeObtainable = 'True'
                    
                    nodesNER.append(('', label, '', node['type'], '', node['command'], str((node['label']).encode('utf-8')), node['entity']))
                    count += 1
                    nodeList.append(count)
                
                #CP output links iterator    
                for rel in nerData['links']:
                    if rel.has_key('param'):
                        param = rel['param']
                    else:
                        param = ''
                    relationNER.append((nodeList[rel['source']], nodeList[rel['target']], 'CommandNet>Relation', '', '', param))
                
                tup = (nodeList[0],makeObtainable)
                self.alreadyNERList.append(name)
                self.alreadyNER[name] = tup
                
                return makeObtainable,nodesNER,relationNER,nodeList[0]
            else:
                self.relationWriter.writerow( (parentNode, self.alreadyNER[name][0], 'token', '', '', '') )    
                return self.alreadyNER[name][1],nodesNER,relationNER,self.alreadyNER[name][0]
        else:
            return 'False',[],[],''
    
#     @profile 
    def commandProcessorHit(self,arg):
        """
        Function to hit command processor socket
        to fetch NER response as JSON
        
        Input : string name
        Output: dict buf of type
            {
            'links':{},
            'nodes':{}
            }
        """
        try:
            s = socket.socket()
            s.connect((c.cpUrl, c.cpSocket))
            s.send(arg)
            buf = ''
            #Iterator applied to receive chunks of data over socket
            while True:
                chunk = s.recv(4096)
                if not chunk:
                    break
                else:
                    buf += chunk
                    
            return buf
        except UnicodeDecodeError:
            print arg + ' is a unicode string'
        except Exception as e:
            print e
            print "Exception in user code:"
            print '-'
            traceback.print_exc(file=sys.stdout)
            print '-'
