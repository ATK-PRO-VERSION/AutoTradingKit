from psygnal import evented
from dataclasses import dataclass

@evented
@dataclass
class Person:
    name: str
    age: int = 0

person = Person('John', age=30)

# connect callbacks
@person.events.age.connect
def _on_age_change(new_age: str):
    print(f"Age changed to {new_age}")

person.age = 31  # prints: Age changed to 31
person.age = 32  # prints: Age changed to 31
person.age = 33  # prints: Age changed to 31
person.age = 34  # prints: Age changed to 31

from psygnal import Signal


class MyEmitter:
    changed = Signal(int,float)

class Rrceiver:
    def receiver(arg1: int,agr2:int):
        print("new value:", arg1,agr2)


emitter = MyEmitter()
emitter.changed.connect(Rrceiver.receiver)
emitter.changed.emit(1,3)  # prints 'new value: 1'

from psygnal import Signal, throttled

class MyEmitter:
    changed = Signal(int)

def on_change(val: int):
    # do something possibly expensive
    print(val)

emitter = MyEmitter()

# connect the `on_change` whenever `emitter.changed` is emitted
# BUT, no more than once every 50 milliseconds
emitter.changed.connect(throttled(on_change, timeout=50))
emitter.changed.emit(123)
