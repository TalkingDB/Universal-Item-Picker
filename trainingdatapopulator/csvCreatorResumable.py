# -*- coding: utf-8 -*-
# -*- coding: latin-1 -*-
__author__="Atul Tagra<atul@ignitras.com>"
__date__ ="$4 Nov, 2014 9:09:04 PM$"


import csv
import sys
import json
import traceback
import glob
import trainingdatapopulator_config as c
import socket
import time
import pickle
import obtainableChecker

#Added for issue Task#2828
sys.setrecursionlimit(100000000)

#Added for issue Error: field larger than field limit (131072)
csv.field_size_limit(sys.maxsize)

class csvCreator():
    def __init__(self,resume):    
        """
        Constructor function to initialize global variables
        """               
        #Global objects
        self.totalNer = 0
        self.tempAlreadyNER = {}
        self.tempAlreadyNERList = []
        
        self.skipList = []
        self.universalRow = {}
        self.alreadyNER = {}
        self.alreadyNERList = []
        self.resume = False
        
        #Read from file if resuming fetching
        if resume:
            self.resume = True
            files = [[c.skipListFile, 'skiplist'], [c.universalRowFile, 'universalrow'], [c.alreadyNERFile, 'alreadyner'], [c.alreadyNERListFile, 'alreadynerlist']]
            for row in files:
                with open(row[0], 'rb') as f:
                    if row[1] == 'skiplist':
                        self.skipList = pickle.load(f)
                    elif row[1] == 'universalrow':
                        self.universalRow = pickle.load(f)    
                    elif row[1] == 'alreadyner':
                        self.alreadyNER = pickle.load(f)
                    elif row[1] == 'alreadynerlist':
                        self.alreadyNERList = pickle.load(f)
        
        #Unique Id not entered at all
        self.notEntered = []
        
        #ID of current restaurant being entered
        self.unique_id = ''
        
        #Variables for writing nodes and relation
        self.finalNodes = []
        self.finalRels = []
        
        #Universal Nodes data
        self.universalNodes = c.universalNodes
        self.exceptionNodes = [] # Get exception nodes for universal nodes
        
        #Main function call
        self.coreCreator()
    
#     @profile        
    def createFiles(self):
        """
        Function to Initialize files in write mode and write first row
        
        Output: int count (number of default entry rows)
        """
        #Initialize file in write mode        
        with open(c.nodeFileName, 'wt') as f1, \
        open(c.relationFileName, 'wt') as f2:
            try:
                nodesWriter = csv.writer(f1,delimiter='\t')
                relationWriter = csv.writer(f2,delimiter='\t')
                
                #Create first rows for logs and nodes csv
                nodesWriter.writerow( ('name', 'l:label', 'uid', 'type', 'obtainable', 'command', 'label', 'entity:string_array') )
                nodesWriter.writerow( (c.apiConceptSpace, 'ConceptSpace,' + c.apiConceptSpace, '', '', '', '', '', '') )
                count = 1
                
                #Create universal nodes in nodes csv
                for n in self.universalNodes:
                    nodesWriter.writerow( (n, 'Universal', '', '', '', '', '', '') )
                    self.universalRow[n] = count
                    count += 1
                    
                #Create first row in rels csv    
                relationWriter.writerow( ('start', 'end', 'type', 'unit', 'value', 'param') )
                
                return count
            except Exception as e:
                self.exceptionHandler(e)

    def getFileRowCount(self,fileName):
        """
        Function to get row count for csv files
        
        Input: string fileName
        
        Output: count of rows in csv
        """
        with open(fileName, 'r') as f:
            reader = csv.reader(f)
            return len(list(reader))
    
#     @profile        
    def createFilesResumeable(self):
        """
        Function to Initialize files in append mode and write first row
        
        Output: int count (number of default entry rows)
        """   
        try:
            nodeFileRowCount = self.getFileRowCount(c.nodeFileName)

            #One is subtracted to counter header row count
            return nodeFileRowCount - 1
        except Exception as e:
            self.exceptionHandler(e)
    
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
            if len(self.skipList):
                count = self.createFilesResumeable()
            else:
                count = self.createFiles()
            #Get all JSON files of restaurant from config path
            print c.pathToFiles
            restaurants = glob.glob(c.pathToFiles)
            restaurants.sort()
            
            #Restaurant file iterator
            for restaurant in restaurants:
                if restaurant not in self.skipList:
                    f = open(restaurant,'r')
                    data = json.loads(f.read())
                    
                    #Output for maintaining logs
                    startTime = int(round(time.time() * 1000))
                    self.unique_id = str(data['unique_value'])
                    print "Restaurant ID being processed:",data['unique_value']
                    
                    logs = []
                    logs.append("Restaurant ID being processed: " + data['unique_value'])
                    self.writeLog(logs)
                    
                    #Variables which need to be refreshed for each restaurant
                    parentIdCount = {}
                    countItem = 0
                    
                    makeObtainable = False
                    
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
                        tokenNodeList = []
                        
                        #List to have row id of parent_id in resData which will be used to create relation
                        parentIdCount[(resData['uid']).encode('ascii')] = count
                        
                        #Create first relation for restaurant with concept space
                        if nodeType == 'parent_group':
                            rel = 'says'
                            label = 'ParentGroup'
                        else:
                            parent = parentIdCount[(resData['parent_id']).encode('ascii')]
                            
                            #Conditional checks for possible node types
                            if nodeType == 'group':
                                rel = 'contains_group'
                                label = 'Group'
                                
                            elif nodeType == 'item':
                                countItem += 1
                                rel = 'says'
                                #Commented because not running separate script for NER
                                label = 'Item,Obtainable,' + name.replace(",", "&comma;")
                                obtainable = 'True'
                                try:
                                    obtainableRet,nodesNER,relNER,tokenNode,tokenNodeList = self.doNER(name,count)
                                    if obtainableRet == 'True':
                                        makeObtainable = True
                                    else:
                                        makeObtainable = False
                                except Exception as e:
                                    self.exceptionHandler(e)
                            
                            elif nodeType == 'option':
                                countItem += 1
                                rel = 'contains_item'
                                #Commented because not running separate script for NER
                                label = 'Option,' + name.replace(",", "&comma;")
                                try:
                                    obtainableRet,nodesNER,relNER,tokenNode,tokenNodeList = self.doNER(name,count)
                                    if makeObtainable:
                                        obtainable = 'True'
                                        label = label + ',Obtainable'
                                except Exception as e:
                                    self.exceptionHandler(e)
                            
                            elif nodeType == 'option_group':
                                rel = 'contains_group'
                                label = 'OptionGroup'
    
                        try:
                            self.finalNodes.append((name, label, resData['uid'], nodeType, obtainable, '', '', ''))
                        except:
                            self.finalNodes.append(('', label, resData['uid'], nodeType, obtainable, '', '', ''))
                            print str(name.encode('utf8'))
                            
                        #Call to function for creating has relation with universal nodes
                        self.processProperties(resData['properties'], count)
                        
                        #Check applied to avoid self relation
                        if parent <> count:
                            self.finalRels.append((parent, count, rel, unit, value, ''))
                        
                        if obtainable:
                            parentGroupNode = parentIdCount[(resData['parent_group']).encode('ascii')]
                            self.finalRels.append((parentGroupNode, count, 'has_obtainable', '', '', ''))
                        
                        #Create relation of item with token node with relation token 
                        #if tokenNode not blank
                        if tokenNode:
                            self.finalRels.append((count, tokenNode, 'token', '', '', ''))
                            
                        if tokenNodeList:
                            for tNode in tokenNodeList:
                                self.finalRels.append((count, tNode, 'has_token', '', '', ''))
                                                   
                        count += 1
                        
                        #If nodesNER list is not empty add NER nodes and its relation
                        if nodesNER:
                            for row in nodesNER:
                                self.finalNodes.append(row)
                                count += 1
                            
                            for relRow in relNER:
                                self.finalRels.append(relRow)
                    
                    #Call to function which will finally write CSV
                    self.finalNodeAndRelWriter(self.tempAlreadyNER, self.alreadyNERList, str(data['unique_value']))
                    
                    #Output for maintaining logs
                    endTime = int(round(time.time() * 1000))
                    print "Items and options in restaurant", countItem
                    timeTaken = (endTime - startTime)/1000
                    print "Time taken to insert restaurant", timeTaken, "\n"
                    
                    logs = []
                    logs.append('INSERTED RESTAURANT INFO')
                    logs.append("Items and options in restaurant " + str(countItem))
                    logs.append("Time taken to insert restaurant " + str(timeTaken))
                else:
                    logs = []
                    logs.append('SKIPPED RESTAURANT INFO')
                    logs.append("Skipped restaurant: " + str(restaurant))
                
                self.writeLog(logs)    
            
            #Output for maintaining logs
            self.finalLogWriter()
            
            logs = []
            logs.append('DATA INSERTION INFO')
            logs.append("Number of Nodes in all Restaurants: " + str(count))
            logs.append("Restaurants: " + str(len(restaurants)))
            logs.append("Total NER nodes: " + str(self.totalNer))
            logs.append(json.dumps(self.exceptionNodes))
            logs.append("#"*120)
            self.writeLog(logs)
            
            print "Number of Nodes in Restaurant:", count
            print "Restaurants:", len(restaurants)
            print "Total NER nodes:", self.totalNer
            #Provide list of currently not present universal nodes
#             print json.dumps(self.exceptionNodes)
            
            print("Process Completed at ",time.ctime(time.time()))
            
        except Exception as e:
            self.exceptionHandler(e)
            
#     @profile
    def writeLog(self,logs):
        """
        Function to write log in log.txt
        
        Input : list logs
        """
        if c.debugging: 
            logFile = open('c.logPath', 'a')
            logFile.write('-'*60 + '\n')
            logFile.write(time.ctime(time.time()) + '\n')
            for log in logs:
                logFile.write(log + '\n')
            logFile.close()
        
    
#     @profile
    def finalNodeAndRelWriter(self,tempDic,tempList,restaurantId):
        """
        Function which will write nodes and rels to respective 
        """
        try:
            with open(c.nodeFileNameTemp, 'wt') as f1, \
            open(c.relationFileNameTemp, 'wt') as f2:
                nodeWriter = csv.writer(f1,delimiter='\t')
                nodeWriter.writerow( ('name', 'l:label', 'uid', 'type', 'obtainable', 'command', 'label', 'entity:string_array') )
                
                relWriter = csv.writer(f2,delimiter='\t')
                relWriter.writerow( ('start', 'end', 'type', 'unit', 'value', 'param') )
                
                for row in self.finalNodes:
                    nodeWriter.writerow(row)
                    
                for relRow in self.finalRels:
                    relWriter.writerow(relRow)
            
            print "Please Don't break at this moment"
                 
            with open(c.nodeFileName, 'a') as wf1, \
            open(c.relationFileName, 'a') as wf2, \
            open(c.nodeFileNameTemp, 'r') as rf1, \
            open(c.relationFileNameTemp, 'r') as rf2:                
                nodeReader = csv.DictReader(rf1,delimiter='\t')
                for rowNode in nodeReader:
                    dictWriter = csv.DictWriter(wf1, fieldnames=['name', 'l:label', 'uid', 'type', 'obtainable', 'command', 'label', 'entity:string_array'], delimiter='\t')
                    dictWriter.writerow(rowNode)
                    
                relReader = csv.DictReader(rf2,delimiter='\t')
                for rowNode in relReader:
                    dictWriter = csv.DictWriter(wf2, fieldnames=['start', 'end', 'type', 'unit', 'value', 'param'], delimiter='\t')
                    dictWriter.writerow(rowNode)
                    
                self.alreadyNERList = self.alreadyNERList + self.tempAlreadyNERList
                self.alreadyNER.update(self.tempAlreadyNER)
                self.skipList.append(c.osPath + restaurantId + '.json')
            print "You can break now"
        except Exception as e:
            self.exceptionHandler(e)
        finally:
            #To empty NER data list and dict
            self.refreshTemp()

#     @profile             
    def exceptionHandler(self,e):
        print e
        print "Exception in user code:"
        print '-'*60
        traceback.print_exc(file=sys.stdout)
        print '-'*60
        self.continueCreator(self.unique_id)

#     @profile            
    def finalLogWriter(self):
        """
        Function to write files in write mode for files required to make
        this operation resumable
        """
        files = [[c.skipListFile, self.skipList], [c.universalRowFile, self.universalRow], [c.alreadyNERFile, self.alreadyNER], [c.alreadyNERListFile, self.alreadyNERList], [c.exceptionListFile, self.notEntered]]
        
        for row in files:  
            with open(row[0], 'wb') as f:
                pickle.dump(row[1], f, pickle.HIGHEST_PROTOCOL)

#     @profile             
    def continueCreator(self,uid):
        """
        Function to resume prefetching automatically and not enter a restaurant
        in list if any exception found in it
        """
        self.notEntered.append(c.osPath + uid + '.json')
        
        self.skipList.append(c.osPath + uid + '.json')
        
        self.refreshTemp()
        
        self.resume = True
        
        logs = []
        logs.append("RESTAURANT NOT ENTERED BECAUSE OF EXCEPTION")
        logs.append(json.dumps(self.notEntered))
        self.writeLog(logs)
       
        self.finalLogWriter()
        
        self.coreCreator()
        
#     @profile             
    def refreshTemp(self):
        """
        Function to refresh lists which are temporarily used
        """
        self.tempAlreadyNERList = []
        self.tempAlreadyNER = {}
        self.finalNodes = []
        self.finalRels = []
            
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
        try:
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
                        self.finalRels.append((count, universal, rel, unit, value, ''))
                    except:
                        self.finalRels.append((count, universal, rel, unit, str(value.encode('utf8')), ''))
                else:
                    if k not in self.exceptionNodes:
                        self.exceptionNodes.append(k)
        except Exception as e:
            self.exceptionHandler(e)
    
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
        try:
            #print name
            count = parentNode
            nodesNER = []
            relationNER = []
            #Check applied for name not blank #2624
            if name:
                #Check if name already in alreadyNERList
                if name not in self.alreadyNERList and name not in self.tempAlreadyNERList:
                    #Counter for output log
                    self.totalNer += 1
                    
                    #Fetch data from CP socket
                    nerData = json.loads(self.commandProcessorHit(name))
    
                    #Variable Declaration  
                    makeObtainable = 'False'
                    nodeList = []
                    tokenNodeList = []
                    
                    #CP output nodes iterator
                    for node in nerData['nodes']:
                        label = ''  
                        #Convert entity comma separated to list (old requirement)
                        entity = (node['entity']).split(',')
                        
                        if node['type'] == 'token':
                            label = 'Token,'+ str(node['entity'])
                        elif node['type'] == 'hypergraph':
                            #TaskId : 3169
                            label = 'Hypergraph'    
                            
                        #Check applied for making soda items obtainable if exist in obtainableList
                        intersectionList = list(set(entity).intersection(set(c.obtainableList)))
                        if len(intersectionList) > 0:
                            makeObtainable = 'True'
                        
#                         nodesNER.append(('', str(label).replace('.',''), '', str(node['type']).replace('.',''), '', str(node['command']).replace('.',''), (str((node['label']).encode('utf-8'))).replace('.',''), node['entity']))
                        nodesNER.append(('', label, '', node['type'], '', node['command'], str((node['label']).encode('utf-8')), node['entity']))
                        count += 1
                        nodeList.append(count)
                        #TaskId:3193
                        if node['type'] == 'token':
                            tokenNodeList.append(count)
                    
                    #CP output links iterator    
                    for rel in nerData['links']:
                        if rel.has_key('param'):
                            param = rel['param']
                        else:
                            param = ''
                        relationNER.append((nodeList[rel['source']], nodeList[rel['target']], 'CommandNet>Relation', '', '', param))
                    
                    #Check applied for verifying if obtainable item in subject Task#3378 
                    if makeObtainable:
                        resValid = obtainableChecker.obtainableChecker(nerData)
                        if resValid.result == 'False':
                            makeObtainable = False
                    
                    tup = (nodeList[0],makeObtainable,tokenNodeList,nodesNER)

#                     import sys
#                     sys.path.append("/usr/lib/python2.7/pysrc")
#                     import pydevd
#                     pydevd.settrace('61.12.32.122', port = 5678)

                    self.tempAlreadyNERList.append(name)
                    self.tempAlreadyNER[name] = tup
                    
                    return makeObtainable,nodesNER,relationNER,nodeList[0],tokenNodeList
                else:
                    if name in self.alreadyNERList:
                        relationNER.append((parentNode, self.alreadyNER[name][0], 'token', '', '', '') )    
                        return self.alreadyNER[name][1],self.alreadyNER[name][3],relationNER,self.alreadyNER[name][0],self.alreadyNER[name][2]
                    elif name in self.tempAlreadyNERList:
                        relationNER.append((parentNode, self.tempAlreadyNER[name][0], 'token', '', '', '') )    
                        return self.tempAlreadyNER[name][1],self.alreadyNER[name][3],relationNER,self.tempAlreadyNER[name][0],self.tempAlreadyNER[name][2]
                        
            else:
                return 'False',[],[],'',[]
        except Exception as e:
            self.exceptionHandler(e)
    
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
            self.exceptionHandler(e)
