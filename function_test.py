import sys
from fastapi import FastAPI
from PySide6.QtCore import QObject, Signal
from qasync import QEventLoop, asyncSlot,QApplication
import asyncio

app = FastAPI()

class Worker(QObject):
    task_completed = Signal(int)

    @asyncSlot(int)
    async def perform_task(self, task_id):
        # Giả lập một tác vụ bất đồng bộ
        await asyncio.sleep(1)
        print(f"Task {task_id} performed")
        self.task_completed.emit(task_id)

worker = Worker()

@worker.task_completed.connect
def on_task_completed(task_id):
    print(f"Task {task_id} completed!")

@app.get("/task/{task_id}")
async def start_task(task_id: int):
    asyncio.create_task(worker.perform_task(task_id))
    return {"message": f"Task {task_id} started"}

if __name__ == "__main__":
    import uvicorn
    app = QApplication(sys.argv)
    loop = QEventLoop(app)

    asyncio.set_event_loop(loop)
    uvicorn.run(app, host="127.0.0.1", port=8000, loop=loop)
