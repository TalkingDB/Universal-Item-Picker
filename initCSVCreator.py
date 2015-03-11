__author__="Atul Tagra<atul@ignitras.com>"
__date__ ="$1 Nov, 2014 1:16:28 PM$"

from trainingdatapopulator import csvCreatorResumable as creator
import traceback
import sys

if __name__ == "__main__":
    
    resume = False
    
    if len(sys.argv) > 1:
        resume = True
        
    try:
        creator.csvCreator(resume)
    except Exception as e:
        print e
        print "Exception in user code:"
        print '-'*60
        traceback.print_exc(file=sys.stdout)
        print '-'*60
