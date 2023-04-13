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

    # Добавляем полученный блок в цепь
    def add_block_from_json(self, json_block):
        self.chain.append(json_block)

    # Конвертация json в блок
    @staticmethod
    def json_to_block(json_block):
        block = Block(json_block['data'], json_block['From node'])
        block.index = json_block['index']
        block.nonce = json_block['nonce']
        block.hash = json_block['hash']
        block.prev_hash = json_block['prev_hash']
        block.timestamp = json_block['timestamp']

        return json_block['From node'], block

    # Проверка валидности сгенерированного/полученного блока
    def validate(self, new_block):
        c = False
        for i, n in enumerate(self.chain):
            # Если блок с таким индексом уже есть в цепи, то проверяем какой блок был сгенерирован раньше
            if n.index == new_block.index:
                c = True
                if n.timestamp > new_block.timestamp:
                    print(f'Block #{new_block.index} from Node{new_block.num_node} replaced: {new_block}')
                    self.chain[i] = new_block
        # Если блока с таким индексом вообще нет в цепи, то добавляем его
        if not c:
            self.chain.append(new_block)
            print(f'New block #{new_block.index} from Node{new_block.num_node}: {new_block}')

    # Конвертация блока в json
    @staticmethod
    def block_to_json(block, from_node):
        return json.dumps(
            {
                'From node': from_node,
                'data': block.data,
                'index': block.index,
                'nonce': block.nonce,
                'hash': block.hash,
                'prev_hash': block.prev_hash,
                'timestamp': block.timestamp
            },
            indent=4)

    def chain_to_json(self):
        return json.dumps([{
            'Block': {
                'From node': item.num_node,
                'data': item.data,
                'index': item.index,
                'nonce': item.nonce,
                'hash': item.hash,
                'prev_hash': item.prev_hash,
                'timestamp': item.timestamp
            }}
            for item in self.chain], indent=4)

    def json_chain_to_blockchain(self, json_chain):
        j = json.loads(json_chain)
        new_blockchain = []
        for e in j:
            _, block = self.json_to_block(e['Block'])
            new_blockchain.append(block)
        return new_blockchain
