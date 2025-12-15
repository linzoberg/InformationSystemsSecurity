import random
import math

def mod_exp(base: int, exponent: int, modulus: int) -> int:
    """
    Быстрое возведение в степень по модулю (метод двоичного возведения).
    base^exponent mod modulus.
    """
    if modulus == 1:
        return 0
    result = 1
    base = base % modulus

    while exponent > 0:
        if exponent % 2 == 1:
            result = (result * base) % modulus
        exponent = exponent >> 1
        base = (base * base) % modulus

    return result

def gcd(a: int, b: int) -> int:
    """Наибольший общий делитель (алгоритм Евклида)."""
    while b:
        a, b = b, a % b
    return abs(a)

def extended_gcd(a: int, b: int):
    """
    Расширенный алгоритм Евклида.
    Возвращает (g, x, y), такие что a*x + b*y = g = НОД(a, b).
    """
    if a == 0:
        return b, 0, 1
    g, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return g, x, y

def mod_inverse(a: int, m: int) -> int:
    """
    Нахождение обратного элемента a по модулю m (a^(-1) mod m).
    Использует расширенный алгоритм Евклида.
    """
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        raise ValueError(f"Обратный элемент не существует: НОД({a}, {m}) = {g}")
    return x % m

def is_coprime(a: int, b: int) -> bool:
    """Проверка, являются ли числа взаимно простыми."""
    return gcd(a, b) == 1

def get_random_coprime(n: int) -> int:
    """Генерирует случайное число, взаимно простое с n."""
    while True:
        a = random.randint(2, n - 1)
        if is_coprime(a, n):
            return a

# Тестирование модуля
if __name__ == "__main__":
    print("Тест быстрого возведения в степень:")
    result = mod_exp(7, 13, 11)
    print(f"7^13 mod 11 = {result} (ожидается 2)")

    print("\nТест обратного элемента:")
    inv = mod_inverse(7, 11)
    print(f"7^(-1) mod 11 = {inv} (ожидается 8)")
    print(f"Проверка: 7*{inv} mod 11 = {(7 * inv) % 11}")