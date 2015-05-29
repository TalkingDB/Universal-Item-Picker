from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from Autocomplete import index as ac
import json
import traceback, sys
autocomplete = ac.Autocomplete()
import os
root_dir_path = os.path.expanduser("~/Smarter.Codes/")


class Autocomplete(APIView):
    """
    List all snippets, or create a new snippet.
    """
    #authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)

    def post(self, request, action, format=None):
        conceptspace = request.user.username
        request_data = json.loads(request.DATA['params'])
        request_data['conceptspace'] = conceptspace
        
        method = getattr(self, action)
        result = method(request_data)
        
        content = dict(result, **{
            'api_version': '2.0',
            'conceptspace': conceptspace
        })
        return Response(content)
    
    def suggestions(self, request_data):
        return_data = {}
        return_data['data'] = []
        try:
            return_data['data'] = autocomplete.searchChunkInNodes(request_data)
        except Exception as e:
            print '-'*60
            print "Autocomplete/Suggestions"
            print '-'*60
            
            traceback.print_exc(file=sys.stdout)
            print '-'*60
            return_data['error'] = "Error: "+ str(e)
            
        return return_data
    
    def itemdetails(self, request_data):
        return_data = {}
        return_data['data'] = []
        try:
            return_data['data'] = autocomplete.getItemChildren(request_data)
        except Exception as e:
            print '-'*60
            print "Autocomplete/Itemdetails"
            print '-'*60
            
            traceback.print_exc(file=sys.stdout)
            print '-'*60
            return_data['error'] = "Error: "+ str(e)
            
        return return_data
    
    def catalog(self, request_data):
        return_data = {}
        return_data['data'] = []
#         return_data['data'] = autocomplete.getCatalog(request_data)
        res_id = str(request_data['parent']["value"])+".json"

        if os.path.isfile(root_dir_path+ "customer_files/foodweasel.com/converted_files/"+res_id):
            with open(root_dir_path+ "customer_files/foodweasel.com/converted_files/"+res_id) as data_file:
                data = json.load(data_file)
            return data
        try:
            return_data['data'] = autocomplete.getCatalog(request_data)

        except Exception as e:
            print '-'*60
            print "Autocomplete/Catalog"
            print '-'*60

            traceback.print_exc(file=sys.stdout)
            print '-'*60
            return_data['error'] = "Error: "+ str(e)

        return return_data
