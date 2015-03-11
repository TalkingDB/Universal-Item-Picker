'''
Created on Oct 14, 2014

@author: Karan S. Sisodia <karansinghsisodia@gmail.com>
'''
from Autocomplete import index as ac

if __name__ == '__main__':
    app = ac.Autocomplete()
    client_app_request_params = {
                                    "conceptspace": "foodweasel.com",
                                     "parent":{
                                         "key": "uid",
                                         "value": 752
                                     },
                                     "search": "iga",
                                     "fields": [
                                                "price"
                                                ]
                                 }
    app.searchChunkInNodes(client_app_request_params)

#     client_app_request_params = {
#                                     "conceptspace": "foodweasel.com",
#                                      "parent":{
#                                          "key": "uid",
#                                          "value": 752
#                                      },
#                                      "child":{
#                                          "key": "uid",
#                                          "value": "N128"
#                                      }
#                                  }
#      
#     print app.getItemChildren(client_app_request_params)

#     client_app_request_params = {
#                                     "conceptspace": "foodweasel.com",
#                                      "parent":{
#                                          "key": "uid",
#                                          "value": 752
#                                      }
#                                  }
#       
#     print app.getCatelog(client_app_request_params)