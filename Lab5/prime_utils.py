import random
import math
from big_number_utils import mod_exp, gcd

def is_prime_lehman(n: int, trials: int = 100) -> bool:
    """
    Тест Лемана на простоту числа.
    Возвращает True, если n, вероятно, простое (ошибка <= (1/2)^trials).

    Args:
        n: Число для проверки (должно быть нечетным и > 2).
        trials: Количество попыток (увеличивает точность).

    Returns:
        bool: Вероятно простое или нет.
    """
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False

    # Проверяем делимость на малые простые для ускорения
    small_primes = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31]
    for p in small_primes:
        if n % p == 0:
            return n == p

    for _ in range(trials):
        a = random.randint(2, n - 2)
        x = mod_exp(a, (n - 1) // 2, n)  # a^((n-1)/2) mod n

        if x == 1 or x == n - 1:
            continue
        else:
            return False  # Найден свидетель того, что n составное

    return True  # Вероятно простое

def generate_prime(bits: int = 32, lehman_trials: int = 100) -> int:
    """
    Генерирует простое число заданной битовой длины, используя тест Лемана.

    Args:
        bits: Длина числа в битах (не менее 32 по условию).
        lehman_trials: Количество испытаний в тесте Лемана.

    Returns:
        int: Сгенерированное простое число.
    """
    if bits < 32:
        raise ValueError("Для оценки 'Хорошо' требуется длина не менее 32 бит")

    while True:
        # Генерируем нечетное число заданной длины
        n = random.getrandbits(bits)
        n |= (1 << (bits - 1)) | 1  # Устанавливаем старший и младший бит

        if is_prime_lehman(n, lehman_trials):
            return n

# Для тестирования модуля
if __name__ == "__main__":
    print("Генерация простых чисел (тест Лемана):")
    for _ in range(5):
        p = generate_prime(32)
        print(f"  {p:#x} ({p.bit_length()} бит) - простое: {is_prime_lehman(p)}")