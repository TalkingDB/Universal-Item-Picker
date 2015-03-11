# -*- coding: utf-8 -*-
__author__="Atul Tagra<atul@ignitras.com>"
__date__ ="$20 Oct, 2014 2:47:55 PM$"

from py2neo import neo4j, rel
from database import graphdb
import explainInstruction as exp
import time
import sys
import traceback
import config as c

class separateNER():
    def __init__(self):
        self.dbObj = neo4j.GraphDatabaseService()
        self.graphdblib = graphdb.GraphDB(self.dbObj)
        self.explain = exp.explain(self.graphdblib)

        print("Process Started at ",time.ctime(time.time()))
        
        rows =  self.getCountRows()
        
        for y in range(rows):
            self.coreNER(y*c.chunkSize,c.chunkSize)
        
        print("Process Completed at ",time.ctime(time.time()))
    
    def getCountRows(self):
        cypCount = ('Match (n)'
            ' WHERE n.type = "item" OR n.type = "option"'
            ' RETURN COUNT(n)')
            
#        To test soda obtainable #2224
#        cypCount = 'start n = node(*) where n.name =~ ".*Soda.*" return count(n)'
        res = self.graphdblib.executeQuery(cypCount)
        resCount = res[0].values[0]
        
        retMod = resCount % c.chunkSize
        
        ret = resCount / c.chunkSize
        
        if(retMod > 0):
            ret += 1
        
        return ret
    
    def coreNER(self,skip,limit):
        print '-'*60
        print skip,limit
        print '-'*60
        
        #        To test soda obtainable #2224
#        cyp = 'START n = node(*) where n.name =~ ".*Soda.*" RETURN n ORDER BY n.name DESC SKIP %d LIMIT %d' % (skip,limit) 
        
        cyp = 'Match (n) WHERE n.type = "item" OR n.type = "option" RETURN n ORDER BY n.name DESC SKIP %d LIMIT %d' % (skip,limit) 
        res = self.graphdblib.executeQuery(cyp)
        for x in res:
            try:
                name = (x.values[0].get_cached_properties()['name']).strip()
                print name
                resExp = self.explain.processExplanation(name,"foodweasel.com",x.values[0]._id)
                self.dbObj.create(rel(self.dbObj.node(x.values[0]._id),'token',self.dbObj.node(resExp)))
            except UnicodeDecodeError:
                print name + ' is a unicode string'
            except Exception as e:
                print e
                print "Exception in user code:"
                print '-'*60
                traceback.print_exc(file=sys.stdout)
                print '-'*60