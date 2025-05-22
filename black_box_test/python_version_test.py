import pickle
import hashlib
import sys
import platform
from datetime import datetime
import pprint


def get_python_version():
    """Get detailed Python environment information"""
    return {
        'version': sys.version.split()[0],
        'full_version': sys.version,
        'implementation': platform.python_implementation(),
        'compiler': platform.python_compiler(),
        'build_info': {
            'build_number': sys.version_info[3],
            'build_date': sys.version.split()[2]
        },
        'system_info': {
            'system': platform.system(),
            'machine': platform.machine()
        },
        'pickle_protocol': pickle.DEFAULT_PROTOCOL
    }


def generate_test_data():
    """Generate test datasets using equivalence partitioning and boundary value analysis"""
    return [
        {
            'description': 'BVA1: Dictionary key name boundaries',
            'data': {
                '': 'empty key',
                ' ': 'space key',
                'key.with.dots': 'dotted',
                'unicode-键': '中文键名',
                'very_long_key_' * 10: 'long key'
            }
        },
        {
            'description': 'BVA2: Digital boundary value',
            'data': {
                'zero': 0,
                'max_int': sys.maxsize,
                'min_int': -sys.maxsize - 1,
                'large_float': 1.7976931348623157e+308,
                'small_float': 2.2250738585072014e-308
            }
        },
        {
            'description': 'BVA3:Container size boundary ',
            'data': {
                'single_item_list': [42],
                'max_recursion': {'level': {'level': {'level': 3}}},
                'large_list': list(range(100))
            }}


        ]


def run_serialization_test(data):
    """Run serialization and hashing test"""
    pickled = pickle.dumps(data)
    return {
        'input_data': data,
        'hash': hashlib.sha256(pickled).hexdigest(),
        'pickle_length': len(pickled)
    }


def print_test_report(version_info, results):
    """Print formatted test report with improved data display"""
    pp = pprint.PrettyPrinter(indent=4, width=80)

    print("[TEST ENVIRONMENT]")
    print("Python Version: {}".format(version_info['version']))

    print("[TEST CASES]")

    max_data_width = max(len(str(test['description'])) for test in results)
    col1_width = min(max_data_width + 2, 80 - 35)  
    col2_width = 64  

    header = "{:<{}} | {:<{}}".format('Data', col1_width, 'SHA256-Hash', col2_width)
    separator = "-" * len(header)
    print(separator)
    print(header)
    print(separator)

    for test in results:
        data_str = str(test['description'])
        hash_str = test['hash']

        data_lines = [data_str[i:i + col1_width] for i in range(0, len(data_str), col1_width)]
        hash_lines = [hash_str[i:i + col2_width] for i in range(0, len(hash_str), col2_width)]

        max_lines = max(len(data_lines), len(hash_lines))

        for i in range(max_lines):
            data_part = data_lines[i] if i < len(data_lines) else ""
            hash_part = hash_lines[i] if i < len(hash_lines) else ""
            print("{:<{width1}} | {:<{width2}}".format(data_part, hash_part, width1=col1_width, width2=col2_width))

    print(separator)




def main():
    """Main test execution"""
    version_info = get_python_version()
    test_cases = generate_test_data()

    results = []
    for case in test_cases:
        test_result = run_serialization_test(case['data'])
        results.append({
            'description': case['description'],
            'input_data': test_result['input_data'],
            'hash': test_result['hash'],
            'pickle_length': test_result['pickle_length']
        })

    print_test_report(version_info, results)


if __name__ == "__main__":
    main()
