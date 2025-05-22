import pickle
import hashlib
import unittest
from collections import deque


class Node:
    """Serializable node class"""
    def __init__(self, value):
        self.value = value
        self.children = []


class TestRecursiveStructureSerialization(unittest.TestCase):
    """Test serialization behavior of recursive data structures"""

    @staticmethod
    def _generate_hash(obj):
        """Generate serialization hash value of an object"""
        serialized = pickle.dumps(obj, protocol=pickle.HIGHEST_PROTOCOL)
        return hashlib.sha256(serialized).hexdigest()

    @staticmethod
    def _create_circular_reference(depth=3):
        """Create multi-level circular reference structure"""
        head = {}
        current = head
        for _ in range(depth):
            current['next'] = {}
            current = current['next']
        current['next'] = head  # Create cycle
        return head

    @staticmethod
    def _create_complex_recursive_structure():
        """Create complex mixed recursive structure"""
        root = Node(0)
        child1 = Node(1)
        child2 = Node(2)
        root.children.extend([child1, child2])
        child1.children.append(root)  # Circular reference
        child2.children.append(child1)  # Cross reference

        # Add dictionary and list circular references
        data = {'root': root, 'meta': {}}
        data['meta']['self_ref'] = data
        return data

    @staticmethod
    def _generate_deterministic_structures():
        """Generate deterministic test structures for consistent output"""
        # Structure 1: Simple self-referential dictionary
        struct1 = {}
        struct1['self'] = struct1

        # Structure 2: List circular reference
        struct2 = []
        struct2.append(struct2)

        # Structure 3: Nested dictionary cycle
        struct3 = {'a': {'b': {}}}
        struct3['a']['b']['back'] = struct3

        # Structure 4: Mixed structure
        struct4 = {'nodes': []}
        node1 = {'id': 1, 'parent': None}
        node2 = {'id': 2, 'parent': node1}
        node1['parent'] = node2
        struct4['nodes'].extend([node1, node2])

        return [struct1, struct2, struct3, struct4]

    def test_circular_reference(self):
        """Test basic circular reference"""
        obj = self._create_circular_reference()
        obj_hash = self._generate_hash(obj)
        print(f"\n{' Basic Circular Reference Test ':-^60}")
        print(f"Hash: {obj_hash}")
        serialized = pickle.dumps(obj)
        loaded = pickle.loads(serialized)
        self.assertIs(loaded['next']['next']['next']['next'], loaded)
        return obj_hash

    def test_complex_recursive_structure(self):
        """Test complex recursive structure"""
        obj = self._create_complex_recursive_structure()
        obj_hash = self._generate_hash(obj)
        print(f"\n{' Complex Recursive Structure Test ':-^60}")
        print(f"Hash: {obj_hash}")
        serialized = pickle.dumps(obj)
        loaded = pickle.loads(serialized)
        self.assertIs(loaded['meta']['self_ref'], loaded)
        self.assertIs(loaded['root'].children[0].children[0], loaded['root'])
        return obj_hash

    def test_boundary_cases(self):
        """Boundary case testing"""
        test_cases = [
            ({'self': None}, "Empty dictionary"),
            ([], "Empty list"),
            ([None, None], "List containing None"),
            ({'a': {'b': {}}}, "Deep empty structure"),
            (deque(), "Empty queue"),
            (deque([deque()]), "Nested empty queue")
        ]

        results = []
        print(f"\n{' Boundary Case Testing ':-^60}")
        for obj, desc in test_cases:
            # Add circular reference
            if isinstance(obj, dict):
                obj['self'] = obj
            elif isinstance(obj, list):
                obj.append(obj)
            elif isinstance(obj, deque):
                obj.append(obj)

            try:
                serialized = pickle.dumps(obj)
                loaded = pickle.loads(serialized)
                obj_hash = self._generate_hash(obj)
                print(f"{desc:20} | Hash: {obj_hash}")
                results.append((desc, obj_hash))
            except Exception as e:
                print(f"{desc:20} | Error: {str(e)}")
                results.append((desc, str(e)))

        return results

    def test_deterministic_structures(self):
        """Test deterministic structures"""
        structures = self._generate_deterministic_structures()
        results = []

        print(f"\n{' Deterministic Structure Testing ':-^60}")
        print(f"{'Structure':15} | {'Hash':64}")
        print("-" * 82)
        for i, obj in enumerate(structures, 1):
            obj_hash = self._generate_hash(obj)
            print(f"Structure {i:8} | {obj_hash}")
            results.append(obj_hash)

            # Verify serialization/deserialization
            serialized = pickle.dumps(obj)
            loaded = pickle.loads(serialized)

            # Verify circular references are maintained
            if i == 1:
                self.assertIs(loaded['self'], loaded)
            elif i == 2:
                self.assertIs(loaded[0], loaded)
            elif i == 3:
                self.assertIs(loaded['a']['b']['back'], loaded)
            elif i == 4:
                self.assertIs(loaded['nodes'][0]['parent']['parent'], loaded['nodes'][0])

        return results


if __name__ == "__main__":
    unittest.main()
