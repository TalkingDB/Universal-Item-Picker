# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__="Karan S. Sisodia"
__email__="karansinghsisodia@gmail.com"
__date__ ="$Sep 20, 2014 11:16:27 AM$"

import unittest
from app import Config
from py2neo import neo4j

from graphdb import GraphDB


class TestDatabase(unittest.TestCase):

    def setUp(self):
        self.config = Config()
        self.db_url = self.config.get('Database')['neo4j_path']
        
        if not self.db_url:
            self.skipTest("Database URL Not Found.")
           
        self.db_instance = neo4j.GraphDatabaseService(self.db_url)
        
        if not isinstance(self.db_instance, neo4j.GraphDatabaseService):
            self.skipTest("Problem detacted during db connection.")
            
        self.db = GraphDB(self.db_instance)
        
        self.node = ''


    def test_insert_node(self):
        """
        Function to test Neo4j node insertion
        """
        self.node = self.db.insertNodes({'name':'test_node'}, 'testing')
        
        if not isinstance(self.node, neo4j.Node):
            self.skipTest("Problem inserting node.")
    
    def tearDown(self):
        self.db.deleteNode(self.node)

if __name__ == '__main__':
    unittest.main(verbosity=2)