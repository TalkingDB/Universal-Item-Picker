# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__="Karan S. Sisodia"
__email__="karansinghsisodia@gmail.com"
__date__ ="$Sep 20, 2014 11:37:09 AM$"

import ConfigParser
import os

class Config():
    
    def __init__(self):
        self.config = ConfigParser.ConfigParser()
        self.config.read(os.path.dirname(os.path.realpath(__file__)) + '/config.ini')
        
    def get(self, section):
        dict1 = {}
        options = self.config.options(section)
        for option in options:
            try:
                dict1[option] = self.config.get(section, option)
                if dict1[option] == -1:
                    DebugPrint("skip: %s" % option)
            except:
                print("exception on %s!" % option)
                dict1[option] = None
        return dict1
