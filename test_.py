from dataclasses import dataclass

@dataclass
class Product:
    name: str
    price: float
    quantity: int

# Lấy kiểu dữ liệu của các trường
field_types = {field_name: field.type for field_name, field in Product.__dataclass_fields__.items()}
print(field_types)


from dataclasses import dataclass

@dataclass
class Product:
    name: str
    price: float
    quantity: int

# Tạo một đối tượng Product
product = Product(name="Laptop", price=999.99, quantity=5)

# Lấy giá trị các trường
field_values = {field_name: getattr(product, field_name) for field_name in product.__dataclass_fields__}
print(field_values)
