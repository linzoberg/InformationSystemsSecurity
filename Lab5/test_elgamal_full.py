#!/usr/bin/env python3
"""
Тестирование системы Эль-Гамаля с 128-битными ключами.
Проверяет шифрование/дешифрование файлов разных типов и размеров.
"""

import os
import tempfile
import random
from elgamal import ElGamal
from prime_utils import generate_prime
from big_number_utils import mod_exp


def test_small_files():
    """Тестирование на маленьких файлах."""
    print("Тест 1: Маленькие файлы")
    print("=" * 50)

    elgamal = ElGamal(prime_bits=128)
    public_key, private_key = elgamal.generate_keys()

    test_cases = [
        ("Пустой файл", b""),
        ("Один символ", b"A"),
        ("Короткий текст", b"Hello, World!"),
        ("Текст с русскими буквами", "Привет, мир!".encode('utf-8')),
        ("Бинарные данные", bytes([0, 1, 2, 3, 255, 254, 253])),
        ("Случайные данные (100 байт)", os.urandom(100)),
    ]

    for name, data in test_cases:
        print(f"\n{name}: {len(data)} байт")

        try:
            encrypted = elgamal.encrypt_bytes(data, public_key)
            decrypted = elgamal.decrypt_bytes(encrypted, private_key)

            if data == decrypted:
                print(f"  ✓ Успешно (зашифровано: {len(encrypted)} байт)")
            else:
                print(f"  ✗ Ошибка: данные не совпадают")
                print(f"    Оригинал: {data[:20]}...")
                print(f"    Результат: {decrypted[:20]}...")

        except Exception as e:
            print(f"  ✗ Ошибка: {e}")


def test_large_files():
    """Тестирование на больших файлах."""
    print("\n\nТест 2: Большие файлы")
    print("=" * 50)

    elgamal = ElGamal(prime_bits=128)
    public_key, private_key = elgamal.generate_keys()

    # Размеры файлов для тестирования (в байтах)
    sizes = [1024, 10 * 1024, 100 * 1024]  # 1KB, 10KB, 100KB

    for size in sizes:
        print(f"\nФайл размером {size} байт ({size / 1024:.1f} КБ):")

        # Генерируем случайные данные
        data = os.urandom(size)

        try:
            # Шифруем
            encrypted = elgamal.encrypt_bytes(data, public_key)

            # Дешифруем
            decrypted = elgamal.decrypt_bytes(encrypted, private_key)

            # Проверяем
            if data == decrypted:
                ratio = len(encrypted) / len(data) if len(data) > 0 else 0
                print(f"  ✓ Успешно (коэффициент: {ratio:.2f}x, время: OK)")
            else:
                print(f"  ✗ Ошибка: данные не совпадают")

        except Exception as e:
            print(f"  ✗ Ошибка: {e}")


def test_file_types():
    """Тестирование на файлах разных типов."""
    print("\n\nТест 3: Файлы разных типов")
    print("=" * 50)

    elgamal = ElGamal(prime_bits=128)
    public_key, private_key = elgamal.generate_keys()

    # Создаем временные файлы разных типов
    with tempfile.TemporaryDirectory() as tmpdir:
        test_files = [
            ("текстовый файл", "test.txt", b"Text content\nMultiple lines\nEnd of file"),
            ("бинарный файл", "test.bin", bytes(range(256)) * 2),
            ("изображение (PNG заголовок)", "test.png", b'\x89PNG\r\n\x1a\n' + os.urandom(100)),
            ("PDF заголовок", "test.pdf", b'%PDF-1.5\n' + os.urandom(200)),
            ("исполняемый файл (MZ заголовок)", "test.exe", b'MZ' + os.urandom(300)),
        ]

        for file_type, filename, content in test_files:
            filepath = os.path.join(tmpdir, filename)

            # Создаем файл
            with open(filepath, 'wb') as f:
                f.write(content)

            print(f"\n{file_type} ({filename}): {len(content)} байт")

            try:
                # Шифруем файл
                encrypted = elgamal.encrypt_bytes(content, public_key)

                # Дешифруем
                decrypted = elgamal.decrypt_bytes(encrypted, private_key)

                # Проверяем
                if content == decrypted:
                    print(f"  ✓ Успешно")
                else:
                    print(f"  ✗ Ошибка: данные не совпадают")

            except Exception as e:
                print(f"  ✗ Ошибка: {e}")


def test_edge_cases():
    """Тестирование граничных случаев."""
    print("\n\nТест 4: Граничные случаи")
    print("=" * 50)

    elgamal = ElGamal(prime_bits=128)
    public_key, private_key = elgamal.generate_keys()
    p = public_key[0]

    print(f"Простое число p = {p:#x} ({p.bit_length()} бит)")
    print(f"Максимальное значение сообщения: {p - 1}")

    # Тестируем граничные значения
    test_values = [
        ("Минимальное значение", 0),
        ("Маленькое значение", 1),
        ("Значение близкое к p/2", p // 2),
        ("Значение близкое к p", p - 100),
        ("Максимальное значение", p - 1),
    ]

    for name, value in test_values:
        print(f"\n{name}: {value}")

        try:
            # Шифруем как число
            a, b = elgamal.encrypt(value, public_key)
            decrypted = elgamal.decrypt((a, b), private_key)

            if value == decrypted:
                print(f"  ✓ Успешно")
            else:
                print(f"  ✗ Ошибка: {value} != {decrypted}")

        except Exception as e:
            print(f"  ✗ Ошибка: {e}")

    # Тест с очень большим блоком (почти p)
    print(f"\nТест с блоком почти максимального размера:")
    block_size = elgamal._calculate_optimal_block_size(p)
    print(f"  Оптимальный размер блока: {block_size} байт")

    # Создаем блок максимального размера
    max_block = bytes([255] * block_size)
    m = int.from_bytes(max_block, 'big')
    print(f"  Числовое значение блока: {m}")
    print(f"  m < p: {m < p}")

    try:
        encrypted = elgamal.encrypt_bytes(max_block, public_key)
        decrypted = elgamal.decrypt_bytes(encrypted, private_key)

        if max_block == decrypted:
            print(f"  ✓ Успешно")
        else:
            print(f"  ✗ Ошибка: данные не совпадают")

    except Exception as e:
        print(f"  ✗ Ошибка: {e}")


def test_performance():
    """Тестирование производительности."""
    print("\n\nТест 5: Производительность")
    print("=" * 50)

    import time

    elgamal = ElGamal(prime_bits=128)

    print("Генерация ключей...")
    start = time.time()
    public_key, private_key = elgamal.generate_keys()
    keygen_time = time.time() - start
    print(f"  Время генерации ключей: {keygen_time:.2f} сек")

    # Тест с разными размерами данных
    sizes = [1024, 10 * 1024, 50 * 1024]  # 1KB, 10KB, 50KB

    for size in sizes:
        print(f"\nРазмер данных: {size} байт ({size / 1024:.1f} КБ)")

        data = os.urandom(size)

        # Шифрование
        start = time.time()
        encrypted = elgamal.encrypt_bytes(data, public_key)
        encrypt_time = time.time() - start

        # Дешифрование
        start = time.time()
        decrypted = elgamal.decrypt_bytes(encrypted, private_key)
        decrypt_time = time.time() - start

        # Проверка
        if data == decrypted:
            ratio = len(encrypted) / len(data)
            print(f"  ✓ Успешно")
            print(f"    Время шифрования: {encrypt_time:.2f} сек ({size / encrypt_time / 1024:.1f} КБ/сек)")
            print(f"    Время дешифрования: {decrypt_time:.2f} сек ({size / decrypt_time / 1024:.1f} КБ/сек)")
            print(f"    Коэффициент увеличения: {ratio:.2f}x")
        else:
            print(f"  ✗ Ошибка: данные не совпадают")


def main():
    """Основная функция тестирования."""
    print("ПОЛНОЕ ТЕСТИРОВАНИЕ СИСТЕМЫ ЭЛЬ-ГАМАЛЯ (128 бит)")
    print("=" * 60)

    tests = [
        ("Маленькие файлы", test_small_files),
        ("Большие файлы", test_large_files),
        ("Разные типы файлов", test_file_types),
        ("Граничные случаи", test_edge_cases),
        ("Производительность", test_performance),
    ]

    for test_name, test_func in tests:
        print(f"\n{test_name}")
        print("-" * 40)
        try:
            test_func()
        except Exception as e:
            print(f"Ошибка при выполнении теста: {e}")

    print("\n" + "=" * 60)
    print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")


if __name__ == "__main__":
    main()