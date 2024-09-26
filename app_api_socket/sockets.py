from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI()

# Mô hình dữ liệu cơ bản (Pydantic model)
class Item(BaseModel):
    name: str
    description: str = None
    price: float
    tax: float = None

# Database giả lập
items = []

# GET - Lấy danh sách tất cả các mục
@app.get("/items/", response_model=List[Item])
def get_items():
    return items

# GET - Lấy một mục cụ thể theo ID
@app.get("/items/{item_id}", response_model=Item)
def get_item(item_id: int):
    if item_id < 0 or item_id >= len(items):
        raise HTTPException(status_code=404, detail="Item not found")
    return items[item_id]

# POST - Tạo một mục mới
@app.post("/items/", response_model=Item)
def create_item(item: Item):
    items.append(item)
    return item
# PUT - Cập nhật toàn bộ một mục theo ID
@app.put("/items/{item_id}", response_model=Item)
def update_item(item_id: int, updated_item: Item):
    if item_id < 0 or item_id >= len(items):
        raise HTTPException(status_code=404, detail="Item not found")
    items[item_id] = updated_item
    return updated_item

# PATCH - Cập nhật một phần thông tin của mục theo ID
@app.patch("/items/{item_id}", response_model=Item)
def patch_item(item_id: int, item: Item):
    if item_id < 0 or item_id >= len(items):
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Cập nhật chỉ những trường được truyền vào
    current_item = items[item_id]
    updated_item = current_item.copy(update=item.dict(exclude_unset=True))
    items[item_id] = updated_item
    return updated_item

# DELETE - Xóa một mục theo ID
@app.delete("/items/{item_id}", response_model=Item)
def delete_item(item_id: int):
    if item_id < 0 or item_id >= len(items):
        raise HTTPException(status_code=404, detail="Item not found")
    return items.pop(item_id)

