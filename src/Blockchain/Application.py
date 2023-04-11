import concurrent.futures
import grequests as grequests


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


