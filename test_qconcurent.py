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

def start_server():
    uvicorn.run("atklip.app_api:app", 
                host="localhost", 
                port=2022, 
                loop="auto",
                http="httptools",
                ws="wsproto",
                workers=1,
                ws_max_queue=1000,
                limit_max_requests=100000,
                reload=False)
def create_server():
        multiprocessing.set_start_method("spawn")
        _socket_process = Process(target=start_server) 
        _socket_process.start()
        process_pid = _socket_process.pid
        return  _socket_process, process_pid


if __name__ == '__main__':
    freeze_support()
    socket_process,socket_process_pid = create_server()
