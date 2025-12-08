import time
import math

# Генератор Парка-Миллера (линейный конгруэнтный генератор)
class ParkMillerGenerator:
    # Инициализация генератора Парка-Миллера
    def __init__(self, seed=None):
        self.m = 2 ** 31 - 1  # модуль
        self.a = 16807  # множитель (7^5)
        if seed is None:
            # Генерация seed на основе текущего времени
            seed = int(time.time() * 1000) % self.m
        # Начальное состояние не должно быть 0
        self.state = seed % self.m
        if self.state == 0:
            self.state = 1
    # Генерация следующего псевдослучайного числа
    def next(self):
        self.state = (self.a * self.state) % self.m
        return self.state
    # Возвращает случайное число в диапазоне 0, 1
    def random(self):
        return self.next() / self.m
    # Генерация последовательности битов заданной длины
    def random_bits(self, n):
        bits = []
        for _ in range(n):
            # Берем младший бит от сгенерированного числа
            bit = self.next() & 1
            bits.append(str(bit))
        return ''.join(bits)

    # Генерация последовательности байтов заданной длины
    def random_bytes(self, n):
        bytes_list = []
        for _ in range(n):
            # Генерируем 8 бит для получения одного байта
            byte_val = 0
            for bit_num in range(8):
                byte_val = (byte_val << 1) | (self.next() & 1)
            bytes_list.append(byte_val)
        return bytes(bytes_list)


# Генератор Blum-Blum-Shub (BBS)
class BBSGenerator:
    # Инициализация генератора BBS с возможностью задания seed
    def __init__(self, seed=None):
        # Два простых числа, удовлетворяющих условию p ≡ 3 mod 4
        self.p = 30000000091  # Простое число, p ≡ 3 mod 4
        self.q = 40000000003  # Простое число, q ≡ 3 mod 4
        self.n = self.p * self.q  # Модуль

        if seed is None:
            # Генерация seed на основе текущего времени
            seed = int(time.time() * 1000) % self.n

        # Начальное значение должно быть взаимно простым с n
        self.state = seed % self.n
        if self.state == 0:
            self.state = 1

        # Убедимся, что НОД(state, n) = 1
        while math.gcd(self.state, self.n) != 1:
            self.state = (self.state + 1) % self.n
            if self.state == 0:
                self.state = 1
    # Генерация следующего бита
    def next_bit(self):
        # x_i = (x_{i-1})^2 mod n
        self.state = pow(self.state, 2, self.n)

        # Возвращаем младший бит
        return self.state & 1
    # Генерация последовательности битов заданной длины
    def random_bits(self, n):
        bits = []
        for _ in range(n):
            bits.append(str(self.next_bit()))
        return ''.join(bits)

    # Генерация последовательности байтов заданной длины
    def random_bytes(self, n):
        bytes_list = []
        for _ in range(n):
            # Генерируем 8 бит для получения одного байта
            byte_val = 0
            for bit_num in range(8):
                byte_val = (byte_val << 1) | self.next_bit()
            bytes_list.append(byte_val)
        return bytes(bytes_list)