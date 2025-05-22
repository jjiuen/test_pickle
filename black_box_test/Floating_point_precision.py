import unittest
import math
import struct
import pickle
import sys

class TestFloatSpecialCases(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_objects = {
            "NaN": float('nan'),
            "PosInf": float('inf'),
            "NegInf": -float('inf'),
            "MixedNaN": struct.unpack('<d', b'\x7f\xf8\x00\x00\x00\x00\x00\x01')[0],
        }

    def test_binary_representation(self):
        print("\n" + "=" * 50)
        print("【Binary representation test】")
        print("{:<10} {:<20} {:<10} {:<20}".format("name", "sexadecimal", "platform", "hash value"))
        for name, value in self.test_objects.items():
            try:
                hex_value = hex(struct.unpack('<Q', struct.pack('<d', value))[0])
                platform = sys.platform
                hash_val = hash(value) if name != "NaN" else None
                print(f"{name:<10} {hex_value:<20} {platform:<10} {hash_val}")
            except Exception as e:
                print(f"{name:<10} {'Error':<20} {sys.platform:<10} {str(e)}")

    def test_comparison_behavior(self):
        print("\n" + "=" * 50)
        print("【Comparative behavior test】")
        print("{:<10} {:<15} {:<15}".format("name", "value == value", "value is value"))
        for name, value in self.test_objects.items():
            with self.subTest(name=name):
                eq = "False" if math.isnan(value) else "True"
                is_same = "True"
                print(f"{name:<10} {eq:<15} {is_same:<15}")

    def test_serialization(self):
        print("\n" + "=" * 50)
        print("【Serialization Test】")
        print("{:<10} {:<10} {:<20} {:<10} {:<20}".format("name", "Pickle succeed", "Pickle error", "JSON succeed", "JSON error"))
        for name, value in self.test_objects.items():
            try:
                pickled = pickle.dumps(value)
                unpickled = pickle.loads(pickled)
                pickle_success = "✅" if unpickled == value else "❌"
                pickle_error = ""
            except Exception as e:
                pickle_success = "❌"
                pickle_error = str(e)

            try:
                import json
                json_str = json.dumps(value)
                json.loads(json_str)
                json_success = "✅"
                json_error = ""
            except Exception as e:
                json_success = "❌"
                json_error = str(e)

            print(f"{name:<10} {pickle_success:<10} {pickle_error:<20} {json_success:<10} {json_error:<20}")


if __name__ == "__main__":
    unittest.main()
