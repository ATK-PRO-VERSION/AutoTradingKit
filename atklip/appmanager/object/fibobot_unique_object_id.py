import uuid

class UniqueIDManager:
    def __init__(self):
        self.list_id = []
        self._objects = {}

    def reset(self):
        self.list_id = []
        self._objects = {}
    
    def __repr__(self):
        return self._objects

    def __getitem__(self, unique_id):
        return self._objects(unique_id)

    def __setitem__(self, obj):
        unique_id = self.generate_id()
        self._objects[unique_id] = obj
        return unique_id

    def __delitem__(self, unique_id):
        if unique_id in self._objects:
            del self._objects[unique_id]
        else:
            raise KeyError(f"Unique ID '{unique_id}' not found in UniqueIDManager")

    def generate_id(self):
        unique_id = str(uuid.uuid4())
        while unique_id in self.list_id:
            unique_id = str(uuid.uuid4())
        return str(unique_id)

    def add(self, obj=None):
        unique_id = self.generate_id()
        self._objects[unique_id] = obj
        return unique_id
    
    def set(self, obj, unique_id):
        self.list_id.append(unique_id)
        self._objects[unique_id] = obj
        return unique_id

    def remove(self, unique_id):
        if unique_id in self._objects:
            del self._objects[unique_id]
        else:
            raise KeyError(f"Unique ID '{unique_id}' not found in UniqueIDManager")

    def get(self, unique_id):
        return self._objects[unique_id]