

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

