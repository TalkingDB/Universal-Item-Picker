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
        result_stores_and_their_items_with_options = instruction_parser.parseInstruction(node_ids,json_data, self.concept_space) #TODO SpecialInstruction: Instead of returning just the prepareList, now we also return special_instructions list. capture that too
        print '[' + str(datetime.datetime.now()) + '] executed parseInstruction in recommendation.py/generateRecommendation'
        
        sorted_stores, special_instructions = self.__sortStoreWithScore(result_stores_and_their_items_with_options)
        
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

# r = Recommendation()
# # test =  r.generateRecommendation({'instruction': 'large coke~beef broccoli with fried rice on the side', 'parent': {u'value': ["1013","10131","1218","1269","13987","1572","1579","24805","2681","2741","2834","29114","2946","29490","2977","29982","30716","30779","3123","3125","3131","3145","3168","3219","32219","32227","3395","3426","35859","36135","36407","37636","38410","38453","38522","39570","43764","44221","44767","46044","46045","46058","51815","57105","57264","57310","57562","58099","58406","58467","58616","58800","58948","58955","59041","59519","59576","59579","59600","59948","60426","60665","60718","60905","60949","61048","61058","61099","61126","61149","61287","61365","61392","61402","61404","61558","61651","61659","61730","61925","61960","61977","61991","62013","62015","62033","62075","62157","62291","62376","62464","62490","62500","62512","62786","62871","62947","63024","63190","63265","63384","63453","63459","63461","63463","63497","63498","63618","63678","63721","63724","63898","63923","63926","63927","64051","64121","64159","64186","64229","64280","64304","64432","64472","64520","64621","64727","64858","65049","65227","65351","65352","65363","65956","66150","66240","66292","66480","66487","66528","66566","66620","66622","66641","66734","66803","66855","66866","66932","67024","67101","67130","67186","67193","67368","67725","67744","67780","67811","67828","67872","68019","68129","68203","68247","68287","68425","68526","68896","69054","69056","69078","69088","69139","69262","69268","69275","69297","69307","69371","69390","69421","69422","69461","69463","69547","69576","69613","69617","69641","69664","69844","69845","69846","69847","69897","70172","70359","70386","70737","70782","70809","70853","71019","71097","71309","71320","71398","71465","71892","71964","72012","72050","72128","72186","72196","72244","72264","72305","72311","72514","72531","72627","73229","73322","73338","73357","73436","73503","73531","73566","73569","73580","73637","73807","73890","73977","74089","74366","74417","74557","74586","74689","74773","74812","74821","74822","75116","75265","75434","75985","76014","76031","76036","76436","76466","76790","76822","76834","78643","78714","78718","78790","78792","78981","79017","79020","79210","79303","79322","79353","79365","79373","79374","79542","79543","79893","79938","79949","80021","80090","80160","80309","80310","80388","80619","81334","81375","81569","81575","81590","81610","81662","81786","81790","81821","81829","81937","82171","82208","82234","82319","82467","82758","82785","82825","83012","835","8898","924","932","948","952"], u'key': u'uid'}, 'concept_space': u'foodweasel.com'})
# found_results, special_instructions =  r.generateRecommendation({'instruction': 'large coke~beef broccoli', 'parent': {u'value': ["1013","10131","1218","1269","13987","1572","1579","24805","2681","2741","2834","29114","2946","29490","2977","29982","30716","30779","3123","3125","3131","3145","3168","3219","32219","32227","3395","3426","35859","36135","36407","37636","38410","38453","38522","39570","43764","44221","44767","46044","46045","46058","51815","57105","57264","57310","57562","58099","58406","58467","58616","58800","58948","58955","59041","59519","59576","59579","59600","59948","60426","60665","60718","60905","60949","61048","61058","61099","61126","61149","61287","61365","61392","61402","61404","61558","61651","61659","61730","61925","61960","61977","61991","62013","62015","62033","62075","62157","62291","62376","62464","62490","62500","62512","62786","62871","62947","63024","63190","63265","63384","63453","63459","63461","63463","63497","63498","63618","63678","63721","63724","63898","63923","63926","63927","64051","64121","64159","64186","64229","64280","64304","64432","64472","64520","64621","64727","64858","65049","65227","65351","65352","65363","65956","66150","66240","66292","66480","66487","66528","66566","66620","66622","66641","66734","66803","66855","66866","66932","67024","67101","67130","67186","67193","67368","67725","67744","67780","67811","67828","67872","68019","68129","68203","68247","68287","68425","68526","68896","69054","69056","69078","69088","69139","69262","69268","69275","69297","69307","69371","69390","69421","69422","69461","69463","69547","69576","69613","69617","69641","69664","69844","69845","69846","69847","69897","70172","70359","70386","70737","70782","70809","70853","71019","71097","71309","71320","71398","71465","71892","71964","72012","72050","72128","72186","72196","72244","72264","72305","72311","72514","72531","72627","73229","73322","73338","73357","73436","73503","73531","73566","73569","73580","73637","73807","73890","73977","74089","74366","74417","74557","74586","74689","74773","74812","74821","74822","75116","75265","75434","75985","76014","76031","76036","76436","76466","76790","76822","76834","78643","78714","78718","78790","78792","78981","79017","79020","79210","79303","79322","79353","79365","79373","79374","79542","79543","79893","79938","79949","80021","80090","80160","80309","80310","80388","80619","81334","81375","81569","81575","81590","81610","81662","81786","81790","81821","81829","81937","82171","82208","82234","82319","82467","82758","82785","82825","83012","835","8898","924","932","948","952"], u'key': u'uid'}, 'concept_space': u'foodweasel.com'})
# # test
# print found_results

# print '[' + str(datetime.datetime.now()) + 'stopped query'