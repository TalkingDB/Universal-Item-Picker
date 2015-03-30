__author__="anik"
__date__ ="$15 Sep, 2014 4:30:14 PM$"

import threadhandler
import outputthreadhandler
import Queue
import operator
from GraphLib import index as gl
from UIP.model import finder_model
# from py2neo import neo4j
from database import graphdb
from app import *

import neo4j

Config = Config()
db_url = str(Config.get('Database')['neo4j_path'])



class InstructionParser():
    def __init__(self):
        pass
    
    #@profile
    def parseInstruction(self,node_ids,user_instruction, concept_space):
        connection = neo4j.connect(db_url)

        GraphDatabase = connection.cursor()
        myQueue = Queue.Queue()
        finished_queue = Queue.Queue()
        self.GL = gl.GraphLib() 
        self.GL.G = self.GL.parseGML(user_instruction)
        self.finderModel = finder_model.FinderModel(GraphDatabase)
        all_instruction = self.GL.getInstructions()
#         print "here", all_instruction
#         exit()
        self.all_instruction_labels = []
        """
        for each instruction. create a new thread
        """
        for i in all_instruction:
            myQueue.put(all_instruction[i])
            self.all_instruction_labels.append(all_instruction[i]['label'])
        processed_instruction = []
        while not myQueue.empty():
            instruction = myQueue.get()
            finder_obj = threadhandler.ThreadHandler(node_ids,instruction,myQueue,self.GL,finished_queue)
            finder_obj.start()
#             exit()
#             processed_instruction.append(finder_obj.getData())
            # print processed_instruction
            # exit()
            # print self.getShortlistedParent(processed_instruction)
            # exit()
        myQueue.join()
        while not finished_queue.empty():
            data = finished_queue.get()
#             print data
            if data:
                processed_instruction.append(data)
            finished_queue.task_done()
#         print self.getShortlistedParent(processed_instruction, concept_space)
#         exit()
#         print processed_instruction
#         exit()

        import sys
        sys.path.append("/usr/lib/python2.7/pysrc")
        import pydevd
        pydevd.settrace('61.12.32.122', port = 5678)
        """
        Items found. Find their store details now 
        """
        if processed_instruction:
            return self.getShortlistedParent(processed_instruction, concept_space)
        else:
            return []

    def getShortlistedParent(self, bukets, concept_space):
        myQueue = Queue.Queue()
        finished_queue = Queue.Queue()
        basket = {}
        for buket in bukets:
            for k, v in buket.items():
                if basket.has_key(k):

                    key = k
                    count = basket[key][0] + 1
                    val = basket[key][1] + v

                    del basket[key]
                    basket[key] = (count, val)
                else:
                    basket[k] = (1, v)

        max_value = max(basket.iteritems(), key=operator.itemgetter(1))[1][0]
        store = {}
        
        """
        for each new store, create a new thread
        """
        for parent_id, val in basket.iteritems():
            if val[0]==max_value:
                myQueue.put((parent_id,val))
                
        while not myQueue.empty():
            data = myQueue.get()
            finder_obj = outputthreadhandler.OutputThreadHandler(myQueue, data[0], data[1], concept_space, finished_queue, self.all_instruction_labels)
            finder_obj.start()
        
        myQueue.join()
        while not finished_queue.empty():
            data = finished_queue.get()
            store[data[0]] = data[1]
            finished_queue.task_done()
#         print "here"
#         exit()

        import sys
        sys.path.append("/usr/lib/python2.7/pysrc")
        import pydevd
        pydevd.settrace('61.12.32.122', port = 5678)

        return self.prepareList(store.values())
    
    def prepareList(self,hierarchy):
#         print hierarchy
#         exit()
        for i in hierarchy:
#             print i
            if isinstance(i['children'], dict):
                i['children'] = i['children'].values()
                self.prepareList(i['children'])
            elif isinstance(i['children'], list):
                for v in i['children']:
                    index = i['children'].index(v)
                    # check to see if it has reached to the level where we are not storing key value pair
                    if 'type' not in v:
                        v = v.values()
                        del i['children'][index]
                        self.prepareList(v)
                        (i['children']).insert(index,v)
        return hierarchy
    
    def __prepareNodeOutput(self,node_id,node_information,add_new_keys):
        if node_id in node_information:
            node_information[node_id].update(add_new_keys)
        else:
            for i in node_information:
                self.__prepareNodeOutput(node_id, node_information[i]['children'], add_new_keys)
            
