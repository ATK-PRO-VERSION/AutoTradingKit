# PyQt with server code
from multiprocessing import Process
from multiprocessing.dummy import freeze_support
import uvicorn as uv
import uvicorn.config
import os
os.environ["POLARS_SKIP_CPU_CHECK"] = "1"
def start_server():
    uv.config.LOOP_SETUPS.update({"winloop":"winloop:install"})
    uv.run("atklip.app_api.sockets:app", 
                host="localhost", 
                port=2022, 
                loop="winloop",
                http="httptools",
                ws="wsproto",
                interface="asgi3",
                # lifespan="on",
                workers=1,
                ws_max_queue=1000,
                limit_max_requests=100000,
                timeout_keep_alive=360,
                reload=False)
    
    """log_config=None,
        log_level= None,
        access_log=False"""

def create_server():
    _socket_process = Process(target=start_server) 
    _socket_process.start()
    process_pid = _socket_process.pid
    return  _socket_process, process_pid

if __name__ == '__main__':
    freeze_support()
    socket_process,socket_process_pid = create_server()
    print(socket_process,socket_process_pid)
