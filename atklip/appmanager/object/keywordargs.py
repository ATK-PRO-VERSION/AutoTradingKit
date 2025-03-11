class DynamicKwargs:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def get(self, key, default=None):
        return self.kwargs.get(key, default)

    def keys(self):
        return self.kwargs.keys()

    def values(self):
        return self.kwargs.values()

    def items(self):
        return self.kwargs.items()

    def add(self, key, value):
        self.kwargs[key] = value

    def remove(self, key):
        if key in self.kwargs:
            del self.kwargs[key]
        else:
            raise KeyError(f"Key '{key}' not found in DynamicKwargs")


