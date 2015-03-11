# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__="Karan S. Sisodia"
__email__="karansinghsisodia@gmail.com"
__date__ ="$Sep 22, 2014 4:53:53 PM$"

import time
import cProfile

class TimeLogger():
    def __init__(self):
        pass
    
    def start(self):
        for i in range(0,10):
            time.sleep(0.5)
    
    def stop(self):
        pass
    
app = TimeLogger()

cProfile.run('app.start()')
