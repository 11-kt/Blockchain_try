import json
import time
from hashlib import sha256


class Block:

    def __init__(self, data=None, node=0):
        # Номер ноды, которая выпустила блок
        self.num_node = node
        # Индекс
        self.index = 0
        # Хэш предыдущего блока цепи
        self.prev_hash = None
        # Случайная строка данных
        self.data = [] if data is None else data
        # nonce
        self.nonce = 0
        # Текущий хэш блока
        self.hash = self.get_hash()
        # Время выпуска блока
        self.timestamp = time.time()

    # Вычисление текущего хэша блока
    def get_hash(self):
        h = sha256()
        string = (str(self.index) + str(self.prev_hash) + str(self.data) + str(self.nonce)).encode('utf-8')
        h.update(string)
        return h.hexdigest()

    def __repr__(self):
        return json.dumps([
            {
                'From node': self.num_node,
                'data': self.data,
                'index': self.index,
                'nonce': self.nonce,
                'hash': self.hash,
                'prev_hash': self.prev_hash,
                'timestamp': self.timestamp
            }], indent=4)
