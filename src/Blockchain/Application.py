import json
import concurrent.futures
import logging
import grequests as grequests
from flask import Flask, request, jsonify
import utils
from Node import Node


def exception_handler(request, exception):
    print("Request failed", request.url)


# Процесс генирации новых блоков и передачи их другим нодам
def mining_process(t, n, urls):
    # Генерация genesis
    if t == '0':
        n.create_first_block(int(t) + 1)
        # async request
        grequests.map((grequests.post(u, json=n.block_to_json(n.get_last_block(), int(t) + 1)) for u in urls))
    else:
        # Если нода не генерирует genesis, то ожидаем его
        while len(n.chain) < 1:
            continue
    # Генерация и передача новых блоков
    while True:
        # Новый блок
        with concurrent.futures.ThreadPoolExecutor(1) as executor:
            new_block_thread = executor.submit(n.create_new_block, int(t) + 1)
            new_block = new_block_thread.result()
        if new_block is None:
            continue
        # Проверяем валидность нового блока (есть ли такой блок в цепи, время его создания
        # (если есть и создан позже -> выкидываем))
        n.validate(new_block)
        # async request
        grequests.map((
            grequests.post(
                u, json=n.block_to_json(new_block, int(t) + 1)) for u in urls), exception_handler=exception_handler
        )


def start_work(t, nonce_type):

    serv = Flask(__name__)

    logging.getLogger('werkzeug').disabled = True

    # Обработка запроса
    @serv.route('/', methods=['GET', 'POST'])
    def req():

        if request.method == 'POST':
            # Конвертируем полученный json в блок
            from_node, json_block = n.json_to_block(json.loads(request.get_json()))

            # Если genesis, то просто добавляем
            if len(n.chain) == 0 and json_block.index == 1:
                n.add_block_from_json(json_block)
                return 'Genesis has been successfully obtained'

            # Если цепь на текущей ноде отстает | minority
            if abs(len(n.chain) - json_block.index) > 1:
                # Спрашиваем у ноды, чей блок пришел
                url = urls[0] if int(urls[0][-2]) == int(json_block.num_node) - 1 else urls[1]
                # async request
                r = grequests.map([grequests.get(url)])
                # Если ответ получен, то восстанавливаем цепь
                if r[0] is not None:
                    a = json.loads(json.dumps(json.loads(r[0].content)))

                    new_chain = n.json_chain_to_blockchain(a)

                    n.chain = new_chain

                    print(f'Chain has been restored from Node{json_block.index}, current block #'
                          f'{n.get_last_block().index}: {n.get_last_block()}')

                return 'Chain has been successfully restored'

            # Проверяем валидность полученного блока
            n.validate(json_block)

            return 'Block has been successfully added'

        else:
            # Передаем запрошенное состояние цепи
            return jsonify(n.chain_to_json())

    p, urls = utils.config(t)

    n = Node(nonce_type)

    with concurrent.futures.ThreadPoolExecutor(2) as executor:
        executor.submit(mining_process, t, n, urls)
        executor.submit(serv.run, '0.0.0.0', p)
