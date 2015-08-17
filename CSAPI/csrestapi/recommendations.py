import json
import subprocess
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import routers, serializers, viewsets
# configure
import sys
sys.path.append("/home/sb/NetBeansProjects/CommonSense/src/")
import recommendation
import traceback, sys
import time


class Recommendation(APIView):
    
#     def get(self, request, format=None):
#         pass
    
    def generate(self, request_data):
        return_data = {}
        import datetime
        print 'request_data = ' + str(request_data) + '\n' + str(datetime.datetime.now())
        return_data['data'] = []
	t1 = time.time()
	try:
            r = recommendation.Recommendation()
            return_data['data'], return_data['special_instructions'] = r.generateRecommendation(request_data) #TODO SpecialInstruction: Instead of returning just the prepareList, now we also return special_instructions list. return it here
        except Exception as e:
            print '-'*60
            print "Recommendation/generate"
            print '-'*60
            
            traceback.print_exc(file=sys.stdout)
            print '-'*60
            return_data['error'] = "Error:"+str(e)
        t2 = time.time()
	print 'in UIP/CSAPI/csrestapi/recommendations.py. r.generateRecommendation took ' + str(t2-t1) + ' time'

        """
        sort with 'warnings' flag. the stores with no warnings will appear first
        """        
        tmp_return_data = return_data['data']
        tmp_return_data.sort(key=lambda e: e['children'][0]['children'][0]['warning'], reverse=False)
        return_data['data'] =tmp_return_data 

        return return_data

    def post(self, request, action, format=None):
        conceptspace = request.user.username
        request_data = {}
        request_data['concept_space'] = conceptspace
#         print request.DATA
        if action == "generate":
            request_data['parent'] = json.loads(request.DATA['parent'])
            request_data['instruction'] = (request.DATA['instruction']).encode("utf-8")
        if action == "restartCSAPI":
            subprocess.call('screen -dmS csapi bash -c "sh /home/anil.gautam/Smarter.Codes/src/run-restart-cs.sh"',shell=True) #kill the system process running on requested port
            
        
        method = getattr(self, action)
        result = method(request_data)
        
        content = dict(result, **{
            'api_version': '2.0',
            'conceptspace': conceptspace
        })
        return Response(content)

    def restartCSAPI(self, request):
        data = {}
        data['data'] ="ok" 
        return data;
        
