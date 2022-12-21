
class Node:
    """
    A node in a doubly linked list.
    """

    def __init__(self, key, value) -> None:
        self.key = key
        self.value = value
        self.prev = None
        self.next = None

    def add(self, node):
        """
        Add a node to the end of the list.
        """

        self.next = node
        node.prev = self

    def remove(self):

        if self.prev:
            self.prev.next = self.next

        if self.next:
            self.next.prev = self.prev

        return self.next


class PlayerCache:
    """
    Keep the n most recently used players in a cache.
    """

    def __init__(self, n) -> None:
        """
        n - cache size
        cache - dictionary of (node, player) pairs
        """

        self.n = n
        self.cache = {}
        self.ll = Node(None, None)
        self.tail = self.ll
        self.cur_size = 0

    def get(self, key):
        """
        Get a player from the cache or None if not found.
        """

        return self.cache.get(key, (None, None))[1]

    def put(self, key, value):
        """
        Put a player into the cache.

        If the cache is full, evict the least recently used player.
        """

        if self.cur_size == 0:
            self.ll = Node(key, value)
            self.tail = self.ll
            self.cache[key] = (self.ll, value)
            self.cur_size += 1
            return

        node, _ = self.cache.get(key, (None, None))

        if node:
            node.remove()
            self.tail.add(node)
        else:
            node = Node(key, value)
            self.tail.add(node)
            self.tail = node
            self.cache[key] = (node, value)
            self.cur_size += 1

        if self.cur_size > self.n:
            try:
                del self.cache[self.ll.key]
            except KeyError:
                # Can happen with multiple threads
                pass
            self.ll = self.ll.remove()
            self.cur_size -= 1

    def is_cached(self, key):
        """
        Return True if the key is in the cache.
        """

        return key in self.cache