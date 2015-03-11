'''
Created on 14-Jul-2014

@author: Karan S. Sisodia
'''
from py2neo import neo4j, cypher, node, rel
import datetime

class GraphDB():
    '''
    Class to access graph db.
    '''
    
    def __init__(self, graph_db):
        """
        Constructor:
        
        @type graph_db: object
        @param graph_db: Graph db class object
        """
        if isinstance(graph_db, neo4j.GraphDatabaseService):
            self.db = graph_db
        else:
            raise ValueError('Class must be initialized with a GraphDatabaseService object')
        
    def checkIfNodeExists(self, label, graph_property):
        """
        Returns boolean, It checks wether a node exists or not
        
        @type label:  string
        @param label: Label of a node
        
        @type graph_property: dictionary
        @param graph_property: {
            key: "property key",
            value: "property value"
        }
        
        @rtype: boolean
        @return: True when node already exists and False in case of not exists.
        """
        node = list(self.db.find(label, property_key=graph_property['key'], property_value=graph_property['value']))
        return node
        
        
    def insertNodes(self, graph_property, label=None):
        """
        Returns inserted node. It inserts node in graph db.
        
        @type graph_property: dictionary
        @param graph_property:
        
        eg. 
        Insert Single Node:
        person = {"name": "Alice"}
        
        Insert Multiple Nodes:
        people = (
            {"name": "Alice", "age": 33}, {"name": "Bob", "age": 44},
            {"name": "Carol", "age": 55}, {"name": "Dave", "age": 66},
        )
        
        @rtype: dictionary
        @return: returns the inserted dictionaries.
        """
        node, = self.db.create(graph_property)
        if(label):
            node.add_labels(label);
        return node
    
    def insertNodesWithRelation(self, property_rel):
        """
        Insert node with relationship
        
        eg. 
        relation = (
            {"name": "Alice"}, {"name": "Bob"},
            (0, "KNOWS", 1, {"since": 2006})
        )
        
        @type property_rel: dictionary
        @param property_rel: Dictionary contains nodes and their relationship
        
        @rtype: dictionary
        @return: the inserted nodes
        """
        node_rel, = self.db.create(property_rel)
        return node_rel
    
#     #@profile
    def executeQuery(self, cyp):
        """
        Function to execute neo4j cypher query
        
        @type cyp: string
        @param cyp: Cypher string to be executed
        
        @rtype: dictionary
        @return: dictionary of {id:property} pair
        """
#         start_time = datetime.datetime.now()
        if cyp:
            query = neo4j.CypherQuery(self.db, cyp)
            a = query.execute()
#             end_time = datetime.datetime.now()
#             c = end_time - start_time
#             print cyp,';',c.microseconds 
#             print c.microseconds
#             print "----------------------------------------------------------"
            return a
        else:
            raise ValueError('cypher must not empty!')
        
    def deleteNode(self, node):
        """
        Function to delete node by ID
        """
        return node.delete()
    
    def jsonToGraph(self, data):
        """
        Function to insert NetwokeX json in neo4j db
        
        ## params:
        _data:_ neo4j json dict
        
        ## Example JSON
        {"directed": true, "graph": [["directed", 1]], 
        "nodes": [
            {"entity": "CommandNet:NewInstruction", "type": "hypergraph", "id": 0, "label": "CRLF"}, 
            {"entity": "CommandNet:UnitsOfX", "type": "hypergraph", "id": 1, "label": "2"}, 
            {"entity": "CommandNet:AlongWith", "type": "hypergraph", "id": 2, "label": ","}, 
            {"entity": "CommandNet:UnitsOfX", "type": "token", "id": 3, "label": "2"}, 
            {"entity": "CommandNet:VagueSizeOf", "type": "hypergraph", "id": 4, "label": "5"}, 
            {"entity": "CommandNet:AlongWith", "type": "hypergraph", "id": 5, "label": "on"}, 
            {"entity": "CommandNet:LessOf", "type": "hypergraph", "id": 6, "label": "7"}, 
            {"entity": "CommandNet:SizeLarge", "type": "token", "id": 7, "label": "large"}, 
            {"entity": "CommandNet:AlongWith", "type": "hypergraph", "id": 8, "label": "9"}, 
            {"entity": "DBPedia:Corned_beef", "type": "token", "id": 9, "label": "corned beef"}, 
            {"entity": "CommandNet:AlongWith", "type": "token", "id": 10, "label": "on"}, 
            {"entity": "DBPedia:Rye", "type": "token", "id": 11, "label": "rye"}, 
            {"entity": "CommandNet:LessOf", "type": "token", "id": 12, "label": "light"}, 
            {"entity": "DBPedia:Mustard", "type": "token", "id": 13, "label": "mustard"}, 
            {"entity": "DBPedia:Pizza", "type": "token", "id": 14, "label": "Cheese Pizza's"}, 
            {"entity": "DBPedia:Pepperoni", "type": "token", "id": 15, "label": "pepperoni"}
            ], 
        "links": [
            {"source": 0, "target": 1}, 
            {"source": 0, "target": 2}, 
            {"source": 1, "target": 3, "param": "object"}, 
            {"source": 1, "target": 4, "param": "subject"}, 
            {"source": 2, "target": 5, "param": "subject"}, 
            {"source": 2, "target": 6, "param": "object"}, 
            {"source": 4, "target": 8, "param": "subject"}, 
            {"source": 4, "target": 7, "param": "object"}, 
            {"source": 5, "target": 9, "param": "subject"}, 
            {"source": 5, "target": 10}, 
            {"source": 5, "target": 11, "param": "object"}, 
            {"source": 6, "target": 12, "param": "object"}, 
            {"source": 6, "target": 13, "param": "subject"}, 
            {"source": 8, "target": 14, "param": "subject"}, 
            {"source": 8, "target": 15, "param": "object"}
            ], 
        "multigraph": false}
        
        TODO: Determine the root node
        """
        map = {}
        batch = neo4j.WriteBatch(self.db)
        for n in data['nodes']:
            id = n['id']
            del n['id']
            res = batch.create(node(n))
            
        i = 0;
        for n in batch.submit():
            map[i] = n._id
            i += 1
        batch.clear()
        
        for r in data['links']:
            source = self.db.node(map[r['source']])
            target = self.db.node(map[r['target']])
            
            del r['source']
            del r['target']
            
            batch.create(rel((source, "CommandNet:Relation", target, r)))
        batch.submit()
        batch.clear()
        return map
    
    def generateDummyGraph(self):
        batch = neo4j.WriteBatch(self.db)

        batch.create(node({'name': 'Price Group'}))
        batch.create(node({'name': 'King Size'}))
        batch.create(rel(0, "contains_item", 1))
        
        # batch.create(node({'name': 'delivery.com'}))
        # batch.create(node({'name': 'kfc'}))
        # batch.create(node({'name': 'Monday Lunch Special'}))
        # batch.create(node({'name': 'Monday Lunch Special'}))
        # batch.create(node({'name':'cheese pizza', 'obtainable': 'true'}))
        
        # batch.create(node({'name': 'MCDonalds'}))
        # batch.create(node({'name':'Classics and McSPICY'}))
        # batch.create(node({'name':'Non-veg'}))
        
        # batch.create(node({'name':'McSpicy Chicken Burger', 'obtainable': 'true'}))
        # batch.create(node({'name':'Chicken Maharaja Burger', 'obtainable': 'true'}))
        
        # batch.create(node({'name': "Beverages"}))
        # batch.create(node({'name': 'Pepsi', 'obtainable': 'true'}))
        
        # batch.create(node({'name':'Toppings'}))
        # batch.create(node({'name':'Pepperoni'}))
        # batch.create(node({'name':'Cheese'}))
        # batch.create(node({'name':'Tomato'}))
        
        # batch.create(node({'name':'Size'}))
        # batch.create(node({'name':'Small'}))
        # batch.create(node({'name':'Medium'}))
        # batch.create(node({'name':'Large'}))
        
        # batch.create(rel(0, "says", 1))
        # batch.create(rel(1, "contains_group", 2))
        # batch.create(rel(2, "contains_group", 3))
        # batch.create(rel(3, "says", 4))
        
        # batch.create(rel(0, "says", 5))
        # batch.create(rel(5, "contains_group", 6))
        # batch.create(rel(6, "contains_group", 7))
        # batch.create(rel(7, "says", 8))
        # batch.create(rel(7, "says", 9))
        # batch.create(rel(5, "contains_group", 10))
        # batch.create(rel(10, "says", 11))
        
        
        # batch.create(rel(4, "contains_group", 12))
        # batch.create(rel(12, "contains_item", 13))
        # batch.create(rel(12, "contains_item", 14))
        # batch.create(rel(12, "contains_item", 15))
        
        # batch.create(rel(4, "contains_group", 16))
        # batch.create(rel(16, "contains_item", 17))
        # batch.create(rel(16, "contains_item", 18))
        # batch.create(rel(16, "contains_item", 19))
        
        return batch.submit()

#For Development/Debuging Perpos only        
#app = GraphDB(neo4j.GraphDatabaseService("http://localhost:7474/db/data/"))
#query = ("START b=node(1)"
#"MATCH (a {obtainable:'true'})<-[:says]-(c)<-[:contains_group*]-(b)"
#" RETURN id(a), a")
#print app.executeQuery(query)