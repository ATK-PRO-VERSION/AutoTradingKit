# PyQt with server code
from multiprocessing import Process
import multiprocessing
from multiprocessing.dummy import freeze_support
from fastapi import FastAPI
import threading
import uvicorn
import sys

import asyncio
import concurrent.futures

def _create_server():
        thread = multiprocessing.Process(target=uvicorn.run, kwargs={
                                                    "app": "atklip.app_api:app", 
                                                    "host": "localhost",
                                                    "port": 2022,
                                                    "ws_max_queue":1000,
                                                    "limit_max_requests":100000,
                                                    "reload": True
                                                    })
        thread.start()
        # thread.terminate()



if __name__ == '__main__':
    freeze_support()
    _create_server()