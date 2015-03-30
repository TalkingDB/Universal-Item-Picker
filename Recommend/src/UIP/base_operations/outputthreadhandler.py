'''
Created on 24-Nov-2014

@author: anik
'''

import threading
from UIP.model import finder_model
import neo4j
from app import *

Config = Config()
db_url = str(Config.get('Database')['neo4j_path'])

threadLimiter = threading.BoundedSemaphore(20)

class OutputThreadHandler(threading.Thread):
    def __init__(self, myQueue, parent_id, val, concept_space, finished_queue, all_instruction_labels):
        threading.Thread.__init__(self)
        connection = neo4j.connect(db_url)
        GraphDatabase = connection.cursor()
        self.myQueue = myQueue
        self.cond = threading.Condition()
        self.parent_id = parent_id
        self.val = val
        self.concept_space = concept_space
        self.finished_queue = finished_queue
        self.finderModel = finder_model.FinderModel(GraphDatabase)
        self.all_instruction_labels = all_instruction_labels
        
    #@profile
    def run(self):
        threadLimiter.acquire()
        self.cond.acquire()
        print "Output Thread"
        try :
            store_details = self.process()
            self.finished_queue.put((self.parent_id, store_details))
        except ValueError as e:
            print e
        finally:
            self.myQueue.task_done()
            threadLimiter.release()    
        self.cond.notify()
        self.cond.release()
    
    #@profile
    def process(self):
        store_details, store_properties = self.finderModel.getNodeDetails(self.parent_id)
        store_details['properties'] = store_properties
        all_node_ids = []
        duplicate_node_ids = []
        keys = {}
        duplicate_keys = {}
        add_new_keys = {}
        duplicate_add_new_keys = {}
        found_instructions = []
        
        import sys
        sys.path.append("/usr/lib/python2.7/pysrc")
        import pydevd
        pydevd.settrace('61.12.32.122', port = 5678)        
        
        for node in self.val[1]:
            node_id = node['search_node']['id']
            if node_id in all_node_ids :
                duplicate_node_ids.append(node_id)
                if node_id not in duplicate_keys :
                    duplicate_keys[node_id] = []
                if node_id not in duplicate_add_new_keys :
                    duplicate_add_new_keys[node_id] = []
                duplicate_keys[node_id].append((node['selected_options']).keys())
                duplicate_add_new_keys[node_id].append({
                    'warning': node['warning'],
                    'not_found': node['not_found'],
                    'quantity': node['quantity'] if 'quantity' in node else 1,
                    'instruction' : node['instruction']
                })
            else :
                all_node_ids.append(node_id)
                keys[node_id] = (node['selected_options']).keys()
                add_new_keys[node_id] = {
                    'warning': node['warning'],
                    'not_found': node['not_found'],
                    'quantity': node['quantity'] if 'quantity' in node else 1,
                    'instruction' : node['instruction']
                }
            
            found_instructions.append(node['instruction'])
        not_found_instructions = list(set(self.all_instruction_labels) - set(found_instructions))
        store_details['children'] = self.finderModel.findNodeChildren(all_node_ids, keys,add_new_keys, self.concept_space)
        if duplicate_node_ids :
            store_details['children'] = self.processDuplicateNodeIds(duplicate_node_ids, duplicate_keys, duplicate_add_new_keys,self.concept_space, store_details['children'])
        store_details['not_found'] = not_found_instructions
        return store_details
    
    def processDuplicateNodeIds(self,duplicate_node_ids,duplicate_keys,duplicate_add_new_keys,concept_space,children):
#         print duplicate_node_ids
#         print duplicate_keys
#         print duplicate_add_new_keys
#         print children
#         exit()
        index_track = {}
        node_ids_track = {}
        for node_id in duplicate_node_ids :
            if node_id not in index_track :
                index_track[node_id] = 0
            if node_id not in node_ids_track :
                node_ids_track[node_id] = 0
            else :
                node_ids_track[node_id] += 1
            index = index_track[node_id]
            details = self.finderModel.findNodeChildren([node_id], {node_id : duplicate_keys[node_id][index]},{node_id : duplicate_add_new_keys[node_id][index]}, concept_space)
            index_track[node_id] += 1
#             print details
#             exit()
            children = self.__mergeResults(details,children,node_id,node_ids_track[node_id])
        return children
    
    def __mergeResults(self, details, children, node_id, unique_number):
        parent_id = 0
        parent_id = self.__getParentId(details, node_id, parent_id)
        node_data = self.__getNodeData(details,node_id, parent_id)
        return self.__mergeNewChildrenInParent(node_data, parent_id, node_id, children, unique_number)
                
    def __getNodeData(self, details,node_id, parent_id):
        for i in details :
            if i == parent_id :
                return details[i]['children'][node_id]
            else :
                return self.__getNodeData(details[i]['children'],node_id, parent_id)
    
    def __mergeNewChildrenInParent(self, details, parent_id, node_id, children, unique_number):
        for i in children :
            if i == parent_id :
                children[i]['children'][str(node_id) + "_" + str(unique_number)] = details
            else :
                children[i]['children'] = self.__mergeNewChildrenInParent(details, parent_id, node_id, children[i]['children'], unique_number)
        return children
        
    def __getParentId(self, details, node_id, parent_id):
        for i in details :
            if i <> node_id :
                parent_id = i
                parent_id = self.__getParentId(details[i]['children'], node_id, parent_id)
            else :
                return parent_id
        return parent_id
        
       
        
        
        
        
