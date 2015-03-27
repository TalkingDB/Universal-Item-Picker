from __future__ import division
# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__="anik"
__date__ ="$16 Sep, 2014 3:13:42 PM$"

from database import graphdb
# from py2neo import neo4j
from UIP.model import finder_model
from app import *
import traceback
import sys
import datetime

import neo4j

Config = Config()
db_url = str(Config.get('Database')['neo4j_path'])

# connection = neo4j.connect(db_url)
# 
# GraphDatabase = connection.cursor()

# graph_db = neo4j.GraphDatabaseService(db_url)
# GraphDatabase = graphdb.GraphDB(graph_db)


class Finder():
    
    def __init__(self,node_ids,instruction,GL):
        connection = neo4j.connect(db_url)

        GraphDatabase = connection.cursor()
#         print instruction['label']
#         exit()
        self.GL = GL
#        self.GL.G = self.GL.parseGML(instruction)
        self.instruction = instruction
#         print instruction
#         exit()
        self.node_ids = node_ids
        self.finderModel = finder_model.FinderModel(GraphDatabase)
        self.pass_bucket_id = []
        self.exhausted_node_id = []
        self.size_check = False
        self.concept_space = "foodweasel.com"
        self.threshold_limit_percent = 0.8
        self.deep_down_percent_decrease = 0.2
        
    def processNode(self,child_nodes):
        """
        getChildNodes(parent_id,edge_relation,field)
        """
        for child_node in child_nodes:
            if child_node['Entity'] == "CommandNet>UnitsOfX":
                quantity = self.GL.getChildNodes(child_node['Id'],'param:object','Label')
                self.processNode(self.GL.getChildNodes(child_node['Id'],'param:subject'))
                pass
            elif child_node['Entity'] == "CommandNet>VagueSizeOf":
                size = self.GL.getChildNodes(child_node['Id'],'param:object','Label')
                self.processNode(self.GL.getChildNodes(child_node['Id'],'param:subject'))
                pass
            elif child_node['Entity'] == "CommandNet>along_With":
                pass
            elif child_node['Entity'] == "CommandNet>LessOf":
                pass
            elif child_node['Entity'] == "CommandNet>nounPhrase":
                pass
            elif child_node['Entity'] == "CommandNet>Remove":
                pass
            elif child_node['Entity'] == "CommandNet>More_of":
                pass
            elif child_node['Entity'] == "CommandNet>List_of_X":
                pass
            elif child_node['Entity'] == "CommandNet>Nothing_but_X":
                pass
            elif child_node['Entity'] == "CommandNet>Container":
                pass
        pass
    
    
    
    def processParentNode(self, parent_node):
        """ Take input of a CommandNet Hypergraph. Execute the corresponding programming function of CommandNet Hypergraph
        """
        if parent_node['type'] == 'token':
            token = parent_node['entity']
            user_tokens = token.split(",")
            if "~NoTag" in user_tokens:
                    user_tokens = user_tokens.remove("~NoTag")
            if not user_tokens:
                user_tokens = []
                item_nodes = []
            else:    
                item_nodes = self.findItemNodes(user_tokens)
        else:    
            command = "process" + (parent_node['command']).replace("CommandNet>","")
#             method = getattr(self,command)
#             return_data = method(parent_node)
#             exit()
            try:
                method = getattr(self,command)
                return_data = method(parent_node)
                if isinstance(return_data,dict) :
                    return return_data
                else :
                    user_tokens, item_nodes = return_data
            except Exception as inst:
                print "Command Not Found"
                print inst
                print inst.args
                print traceback.print_exc(file=sys.stdout)
                item_nodes = []
                user_tokens = []
        return user_tokens, item_nodes
        
    #@profile
    def process(self):
        """
        Main function in finder.py module which gets called first, and calls rest all functions in finder.py
        Takes input of 'user instruction' and returns 'matching nodes'
        """
        pass_nodes = self.getAllExactMatchNodes(self.instruction['label'])

        pass_bucket = self.generatePassBucket(pass_nodes)

        return_data = self.processParentNode(self.instruction) #iterate through each CommandNet hypergraph node, starting from NewInstruction Hypergraph
# 
#         import sys
#         sys.path.append("/usr/lib/python2.7/pysrc")
#         import pydevd
#         pydevd.settrace('61.12.32.122', port = 5678)

        if isinstance(return_data,dict) :
            return dict(pass_bucket, **return_data)
        else :
            user_tokens, item_nodes = return_data
        item_nodes = self.processSearchedNode(user_tokens,item_nodes)

        selected_nodes = self.processSelectedNodes(item_nodes,user_tokens)

        final_bucket = {}
        if pass_bucket :
            for i in pass_bucket :
                if i in selected_nodes :
                    final_bucket[i] = pass_bucket[i] + selected_nodes[i]
                else :
                    final_bucket[i] = pass_bucket[i]
                    
        if selected_nodes :
            for i in selected_nodes :
                if i not in final_bucket :
                    final_bucket[i] = selected_nodes[i]
        return final_bucket
    
    def getAllExactMatchNodes(self, text):
        separated_node_ids = ",".join(str(x) for x in self.node_ids)
        return self.finderModel.findNodesByName(separated_node_ids,text)
    
    def generatePassBucket(self, item_nodes, node_instruction = None):
        selected_bucket = {}
        for node in item_nodes:
            self.pass_bucket_id.append(str(node['search_node']['id']))
            node['selected_options'] = {}
            parent_id = self.finderModel.findConceptSpaceParentNode(self.concept_space,node['search_node']['id'])
#             print parent_id
            if node['search_node']['type'] == 'option':
                node,total_score,selected_option_ids = self.convertOptionToItem(node, 1, {})
                node['selected_options'] = selected_option_ids
            node['not_found'] = []
            node['warning'] = {}
            if node_instruction is None :
                node['instruction'] = self.instruction['label']
            else :
                node['instruction'] = node_instruction
            if parent_id not in selected_bucket:
                selected_bucket[parent_id] = []
            selected_bucket[parent_id].append(node)
        return selected_bucket
    
    
    def convertOptionToItem(self,node,total_score,selected_option_ids):
        """
            If an option which is a option get shortlisted, this function will find its
            parent item and convert the node in required format
        """
        option_parent_node = self.finderModel.getOptionParentNode(node['search_node']['id'])
        if 'warning' in node :
            option_parent_node['warning'] = node['warning']
        option_parent_node['quantity'] = node['quantity'] if 'quantity' in node else 1
        if 'option_tokens' in node :
            option_parent_node['option_tokens'] = node['option_tokens']
        option_parent_node['token_node'] = []
        option_parent_node['option_selected'] = []
        path_length = self.finderModel.findPathLength(node['search_node']['id'],option_parent_node['search_node']['id'])
        selected_option_ids[node['search_node']['id']] = (1 - (path_length * self.deep_down_percent_decrease)) * total_score
        total_score = 0;
        return option_parent_node,total_score,selected_option_ids
    
    def processSelectedNodes(self,item_nodes,user_tokens,node_instruction = None):

        highest_score = 0
        for nodes in item_nodes:
            # print nodes
            list_index = item_nodes.index(nodes)
            match_score = 0
            intersection_list = list(set(nodes["tokens"]).intersection(set(user_tokens)))
            match_score += len(intersection_list)
            user_token_matching = (match_score / len(user_tokens))
            nodes["tokens"] = [x for x in nodes['tokens'] if x != '~NoTag']
            menu_token_matching = (match_score / len(nodes["tokens"]))

            if user_token_matching > 0.5:
                total_score = user_token_matching + menu_token_matching
            else:
                total_score = 0
                
            self.non_exhausted_list = list(set(user_tokens) - set(nodes['tokens']))
            if set(user_tokens) - set(nodes['option_tokens']):
                nodes = self.processSearchedNode(user_tokens, nodes)
            selected_option_ids = self.processAllSearchedOptions(nodes, nodes['search_node']['id'])
            # Code to check if the node selected is option. If an option is selected we will find its 
            # parent, and selected item would be parent along with the option selected.
#             print nodes['search_node']
            if nodes['search_node']['type'] == 'option':
                nodes,total_score,selected_option_ids = self.convertOptionToItem(nodes, total_score, selected_option_ids)

            total_option_score = sum(selected_option_ids.values())
            # average_score = (total_score + total_option_score) / (1 + len(selected_option_ids))

            # Above line is commented because average score is not correct to use here as it will
            # not decrease the score of item in which item is not found. Instead total score should
            # be used
            average_score = (total_score + total_option_score/4)

            # if average score calculated is above the threshold limit of maximum score that can be given to item :
            # this part need to be re think
            if node_instruction is None :
                nodes['instruction'] = self.instruction['label']
            else :
                nodes['instruction'] = node_instruction
            
            if (average_score > highest_score) and (average_score) < 2 :
                highest_score = average_score
            nodes['score'] = average_score
            nodes['selected_options'] = selected_option_ids
            remaining_tokens = list(set(user_tokens) - set(nodes['option_tokens']))
            not_found = []
#             print remaining_tokens
            # exit()
            if remaining_tokens :
                for token in remaining_tokens:
                    nodes_not_found = self.GL.searchNode(self.instruction['id'],('entity',token))
                    for node_not_found in nodes_not_found:
                        if node_not_found['label'] not in not_found:
                            not_found.append(node_not_found['label'])
            nodes['not_found'] = not_found
#             exit()
            del nodes['token_node']
            del nodes['option_selected']
            del nodes['option_tokens']
            del nodes['tokens']

            del item_nodes[list_index]
            item_nodes.insert(list_index,nodes)

        selected_bucket = {}
        threshold_limit = self.threshold_limit_percent * highest_score
        for node in item_nodes:
            if(node['score'] >= threshold_limit) and (threshold_limit >0):
                parent_id = self.finderModel.findConceptSpaceParentNode(self.concept_space,node['search_node']['id'])
#                 print parent_id
                if parent_id not in selected_bucket:
                    selected_bucket[parent_id] = []
                selected_bucket[parent_id].append(node)
#         print "here"
        return selected_bucket
    
    
    def processAllSearchedOptions(self, node, parent_id):
        scoring_cache = {}
        selected_option_id = {}
        for option_node in node['option_selected']:
            length = self.finderModel.findPathLength(option_node['search_node']['id'],parent_id)
            option_node['intersection_list'] = list(set(option_node["tokens"]).intersection(set(self.non_exhausted_list)))
            match_score = len(option_node['intersection_list'])
            option_node['score'] = ((1 - (length * self.deep_down_percent_decrease)) 
            * ( ( (match_score/len(self.non_exhausted_list)) if (len(self.non_exhausted_list) > 0) else 0) 
                + ( (match_score/len(option_node["tokens"])) if (len(option_node["tokens"]) > 0) else 0)))
            list_index = node['option_selected'].index(option_node)
            del node['option_selected'][list_index]
            node['option_selected'].insert(list_index,option_node)
            for token in option_node['tokens']:
                if token in scoring_cache:
                    pre_score = scoring_cache[token]
                    if option_node['score'] > pre_score :
                        scoring_cache[token] = option_node['score']
                else:
                    scoring_cache[token] = option_node['score']
        token_selected = []
        option_groups_selection = {}
        for option_node in node['option_selected']:
            if option_node['option_group']['id'] not in option_groups_selection:
                option_groups_selection[option_node['option_group']['id']] = {
                'max_selection' : option_node['option_group']['max_selection'],
                'selected' : 0
                }
            option_token_selected = []
            select = False
            
                
            for token in option_node['tokens']:
                token_list_added = False
                max_score_of_token = scoring_cache[token]
                if(option_node['score'] == max_score_of_token and token not in token_selected and token in self.non_exhausted_list):
                    select = True
                    if not token_list_added:
                        option_token_selected += option_node['tokens']
                        token_list_added = True 
            if select and (option_groups_selection[option_node['option_group']['id']]['selected'] 
                < option_groups_selection[option_node['option_group']['id']]['max_selection']) :
                    option_groups_selection[option_node['option_group']['id']]['selected'] += 1
                    selected_option_id[option_node['search_node']['id']] = option_node['score']
                    token_selected += option_token_selected
        return selected_option_id

    
    def processSearchedNode(self, user_tokens, item_nodes):
        if(isinstance(item_nodes, list)):
            for node in item_nodes:
                self.__checkSizeWarning(node, user_tokens)
        else :
            self.__checkSizeWarning(item_nodes, user_tokens)

        # print item_nodes
        # exit()
        return item_nodes
    
    def __checkSizeWarning(self, node, user_tokens):
        self.findOptionNodeAndProcess(node, user_tokens)
        if 'warning' not in node :
            node['warning'] = {}

        if self.size_check and self.size_token not in node['option_tokens'] :
            node['warning'] = dict(node['warning'], **{'size':'not_found'})
    
    def findOptionNodeAndProcess(self, node, user_tokens):
#         print node['search_node']['name']
        option_tokens = []
        if 'option_tokens' in node:
            option_tokens = set(node['option_tokens'])
        user_token_set = set(user_tokens)
        # print node
#         print node["tokens"]
        node_token_set = set(node["tokens"])
#         exit()
        intersection = (node_token_set.union(option_tokens)).intersection(user_token_set)
        non_exhausted_set = user_token_set - intersection
        new_option_node = self.findOptionNodes(node['search_node']['id'],list(non_exhausted_set))
#         print new_option_node
        if 'option_selected' in node:
            node['option_selected'] += new_option_node
        else:
            node['option_selected'] = new_option_node
#         print node['option_selected']
        
        for option in node['option_selected'] :
            node_token_set = node_token_set.union(set(option['tokens']))

        if 'option_tokens' in node:
            option_tokens = set(option_tokens).union(node_token_set)
            node["option_tokens"] = list(option_tokens)
        else:
            node["option_tokens"] = list(node_token_set)
    
    def processNewInstruction(self,parent_node,return_item_nodes = True, subject_check = False):
        # @TODO : Logic for new instruction need to be created.
        user_tokens = []
        item_nodes = []

        node_level = self.GL.getNodeLevel(parent_node['id'])
        if node_level == 0:
            all_nodes = self.GL.getChildNodes(parent_node['id'])
        else:
#             all_nodes = self.GL.getChildNodes(parent_node['id'], 'param:subject')
            if subject_check :
                all_nodes = self.GL.getChildNodes(parent_node['id'], 'param:subject')
            else :
                if node_level == 2:
                    all_nodes = self.GL.getChildNodes(parent_node['id'], 'param:subject')
                else :
                    all_nodes = self.GL.getChildNodes(parent_node['id'])
#         print all_nodes
#         print node_level
#         print len(all_nodes)
#         exit()

        if node_level == 0 or node_level == 1 :
            selected_check = False
            selected_bucket = {}
            if len(all_nodes) > 1 :
                for i in all_nodes :
                    node = all_nodes[i]
                    if(node['type'] == 'hypergraph'):
                        command = "process" + (node['command']).replace("CommandNet>","")
                        if node_level == 1 and command == "processNewInstruction" :
                            selected_check = True
                            selected_bucket = dict(selected_bucket, **self.processNodeOfNewInstruction(node,return_item_nodes, user_tokens, item_nodes))
                        else:
                            data = self.processNodeOfNewInstruction(node,return_item_nodes, user_tokens, item_nodes)
                            if isinstance(data, dict) :
                                selected_check = True
                                selected_bucket = dict(selected_bucket, **data)
                            else :
                                user_tokens, item_nodes = data
                    else :
                        token = node['entity']
                        token_list = token.split(",")
                        if "~NoTag" in token_list:
                            token_list = token_list.remove("~NoTag")
                        
                        if token_list is None:
                            token_list = []    
                        
                        user_tokens = user_tokens + token_list
                        if token_list :
                            item_nodes = item_nodes + self.findItemNodes(token_list)
            else :
                node = all_nodes.values()[0]
#                 print node
#                 exit()
                if(node['type'] == 'hypergraph'):
                    command = "process" + (node['command']).replace("CommandNet>","")
#                     print node_level
#                     print command
                    if node_level == 1 and command == "processNewInstruction" :
                        selected_check = True
                        selected_bucket = dict(selected_bucket, **self.processNodeOfNewInstruction(node,return_item_nodes, user_tokens, item_nodes))
                    else:
                        data = self.processNodeOfNewInstruction(node,return_item_nodes, user_tokens, item_nodes)
#                         print "-->", data
                        if isinstance(data, dict) :
                            selected_check = True
                            selected_bucket = dict(selected_bucket, **data)
                        else :
                            user_tokens, item_nodes = data
                else :
                    token = node['entity']
                    token_list = token.split(",")
                    if "~NoTag" in token_list:
                        token_list = token_list.remove("~NoTag")
                    
                    if token_list is None:
                        token_list = []    
                    
                    user_tokens = user_tokens + token_list
#                     print token_list
#                     print item_nodes
#                     print self.findItemNodes(token_list)
#                     exit()
                    if token_list and return_item_nodes :
                        item_nodes = item_nodes + self.findItemNodes(token_list)
                    
            if selected_check:
                return selected_bucket
        elif node_level == 2 :
            selected_bucket = {}
            if len(all_nodes) > 1 :
                for i in all_nodes :
                    node = all_nodes[i]
                    user_tokens, item_nodes = self.processNodeOfNewInstruction(node,return_item_nodes)
                    item_nodes = self.processSearchedNode(user_tokens,item_nodes)
                    selected_bucket = self.mergeDict(selected_bucket, self.processSelectedNodes(item_nodes, user_tokens))
#                     selected_bucket = dict(selected_bucket, **self.processSelectedNodes(item_nodes, user_tokens))
            else :
                node = all_nodes.values()[0]
                user_tokens, item_nodes = self.processNodeOfNewInstruction(node,return_item_nodes)
                item_nodes = self.processSearchedNode(user_tokens,item_nodes)
                selected_bucket = self.mergeDict(selected_bucket, self.processSelectedNodes(item_nodes, user_tokens))
#             print selected_bucket
#             exit()
            return selected_bucket    
        else :
            item_nodes = []
            if len(all_nodes) > 1 and 'start' not in all_nodes :
                for i in all_nodes :
                    node = all_nodes[i]
                    user_tokens += self.getTokensFromNode(node)
            elif 'start' in all_nodes :
                user_tokens += self.getTokensFromNode(all_nodes)
            else :
                node = all_nodes.values()[0]
                user_tokens += self.getTokensFromNode(node)
        
        return user_tokens, item_nodes
    
    def mergeDict(self, first_dict, second_dict):
#         print "though"
        final_dict = {}
        final_dict = self.processDictToBeMerged(final_dict, first_dict)
        final_dict = self.processDictToBeMerged(final_dict, second_dict)
        return final_dict
        
    def processDictToBeMerged(self, final_dict, second_dict):
        for i in second_dict :
            if i not in final_dict :
                final_dict[i] = second_dict[i]
            else :
                final_dict[i] = final_dict[i] + second_dict[i]
#                 print final_dict[i]
#                 print second_dict[i]
# #                 exit()
#                 for ref_value in final_dict[i] :
#                     for curr_value in second_dict[i] :
#                         print ref_value
#                         print curr_value
#                         exit()
#                         if ref_value <> curr_value :
#                             final_dict[i].append(curr_value)
                            
        return final_dict
    
    def getTokensFromNode(self,node):
        token = node['entity']
        token_list = token.split(",")
        
        if "~NoTag" in token_list:
            token_list = token_list.remove("~NoTag")
        
        if token_list is None:
            token_list = []
            
        return token_list

    def processNodeOfNewInstruction(self, node,return_item_nodes = True, user_tokens = [], item_nodes = []):
        if(node['type'] == 'hypergraph'):
            command = "process" + (node['command']).replace("CommandNet>","")
            method = getattr(self,command)
            if command == "processNewInstruction" or command == "processNewInstructionOfNouns" :
                return method(node)
            else :
#                 print method(node)
                user_tokens_returned, item_nodes_returned = method(node)
            user_tokens = user_tokens + user_tokens_returned
            if return_item_nodes :
                item_nodes = item_nodes + item_nodes_returned
        else:
            token = node['entity']
            token_list = token.split(",")
            if "~NoTag" in token_list:
                token_list = token_list.remove("~NoTag")
            
            if token_list is None:
                token_list = []
                
            
            user_tokens = user_tokens + token_list
            if token_list and return_item_nodes:
                item_nodes = item_nodes + self.findItemNodes(token_list)
        
        return user_tokens, item_nodes
    
    def processUnitOfMeasurement(self,parent_node, return_item_nodes = True):
        user_tokens = []
        item_nodes = []
        return user_tokens, item_nodes
    
    #Processed  
      
    def processAlongWith(self,parent_node, return_item_nodes = True):
        user_tokens = []
        item_nodes = []
        subject_node = self.GL.getChildNodes(parent_node['id'],'param:subject')
        # print subject_node
        # exit()
        if(subject_node['type'] == 'hypergraph'):
            command = "process" + (subject_node['command']).replace("CommandNet>","")
            method = getattr(self,command)
            user_tokens_returned, item_nodes_returned = method(subject_node)
            user_tokens = user_tokens + user_tokens_returned
            if return_item_nodes :
                item_nodes = item_nodes + item_nodes_returned
        else :
            token = subject_node['entity']
            token_list = token.split(",")
            token_list = token_list.remove("~NoTag") if "~NoTag" in token_list else token_list
            user_tokens = user_tokens + token_list
            if token_list and return_item_nodes :
                item_nodes = item_nodes + self.findItemNodes(token_list)

        # print item_nodes
        # exit()

        object_node = self.GL.getChildNodes(parent_node['id'],'param:object')
        if(object_node['type'] == 'hypergraph'):
            command = "process" + (object_node['command']).replace("CommandNet>","")
            method = getattr(self,command)
            
            user_tokens_returned, item_nodes_returned = method(object_node, False)
            user_tokens = user_tokens + user_tokens_returned
        else :
            token_list = (object_node['entity']).split(",")
            user_tokens = user_tokens + ((token_list).remove("~NoTag") if "~NoTag" in token_list else token_list)
            
        return user_tokens, item_nodes
    
    def processQuantityOrSizeOf(self,parent_node):
        user_tokens = []
        item_nodes = []
        return user_tokens, item_nodes
    
    
    def processLessOf(self,parent_node):
        user_tokens = []
        item_nodes = []
        subject_node = self.GL.getChildNodes(parent_node['id'],'param:subject')
        if(subject_node['type'] == 'hypergraph'):
            command = "process" + (subject_node['command']).replace("CommandNet>","")
            method = getattr(self,command)
            user_tokens_returned, item_nodes_returned = method(subject_node)
            user_tokens = user_tokens + user_tokens_returned
        else :
            token_list = (subject_node['entity']).split(",")
            user_tokens = user_tokens + ((token_list).remove("~NoTag") if "~NoTag" in token_list else token_list)
            
        return user_tokens, item_nodes

    #Processed
    
    def processVagueSizeOf(self,parent_node, return_item_nodes = True):

        user_tokens = []
        item_nodes = []

        object_node = self.GL.getChildNodes(parent_node['id'],'param:object')
        user_tokens.append(object_node['entity'])
        subject_node = self.GL.getChildNodes(parent_node['id'],'param:subject')
        if(subject_node['type'] == 'hypergraph'):
            command = "process" + (subject_node['command']).replace("CommandNet>","")
            method = getattr(self,command)
            user_tokens_returned, item_nodes_returned = method(subject_node)
            user_tokens = user_tokens + user_tokens_returned
            if return_item_nodes :
                item_nodes = item_nodes + item_nodes_returned
        else :
            token = subject_node['entity']
            token_list = token.split(",")
            token_list = token_list.remove("~NoTag") if "~NoTag" in token_list else token_list
            user_tokens = user_tokens + token_list
            if token_list and return_item_nodes :
                item_nodes = item_nodes + self.findItemNodes(token_list)
        if return_item_nodes :
            self.size_check = True
            self.size_token = object_node['entity']

#             item_nodes = self.processSearchedNode(object_node['entity'], item_nodes)
            item_nodes = self.processSearchedNode(user_tokens, item_nodes)
        self.size_check = False
        user_tokens.remove(object_node['entity'])
        return user_tokens, item_nodes

    #Processed
    
    def processUnitsOfX(self,parent_node, return_item_nodes = True):
        user_tokens = []
        item_nodes = []
        object_node = self.GL.getChildNodes(parent_node['id'],'param:object')
        quantity = object_node['label']
        
        subject_node = self.GL.getChildNodes(parent_node['id'],'param:subject')
        if(subject_node['type'] == 'hypergraph'):
            command = "process" + (subject_node['command']).replace("CommandNet>","")
            method = getattr(self,command)
            user_tokens_returned, item_nodes_returned = method(subject_node)
            user_tokens = user_tokens + user_tokens_returned
            if return_item_nodes :
                item_nodes = item_nodes + item_nodes_returned
        else :
            token = subject_node['entity']
            token_list = token.split(",")
            token_list = token_list.remove("~NoTag") if "~NoTag" in token_list else token_list
            user_tokens = user_tokens + token_list
            if token_list and return_item_nodes :
                item_nodes = item_nodes + self.findItemNodes(token_list)
        
        if return_item_nodes :
            for node in item_nodes:
                node['quantity'] = quantity

        return user_tokens, item_nodes

    #Processed 
           
    def processNoun(self,parent_node, return_item_nodes = True):
        user_tokens = []
        item_nodes = []
        all_nodes = self.GL.getChildNodes(parent_node['id'])
        for i in all_nodes :
            token = all_nodes[i]['entity']
            token_list = (token).split(",")
            user_tokens = user_tokens + ((token_list).remove("~NoTag") if "~NoTag" in token_list else token_list)
        
        final_nodes = []
        if return_item_nodes :
            item_nodes = item_nodes + self.findItemNodes(user_tokens)
            for node in item_nodes:
                if(set(user_tokens).intersection(set(node['tokens'])) == set(user_tokens)):
                    final_nodes.append(node)
        return user_tokens, final_nodes
    
    def processRemoveX(self,parent_node):
        # @TODO : Logics for this part need to be prepared. It will be coded later
        user_tokens = []
        item_nodes = []

        return user_tokens, item_nodes

        subject_node = self.GL.getChildNodes(parent_node['id'],'param:subject')
        if(subject_node['type'] == 'hypergraph'):
            self.processParentNode(subject_node)
        else :
            # Some neo4j NOT query to be included here
            pass
    
    #Processed
    # Depreciated
    
    def processMoreOf(self,parent_node):
        user_tokens = []
        item_nodes = []
        subject_node = self.GL.getChildNodes(parent_node['id'],'param:subject')
        if(subject_node['type'] == 'hypergraph'):
            command = "process" + (subject_node['command']).replace("CommandNet>","")
            method = getattr(self,command)
            user_tokens_returned, item_nodes_returned = method(subject_node)
            user_tokens = user_tokens + user_tokens_returned
        else :
            token = subject_node['entity']
            token_list = (token).split(",")
            user_tokens = user_tokens + ((token_list).remove("~NoTag") if "~NoTag" in token_list else token_list)

        return user_tokens, item_nodes
    
    
    def processMoreObjectInSubject(self,parent_node):
        user_tokens = []
        item_nodes = []
        return user_tokens, item_nodes
        subject_node = self.GL.getChildNodes(parent_node['id'],'param:subject')
        if(subject_node['type'] == 'hypergraph'):
            command = "process" + (subject_node['command']).replace("CommandNet>","")
            method = getattr(self,command)
            user_tokens_returned, item_nodes_returned = method(subject_node)
            user_tokens += user_tokens_returned
            item_nodes +=  item_nodes_returned
        else :
            token = subject_node['entity']
            token_list = (token).split(",")
            user_tokens = user_tokens + ((token_list).remove("~NoTag") if "~NoTag" in token_list else token_list)

        return user_tokens, item_nodes
    

    #Processed
    # Depreciated
    
    def processListOfX(self,parent_node):
        user_tokens = []
        item_nodes = []
        all_nodes = self.GL.getChildNodes(parent_node['id'])
        for i in all_nodes :
            token = all_nodes[i]['entity']
            token_list = (token).split(",")
            user_tokens = user_tokens + ((token_list).remove("~NoTag") if "~NoTag" in token_list else token_list)

        return user_tokens, item_nodes

    def processNewInstructionOfNouns(self, parent_node, return_item_nodes = True):
        return self.processNewInstruction(parent_node,return_item_nodes, True)
        user_tokens = []
        item_nodes = []
        all_nodes = self.GL.getChildNodes(parent_node['id'], 'param:subject')
        for i in all_nodes :
            token = all_nodes[i]['entity']
            token_list = (token).split(",")
            user_tokens = user_tokens + ((token_list).remove("~NoTag") if "~NoTag" in token_list else token_list)

        return user_tokens, item_nodes

    #Processed
    
    def processContainer(self,parent_node, return_item_nodes = True):
        user_tokens = []
        item_nodes = []

        object_node = self.GL.getChildNodes(parent_node['id'],'param:object')
        user_tokens = user_tokens + (object_node['entity']).split(",")

        subject_node = self.GL.getChildNodes(parent_node['id'],'param:subject')
        if(subject_node['type'] == 'hypergraph'):
            command = "process" + (subject_node['command']).replace("CommandNet>","")
            method = getattr(self,command)
            user_tokens_returned, item_nodes_returned = method(subject_node)
            user_tokens = user_tokens + user_tokens_returned
            if return_item_nodes :
                item_nodes = item_nodes + item_nodes_returned
        else :
            token = subject_node['entity']
            token_list = token.split(",")
            token_list = token_list.remove("~NoTag") if "~NoTag" in token_list else token_list
            user_tokens = user_tokens + token_list
            if token_list and return_item_nodes:
                item_nodes = item_nodes + self.findItemNodes(token_list)
            
        
        return user_tokens, item_nodes
    
    def processEverything(self,parent_node):
#       @TODO : This is not yet coded. Logic need to be prepared for this
        user_tokens = []
        item_nodes = []

        return user_tokens, item_nodes

    #Processed
    
    def processNothingButX(self,parent_node):
        user_tokens = []
        item_nodes = []
        all_nodes = self.GL.getChildNodes(parent_node['id'])
        if (all_nodes[i]['type'] == 'hypergraph'):
            command = "process" + (subject_node['command']).replace("CommandNet>","")
            method = getattr(self,command)
            user_tokens_returned, item_nodes_returned = method(subject_node)
            user_tokens = user_tokens + user_tokens_returned
        else:
            token = subject_node['entity']
            user_tokens = user_tokens + token.split(",")

        return user_tokens, item_nodes
    
    #Processed
    
    def processAOrB(self,parent_node):
        user_tokens = []
        item_nodes = []
        all_nodes = self.GL.getChildNodes(parent_node['id'])
        for i in all_nodes :
            node = all_nodes[i]
            if all_nodes[i]['entity'] == "hypergraph" :
                command = "process" + (node['command']).replace("CommandNet>","")
                method = getattr(self,command)
                user_tokens_returned, item_nodes_returned = method(node)
                user_tokens = user_tokens + user_tokens_returned
                item_nodes = item_nodes + item_nodes_returned
            else:
                token = all_nodes[i]['entity']
                token_list = token.split(",")
                token_list = token_list.remove("~NoTag") if "~NoTag" in token_list else token_list
                user_tokens = user_tokens + token_list
                if token_list :
                    item_nodes = item_nodes + self.findItemNodes(token_list)

        return user_tokens, item_nodes

    
    def findItemNodes(self,tokens):
        # print self.node_ids
        # exit()
        separated_node_ids = ",".join(str(x) for x in self.node_ids)
        item_data = self.finderModel.findNodesByNodeIds(separated_node_ids,tokens,self.pass_bucket_id)
        return item_data
    
    
    def findOptionNodes(self, item_node_id, tokens):
        item_data = []
        if tokens :
            item_data = self.finderModel.findOptionNodes(item_node_id,tokens)
        return item_data
