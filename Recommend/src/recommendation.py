'''
Created on 16-Oct-2014

@author: anik
'''

from UIP.base_operations import instructionparser
from GraphLib import index as gl
from UIP import userinstruction

GL = gl.GraphLib()

"""
support for pydev remote debugging
"""

class Recommendation():

    def __init__(self):
        pass
    
    #@profile
    def generateRecommendation(self,params):
        import datetime
        print '[' + str(datetime.datetime.now()) + '] received query in recommendation.py/generateRecommendation'
        self.__generateVariables(params)
        user_instruction = userinstruction.UserInstruction()
        node_ids = user_instruction.findNodeIds(self.concept_space, self.key, self.values)
        print '[' + str(datetime.datetime.now()) + '] executed findNodeIds in recommendation.py/generateRecommendation'
        json_data = user_instruction.commandProcessorHit(self.instruction)
        print '[' + str(datetime.datetime.now()) + '] executed commandPorcessorHit in recommendation.py/generateRecommendation'
	json_data = json_data.decode('string_escape')
#        json_data = json_data.replace('&gt;','>')
        instruction_parser = instructionparser.InstructionParser()
        result_stores_and_their_items_with_options = instruction_parser.parseInstruction(node_ids,json_data, self.concept_space)
        print '[' + str(datetime.datetime.now()) + '] executed parseInstruction in recommendation.py/generateRecommendation'
        
        sorted_stores = self.__sortStoreWithScore(result_stores_and_their_items_with_options)
        
        return sorted_stores
    
    def __generateVariables(self,params):
        self.concept_space = params['concept_space']
        self.key = params['parent']['key']
        self.values = params['parent']['value']
        self.instruction = params['instruction']
    
    def __sortStoreWithScore(self,stores_and_items):

        tmp_stores_and_items = []
         
        for store in stores_and_items:
            store_item_groups = store['children'] 

            highest_score_for_particular_instruction = {} #for each instruction, it stores the highest score attained by an item

            for item_group in store_item_groups:
                store_items = item_group['children']
                for store_item in store_items:
                    instruction = store_item['instruction']
                    if not instruction in highest_score_for_particular_instruction.keys():
                        highest_score_for_particular_instruction[instruction] = store_item['score']
                    else:
                        if highest_score_for_particular_instruction[instruction] < store_item['score']:
                            highest_score_for_particular_instruction[instruction] = store_item['score']
            
            store_score = sum(highest_score_for_particular_instruction.values())
                
#             import sys
#             sys.path.append("/usr/lib/python2.7/pysrc")
#             import pydevd
#             pydevd.settrace('61.12.32.122', port = 5678)
            
            store['score'] = store_score
            tmp_stores_and_items.append(store)
        
        sorted_stores =  sorted(tmp_stores_and_items,key=lambda particular_store: particular_store['score'],reverse=True)
        
        return sorted_stores
    
# r = Recommendation()
#  
# test =  r.generateRecommendation({'instruction': 'wonton soup~fries', 'parent': {u'value': [u'72894', u'81443', u'70681', u'30857', u'52951', u'73498', u'70263', u'68964', u'29602', u'79779', u'65010', u'68924', u'46911', u'75328', u'79960', u'38911', u'74661', u'71519', u'70131', u'69384', u'75272', u'73597', u'64309', u'64265', u'69210', u'71414', u'73185', u'68291', u'73578', u'60176', u'75342', u'73027', u'71099', u'73039', u'74101', u'58898', u'66713', u'70377', u'74661', u'70131', u'71519', u'65142', u'68924', u'72288', u'3028', u'79963', u'66109', u'72287', u'73578', u'70727', u'80415', u'31687', u'71093', u'72905', u'79753', u'80237', u'80229', u'79540', u'75297', u'74541', u'71913', u'71022', u'73926', u'74845', u'69052', u'68660', u'75449', u'71677', u'69984', u'64758', u'70029', u'75209', u'79021', u'77734', u'77748', u'71064', u'71274', u'71059', u'71028', u'76851', u'75653', u'75511', u'69917', u'60438', u'62171', u'70778', u'62335'], u'key': u'uid'}, 'concept_space': u'foodweasel.com'})
# # print test
