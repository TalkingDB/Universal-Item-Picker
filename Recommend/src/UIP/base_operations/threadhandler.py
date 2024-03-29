__author__="Karan S. Sisodia"
__email__="karansinghsisodia@gmail.com"
__date__ ="$Sep 11, 2014 3:38:31 PM$"

import finder
import threading
import time
#threadLimiter = threading.BoundedSemaphore(config.max_threads)
threadLimiter = threading.BoundedSemaphore(5)

class ThreadHandler(threading.Thread):
    def __init__(self, node_ids, instruction,instruction_index,myQueue,GL,finished_queue):
        threading.Thread.__init__(self)
        self.myQueue = myQueue
        self.instruction = instruction
        self.instruction_index = instruction_index
        self.node_ids = node_ids
        self.special_instruction = ""
        self.GL = GL
        self.cond = threading.Condition()
        self.done = False
        self.finished_queue = finished_queue
        
    #@profile
    def run(self):
        print "Thread"
        threadLimiter.acquire()
        self.cond.acquire()
        try:
            finder_obj = finder.Finder(self.node_ids,self.instruction,self.GL)
            self.selected_bucket, self.special_instruction = finder_obj.process() 
            self.finished_queue.put((self.selected_bucket,self.special_instruction,self.instruction_index)) #whatever we pass in PUT method here is later returned in our 'thread callee' in 'getData' function
            # time.sleep(2)
            #print "Thread completed"
        except ValueError as e:
            print e
        finally:
            self.myQueue.task_done()
            threadLimiter.release()
        self.done = True
        self.cond.notify()
        self.cond.release()

    def getData(self):
        self.cond.acquire()
        while not self.done: #  <--
            self.cond.wait()#  <--  We're waiting that self.done becomes True
        self.cond.release() #  <--
        return (self.selected_bucket,self.special_instruction,self.instruction_index)