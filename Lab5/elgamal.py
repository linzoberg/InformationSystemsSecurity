import random
from big_number_utils import mod_exp, mod_inverse, get_random_coprime, is_coprime


class ElGamal:
    """Реализация криптосистемы Эль-Гамаля."""

    def __init__(self, prime_bits: int = 32):
        """
        Инициализация системы Эль-Гамаля.

        Args:
            prime_bits: Длина простого числа p в битах.
        """
        self.prime_bits = prime_bits
        self.p = None  # Большое простое число
        self.g = None  # Первообразный корень по модулю p
        self.x = None  # Закрытый ключ (1 < x < p-1)
        self.y = None  # Открытый ключ (y = g^x mod p)

    def generate_keys(self):
        """Генерация пары ключей (открытый и закрытый)."""
        from prime_utils import generate_prime

        # 1. Генерируем большое простое число p
        self.p = generate_prime(self.prime_bits)

        # 2. Находим первообразный корень g (упрощенный поиск)
        self.g = self._find_primitive_root()

        # 3. Выбираем случайный закрытый ключ x
        self.x = random.randint(2, self.p - 2)

        # 4. Вычисляем открытый ключ y = g^x mod p
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
        # Берем несколько простых делителей (для учебных целей)
        factors = set()
        temp = phi
        for i in [2, 3, 5, 7, 11, 13, 17, 19]:
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
            message: Число для шифрования (0 < message < p).
            public_key: Открытый ключ (p, g, y).

        Returns:
            Кортеж (a, b) - шифротекст.
        """
        p, g, y = public_key

        if not (0 < message < p):
            raise ValueError(f"Сообщение должно быть в диапазоне (0, {p})")

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

    def encrypt_bytes(self, data: bytes, public_key: tuple) -> bytes:
        """
        Шифрование байтовых данных.
        Разбивает данные на блоки, соответствующие числам < p.
        """
        p, _, _ = public_key

        # Вычисляем максимальный размер блока в байтах
        # Чтобы число было меньше p, используем (битовая_длина(p) - 1) / 8
        max_block_size = (p.bit_length() - 1) // 8

        # Гарантируем хотя бы 1 байт для маленьких p
        if max_block_size < 1:
            max_block_size = 1

        # Дополнительная проверка: если 2^(8*max_block_size) >= p, уменьшаем размер блока
        while (1 << (8 * max_block_size)) >= p and max_block_size > 1:
            max_block_size -= 1

        encrypted_blocks = []
        for i in range(0, len(data), max_block_size):
            block = data[i:i + max_block_size]
            # Преобразуем блок байт в число
            m = int.from_bytes(block, byteorder='big')

            # Проверяем, что число меньше p
            if m >= p:
                # Если число слишком большое, уменьшаем размер блока для этого конкретного случая
                # Это может произойти для последнего блока, который может быть меньше max_block_size
                # но все равно дать большое число
                for reduced_size in range(max_block_size - 1, 0, -1):
                    if reduced_size <= len(block):
                        reduced_block = block[:reduced_size]
                        m = int.from_bytes(reduced_block, byteorder='big')
                        if m < p:
                            break
                if m >= p:
                    # Если все еще слишком большое, берем только 1 байт
                    m = block[0] if block else 0

            # Шифруем
            a, b = self.encrypt(m, public_key)

            # Кодируем a и b в байты фиксированной длины
            int_size = (p.bit_length() + 7) // 8  # Байт для хранения числа < p
            encrypted_blocks.append(a.to_bytes(int_size, 'big'))
            encrypted_blocks.append(b.to_bytes(int_size, 'big'))

        return b''.join(encrypted_blocks)

    def decrypt_bytes(self, data: bytes, private_key: tuple) -> bytes:
        """
        Дешифрование байтовых данных.
        """
        p, _ = private_key
        int_size = (p.bit_length() + 7) // 8  # Байт для хранения числа < p

        if len(data) % (2 * int_size) != 0:
            raise ValueError("Некорректный размер зашифрованных данных")

        decrypted_blocks = []
        for i in range(0, len(data), 2 * int_size):
            a = int.from_bytes(data[i:i + int_size], 'big')
            b = int.from_bytes(data[i + int_size:i + 2 * int_size], 'big')

            # Дешифруем
            m = self.decrypt((a, b), private_key)

            # Вычисляем максимальный размер блока в байтах для этого p
            max_block_size = (p.bit_length() - 1) // 8
            if max_block_size < 1:
                max_block_size = 1

            # Преобразуем число обратно в байты
            decrypted_blocks.append(m.to_bytes(max_block_size, 'big'))

        return b''.join(decrypted_blocks)


# Тестирование модуля
if __name__ == "__main__":
    print("Тестирование системы Эль-Гамаля:")

    # Создаем экземпляр
    elgamal = ElGamal(prime_bits=32)

    # Генерируем ключи
    public_key, private_key = elgamal.generate_keys()
    print(f"Открытый ключ (p, g, y):")
    print(f"  p = {public_key[0]:#x}")
    print(f"  g = {public_key[1]}")
    print(f"  y = {public_key[2]:#x}")

    # Тестовое сообщение
    test_message = 123456789
    print(f"\nТестовое сообщение: {test_message}")

    # Шифрование
    ciphertext = elgamal.encrypt(test_message, public_key)
    print(f"Шифротекст (a, b):")
    print(f"  a = {ciphertext[0]:#x}")
    print(f"  b = {ciphertext[1]:#x}")

    # Дешифрование
    decrypted = elgamal.decrypt(ciphertext, private_key)
    print(f"Расшифрованное: {decrypted}")
    print(f"Совпадает: {test_message == decrypted}")

    # Тест с байтами
    print("\nТест шифрования байтов:")
    test_bytes = b"Hello, ElGamal!"
    encrypted_bytes = elgamal.encrypt_bytes(test_bytes, public_key)
    decrypted_bytes = elgamal.decrypt_bytes(encrypted_bytes, private_key)
    print(f"Исходные: {test_bytes}")
    print(f"После шифрования-дешифрования: {decrypted_bytes}")
    print(f"Совпадает: {test_bytes == decrypted_bytes}")