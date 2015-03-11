__author__="Karan S. Sisodia"
__email__="karansinghsisodia@gmail.com"
__date__ ="$Sep 15, 2014 1:22:06 PM$"

from GraphLib.index import *
import networkx as nx
import json
import cProfile
from time import gmtime, strftime

if __name__ == "__main__":
    gl = GraphLib()
    
    gl.addNode(1, {'type': 'hypergraph', 'entity': 'CommandNet:NewInstruction', 'label': 'CRLF'})
    gl.addNode(2, {'type': 'hypergraph', 'entity': 'CommandNet:UnitsOfX'})
    gl.addNode(3, {'type': 'hypergraph', 'entity': 'CommandNet:AlongWith', 'label':','})
    
    gl.addNode(4, {'type': 'token', 'entity': 'CommandNet:UnitsOfX', 'label':'2'})
    gl.addNode(5, {'type': 'hypergraph', 'entity': 'CommandNet:VagueSizeOf'})
    gl.addNode(6, {'type': 'hypergraph', 'entity': 'CommandNet:AlongWith', 'label':'on'})
    gl.addNode(7, {'type': 'hypergraph', 'entity': 'CommandNet:LessOf'})
    
    gl.addNode(8, {'type': 'token', 'entity': 'large', 'label':'large'})
    gl.addNode(9, {'type': 'hypergraph', 'entity': 'CommandNet:AlongWith'})
    gl.addNode(10, {'type': 'token', 'entity': 'DBPedia:Corned_beef', 'label':'corned beef'})
    gl.addNode(11, {'type': 'token', 'entity': 'CommandNet:AlongWith', 'label':'on'})
    gl.addNode(12, {'type': 'token', 'entity': 'DBPedia:Rye', 'label':'rye'})
    gl.addNode(13, {'type': 'token', 'entity': 'CommandNet:LessOf', 'label':'light'})
    gl.addNode(14, {'type': 'token', 'entity': 'DBPedia:Mustard', 'label':'mustard'})
    
    gl.addNode(15, {'type': 'token', 'entity': 'DBPedia:Pizza', 'label':'Cheese Pizza\'s'})
    gl.addNode(16, {'type': 'token', 'entity': 'DBPedia:Pepperoni', 'label':'pepperoni'})
    
    
    gl.addRelation((1, 2), {})
    gl.addRelation((1, 3), {})
    gl.addRelation((2, 4), {'param':'object'})
    gl.addRelation((2, 5), {'param':'subject'})
    gl.addRelation((3, 6), {'param':'subject'})
    gl.addRelation((3, 7), {'param':'object'})
    gl.addRelation((5, 8), {'param':'object'})
    gl.addRelation((5, 9), {'param':'subject'})
    gl.addRelation((6, 10), {'param':'subject'})
    gl.addRelation((6, 11), {'param':'subject'})
    gl.addRelation((6, 12), {'param':'object'})
    gl.addRelation((7, 13), {'param':'object'})
    gl.addRelation((7, 14), {'param':'subject'})
    gl.addRelation((9, 15), {'param':'subject'})
    gl.addRelation((9, 16), {'param':'object'})

#    gl.addNode(1, {'type': 'hypergraph', 'entity': 'CommandNet:NewInstruction', 'label': 'CRLF'})
#    gl.addNode(2, {'type': 'token', 'entity': 'DBPedia:Pepperoni', 'label': 'Pepperoni'})
#    gl.addRelation((1, 2), {})
#    
#    gl.addNode(3, {'type': 'hypergraph', 'entity': 'CommandNet:NewInstruction', 'label': 'CRLF'})
#    gl.addNode(4, {'type': 'token', 'entity': 'DBPedia:Tomato', 'label': 'Tomato'})
#    gl.addRelation((3, 4), {})
#    
#    gl.addNode(5, {'type': 'hypergraph', 'entity': 'CommandNet:NewInstruction', 'label': 'CRLF'})
#    gl.addNode(6, {'type': 'token', 'entity': 'DBPedia:Cheese', 'label': 'Cheese'})
#    gl.addRelation((5, 6), {})
#    
#    gl.addNode(7, {'type': 'hypergraph', 'entity': 'CommandNet:NewInstruction', 'label': 'CRLF'})
#    gl.addNode(8, {'type': 'token', 'entity': 'large', 'label': 'large'})
#    gl.addRelation((7, 8), {})
#    
#    gl.addNode(9, {'type': 'hypergraph', 'entity': 'CommandNet:NewInstruction', 'label': 'CRLF'})
#    gl.addNode(10, {'type': 'token', 'entity': 'medium', 'label': 'medium'})
#    gl.addRelation((9, 10), {})
#    
#    gl.addNode(11, {'type': 'hypergraph', 'entity': 'CommandNet:NewInstruction', 'label': 'CRLF'})
#    gl.addNode(12, {'type': 'token', 'entity': 'small', 'label': 'small'})
#    gl.addRelation((11, 12), {})
    
#    nx.write_graphml(gl.G, "/home/sb/Desktop/Dummy output of CommandNet Processor/yedoutput.gml")
    
    out = gl.gmlOutput()
#    print out
    
    gl.G = gl.parseGML(out)
#    gl.getInstructions()
#    print gl.getChildNodes(1, "param:object")
#    print gl.getChildNodes(1)
#    cProfile.run('gl.getChildNodes(1, "param:subject")')
#    print gl.getLeafNodesByCommand(1, 'DBPedia')
#    cProfile.run("print gl.getLeafNodesByCommand(1, 'DBPedia')")
#    gl.drawGraph()
#    print  json.dumps(gl.jsonOutput())
    # data =  gl.jsonOutput()

    print gl.searchNode(1,('entity', 'DBPedia:Pizza'))
    
# from database import graphdb
# from py2neo import neo4j
# app = graphdb.GraphDB(neo4j.GraphDatabaseService("http://localhost:7474/db/data/"))

#app.jsonToGraph(data)
#cProfile.run("print app.jsonToGraph(data)")
    
# app.generateDummyGraph()
    
#    print gl.jsonOutput()
#    
#    print gl.jsonOutput()
#    print gl.getSubjectLeaves()
