__author__="Karan S. Sisodia"
__date__ ="$Oct 07, 2014 12:12:10 PM$"

import time
from database import graphdb
from py2neo import neo4j
from app import *

# Configuration File
Config = Config()
neo4j_path = str(Config.get('Database')['neo4j_path'])
db = graphdb.GraphDB(neo4j.GraphDatabaseService(neo4j_path))

class Autocomplete(object):
     
    def __int__(self):
        pass
       
    def searchChunkInNodes(self, params):
        """
        Function to get nodes from the db whos name contains the given chunk
        """
        start_time = int(round(time.time() * 1000))
        
        chunk = (params['search']).strip()
        
        f = []
        for x in params["fields"]:
            f.append("'"+x+"'")
            
        fields = " AND e.name IN ["+ ",".join(f) +"]" if params["fields"] else ""
        
        search_string = ("MATCH (x{name:'"+params["conceptspace"]+"'})-[:says]"
        "->(a{"+params['parent']['key']+":'"+str(params['parent']['value'])+"'})"
        " MATCH (a)-[*]->(b{obtainable:'True'})"
        " MATCH (b)-[relation:has]->(e)"
        " WHERE b.name =~ '.*"+chunk+".*'" + fields +
        " RETURN b as item_nodes, e as has_nodes, relation")
        #print search_string
        rows = db.executeQuery(search_string)
        #end_time = int(round(time.time() * 1000))
        has = {}
        for row in rows:
            node = row.item_nodes
            has_name = ((row.has_nodes).get_properties())['name']
            has_relation = row.relation
            has_relation_start_node = node._id #has_relation.start_node._id
            has_relation_properties = has_relation.get_properties()
            
            if not has_relation_start_node in has:
                has.update({has_relation_start_node: node.get_properties()})
                has[has_relation_start_node]['properties'] = {}
            properties = self.__prepareProperties({has_name: has_relation_properties})
            has[has_relation_start_node]['properties'].update(properties)

        end_time = int(round(time.time() * 1000))
        
        print "\n*Time Profile:*"
        print "Start Time: ", start_time, "ms"
        print "End Time: ", end_time, "ms"
        print "Time taken: ", end_time - start_time, "ms", "\n"
        #print has.values()
        return has.values()
    
    def getItemChildren(self, params):
        """
        Function to get all the children and their properties on the bases of given params
        """
        
        start_time = int(round(time.time() * 1000))
        query = ("MATCH (p{name:'"+params["conceptspace"]+"'})-[:says]"
        "->(k{"+params['parent']['key']+":'"+str(params['parent']['value'])+"'})"
        " MATCH (k)-[*]->(b)"
        " MATCH a = (b)-[:contains_group|says|contains_item|token*]->(h)"
        " WHERE b."+params['child']['key']+" = '" + str(params['child']['value']) + "'"
        " RETURN a as path")
        
        rows = db.executeQuery(query)
        
        if len(rows) > 0:
            hierarchy = self.__prepareChildren(rows, True)
                    
        end_time = int(round(time.time() * 1000))
        
        print "\n*Time Profile:*"
        print "Start Time: ", start_time, "ms"
        print "End Time: ", end_time, "ms"
        print "Time taken: ", end_time - start_time, "ms", "\n"
        
        return self.__prepareOutput(hierarchy.values())[0]
    
    def getCatalog(self, params):
        """
        Function to fetch full catalog from the DB and prepare the output
        """
        
        start_time = int(round(time.time() * 1000))
        
        query = ("MATCH (p{name:'"+params["conceptspace"]+"'})-[:says]->(k{"+params['parent']['key']+":'"+str(params['parent']['value'])+"'})"
        " MATCH a = (k)-[:contains_group|says*]->(b)"
        " WHERE b.type IN ['group','item']"
        " RETURN a as path")
        
        rows = db.executeQuery(query)
        
        if len(rows) > 0:
            hierarchy = self.__prepareChildren(rows)
        
        end_time = int(round(time.time() * 1000))
        
        print "\n*Time Profile:*"
        print "Start Time: ", start_time, "ms"
        print "End Time: ", end_time, "ms"
        print "Time taken: ", end_time - start_time, "ms", "\n"
        
        return self.__prepareOutput(hierarchy.values())[0]
    
    def __prepareChildren(self, rows, token_check = False):
        hierarchy = {}
        done_nodes = []
        for row in rows:
            path = row.path
            nodes = path.nodes
            
            parent_id = ""
            tkck = True
            for node in nodes:
                current_id = node._id
                has = {}
                if current_id not in done_nodes:
                    properties = node.get_properties()
                    
                    if token_check:
                        if properties['type'] <> 'hypergraph':
                            tkck = True
                        else:
                            tkck = False
                    
                    if tkck:
                        has = self.__getRelation("has", node)
                        if has:
                            properties["properties"] = has
                        
                        if hierarchy:
                            hierarchy = self.__insertRecursive(parent_id, current_id, hierarchy, properties)
                        else:
                            properties['children'] = {}
                            hierarchy[current_id] = properties
                        done_nodes.append(current_id)
                parent_id = current_id
        return hierarchy
    
    def __prepareOutput(self, hierarchy):
        """
        Function to prepare output: Remove Dictionary keys from the main dictionary
        """
        for i in hierarchy:
            if isinstance(i['children'], dict):
                i['children'] = i['children'].values()
                self.__prepareOutput(i['children'])
            elif isinstance(i['children'], list):
                for v in i['children']:
                    index = i['children'].index(v)
                    if 'type' not in v:
                        v = v.values()
                        del i['children'][index]
                        self.__prepareOutput(v)
                        (i['children']).insert(index,v)
        return hierarchy
            
    
    def __getRelation(self, relation_type, node):
        """
        Function to get out relations of a given node
        """
        
        has = {}
        for relation in node.match_outgoing(relation_type):
            relation_name = relation.end_node.get_properties()['name']
            relation_properties = relation.get_properties()
            has[relation_name] = self.__prepareSingleProperties(relation_properties)
            
        return has
        
    def __insertRecursive(self, parent_id, current_id, hierarchy, properties):
        """
        Function to recursively append child parent in a dictionary
        """
        
        if parent_id in hierarchy:
            properties['children'] = {}
            hierarchy[parent_id]['children'][current_id] = properties
        else:
            for k, v in hierarchy.iteritems():
                hierarchy[k]['children'] = self.__insertRecursive(parent_id, current_id, v['children'], properties)
            
        return hierarchy
    
    def __prepareSingleProperties(self, property_value):
        """
        Function to prepare single property at a time on the bases of unit/value
        """
        if property_value and isinstance(property_value, dict):
            if 'unit' not in property_value or not property_value['unit']:
                property_value = property_value['value']
        return property_value

    def __prepareProperties(self, properties):
        """
        Function to prepare property object on the bases of unit/value
        """
        for k, v in properties.iteritems():
            if isinstance(v, dict):
                if 'unit' not in v or not v['unit']:
                    properties[k] = v['value']

        return properties
    