import uuid

class ObjManager:
    def __init__(self):
        self.list_id = []
        self.list_obj_name = []
        self._objects = {}

    def generate_id(self):
        unique_id = str(uuid.uuid4())
        while unique_id in self.list_id:
            unique_id = str(uuid.uuid4())
        return str(unique_id)

    def remove_id_from_listid_objname(self,unique_id):
        while unique_id in self.list_id:
            self.list_id.remove(unique_id)
        for _id in self.list_obj_name:
            if _id.__contains__(unique_id):
                self.list_obj_name.remove(_id)

    def add(self, obj=None):
        unique_id = self.generate_id()
        self.list_id.append(unique_id)
        obj_name = obj.has["name"]
        name = f"{obj_name}-{unique_id}"
        self.list_obj_name.append(name)
        self._objects[name] = obj
        return name

    def remove(self, unique_id):
        if unique_id in self.list_obj_name:
            del self._objects[unique_id]
        else:
            raise KeyError(f"Unique ID '{unique_id}' not found in UniqueIDManager")

    def get(self, unique_id):
        return self._objects.get(unique_id,None)
    
    def replace(self,obj):
        for key, ob in self._objects.items():
            if ob == obj:
                self.remove(key)
                break
        self.add(obj)
    
    def clear(self):
        self.list_id = []
        self._objects = {}