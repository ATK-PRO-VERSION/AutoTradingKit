import multiprocessing
from concurrent.futures import ThreadPoolExecutor
import traceback
from typing import Callable

num_threads = multiprocessing.cpu_count()
ThreadPoolExecutor_global = ThreadPoolExecutor(max_workers=num_threads*50)

class IndicatorWorker():
    "Worker này dùng để update  data trong một cho graph object khi có data mới"
    def __init__(self,fn:Callable=None, *args, **kwargs):
        self.fn = fn
        self.args = args
        self.kwargs = kwargs.copy()
        self.threadpool = ThreadPoolExecutor_global
        
    def start(self):
        funture = self.threadpool.submit(self.run)
        return funture
    
    def run(self):
        try:
            self.fn(*self.args, **self.kwargs)
        except Exception as e:
            traceback.print_exception(e)