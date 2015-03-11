__author__="Anik Goel"
__email__="anik.goel@solutionbeyond.net"
__date__ ="$Oct 08, 2014 3:24:23 PM$"


import socket
from model import finder_model
from database import graphdb
# from py2neo import neo4j
from app import *

import neo4j

Config = Config()
db_url = str(Config.get('Database')['neo4j_path'])

class UserInstruction():

    def __init__(self):
        connection = neo4j.connect(db_url)

        GraphDatabase = connection.cursor()

        self.finderModel = finder_model.FinderModel(GraphDatabase)

    def commandProcessorHit(self,arg):
        """
        Function to hit command processor socket
        to fetch NER response as GML
        """
        s = socket.socket()
        ip = str(Config.get('NER')['ip'])
        port = int(Config.get('NER')['port'])
        
        s.connect((ip, port))
        s.send(arg)
        buff = ''
        while True:
            buf = s.recv(4096)
            if not buf:
                break
            else:
                buff += buf
        result = repr(buff)
        return result.strip("'")  

    def findNodeIds(self, concept_space, key, values):
        return self.finderModel.getNodeIdsByConceptSpaceAndKeyValue(concept_space, key, values)

