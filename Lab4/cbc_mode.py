#    Режим сцепления блоков шифротекста (CBC).
#    Работает с любым блочным шифром, поддерживающим encrypt_block и decrypt_block.
class CBCMode:

    # Инициализация режима CBC.
    def __init__(self, block_cipher, block_size=5):
        self.block_cipher = block_cipher # Объект блочного шифра с методами encrypt_block и decrypt_block
        self.block_size = block_size # Размер блока в байтах (по умолчанию 5)

    # Добавляет конец к данным до размера, кратного 5. Используется PKCS#7 padding.
    def pad_data(self, data):
        padding_length = self.block_size - (len(data) % self.block_size)
        if padding_length == 0:
            padding_length = self.block_size
        # PKCS#7: добавляем байты со значением padding_length
        padding = bytes([padding_length] * padding_length)
        return data + padding

    # Удаляет padding из данных
    def unpad_data(self, data):
        if len(data) == 0:
            return data
        # Последний байт указывает длину padding
        padding_length = data[-1]
        # Проверяем корректность padding
        if padding_length < 1 or padding_length > self.block_size:
            return data
        # Проверяем, что все байты padding одинаковы
        padding = data[-padding_length:]
        if not all(b == padding_length for b in padding):
            return data
        return data[:-padding_length]

    # Шифрует данные в режиме CBC
    def encrypt(self, data, iv):
        if len(iv) != self.block_size:
            raise ValueError(f"IV должен быть длиной {self.block_size} байт")
        # Добавляем padding
        padded_data = self.pad_data(data)
        # Разбиваем на блоки
        blocks = []
        for i in range(0, len(padded_data), self.block_size):
            blocks.append(padded_data[i:i + self.block_size])
        # Шифруем в режиме CBC
        encrypted_blocks = []
        previous_block = iv
        for block in blocks:
            # XOR с предыдущим зашифрованным блоком (или IV)
            xored_block = bytes(a ^ b for a, b in zip(block, previous_block))
            # Шифруем блок
            encrypted_block = self.block_cipher.encrypt_block(xored_block)
            encrypted_blocks.append(encrypted_block)
            # Обновляем предыдущий блок
            previous_block = encrypted_block
        # Объединяем все блоки
        encrypted_data = b"".join(encrypted_blocks)
        return encrypted_data

    # Дешифрует данные в режиме CBC
    def decrypt(self, encrypted_data, iv):
        if len(iv) != self.block_size:
            raise ValueError(f"IV должен быть длиной {self.block_size} байт")
        # Проверяем, что длина данных кратна размеру блока
        if len(encrypted_data) % self.block_size != 0:
            raise ValueError("Длина зашифрованных данных должна быть кратна размеру блока")
        # Разбиваем на блоки
        blocks = []
        for i in range(0, len(encrypted_data), self.block_size):
            blocks.append(encrypted_data[i:i + self.block_size])
        # Дешифруем в режиме CBC
        decrypted_blocks = []
        previous_block = iv
        for block in blocks:
            # Дешифруем блок
            decrypted_block = self.block_cipher.decrypt_block(block)
            # XOR с предыдущим зашифрованным блоком (или IV)
            original_block = bytes(a ^ b for a, b in zip(decrypted_block, previous_block))
            decrypted_blocks.append(original_block)
            # Обновляем предыдущий блок
            previous_block = block
        # Объединяем все блоки
        decrypted_data = b"".join(decrypted_blocks)
        # Удаляем padding
        unpadded_data = self.unpad_data(decrypted_data)
        return unpadded_data

# Тестирование режима CBC
def test_cbc_mode():
    print("\nТестирование CBCMode...")

    # Импортируем здесь, чтобы избежать циклического импорта
    from matrix_cipher import MatrixCipher5x5

    # Создаем тестовый шифр
    block_cipher = MatrixCipher5x5(12345)
    cbc = CBCMode(block_cipher, block_size=5)

    # Тестовые данные
    test_data = b"Hello World! This is a test message."
    test_iv = b"12345"  # 5 байт

    print(f"Исходные данные ({len(test_data)} байт): {test_data[:20]}...")
    print(f"IV: {test_iv}")

    # Шифрование
    encrypted = cbc.encrypt(test_data, test_iv)
    print(f"Зашифрованные данные ({len(encrypted)} байт): {encrypted[:20]}...")

    # Дешифрование
    decrypted = cbc.decrypt(encrypted, test_iv)
    print(f"Дешифрованные данные ({len(decrypted)} байт): {decrypted[:20]}...")

    # Проверка
    if decrypted == test_data:
        print("✓ Тест пройден: CBC работает корректно")
    else:
        print("✗ Тест не пройден: данные не совпадают")

    # Тестирование padding
    print("\nТестирование padding...")
    test_cases = [
        b"",
        b"A",
        b"AB",
        b"ABC",
        b"ABCD",
        b"ABCDE",
        b"ABCDEF"
    ]

    for data in test_cases:
        padded = cbc.pad_data(data)
        unpadded = cbc.unpad_data(padded)
        correct = data == unpadded
        status = "✓" if correct else "✗"
        print(f"{status} '{data}' -> padding -> '{unpadded}' ({len(padded)} байт)")

    return True


if __name__ == "__main__":
    test_cbc_mode()