import time
import math

# Генератор Парка-Миллера (линейный конгруэнтный генератор)
class ParkMillerGenerator:
    # Инициализация генератора
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

# Линейный сдвиговый регистр с обратной связью (компонент для генератора Геффа)
class LFSR:
    def __init__(self, length, taps, seed=None):
        self.length = length
        self.taps = taps
        self.mask = (1 << length) - 1
        if seed is None:
            seed = int(time.time() * 1000) & self.mask
        # Начальное состояние не должно быть 0
        self.state = seed & self.mask
        if self.state == 0:
            self.state = 1
    # Генерация следующего бита
    def next_bit(self):
        # Вычисляем обратную связь как XOR отведенных битов
        feedback = 0
        for tap in self.taps:
            # tap-1, так как taps задаются начиная с 1
            feedback ^= (self.state >> (tap - 1)) & 1
        # Выходной бит - младший бит текущего состояния
        output = self.state & 1
        # Сдвигаем регистр вправо и добавляем новый бит слева
        self.state = ((self.state >> 1) | (feedback << (self.length - 1))) & self.mask
        return output

# Генератор Геффа - комбинирующий генератор на основе трех LFSR
class GeffeGenerator:
    # Инициализация генератора
    def __init__(self, seeds=None):
        if seeds is None:
            seeds = [None, None, None]
        # LFSR1: длина 19, отводы [19, 18, 17, 14]
        self.lfsr1 = LFSR(19, [19, 18, 17, 14], seeds[0])
        # LFSR2: длина 23, отводы [23, 22, 20, 18]
        self.lfsr2 = LFSR(23, [23, 22, 20, 18], seeds[1])
        # LFSR3: длина 29, отводы [29, 27, 24, 23]
        self.lfsr3 = LFSR(29, [29, 27, 24, 23], seeds[2])
    # Генерация следующего бита по алгоритму Геффа
    def next_bit(self):
        # Получаем биты от каждого LFSR
        x1 = self.lfsr1.next_bit()
        x2 = self.lfsr2.next_bit()
        x3 = self.lfsr3.next_bit()
        # Нелинейная функция Геффа: f(x1, x2, x3) = (x1 & x2) | (~x1 & x3)
        # В терминах XOR: f(x1, x2, x3) = (x1 & x2) ^ ((1 ^ x1) & x3)
        return (x1 & x2) ^ ((1 ^ x1) & x3)
    # Генерация последовательности битов заданной длины
    def random_bits(self, n):
        bits = []
        for _ in range(n):
            bits.append(str(self.next_bit()))
        return ''.join(bits)

# Тестирование модуля
if __name__ == "__main__":
    # Тест генератора Парка-Миллера
    print("Тестирование генератора Парка-Миллера:")
    pm = ParkMillerGenerator(12345)
    test_bits_pm = pm.random_bits(20)
    print(f"Первые 20 бит: {test_bits_pm}")
    print(f"Следующее случайное число: {pm.random():.6f}")

    # Тест генератора Геффа
    print("\nТестирование генератора Геффа:")
    geffe = GeffeGenerator()
    test_bits_geffe = geffe.random_bits(20)
    print(f"Первые 20 бит: {test_bits_geffe}")

    # Статистика для 1000 бит
    test_bits_geffe_long = geffe.random_bits(1000)
    zeros = test_bits_geffe_long.count('0')
    ones = test_bits_geffe_long.count('1')
    print(f"Для 1000 бит: нулей={zeros}, единиц={ones}, соотношение={zeros / 1000:.3f}")