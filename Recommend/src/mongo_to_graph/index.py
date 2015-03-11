# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__="anik"
__date__ ="$10 Sep, 2014 2:07:53 PM$"


#Database
from database import mongodb
from database import graphdb
from py2neo import neo4j
import entity_model
from time import gmtime, strftime

graph_db = neo4j.GraphDatabaseService("http://192.168.1.146:7474/db/data/")

Database = mongodb.MongoDB()
GraphDatabase = graphdb.GraphDB(graph_db)
Mongodb = Database.connect()
EntityModel = entity_model.EntityModel(Mongodb)

if __name__ == "__main__":
#    entity = EntityModel.select_all()
    types = []
#    graph_nodes = ()
    data = dict()
#    graph_nodes.__add__(a, b)
    t = []
    i = 0
    
    print strftime("%Y-%m-%d %H:%M:%S", gmtime())
    print 'Processing...'
    for type in EntityModel.select_all().batch_size(1000):
        if not GraphDatabase.checkIfNodeExists('training_data',{'key':'name','value':type['name']}):
            GraphDatabase.insertNodes({'name':type['name'],'dbpedia_url':type['dbpedia_url']},'training_data')
    
    print 'Process Completed'
    print strftime("%Y-%m-%d %H:%M:%S", gmtime())
