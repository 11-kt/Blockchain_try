import time


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
        self.hash = None
        # Время выпуска блока
        self.timestamp = time.time()

