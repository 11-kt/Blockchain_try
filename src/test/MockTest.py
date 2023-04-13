from unittest.mock import patch, Mock
import unittest
from Blockchain.Application import *
from Blockchain.utils import *


class MockTest(unittest.TestCase):

    # Проверка ветки генерации генезиса
    @patch('Blockchain.Application.grequests')
    def test_mining_process_add_genesis(self, mock_grequests):

        # Пропатчен асинхронный запрос (бросает исключение для выхода из цикла)
        mock_grequests.map.side_effect = FileNotFoundError

        # Создаем нод, который сгенерирует genesis
        n = Node(0)
        t = '0'
        p, urls = config(t)

        try:
            # Запускаем процесс генерации блоков, заходим в ветку if t == '0':
            mining_process(t, n, urls)
        except FileNotFoundError:
            pass

        self.assertEqual(len(n.chain), 1)
        self.assertEqual(n.get_last_block().index, 1)
        self.assertEqual(len(n.get_last_block().data), 256)
        self.assertEqual(n.get_last_block().num_node, 1)
        self.assertEqual(mock_grequests.map.call_count, 1)

    # Проверка ветки ожидания генезиса
    @patch('Blockchain.Application.len')
    def test_mining_process_wait_genesis(self, mock_len):

        # Пропатчен len (бросает исключение для выхода из цикла)
        mock_len.side_effect = FileNotFoundError

        # Создаем нод, который не будет генерировать genesis, а будет ожидать его
        n = Node(0)
        t = '1'
        p, urls = config(t)

        try:
            # Запускаем процесс генерации блоков, заходим в ветку else: (while len(n.chain) < 1:)
            mining_process(t, n, urls)
        except FileNotFoundError:
            pass

        self.assertEqual(len(n.chain), 0)
        self.assertEqual(mock_len.call_count, 1)

    # Проверка ветки создания новых блоков
    @patch('Blockchain.Application.grequests')
    def test_mining_process_create_new_block(self, mock_grequests):

        # Пропатчен асинхронный запрос (бросает исключение для выхода из цикла)
        mock_grequests.map.side_effect = FileNotFoundError

        # Создаем нод, который уже сгенерирует genesis
        n = Node(1)
        t = '1'
        p, urls = config(t)

        # Генерация genesis
        n.create_first_block(1)

        try:
            # Запускаем процесс генерации блоков, заходим в цикл постоянной генерации блоков while True:
            mining_process(t, n, urls)
        except FileNotFoundError:
            pass

        self.assertNotEqual(len(n.chain), 0)
        self.assertEqual(len(n.chain), 2)
        self.assertEqual(n.get_last_block().index, 2)
        self.assertEqual(len(n.get_last_block().data), 256)
        self.assertEqual(n.get_last_block().num_node, 2)
        self.assertNotEqual(mock_grequests.map.call_count, 2)
        self.assertTrue(mock_grequests.map.called)

    # Взаимодействие двух нод, n1 генерирует genesis, n2 ждет, а потом добавляет
    @patch('Blockchain.Application.grequests')
    def test_mining_process_node_com_genesis(self, mock_grequests):

        n1 = Node(0)

        t = '0'
        p, urls = config(t)

        n2 = Node(1)

        def grequests_map_se(args):
            n2.validate(n1.get_last_block())
            raise FileNotFoundError

        mock_grequests.map = Mock(side_effect=grequests_map_se)

        with concurrent.futures.ThreadPoolExecutor(2) as executor:
            executor.submit(mining_process, '1', n2, urls)
            executor.submit(mining_process, t, n1, urls)

        # mock_grequests вызывается 2 раза (1ый при создании генезиса, второй при генерации нового блока в While True:)
        self.assertEqual(mock_grequests.map.call_count, 2)
        # Так как вторая нода заходит в цикл и генерирует новый блок, то новый блок будет добавлен в цепь ->
        # цепь = генезис от 1ой ноды + новый блок
        self.assertEqual(n1.get_last_block(), n2.chain[0])
        self.assertEqual(len(n1.chain) + 1, len(n2.chain))
