from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from trainingdatapopulator import graphdbpopulator as gdp
import json

class Training(APIView):
    """
    List all snippets, or create a new snippet.
    """
    #authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    
    def catalog(self, request_data):
        gdp.GraphDbPopulator(request_data)
        return gdp.initialize()

    def post(self, request, action, format=None):
        conceptspace = request.user.username
        request_data['conceptspace'] = conceptspace
        request_data['catalog'] = json.loads(request.DATA['catalog'])
        
        method = getattr(self, action)
        content = {
            'api_version': '2.0',
            'conceptspace': conceptspace,
            'data': method(request_data)
        }
        return Response(content)