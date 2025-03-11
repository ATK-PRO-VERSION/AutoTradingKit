import uuid

class UniqueManager:
    def __init__(self):
        self.list_id = []
        self._objects = {}

    def generate_id(self):
        unique_id = str(uuid.uuid4())
        while unique_id in self.list_id:
            unique_id = str(uuid.uuid4().hex)
        return str(unique_id)

    def add(self, obj=None):
        unique_id = self.generate_id()
        ob = self.get(unique_id)
        if ob != None:
            ob.deleteLater()
        self._objects[unique_id] = obj
        return unique_id
    
    def set(self, obj, unique_id):
        self.list_id.append(unique_id)
        self._objects[unique_id] = obj
        return unique_id

    def remove(self, unique_id):
        if unique_id in self.list_id:
            self.list_id.remove(unique_id)
            ob = self.get(unique_id)
            if ob != None:
                ob.deleteLater()
                del self._objects[unique_id]     
                return {unique_id:"remove DONE"}
            return {unique_id:"This object is not in list"}
        else:
            return {unique_id:"This object is not in list"}

    def get(self, unique_id):
        return self._objects.get(unique_id)

global objmanager
objmanager:UniqueManager = UniqueManager()