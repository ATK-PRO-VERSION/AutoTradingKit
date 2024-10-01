from PySide6.QtCore import QObject, Signal, Slot

# Tạo một lớp kế thừa từ QObject
class Worker(QObject):
    # Khai báo một tín hiệu (Signal) nhận một giá trị int
    task_completed = Signal(int)

    def __init__(self):
        super().__init__()

    # Khai báo một slot để xử lý công việc
    @Slot(int)
    def perform_task(self, task_id):
        print(f"Performing task {task_id}...")
        # Sau khi hoàn thành, phát ra tín hiệu
        self.task_completed.emit(task_id)

# Tạo một lớp khác để xử lý kết quả
class ResultHandler(QObject):
    @Slot(int)
    def handle_result(self, task_id):
        print(f"Task {task_id} completed!")

if __name__ == "__main__":
    # Tạo đối tượng Worker và ResultHandler
    worker = Worker()
    result_handler = ResultHandler()

    # Kết nối tín hiệu từ Worker với Slot của ResultHandler
    worker.task_completed.connect(result_handler.handle_result)

    # Thực hiện tác vụ và xử lý kết quả
    worker.perform_task(1)
