import concurrent.futures
import json
import unittest

from Blockchain.Node import Node
from Blockchain.utils import config


class NodeTest(unittest.TestCase):

    # Создание genesis
    def test_first_block(self):
        node = Node(0)
        node.create_first_block(0)

        self.assertEqual(node.chain[0].hash[-4:], '0000')
        self.assertEqual(node.chain[0].index, 1)
        self.assertEqual(node.chain[0].nonce, 0)

    # Создание genesis + добваление еще одного блока
    def test_add_new_block(self):
        node = Node(0)
        node.create_first_block(0)
        node.chain.append(node.create_new_block(1))

        self.assertEqual(len(node.chain), 2)
        self.assertEqual(node.chain[0].hash, node.get_last_block().prev_hash)
        self.assertEqual(node.chain[0].hash[-4:], '0000')
        self.assertEqual(node.get_last_block().hash[-4:], '0000')
        self.assertEqual(node.get_last_block().index, 2)

    # Создание цепи
    def test_create_chain(self):
        node = Node(0)
        node.create_first_block(0)
        for i in range(10):
            node.chain.append(node.create_new_block(0))

        self.assertEqual(len(node.chain), 11)
        self.assertEqual(node.get_last_block().hash[-4:], '0000')
        self.assertEqual(node.get_last_block().index, 11)

    # Генерация следующего значения nonce
    # Type 1: += random.randint(0, 5)
    def test_add_nonce_1(self):
        node = Node(0)
        self.assertEqual(node.cur_nonce, 0)
        last_nonce = node.cur_nonce
        node.add_nonce()
        res = abs(node.cur_nonce - last_nonce) <= 5
        self.assertEqual(res, True)

    # Генерация следующего значения nonce
    # Type 2: += random.randint(5, 10)
    def test_add_nonce_2(self):
        node = Node(1)
        self.assertEqual(node.cur_nonce, 0)
        last_nonce = node.cur_nonce
        node.add_nonce()
        res = abs(node.cur_nonce - last_nonce) <= 10
        self.assertEqual(res, True)

    # Генерация следующего значения nonce
    # Type 3: += random.randint(10, 15)
    def test_add_nonce_3(self):
        node = Node(2)
        self.assertEqual(node.cur_nonce, 0)
        last_nonce = node.cur_nonce
        node.add_nonce()
        res = abs(node.cur_nonce - last_nonce) <= 15
        self.assertEqual(res, True)

    # Получение последнего блока
    def test_get_last_block(self):
        node = Node(0)
        node.create_first_block(0)
        last_block = None
        for i in range(11):
            last_block = node.create_new_block(0)
            node.chain.append(last_block)

        self.assertEqual(len(node.chain), node.get_last_block().index)
        self.assertEqual(last_block, node.get_last_block())

    # Конвертация json в блок и обратно
    def test_json_to_block_and_back(self):
        node = Node(0)
        # Первый блок
        node.create_first_block(0)
        # Блок в json
        json_block = node.block_to_json(node.get_last_block(), 0)
        # Json обратно в блок и сравнение с исходным
        from_node, block_json = node.json_to_block(json.loads(json_block))

        self.assertEqual(from_node, 0)
        self.assertEqual(block_json.num_node, node.get_last_block().num_node)
        self.assertEqual(block_json.index, node.get_last_block().index)
        self.assertEqual(block_json.prev_hash, node.get_last_block().prev_hash)
        self.assertEqual(block_json.data, node.get_last_block().data)
        self.assertEqual(block_json.nonce, node.get_last_block().nonce)
        self.assertEqual(block_json.hash, node.get_last_block().hash)
        self.assertEqual(block_json.timestamp, node.get_last_block().timestamp)

    # Конвертация цепи блоков в цепь json и обратно
    def test_block_to_json_and_back(self):
        node = Node(0)
        # Первый блок
        node.create_first_block(0)

        # Цепь блоков
        for i in range(4):
            node.chain.append(node.create_new_block(0))

        # Конвертация цепи в json
        json_chain = json.loads(json.dumps(node.chain_to_json()))

        # Обратная операция
        chain_json = node.json_chain_to_blockchain(json_chain)

        # Сравнение блоков
        for i in range(len(node.chain)):
            self.assertEqual(chain_json[i].num_node, node.chain[i].num_node)
            self.assertEqual(chain_json[i].index, node.chain[i].index)
            self.assertEqual(chain_json[i].prev_hash, node.chain[i].prev_hash)
            self.assertEqual(chain_json[i].data, node.chain[i].data)
            self.assertEqual(chain_json[i].nonce, node.chain[i].nonce)
            self.assertEqual(chain_json[i].hash, node.chain[i].hash)
            self.assertEqual(chain_json[i].timestamp, node.chain[i].timestamp)

    # Проверка валидности нового блока
    # Первый блок лучше, чем новый
    def test_validate_1(self):
        node = Node(0)
        # Первый блок
        node.create_first_block(0)
        node.get_last_block().timestamp = 1.5
        block1 = node.get_last_block()
        # Новый блок с таким же индексом, но другим значением timestamp
        block2 = node.create_new_block(1)
        block2.index = 1
        block2.timestamp = 2.5
        node.validate(block2)

        self.assertEqual(node.get_last_block(), block1)
        self.assertNotEqual(node.get_last_block(), block2)
        self.assertEqual(len(node.chain), 1)

    # Проверка валидности нового блока
    # Второй блок лучше, чем первый
    def test_validate_2(self):
        node = Node(0)
        # Первый блок
        node.create_first_block(0)
        node.get_last_block().timestamp = 100.5
        block1 = node.get_last_block()
        # Новый блок с таким же индексом, но другим значением timestamp
        block2 = node.create_new_block(1)
        block2.index = 1
        block2.timestamp = 50.5
        node.validate(block2)

        self.assertEqual(node.get_last_block(), block2)
        self.assertNotEqual(node.get_last_block(), block1)
        self.assertEqual(len(node.chain), 1)

    # Проверка валидности нового блока
    # Третий блок лучше, чем первый и второй
    def test_validate_3(self):
        node = Node(0)
        # Первый блок
        node.create_first_block(0)
        node.get_last_block().timestamp = 100.5
        block1 = node.get_last_block()
        # Новый блок с таким же индексом, но другим значением timestamp
        block2 = node.create_new_block(1)
        block2.index = 1
        block2.timestamp = 50.5
        node.validate(block2)

        # Новый блок с таким же индексом, но другим значением timestamp
        block3 = node.create_new_block(2)
        block3.index = 1
        block3.timestamp = 10.5
        node.validate(block3)

        self.assertEqual(node.get_last_block(), block3)
        self.assertNotEqual(node.get_last_block(), block2)
        self.assertNotEqual(node.get_last_block(), block1)
        self.assertEqual(len(node.chain), 1)

    # Проверка валидности нового блока
    # Третий блок лучше, чем второй
    def test_validate_4(self):
        node = Node(0)
        # Первый блок
        node.create_first_block(0)
        node.get_last_block().timestamp = 100.5
        block1 = node.get_last_block()
        # Новый блок с таким же индексом, но другим значением timestamp
        block2 = node.create_new_block(1)
        block2.index = 2
        block2.timestamp = 50.5
        node.validate(block2)

        # Новый блок с таким же индексом, но другим значением timestamp
        block3 = node.create_new_block(2)
        block3.index = 2
        block3.timestamp = 10.5
        node.validate(block3)

        self.assertEqual(node.get_last_block(), block3)
        self.assertNotEqual(node.get_last_block(), block2)
        self.assertEqual(node.chain[0], block1)
        self.assertEqual(len(node.chain), 2)

    # Добавление в цепь блока в формате json
    def test_add_block_from_json(self):
        n1 = Node(0)

        node_num = 1
        n1.create_first_block(node_num)

        json_block = n1.block_to_json(n1.get_last_block(), node_num)

        from_node, json_block = n1.json_to_block(json.loads(json_block))

        n2 = Node(0)
        n2.add_block_from_json(json_block)

        self.assertEqual(node_num, from_node)

        self.assertEqual(n1.get_last_block().num_node, n2.get_last_block().num_node)
        self.assertEqual(n1.get_last_block().index, n2.get_last_block().index)
        self.assertEqual(n1.get_last_block().prev_hash, n2.get_last_block().prev_hash)
        self.assertEqual(n1.get_last_block().data, n2.get_last_block().data)
        self.assertEqual(n1.get_last_block().nonce, n2.get_last_block().nonce)
        self.assertEqual(n1.get_last_block().hash, n2.get_last_block().hash)
        self.assertEqual(n1.get_last_block().timestamp, n2.get_last_block().timestamp)

    def test_utils_t_0(self):
        t = '0'

        port, urls = config(t)

        self.assertEqual(port, 11110)
        self.assertEqual(urls, ['http://localhost:11111/', 'http://localhost:11112/'])

    def test_utils_t_1(self):
        t = '1'

        port, urls = config(t)

        self.assertEqual(port, 11111)
        self.assertEqual(urls, ['http://localhost:11110/', 'http://localhost:11112/'])

    def test_utils_t_2(self):
        t = '2'

        port, urls = config(t)

        self.assertEqual(port, 11112)
        self.assertEqual(urls, ['http://localhost:11110/', 'http://localhost:11111/'])

    # Прерываем генерацию нового блока
    def test_create_None_block(self):
        n1 = Node(0)

        node_num = 1
        # Genesis
        n1.create_first_block(node_num)

        # Новый блок, но его пока нет в цепи
        new_block = n1.create_new_block(1)

        with concurrent.futures.ThreadPoolExecutor(2) as executor:
            # Запускаем генерацию блока, чей индекс = genesis.index + 1 == new_block.index
            futures = executor.submit(n1.create_new_block, 1)
            # Добавляем new_block в цепь
            executor.submit(n1.chain.append, new_block)
            result = futures.result()

        # Отмена генерации
        self.assertIsNone(result)
        # Последний блок цепи == new_block
        self.assertEqual(n1.get_last_block(), new_block)
