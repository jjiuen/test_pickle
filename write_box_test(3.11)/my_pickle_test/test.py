import sys
import hashlib
import coverage
import importlib.util
import io
from test_pickle_usage import PurePythonPickleTester

sys.modules['_pickle'] = None
if 'pickle' in sys.modules:
    del sys.modules['pickle']
spec = importlib.util.spec_from_file_location("pickle", "./std_pickle/pickle.py")
pickle = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pickle)

def sha256_digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

class SimpleClass:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __eq__(self, other):
        return isinstance(other, SimpleClass) and self.x == other.x and self.y == other.y
    def __repr__(self):
        return f"SimpleClass({self.x}, {self.y})"

class ReduceClass:
    def __init__(self, name):
        self.name = name
    def __reduce__(self):
        return (ReduceClass, (self.name,))
    def __eq__(self, other):
        return isinstance(other, ReduceClass) and self.name == other.name
    def __repr__(self):
        return f"ReduceClass({self.name!r})"

class SlotClass:
    __slots__ = ['a', 'b']
    def __init__(self, a, b):
        self.a = a
        self.b = b
    def __eq__(self, other):
        return isinstance(other, SlotClass) and self.a == other.a and self.b == other.b
    def __getstate__(self):
        return (self.a, self.b)
    def __setstate__(self, state):
        self.a, self.b = state
    def __repr__(self):
        return f"SlotClass({self.a}, {self.b})"

class ExternalObject:
    def __init__(self, external_id):
        self.external_id = external_id
    def __eq__(self, other):
        return isinstance(other, ExternalObject) and self.external_id == other.external_id
    def __repr__(self):
        return f"ExternalObject({self.external_id!r})"

external_storage = {
    "obj_123": ExternalObject("obj_123")
}

class MyPickler(pickle.Pickler):
    def persistent_id(self, obj):
        if isinstance(obj, ExternalObject):
            return obj.external_id
        return None

class MyUnpickler(pickle.Unpickler):
    def persistent_load(self, pid):
        return external_storage[pid]

def test_pickle_coverage():
    test_objects = [
        42,
        3.14159,
        True,
        False,
        None,
        "Hello, 世界",
        b"bytes data",
        [1, 2, 3],
        (4, 5, 6),
        {"key": "value", "list": [7, 8, 9]},
        SimpleClass(10, 20),
        ReduceClass("example"),
        SlotClass(5, 6),
        ExternalObject("obj_123"), 
    ]

    recursive_list = []
    recursive_list.append(recursive_list)
    recursive_dict = {}
    recursive_dict["self"] = recursive_dict
    recursive_set = set()
    recursive_set.add(frozenset(recursive_set))  

    recursive_objects = [recursive_list, recursive_dict]

    for obj in test_objects:
        print(f"\nTesting object: {repr(obj)}")
        for proto in range(pickle.HIGHEST_PROTOCOL + 1):
            print(f"  Protocol {proto} ...", end=" ")
            buf = io.BytesIO()
            pickler = MyPickler(buf, protocol=proto)
            try:
                pickler.dump(obj)
            except Exception as e:
                print(f"dump failed: {e}")
                continue

            data = buf.getvalue()
            digest = sha256_digest(data)
            print(f"SHA256={digest}")

            buf.seek(0)
            unpickler = MyUnpickler(buf)
            restored = unpickler.load()

            assert restored == obj, f"Mismatch: {restored} != {obj}"

    for obj in recursive_objects:
        print(f"\nTesting recursive object: {repr(obj)}")
        for proto in range(pickle.HIGHEST_PROTOCOL + 1):
            print(f"  Protocol {proto} ...", end=" ")
            try:
                data = pickle.dumps(obj, protocol=proto)
                digest = sha256_digest(data)
                print(f"SHA256={digest}")
                restored = pickle.loads(data)
                
                if isinstance(obj, list):
                    assert restored[0] is restored, "Recursive list not preserved"
                elif isinstance(obj, dict):
                    assert restored["self"] is restored, "Recursive dict not preserved"
            except Exception as e:
                print(f"Recursive test failed: {e}")

    class Unserializable:
        def __getstate__(self):
            raise RuntimeError("Can't serialize me")

    print("\nTesting serialization of unserializable object (should raise)")
    try:
        pickle.dumps(Unserializable())
    except Exception as e:
        print(f"Expected exception caught: {e}")

def main():
    cov = coverage.Coverage(source=["std_pickle"])
    cov.start()

    test_pickle_coverage()

    tester = PurePythonPickleTester(pickle_path="./std_pickle/pickle.py")
    tester.test_unpickler_methods()

    cov.stop()
    cov.save()
    cov.report(show_missing=True)
    cov.html_report(directory="pickle_coverage_html")

if __name__ == "__main__":
    main()

