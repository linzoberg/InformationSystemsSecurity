import random
from big_number_utils import mod_exp, mod_inverse, get_random_coprime, is_coprime


class ElGamal:
    """Реализация криптосистемы Эль-Гамаля (128 бит)."""

    def __init__(self, prime_bits: int = 128):
        """
        Инициализация системы Эль-Гамаля.

        Args:
            prime_bits: Длина простого числа p в битах (128 бит).
        """
        self.prime_bits = 128  # Всегда 128 бит
        self.p = None
        self.g = None
        self.x = None
        self.y = None

    def generate_keys(self):
        """Генерация пары ключей (128 бит)."""
        from prime_utils import generate_prime

        # Генерируем 128-битное простое число
        self.p = generate_prime(128)

        # Находим первообразный корень g
        self.g = self._find_primitive_root()

        # Выбираем случайный закрытый ключ x
        self.x = random.randint(2, self.p - 2)

        # Вычисляем открытый ключ y = g^x mod p
        self.y = mod_exp(self.g, self.x, self.p)

        return self.get_public_key(), self.get_private_key()

    def _find_primitive_root(self, max_attempts: int = 1000) -> int:
        """
        Поиск первообразного корня по модулю p (упрощенный алгоритм).
        """
        if self.p is None:
            raise ValueError("Сначала нужно сгенерировать простое число p")

        # Разложение p-1 на простые множители (упрощенное)
        phi = self.p - 1
        factors = set()
        temp = phi
        for i in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]:
            if temp % i == 0:
                factors.add(i)
                while temp % i == 0:
                    temp //= i

        for attempt in range(max_attempts):
            g = random.randint(2, self.p - 2)
            ok = True
            for factor in factors:
                if mod_exp(g, phi // factor, self.p) == 1:
                    ok = False
                    break
            if ok:
                return g

        # Если не нашли - возвращаем небольшое число (2 часто работает)
        return 2

    def get_public_key(self) -> tuple:
        """Возвращает открытый ключ (p, g, y)."""
        if None in (self.p, self.g, self.y):
            raise ValueError("Ключи не сгенерированы")
        return (self.p, self.g, self.y)

    def get_private_key(self) -> tuple:
        """Возвращает закрытый ключ (p, x)."""
        if None in (self.p, self.x):
            raise ValueError("Ключи не сгенерированы")
        return (self.p, self.x)

    def encrypt(self, message: int, public_key: tuple) -> tuple:
        """
        Шифрование сообщения (числа) с использованием открытого ключа.

        Args:
            message: Число для шифрования (0 <= message < p).
            public_key: Открытый ключ (p, g, y).

        Returns:
            Кортеж (a, b) - шифротекст.
        """
        p, g, y = public_key

        # ВАЖНОЕ ИСПРАВЛЕНИЕ: message может быть 0!
        if not (0 <= message < p):
            raise ValueError(f"Сообщение должно быть в диапазоне [0, {p})")

        # Выбираем случайное k, взаимно простое с p-1
        k = get_random_coprime(p - 1)

        # Шифрование: a = g^k mod p, b = message * y^k mod p
        a = mod_exp(g, k, p)
        b = (message * mod_exp(y, k, p)) % p

        return (a, b)

    def decrypt(self, ciphertext: tuple, private_key: tuple) -> int:
        """
        Дешифрование шифротекста с использованием закрытого ключа.

        Args:
            ciphertext: Шифротекст (a, b).
            private_key: Закрытый ключ (p, x).

        Returns:
            int: Расшифрованное сообщение.
        """
        a, b = ciphertext
        p, x = private_key

        # Дешифрование: message = b * (a^x)^(-1) mod p
        ax = mod_exp(a, x, p)
        ax_inv = mod_inverse(ax, p)
        message = (b * ax_inv) % p

        return message

    def _calculate_optimal_block_size(self, p: int) -> int:
        """
        Рассчитывает оптимальный размер блока в байтах.
        Для 128-битного p используем блоки по 8 байт (64 бита).

        Args:
            p: Простое число

        Returns:
            int: Оптимальный размер блока в байтах
        """
        # Максимальный размер блока, чтобы число было < p
        max_possible = (p.bit_length() - 1) // 8

        # Используем блоки по 8 байт для лучшей производительности
        optimal = min(8, max_possible)

        # Гарантируем минимум 1 байт
        return max(1, optimal)

    def encrypt_bytes(self, data: bytes, public_key: tuple) -> bytes:
        """
        Шифрование байтовых данных с использованием оптимального размера блока.

        Args:
            data: Байтовые данные для шифрования
            public_key: Открытый ключ (p, g, y)

        Returns:
            bytes: Зашифрованные данные
        """
        p, _, _ = public_key

        # Рассчитываем оптимальный размер блока
        block_size = self._calculate_optimal_block_size(p)
        int_size = (p.bit_length() + 7) // 8

        # Создаем заголовок с информацией
        header = bytearray()

        # 1. Магия (4 байта)
        header.extend(b'ELG1')

        # 2. Размер исходных данных (8 байт)
        header.extend(len(data).to_bytes(8, 'big'))

        # 3. Размер блока (1 байт)
        header.extend(block_size.to_bytes(1, 'big'))

        # 4. Размер числа в байтах (1 байт)
        header.extend(int_size.to_bytes(1, 'big'))

        # Шифруем данные блоками
        encrypted_blocks = []

        for i in range(0, len(data), block_size):
            block = data[i:i + block_size]

            # Если блок неполный, добавляем padding
            if len(block) < block_size:
                padding_len = block_size - len(block)
                block += bytes([padding_len] * padding_len)

            # Преобразуем блок в число
            m = int.from_bytes(block, byteorder='big')

            # Проверяем, что число меньше p
            if m >= p:
                # Если число слишком большое, берем только часть байтов
                # Это может произойти при большом padding
                reduced_size = block_size - 1
                while reduced_size > 0 and m >= p:
                    block = data[i:i + reduced_size] if i + reduced_size <= len(data) else data[i:]
                    if not block:
                        block = b'\x00'
                    m = int.from_bytes(block, byteorder='big')
                    reduced_size -= 1

            # Шифруем блок
            a, b = self.encrypt(m, public_key)

            # Сохраняем зашифрованный блок
            encrypted_blocks.append(a.to_bytes(int_size, 'big'))
            encrypted_blocks.append(b.to_bytes(int_size, 'big'))

        # Объединяем заголовок и зашифрованные данные
        result = bytes(header) + b''.join(encrypted_blocks)

        return result

    def decrypt_bytes(self, data: bytes, private_key: tuple) -> bytes:
        """
        Дешифрование байтовых данных.

        Args:
            data: Зашифрованные байтовые данные
            private_key: Закрытый ключ (p, x)

        Returns:
            bytes: Расшифрованные данные
        """
        p, _ = private_key

        # Парсим заголовок
        if len(data) < 14:  # Минимальный размер заголовка
            raise ValueError("Некорректный формат зашифрованных данных")

        magic = data[:4]
        if magic != b'ELG1':
            raise ValueError("Некорректный формат данных (неверная магия)")

        original_size = int.from_bytes(data[4:12], 'big')
        block_size = data[12]
        int_size = data[13]

        # Проверяем согласованность
        if int_size != (p.bit_length() + 7) // 8:
            raise ValueError("Несоответствие размера числа в зашифрованных данных")

        # Пропускаем заголовок
        data = data[14:]

        # Проверяем корректность размера данных
        if len(data) % (2 * int_size) != 0:
            raise ValueError("Некорректный размер зашифрованных данных")

        # Дешифруем блоки
        decrypted_blocks = []

        for i in range(0, len(data), 2 * int_size):
            a = int.from_bytes(data[i:i + int_size], 'big')
            b = int.from_bytes(data[i + int_size:i + 2 * int_size], 'big')

            # Дешифруем блок
            m = self.decrypt((a, b), private_key)

            # Преобразуем число обратно в байты
            block_bytes = m.to_bytes(block_size, 'big')
            decrypted_blocks.append(block_bytes)

        # Объединяем все блоки
        result = b''.join(decrypted_blocks)

        # Если оригинальный размер меньше размера всех блоков, удаляем padding
        if len(result) > original_size:
            result = result[:original_size]

        return result


# Тестирование модуля
if __name__ == "__main__":
    print("Тестирование системы Эль-Гамаля (128 бит):")
    print("=" * 50)

    # Создаем экземпляр с 128-битными простыми числами
    elgamal = ElGamal(prime_bits=128)

    # Генерируем ключи
    public_key, private_key = elgamal.generate_keys()
    print(f"Открытый ключ (p, g, y):")
    print(f" p = {public_key[0]:#x}")
    print(f" g = {public_key[1]}")
    print(f" y = {public_key[2]:#x}")
    print(f" Длина p: {public_key[0].bit_length()} бит")

    # Тестовое сообщение
    test_message = 123456789
    print(f"\nТестовое сообщение: {test_message}")

    # Шифрование
    ciphertext = elgamal.encrypt(test_message, public_key)
    print(f"Шифротекст (a, b):")
    print(f" a = {ciphertext[0]:#x}")
    print(f" b = {ciphertext[1]:#x}")

    # Дешифрование
    decrypted = elgamal.decrypt(ciphertext, private_key)
    print(f"Расшифрованное: {decrypted}")
    print(f"Совпадает: {test_message == decrypted}")

    # Тест с байтами
    print("\nТест шифрования байтов:")

    # Маленький файл
    test_bytes = b"Hello, ElGamal! This is a test of 128-bit encryption."
    print(f"Исходные данные ({len(test_bytes)} байт): {test_bytes[:50]}...")

    encrypted_bytes = elgamal.encrypt_bytes(test_bytes, public_key)
    print(f"Зашифрованные данные ({len(encrypted_bytes)} байт)")

    decrypted_bytes = elgamal.decrypt_bytes(encrypted_bytes, private_key)
    print(f"Дешифрованные данные: {decrypted_bytes[:50]}...")
    print(f"Совпадает: {test_bytes == decrypted_bytes}")

    # Большой файл (имитация)
    print("\nТест с большими данными:")
    large_data = b"X" * 10000  # 10 КБ данных
    print(f"Размер исходных данных: {len(large_data)} байт")

    encrypted_large = elgamal.encrypt_bytes(large_data, public_key)
    print(f"Размер зашифрованных данных: {len(encrypted_large)} байт")
    print(f"Коэффициент увеличения: {len(encrypted_large) / len(large_data):.2f}x")

    decrypted_large = elgamal.decrypt_bytes(encrypted_large, private_key)
    print(f"Дешифрование успешно: {large_data == decrypted_large}")