import unittest
from PlayerCache import PlayerCache

class TestPlayerCache(unittest.TestCase):

    def test_get(self):
        pc = PlayerCache(1)
        pc.put('a', 1)
        
        self.assertEqual(pc.get('a'), 1)

    def test_put(self):
        pc = PlayerCache(1)
        pc.put('a', 1)
        pc.put('b', 2)
        self.assertEqual(pc.get('a'), None)
        self.assertEqual(pc.get('b'), 2)

    def test_evict(self):
        pc = PlayerCache(1)
        pc.put('a', 1)
        pc.put('b', 2)
        pc.put('c', 3)
        self.assertEqual(pc.get('a'), None)
        self.assertEqual(pc.get('b'), None)
        self.assertEqual(pc.get('c'), 3)

    def test_evict_10(self):
        pc = PlayerCache(10)
        for i in range(10):
            pc.put(i, i)
        pc.put(10, 10)
        self.assertEqual(pc.get(0), None)
        self.assertEqual(pc.get(1), 1)
        self.assertEqual(pc.get(10), 10)

    def test_refresh_10(self):
        pc = PlayerCache(10)
        for i in range(11):
            pc.put(i, i)

        for _ in range(10):
            pc.put(0, 0)

        # 0 is definitely in the cache
        self.assertEqual(pc.get(0), 0)

        # 1 should have been evicted to make room for 0
        self.assertEqual(pc.get(1), None)
        
        # all other numbers should remain.
        for i in range(2, 11):
            self.assertEqual(pc.get(i), i)


if __name__ == '__main__':
    unittest.main()