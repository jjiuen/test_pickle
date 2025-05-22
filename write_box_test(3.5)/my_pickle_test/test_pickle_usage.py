import sys
import io
import coverage
import importlib.util
import hashlib

class PurePythonPickleTester:
    def __init__(self, pickle_path="./std_pickle2/pickle2.py", coverage_source=None, coverage_html_dir="pickle_coverage_html"):
        sys.modules['_pickle'] = None

        spec = importlib.util.spec_from_file_location("pickle", pickle_path)
        self.pickle = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.pickle)

        self.Unpickler = getattr(self.pickle, '_Unpickler', getattr(self.pickle, 'Unpickler'))

        self.coverage_source = coverage_source or [pickle_path.rsplit('/', 1)[0]]
        self.coverage_html_dir = coverage_html_dir

    def hash_pickled_data(self, obj):
        pickled = self.pickle.dumps(obj)
        return hashlib.sha256(pickled).hexdigest(), pickled

    def test_unpickler_methods(self, test_cases=None):
        test_cases = test_cases or [
            123456,                    # load_binint, load_binint1, load_binint2
            12345678901234567890,      # load_long, load_long1, load_long4
            3.1415926,                 # load_float, load_binfloat
            "hello world",             # load_string, load_binunicode, load_binunicode8
            b"bytes data",             # load_binbytes, load_binbytes8
            bytearray(b"bytearray"),   # load_bytearray8
            [1, 2, 3],                 # load_list
            (4, 5),                    # load_tuple, load_tuple2, load_tuple3
            { "a": 1, "b": 2 },        # load_dict
            set([1, 2]),               # load_empty_set, load_frozenset
            frozenset([3, 4]),         # load_frozenset
        ]

        for obj in test_cases:
            obj_hash, pickled = self.hash_pickled_data(obj)

            f = io.BytesIO(pickled)
            unpickler = self.Unpickler(f)
            result = unpickler.load()

            assert result == obj, "Unpickled value {} != original {}".format(result, obj)

            print("Object: {0}".format(repr(obj)))
            print("Pickled SHA256 Hash: {0}".format(obj_hash))
            print("-" * 50)

        print(" All test cases passed.")

    def run_coverage_test(self):
        cov = coverage.Coverage(source=self.coverage_source)
        cov.start()

        self.test_unpickler_methods()

        cov.stop()
        cov.save()
        cov.report(show_missing=True)
        cov.html_report(directory=self.coverage_html_dir)

def main():
    tester = PurePythonPickleTester()
    tester.run_coverage_test()

if __name__ == "__main__":
    main()
