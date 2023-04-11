import json
import time
from Blockchain.utils import *
from Blockchain.Block import Block


class Node:
    def __init__(self, nonce_type):
        # Текущая цепь
        self.chain = []
        # Требование к точности хэша
        self.diff = 4
        # Текущее значение nonce у последнего блока
        self.cur_nonce = 0
        # Тип вычисления nonce
        self.nonce_type = nonce_type

    # Получение последнего блока цепи
    def get_last_block(self):
        return self.chain[len(self.chain) - 1]

    # Генерация следующего значения nonce
    def add_nonce(self):
        if self.nonce_type == 0:
            self.cur_nonce += random.randint(0, 5)
        elif self.nonce_type == 1:
            self.cur_nonce += random.randint(5, 10)
        else:
            self.cur_nonce += random.randint(10, 15)

    # Создание нового блока
    def create_new_block(self, num_node):
        current_block = Block(random_string(256), num_node)
        current_block.index = self.get_last_block().index + 1
        current_block.prev_hash = self.get_last_block().hash
        current_block.nonce = 0
        self.cur_nonce = 0
        current_block.hash = current_block.get_hash()

        # Пока не выполняется требование к точности, генерируем новый блок
        while current_block.hash[-4:] != '0' * self.diff:
            if len(self.chain) > 1 and self.get_last_block().index == current_block.index:
                return None
            self.add_nonce()
            current_block.nonce = self.cur_nonce
            current_block.hash = current_block.get_hash()

        # Время создания блока
        current_block.timestamp = time.time()

        return current_block

    # Создание genesis
    def create_first_block(self, num_node):
        data = random_string(256)
        first_hash = create_hash(1, None, data, 0)
        while first_hash[-4:] != '0' * self.diff:
            data = random_string(256)
            first_hash = create_hash(1, None, data, 0)

        block = Block(data, num_node)
        block.index = 1
        block.hash = block.get_hash()
        self.chain.append(block)

