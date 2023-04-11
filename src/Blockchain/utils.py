import string
import random
from hashlib import sha256


# Генерация случайной строки
def random_string(length):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


# Рассчет хэша (sha2)
def create_hash(index, prev_hash, data, nonce):
    h = sha256()
    h.update((str(index) + str(prev_hash) + str(data) + str(nonce)).encode('utf-8'))
    return h.hexdigest()


# Конфигурация сети
def config(t):
    if t == '0':
        return 11110, ['http://localhost:11111/', 'http://localhost:11112/']
    if t == '1':
        return 11111, ['http://localhost:11110/', 'http://localhost:11112/']
    else:
        return 11112, ['http://localhost:11110/', 'http://localhost:11111/']
