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

