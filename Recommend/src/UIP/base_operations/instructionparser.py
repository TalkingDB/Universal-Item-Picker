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
        all_instruction = self.GL.getInstructions() #TODO SpecialInstruction: verify whether all wordIDs are contained in all_instruction. If they are, it would be easy to loop through each word ID and concatinate special instruction
#         print "here", all_instruction
#         exit()
        self.all_instruction_labels = []
        """
        for each instruction. create a new thread
        """
#         import sys
#         sys.path.append("/usr/lib/python2.7/pysrc")
#         import pydevd
#         pydevd.settrace('61.12.32.122', port = 5678)        
        for i in all_instruction:
            myQueue.put((all_instruction[i],i))
            self.all_instruction_labels.append(all_instruction[i]['label'])
        found_results_grouped_by_instruction = [] #it holds the items and options found from graph data set. along with special instructions and a copy of each instruction user had requested
        
        while not myQueue.empty():
            instruction,instruction_index = myQueue.get()
            finder_obj = threadhandler.ThreadHandler(node_ids,instruction,instruction_index,myQueue,self.GL,finished_queue)
            finder_obj.start()
#             exit()
#             found_results_grouped_by_instruction.append(finder_obj.getData())
            # print found_results_grouped_by_instruction
            # exit()
            # print self.getShortlistedParent(found_results_grouped_by_instruction)
            # exit()
        myQueue.join()
        while not finished_queue.empty():
            found_results, special_instruction, instruction_index = finished_queue.get()
            if found_results:
                found_results_grouped_by_instruction.append((found_results, special_instruction, instruction_index))#TODO SpecialInstruction: Than just data, instruction_index, now we would also be returning special_instruction
                print str(instruction_index) +  ":" + special_instruction
            finished_queue.task_done()

        """
        Sort process_instruction with instruction_index. This way all stores will show their results in the same sort order
        as the user typed his instructions
        """
        found_results_grouped_by_instruction.sort(key=lambda instruction_with_find_results_element:instruction_with_find_results_element[2])
        
        """
        Items found. Find their store details now 
        """       
        if found_results_grouped_by_instruction:
            return self.getShortlistedParent(found_results_grouped_by_instruction, concept_space)
        else:
            return []

    def getShortlistedParent(self, found_results_grouped_by_instruction, concept_space):
        myQueue = Queue.Queue()
        finished_queue = Queue.Queue()
        found_results_grouped_by_store = {}
        special_instructions = []
        
        """
        group items by their store ID
        """
        for tuple_of_bucket_data_and_special_instruction_and_instruction_index in found_results_grouped_by_instruction: #loop for each instruction
            found_results_of_particular_instruction , special_instruction, instruction_index = tuple_of_bucket_data_and_special_instruction_and_instruction_index
            
            # k and key represent 'store ID' or 'restaurant ID' (in context of Foodyo)
            # v and val represent item and option selection data
            for k, v in found_results_of_particular_instruction.items(): #loop for each item found in given instruction
                v = v[:10] # pick only 15 items per store per instruction
                
                for item_index in xrange(0,len(v)):
                    v[item_index]['instruction_index'] = instruction_index
                    
                if found_results_grouped_by_store.has_key(k):

                    key = k
                    count = found_results_grouped_by_store[key][0] + 1 #increment the total number of items found
                    val = found_results_grouped_by_store[key][1] + v # concatinate new item details (in v) with older items details (residing in val)

                    del found_results_grouped_by_store[key]
                    found_results_grouped_by_store[key] = (count, val)
                else:
                    found_results_grouped_by_store[k] = (1, v) # add the first item and its option details
            

            """
            create a new list called 'special_instructions'. Append in it the special_instruction.
            Because we are already sorted by instruction_index hence automatically we will save the
            correspending special_instruction against the instruction_index's list index
            """ 
            special_instructions.append(special_instruction)

        """
        find stores which hax maximum amount of insutrctions met. later this number will be used to filter down store resul
        """
        maximum_items_possible_in_particular_store = max(found_results_grouped_by_store.iteritems(), key=operator.itemgetter(1))[1][0]
        store = {}
        
        """
        for each new store, create a new thread
        """
        stores_count = 0
        for parent_id, val in found_results_grouped_by_store.iteritems():
            if val[0]==maximum_items_possible_in_particular_store: #return only those stores which have met all the instructions
                myQueue.put((parent_id,val))
                stores_count = stores_count + 1
                if stores_count > 50: break 
                
        while not myQueue.empty():
            data = myQueue.get()
            finder_obj = outputthreadhandler.OutputThreadHandler(myQueue, data[0], data[1], concept_space, finished_queue, self.all_instruction_labels)
            finder_obj.start()
        
        myQueue.join()
        while not finished_queue.empty():
            data = finished_queue.get()
            store[data[0]] = data[1]
            finished_queue.task_done()

        return self.prepareList(store.values()), special_instructions
    
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
            
