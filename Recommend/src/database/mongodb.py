__author__="Karan S. Sisodia"
__email__="karansinghsisodia@gmail.com"
__date__ ="$Jun 6, 2014 9:01:10 AM$"

import peewee
import datetime
from peewee import *

from pymongo import MongoClient

class MongoDB():
    
    def connect(self):
        client = MongoClient()
        client = MongoClient('localhost', 27017)
        db = client['FoodWeaselData']
        return db
