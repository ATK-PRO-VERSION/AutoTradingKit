from PySide6.QtCore import QThreadPool
import multiprocessing
from multiprocessing.pool import ThreadPool
from concurrent.futures import ThreadPoolExecutor,ProcessPoolExecutor

QThreadPool_global = QThreadPool.globalInstance()
num_threads = multiprocessing.cpu_count()
# cpu_count = QThreadPool_global.maxThreadCount()
# print(num_threads,cpu_count)
QThreadPool_global.setMaxThreadCount(num_threads)

# global ThreadPoolExecutor_global
ThreadPoolExecutor_global = ThreadPoolExecutor(max_workers=num_threads*20)

# global ProcessPoolExecutor_global
ProcessPoolExecutor_global = ProcessPoolExecutor(max_workers=num_threads*2)
