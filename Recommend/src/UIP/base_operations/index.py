__author__="Karan S. Sisodia"
__email__="karansinghsisodia@gmail.com"
__date__ ="$Sep 10, 2014 4:27:23 PM$"

import json
import instructionparser
from GraphLib import index as gl

GL = gl.GraphLib()

if __name__ == "__main__":
    fp = open("../../data/cp_output.json","r")
#    json_data = json.loads(fp.read())
    json_data = fp.read()
#    GL.G = GL.parseGML(fp.read())
    node_ids = ['13','2']
    instruction_parser = instructionparser.InstructionParser()
    instruction_parser.parseInstruction(node_ids,json_data)
#    print json_data
    pass
