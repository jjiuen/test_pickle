import pickle
import hashlib
import sys
import unittest
from pathlib import Path


class TestSysObjectsSerialization(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_objects = {
            'stdin': sys.stdin,
            'stdout': sys.stdout,
            'stderr': sys.stderr,
            'modules': sys.modules,
            'path': sys.path,
            'executable': sys.executable,
            'version': sys.version,
            'platform': sys.platform,
            'argv': sys.argv,
            'path_importer_cache': sys.path_importer_cache,
            'hexversion': sys.hexversion,
            'implementation': sys.implementation,
            'thread_info': sys.thread_info,
        }
      
        cls.hashes = {}
        for name, obj in cls.test_objects.items():
            try:
                if name in ['stdin', 'stdout', 'stderr']:
                    data = f"{type(obj)}"
                    cls.hashes[name] = hashlib.sha256(data.encode()).hexdigest()
                elif name == 'modules':
                    data = str(sorted(sys.modules.keys()))
                    cls.hashes[name] = hashlib.sha256(data.encode()).hexdigest()
                else:
                    cls.hashes[name] = hashlib.sha256(pickle.dumps(obj)).hexdigest()
            except (pickle.PicklingError, TypeError, AttributeError) as e:
                cls.hashes[name] = f"NOT_SERIALIZABLE: {type(e).__name__}: {str(e)}"

    def test_hashes_output(self):
        print("\nSys objects serialization hashes:")
        print("{:<25} {:<64}".format("Object type", "SHA-256 hash value or error"))
        print("-" * 90)

        for name, hash_value in self.hashes.items():
            print("{:<25} {}".format(name, hash_value))
            self.assertTrue(isinstance(hash_value, str))

    def test_serializable_objects(self):
        serializable_objects = [
            'path', 'executable', 'version', 'platform',
            'argv', 'hexversion'
        ]

        for name in serializable_objects:
            self.assertFalse(
                self.hashes[name].startswith("NOT_SERIALIZABLE"),
                f"{name} should be serializable but got: {self.hashes[name]}"
            )

if __name__ == '__main__':
    unittest.main(verbosity=2)



