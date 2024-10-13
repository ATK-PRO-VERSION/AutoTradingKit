import multiprocessing
from concurrent.futures import ThreadPoolExecutor
num_threads = multiprocessing.cpu_count()
ApiThreadPool = ThreadPoolExecutor(max_workers=num_threads*40)