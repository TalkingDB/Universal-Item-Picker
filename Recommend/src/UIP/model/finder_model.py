__author__="anik"
__date__ ="$16 Sep, 2014 5:14:00 PM$"

from py2neo import neo4j, cypher, node, rel
import datetime

class FinderModel():
    
    def __init__(self,GraphDatabase):
        self.GraphDatabase = GraphDatabase
        self.data = {}
        self.current_id_found = False


    def getNodeIdsByConceptSpaceAndKeyValue(self,concept_space,key,values):
#         query = ("MATCH (a{name:'" + concept_space + "'})-[:says]->(b{type:'parent_group'})"
#             "WHERE b."+key+" IN ['" +"','".join(values)+ "']"
#             "RETURN id(b)")
        query = ("MATCH (a:ConceptSpace)-[:says]->(b:ParentGroup)"
            " WHERE b."+key+" IN ['" +"','".join(values)+ "']"
            " RETURN id(b) as node_id")
#         print query
#         exit()
        data = self.GraphDatabase.execute(query)
#         for x in data :
#             print x
#         print data
#         exit()
        node_ids = []
        for row in data:
#             print row.node_id
            node_ids.append(row[0])
#         print node_ids
#         exit()
        return node_ids

    def findNodeChildren(self, all_node_ids, selected,add_new_keys, concept_space):
        """
        Function to find all children nodes and their properties
        which is connected by [:has] relation and attributes
        """
#         print selected
#         print add_new_keys
#         exit()
#         start_time = datetime.datetime.now()
        separated_node_ids = ",".join(str(x) for x in all_node_ids)
#         node_ids = all_node_ids.j

#         query = ("START n = node("+separated_node_ids+")"
#                  "MATCH (q)-[:says]->(parent_group)"
#                  "MATCH (parent_group)-[:contains_group]->(item_groups)"
#                  "MATCH p = (item_groups)-[*]->(n)-[*]->(a)"
#                  "WHERE q.name = '"+concept_space+"'"
#                  "and parent_group.type = 'parent_group'"
#                  "and (a)-[:token]->()"
#                  "RETURN p as path")


#         query = ("START n = node("+separated_node_ids+")"
#                  "MATCH (q)-[:says]->(parent_group)"
#                  "MATCH (parent_group)-[:contains_group]->(item_groups)"
#                  "MATCH p = (item_groups)-[*]->(n)-[:contains_group|contains_item|token*]->(a)"
#                  "WHERE q.name = '"+concept_space+"'"
#                  "and parent_group.type = 'parent_group'"
#                  "RETURN p as path")
        
        query = (
#                  "START n = node("+separated_node_ids+")"
#                  "MATCH (q)-[:says]->(parent_group:ParentGroup)"
#                  "MATCH (parent_group)-[:contains_group]->(item_groups:Group)"
                 "MATCH p = (item_groups:Group)-->(n)-[:contains_group|contains_item|token*]->(a)"
                 " WHERE id(n) in ["+separated_node_ids+"]"
                 " RETURN nodes(p), EXTRACT(n in nodes(p) | ID(n))")

#         print "DEADLY - ", query
#         exit()
        
        hierarchy, has = {}, {}
        done_nodes = []
        
        rows = self.GraphDatabase.execute(query)
#         print "DEADLY DONE"
#         print rows.rowcount
#         exit()
#         end_time = datetime.datetime.now()
#         c = end_time - start_time
#         print c.microseconds
#         exit() 
        for row in rows.fetchall():
#             print row
#             exit()
            nodes = row[0]
#             print nodes
#             exit()
            parent_id = ""
            item_id = ""
            for node in nodes:
#                     print node
#                     exit()
                properties = node
                if properties['type'] <> 'hypergraph':
                    current_id = row[1][nodes.index(node)]
                    has = {}
                    if properties['type'] == 'item':
                        item_id = current_id
                        if item_id in add_new_keys :
                            properties = dict(properties, **add_new_keys[item_id])
                    if current_id not in done_nodes:
                        
                        self.current_id_found = False
                        has = self.__getRelation("has", current_id)
                        if has:
                            properties["properties"] = has
                        
                        if item_id <> "" and item_id in selected and current_id in selected[item_id]:
                            properties['selected'] = 1
                        else:
                            properties['selected'] = 0
                        
                        if hierarchy:
                            hierarchy = self.__insertRecursive(parent_id, current_id, hierarchy, properties)
                            if not self.current_id_found:
                                properties['children'] = {}
                                hierarchy[current_id] = properties
                        else:
                            properties['children'] = {}
                            hierarchy[current_id] = properties
                    
                    done_nodes.append(current_id)
                    parent_id = current_id
#                     print hierarchy
#         print hierarchy
#         print rows.rowcount
#         exit()
        return hierarchy
    
    def __getRelation(self, relation_type, node_id):
        """
        Function to get out relations of a given node
        """
        query = (
                "START n = node("+str(node_id)+")"
                "MATCH (n)-[r:"+relation_type+"]->(a)"
                "return a,r"
                 )
#         print query
        rows = self.GraphDatabase.execute(query)
        has = {}
        for i in rows.fetchall() :
#             print "Printing i ->", i
            relation_name = i[0]['name']
            relation_properties = i[1]
            has[relation_name] = self.__prepareSingleProperties(relation_properties)
        
        return has

    def __prepareSingleProperties(self, property_value):
        """
        Function to prepare single property at a time on the bases of unit/value
        """
        if property_value and isinstance(property_value, dict):
            if 'unit' not in property_value or not property_value['unit']:
                property_value = property_value['value']
        else :
            property_value = ""
        return property_value

    
    def __insertRecursive(self, parent_id, current_id, hierarchy, properties):
        if parent_id in hierarchy:
            self.current_id_found = True
            properties['children'] = {}
            hierarchy[parent_id]['children'][current_id] = properties
        else:
            for k, v in hierarchy.iteritems():
                hierarchy[k]['children'] = self.__insertRecursive(parent_id, current_id, v['children'], properties)
            
                
        return hierarchy
    
    def prepareList(self,hierarchy):
#         print hierarchy
#         exit()
        for i in hierarchy:
            i['children'] = i['children'].values()
            self.prepareList(i['children'])
        return hierarchy
#         for k, v in hierarchy.iteritems():
#             print v['children']
#             exit()
#             if isinstance(v, dict):
#                 self.prepareList(v)
#             else:
#                 print v
#                 exit()
#                 return v.values()


    def __prepareProperties(self, properties):
        """
        Function to prepare property object on the bases of unit/value
        """

        for k, v in properties.iteritems():
            if isinstance(v, dict):
                if 'unit' not in v or not v['unit']:
                    properties[k] = v['value']

        return properties


    def __prepareProperties_temp(self, node_id, properties, selected, has):
        """
        Function to prepare property object (dict)
        """

        name, type_of_node, obtainable = '', '', ''

        if 'name' in properties:
            name = properties['name']
            del properties['name']

        if 'type' in properties:
            type_of_node = properties['type']
            del properties['type']

        if 'obtainable' in properties:
            obtainable = properties['obtainable']
            del properties['obtainable']

        if node_id in has:
            for k, v in (has[node_id]).iteritems():
                if isinstance(v, dict):
                    if 'unit' not in v or not v['unit']:
                        has[node_id][k] = v['value']
            properties.update(has[node_id])

        return {
            'name': name,
            'type': type_of_node,
            'obtainable': obtainable,
            'properties': properties,
            'selected': 1 if node_id in selected else 0
        }

    def getNodeDetails(self, node_id):
        """
        Function to get all the details of node and its connected children with
        [:has] relation
        """
        query = ("START n = node("+str(node_id)+")"
        "MATCH (n)-[relation:has]-(b)"
        "RETURN n, b, relation")

        properties, has = {}, {}
        rows = self.GraphDatabase.execute(query)

        properties = rows.fetchone()[0]
        for row in rows:
            relation_property = row[2]
#             print relation_property
            if relation_property :
                if 'unit' in relation_property and relation_property['unit']:
                    has[row[1]['name']] = relation_property
                else:
                    has[row[1]['name']] = relation_property['value']
            
        return properties, has

    def getOptionParentNode(self, node_id):
        query = ("START n = node("+str(node_id)+")"
            "MATCH (n)<-[*]-(a)-[:says]-()"
            "MATCH (a)-[:token]->(q{command:'CommandNet>NewInstruction'})-[:`CommandNet>Relation`*]->(token)"
            "RETURN a, token, id(a)")
#         print query
#         exit()
        data = self.GraphDatabase.execute(query)
        data_detail = data.fetchone()
        node_detail = data_detail[0]
        id_detail = {'id':data_detail[2]}
        # print data[0].values[1]
        # exit()
        tokens = []
        for row in data :
            if "entity" in row[1] :
                tokens.append(",".join((row[1])['entity']))

        # print tokens
        # exit()


        return_data = {
        'search_node' : dict(node_detail, **id_detail),
        'tokens' : tokens
        }
        return return_data

    def selectAllParentNode(self, node_ids):
        for nid in node_ids:
            query = ("START n = node("+str(nid)+")"
            "MATCH  (n)<-[:contains_item]-(a)<-[:contains_group]-(b)<-[:contains_item]-(c)<-[:contains_group]-()"
            "RETURN id(c) as node_id")
#             print query
#             exit()
            data = self.GraphDatabase.execute(query)
            for i in data:
                node_ids.append(i[0])

        return node_ids


    def findPathLength(self, start_node_id, end_node_id):
        query = ("START n = node(" + str(start_node_id) + "), m = node(" + str(end_node_id) + ")"
        "MATCH p = (n)<-[*]-(m)"
        "return length(p) as length")
#         print query
        # exit()
        length = self.GraphDatabase.execute(query)
        return self.__filterLengthForOption(length.fetchone()[0])

    def __filterLengthForOption(self, length):
        return length/2

    def findConceptSpaceParentNode(self, concept_space, node_id):
        """
        This function will find the node which is connected to the concept space
        and got the child with the specified node id
        Example - Concept space can be foodweasel.com. So in this case we will find
        the node id which is connected to the node named foodweasel.com (Concept space
        node) and has got a child with the specified node id.
        """
        query = ("START n = node("+str(node_id)+")"
        "MATCH (a:`"+concept_space+"`)-[:says]->(b)-[*]->(n)"
        "return id(b)")
#         print query
#         exit()
        result = self.GraphDatabase.execute(query)
        return result.fetchone()[0]
    
#     #@profile
    def findOptionNodes(self,item_node_id,tokens):
        
        query = (
                 " MATCH (b)-[:contains_group|contains_item*]->(option_group:OptionGroup)"
                 " WHERE id(b) = " + str(item_node_id) +
                 " MATCH (option_group)-[:contains_item]->(c:Option)"
                 " MATCH (c)-[:has_token]->(t)"
                 " WHERE " + " or ".join(["t:`"+ i +"`" for i in tokens]) +
                 " MATCH (token)<-[:has_token]-(c)"
                 " MATCH (option_group)-[max_selection:has]->(f{name:'max_selection'})"
                 " RETURN id(c), c, token, id(token),id(option_group),max_selection")
#         print "OPTIONS - ", query
#         exit()
        item_data = self.GraphDatabase.execute(query)
#         if item_data:
#         print query
#             exit()
        return self.__prepareOptionData(item_data)
    
    def findNodesByNodeIds(self,separated_node_ids,leaves, pass_bucket_id):
        """
        Function to get all the nodes from graph database by node ids. It check
        property obtainable as true for item node and it matches the token of
        user whether any of them is connected to the item node.
        """
#         print "','".join(pass_bucket_id)
#         exit()
        query = (
        " MATCH (t:Token)"
        " WHERE " + " or ".join(["t:`"+ i +"`" for i in leaves]) +
        " MATCH (a:Obtainable{obtainable:'True'})-[:has_token]->(t)"
        )
        query += " WHERE NOT id(a) IN [" +",".join(pass_bucket_id)+ "]" if pass_bucket_id else ""
        
        query += (
                  
                  " MATCH (b)-[:has_obtainable]->(a)"
                  " WHERE id(b) in ["+separated_node_ids+"]"
                  " MATCH (a)-[:has_token]->(token)"
                  " RETURN DISTINCT id(a), a, token, id(token)")
        
        print query
#         exit()
        item_data = self.GraphDatabase.execute(query)
        return self.__prepareData(item_data)
        
    def findNodesByName(self,separated_node_ids, text):
        """
        Find all nodes which have exact match to user instruction
        """
        query = (
#                  "START b=node("+separated_node_ids+")"
                 " MATCH (a:`"+text.lower()+"`)"
                 " MATCH (b)-[:has_obtainable]->(a)"
                 " WHERE id(b) in ["+separated_node_ids+"]"
                 " RETURN a, id(a)"
                 )
        item_data = self.GraphDatabase.execute(query)
        return self.__prepareDataForExactMatch(item_data)
        
    def __prepareDataForExactMatch(self, item_data):
        exhausted_id = []
        return_data = []
        search_node = {}
        item_data_final = {}
        token_nodes = []
        token_list = []
        check = True
#         print "here"
        item_data_length = item_data.rowcount
#         print item_data_length
        j = 0
        for i in item_data.fetchall():
            j += 1
            search_node_id = i[1]
            if search_node_id not in exhausted_id:
                if not check:
                    self.__prepareReturnData(item_data_final,token_nodes,return_data,token_list)
                check = False
                item_data_final = {}
                token_nodes = []
                token_list = []
                exhausted_id.append(search_node_id)
                search_node = i[0]
                search_node["id"] = search_node_id
                item_data_final["search_node"] = search_node
            if(j==item_data_length):
                self.__prepareReturnData(item_data_final,token_nodes,return_data,token_list)
        return return_data
    
    
    
    
    def __prepareData(self, item_data):
        exhausted_id = []
        return_data = []
        search_node = {}
        item_data_final = {}
        token_nodes = []
        token_list = []
        check = True
        item_data_length = item_data.rowcount
        j = 0
        for i in item_data:
            j += 1
            search_node_id = i[0]
            if search_node_id not in exhausted_id:
                if not check:
                    self.__prepareReturnData(item_data_final,token_nodes,return_data,token_list)
                check = False
                item_data_final = {}
                token_nodes = []
                token_list = []
                exhausted_id.append(search_node_id)
                search_node = i[1]
                search_node["id"] = i[0]
                item_data_final["search_node"] = search_node
                self.__processCurentTokenNode(i,token_nodes,token_list)
            else :
                self.__processCurentTokenNode(i,token_nodes,token_list)
            if(j==item_data_length):
                self.__prepareReturnData(item_data_final,token_nodes,return_data,token_list)
#         print return_data
#         exit()
        return return_data
    
#     #@profile
    def __prepareOptionData(self, item_data):
        exhausted_id = []
        return_data = []
        search_node = {}
        item_data_final = {}
        token_nodes = []
        token_list = []
        check = True
        item_data_length = item_data.rowcount
        j = 0
        for i in item_data:
            j += 1
            search_node_id = i[0]
            if search_node_id not in exhausted_id:
                if not check:
                    self.__prepareReturnData(item_data_final,token_nodes,return_data,token_list)
                check = False
                item_data_final = {}
                token_nodes = []
                token_list = []
                exhausted_id.append(search_node_id)
                search_node = i[1]
                search_node["id"] = i[0]
                item_data_final["search_node"] = search_node
                item_data_final["option_group"] = {'id':i[4],'max_selection':i[5]['value']}
                self.__processCurentTokenNode(i,token_nodes,token_list)
            else :
                self.__processCurentTokenNode(i,token_nodes,token_list)
            if(j==item_data_length):
                self.__prepareReturnData(item_data_final,token_nodes,return_data,token_list)
        return return_data
    
    def __processCurentTokenNode(self,i,token_nodes,token_list):
        """
        Function to process current node token, insert its id in the dictionary
        and append the data in token node list
        """
        current_token_node = i[2]
        current_token_node["id"] = i[3]
        token_nodes.append(current_token_node)
#         print current_token_node["entity"]
#         exit()
        if "entity" in current_token_node :
            for token in current_token_node["entity"]:
                token_list.append(token)
#         token_list.append(",".join(current_token_node["entity"]))
#         token_list.append(current_token_node["entity"])
    
    def __prepareReturnData(self,item_data_final,token_nodes,return_data,token_list):
        """
        Function to process the return data. It inserts token nodes data and
        list of all the tokens and append the resulting data in a list.
        """
        item_data_final["token_node"] = token_nodes
        item_data_final["tokens"] = token_list
        return_data.append(item_data_final)
