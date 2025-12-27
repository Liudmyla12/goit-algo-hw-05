class HashTable:
    def __init__(self, size: int = 10):
        self.size = size
        self.table = [[] for _ in range(size)]  # separate chaining

    def _hash(self, key: str) -> int:
        return hash(key) % self.size

    def put(self, key: str, value):
        idx = self._hash(key)
        bucket = self.table[idx]

        for i, (k, v) in enumerate(bucket):
            if k == key:
                bucket[i] = (key, value)
                return
        bucket.append((key, value))

    def get(self, key: str):
        idx = self._hash(key)
        bucket = self.table[idx]

        for k, v in bucket:
            if k == key:
                return v
        return None

    def delete(self, key: str) -> bool:
        """
        Видаляє пару ключ-значення з хеш-таблиці.
        Повертає True, якщо ключ знайдено і видалено, інакше False.
        """
        idx = self._hash(key)
        bucket = self.table[idx]

        for i, (k, v) in enumerate(bucket):
            if k == key:
                bucket.pop(i)
                return True
        return False


if __name__ == "__main__":
    ht = HashTable(size=5)
    ht.put("apple", 10)
    ht.put("banana", 20)
    ht.put("orange", 30)

    print("apple:", ht.get("apple"))
    print("delete banana:", ht.delete("banana"))
    print("banana:", ht.get("banana"))
    print("delete missing:", ht.delete("missing_key"))
