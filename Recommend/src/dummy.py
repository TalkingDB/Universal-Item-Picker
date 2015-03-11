__author__="Karan S. Sisodia"
__email__="karansinghsisodia@gmail.com"
__date__ ="$Sep 10, 2014 4:27:23 PM$"

import json
from UIP.base_operations import instructionparser
from GraphLib import index as gl
from UIP import userinstruction
import recommendation


GL = gl.GraphLib()

if __name__ == "__main__":
    
    def process() :
#         instruction = "Rigatoni with meat sauce~Cheese Pizza~pepsi~breadsticks"
#         instruction = "hamburger , pepsi , french fries"
#         instruction = "Rigatoni with meat sauce"
#         instruction = "2 large Cheese Pizza with Pepperoni\nPepsi"
#         instruction = "Pizza\nPepsi"
#         instruction = "Chicken with Broccoli~pepsi"
#         instruction = "Cold Antipasto Salad"
#         instruction = "Chicken with broccoli~Rigatoni"
#         instruction = "Chicken with broccoli , pepsi with sauce~Rigatoni"
#         instruction = "pepsi~coke"
#         instruction = "2 Large cheese pizza's with pepperoni ~ 1 large order of breadsticks ~ 1 large BBQ chicken salad with ranch dressing on the side ~ two 2 liter soda, one coke, and one diet coke"
#         instruction = "cheese pizza with olives , onions , lettuce , garlic"
#         instruction = "Cheese Pizza extra cheese"
#         instruction = "Soda"
#         instruction = "pepsi"
#         instruction = "Mini Pizza Pie"
        instruction = "Ravioli"
#         instruction = "cheese pizza with pepperoni , pepsi with sauce"
#         instruction = "Chicken Rollatini with Spinach , pepsi with sauce"
#         instruction = "Chicken Rollatini with Spinach"
#         instruction = "abbbba chabbbba dabbbba"
#         instruction = "cheese pizza with pepperoni"
#         instruction = "bowl of fruit"
#         instruction = "Enchalada"
#         instruction = "cheese pizza with jam"
#         instruction = "Chili Chicken Entree\ncan of pepsi"
#         instruction = "Cheese steak hoagie\nlarge cheese pizza\nturkey culb sandwich\n2 liter coke"
#         instruction = "Turkey Club Sandwich"
#         instruction = "turkey culb sandwich"
#         instruction = "Cheese steak hoagie"
#         instruction = "two pastrami sandwiches~fries~large diet coke~bowl of fruit"
#         instruction = "Cheese steak hoagie ~ large cheese pizza  ~ turkey culb sandwich ~ 2 liter coke"
        # instruction = "Egg Cheese Pizza with Pepperoni"
#         instruction = "Cheese Pizza"
        # instruction = "Cinnamon Raisin Bagel with cheese"
        # instruction = "Salad"
        # instruction = "Pizza Special with Everything Regular Pizza Pie"
        # instruction = "R5. Buddha plus Sesame Tofu- Snow Peas, Green Beans, Baby Corn, Mushrooms, Bean Sprouts and Broccoli combined with Sesame Baked Tofu"
        key = "uid"
        values = ['752','973','1071','1280','1511','1579','2712','3249','3875','3893','4456','9390','17118','25826','27957','29168','29854','29982','30435','30857','30858','35814','36414','38350','51107','52951','52960','53890','57635','57881','58193','58298','58445','58508','59572','59857','60070','60117','60372','60454','60462','60665','60734','60829','60908','60939','61135','61169','61245','61288','61364','61424','61455','61571','61603','61632','61668','61669','61826','62028','62095','62129','62214','62719','62759','63926','64171','64265','64434','64666','64817','65129','65964','65988','66029','66292','66361','66472','66526','66626','66627','66660','66669','66670','66805','66844','66913','67109','67125','67367','67391','67734','67920','68029','68079','68129','68158','68190','68219','68247','68765','69023','69090','69091','69235','69381','69389','69391','69409','69523','69524','69723','70097','70358','70681','70843','70899','71567','71807','71923','72082','72126','72263','72335','72851','72894','72908','73056','73060','73277','73305','73336','73465','73489','73498','73501','73560','73566','73591','73748','73809','73991','74040','74064','74361','74375','74377','74456','74610','74667','74668','74680','75062','75154','75162','75165','75197','75225']
#         values = ['1071','3249','1579','973','752']
#         values = ['1071','3249','1579','973','752','1511','2712','1280','3875','3893','4456','9390','17118']
        concept_space = "foodweasel.com"
        
        params = {
                  "concept_space" : "foodweasel.com",
                  "instruction":instruction,
                  "parent" : {
                              "key":key,
                              "value":values
                              }
                  }
        
        Recommendation = recommendation.Recommendation()
        print Recommendation.generateRecommendation(params)
        exit()
        user_instruction = userinstruction.UserInstruction()
        node_ids = user_instruction.findNodeIds(concept_space, key, values)
        # print node_ids
        # exit()
        json_data = user_instruction.commandProcessorHit(instruction)
        json_data = json_data.replace('&gt;','>')
        print json_data
#         exit()
        # fp = open("data/cp_output.json","r")
    #    json_data = json.loads(fp.read())
        # json_data = fp.read()
    #    GL.G = GL.parseGML(fp.read())
        # node_ids = ['11983']
        instruction_parser = instructionparser.InstructionParser()
        instruction_parser.parseInstruction(node_ids,json_data, concept_space)
    #    print json_data
#     cProfile.run('process()',None,2)
    process()
