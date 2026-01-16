import random
import math
from big_number_utils import mod_exp, gcd


def is_prime_lehman(n: int, trials: int = 50) -> bool:
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
    small_primes = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]
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


def generate_prime(bits: int = 128, lehman_trials: int = 50) -> int:
    """
    Генерирует простое число заданной битовой длины, используя тест Лемана.

    Args:
        bits: Длина числа в битах (128 бит для оценки "Отлично").
        lehman_trials: Количество испытаний в тесте Лемана.

    Returns:
        int: Сгенерированное простое число.
    """
    # Убрана проверка на 32 бита - теперь только 128 бит для оценки "Отлично"
    # Генерируем простое число сразу 128 бит
    target_bits = 128

    while True:
        # Генерируем нечетное число заданной длины
        n = random.getrandbits(target_bits)
        n |= (1 << (target_bits - 1)) | 1  # Устанавливаем старший и младший бит

        # Пропускаем четные числа
        if n % 2 == 0:
            n += 1

        # Проверяем делимость на малые простые числа
        small_primes = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31]
        is_divisible = False
        for prime in small_primes:
            if n % prime == 0 and n != prime:
                is_divisible = True
                break

        if is_divisible:
            continue

        # Проверяем на простоту с помощью теста Лемана
        if is_prime_lehman(n, lehman_trials):
            return n


# Для тестирования модуля
if __name__ == "__main__":
    print("Генерация простых чисел (тест Лемана, 128 бит):")
    print("=" * 50)

    for i in range(3):
        p = generate_prime(128)
        print(f"{i + 1}. Простое число (128 бит):")
        print(f"   Десятичное: {p}")
        print(f"   Шестнадцатеричное: {p:#x}")
        print(f"   Длина в битах: {p.bit_length()}")
        print()