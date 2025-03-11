from PySide6.QtCore import QThreadPool
import multiprocessing
from concurrent.futures import ThreadPoolExecutor,ProcessPoolExecutor


global num_threads
num_threads = multiprocessing.cpu_count()

global QThreadPool_global
QThreadPool_global = QThreadPool.globalInstance()
QThreadPool_global.setMaxThreadCount(num_threads)


global ThreadPoolExecutor_global
ThreadPoolExecutor_global = ThreadPoolExecutor(max_workers=num_threads*20)

global Heavy_ProcessPoolExecutor_global
Heavy_ProcessPoolExecutor_global = ProcessPoolExecutor(max_workers=int(num_threads/2)) # ,max_tasks_per_child=num_threads*10
