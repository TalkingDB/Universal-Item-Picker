'''
recommendation.py Created on 16-Oct-2014

@author: anik

Tips to debug :
recommendations.py       calls    recommendation.py
recommendation.py        calls    instructionparser.py
instructionparser.py     calls    threadhandler.py
threadhandler.py         calls    finder.py
'''

from UIP.base_operations import instructionparser
from GraphLib import index as gl
from UIP import userinstruction

GL = gl.GraphLib()

class Recommendation():

    def __init__(self):
        pass
    
    #@profile
    def generateRecommendation(self,params):
#         import sys
#         sys.path.append("/usr/lib/python2.7/pysrc")
#         import pydevd
#         pydevd.settrace('61.12.32.122', port = 5678)
        
        import datetime
        print '[' + str(datetime.datetime.now()) + '] received query in recommendation.py/generateRecommendation'
        self.__generateVariables(params)
        user_instruction = userinstruction.UserInstruction()
        node_ids = user_instruction.findNodeIds(self.concept_space, self.key, self.values)
        print '[' + str(datetime.datetime.now()) + '] executed findNodeIds in recommendation.py/generateRecommendation'
        decoded = self.instruction.decode("utf-8")
        decoded = decoded.replace(".", " ")
        json_data = user_instruction.commandProcessorHit(decoded)

        print '[' + str(datetime.datetime.now()) + '] executed commandPorcessorHit in recommendation.py/generateRecommendation'
    	json_data = json_data.decode('string_escape')
        json_data = json_data.replace('&gt;','>')
        instruction_parser = instructionparser.InstructionParser()
        result_stores_and_their_items_with_options, special_instructions = instruction_parser.parseInstruction(node_ids,json_data, self.concept_space) #TODO SpecialInstruction: Instead of returning just the prepareList, now we also return special_instructions list. capture that too
        print '[' + str(datetime.datetime.now()) + '] executed parseInstruction in recommendation.py/generateRecommendation'
        
        sorted_stores = self.__sortStoreWithScore(result_stores_and_their_items_with_options)
        
        return sorted_stores, special_instructions
    
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
            
            store['score'] = store_score
            tmp_stores_and_items.append(store)
        
        sorted_stores =  sorted(tmp_stores_and_items,key=lambda particular_store: particular_store['score'],reverse=True)
        
        return sorted_stores


# import datetime
# print '[' + str(datetime.datetime.now()) + 'started query'
#
# r = Recommendation()
# found_results, special_instructions =  r.generateRecommendation({'instruction': 'abra ka dabra', 'parent': {u'value': ["1234"], u'key': u'uid'}, 'concept_space': u'eric_tucker'})
# print found_results
#
# print '[' + str(datetime.datetime.now()) + 'stopped query'