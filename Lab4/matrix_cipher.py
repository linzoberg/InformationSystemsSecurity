# matrix_cipher.py
"""
Реализация матричного шифрования с размером блока 5 байт и режимом CBC
Лабораторная работа №4, вариант 4: Матричное шифрование (5 байт) + режим CBC
"""

import os
import hashes
from typing import Tuple, List, Optional, Callable
import struct

# Размер блока матричного шифрования (5 байт)
BLOCK_SIZE = 5


class MatrixCipher:
    """
    Класс для матричного шифрования с режимом CBC.
    Использует матрицы 5x5 для шифрования блоков по 5 байт.
    """

    def __init__(self, seed: int):
        """
        Инициализация матричного шифра с заданным seed.

        Args:
            seed: 32-битное число для генерации матрицы и IV
        """
        self.seed = seed
        self.matrix = self._generate_matrix_from_seed(seed)
        self.inverse_matrix = self._calculate_inverse_matrix(self.matrix)
        self.iv = self._generate_iv_from_seed(seed)

    def _generate_matrix_from_seed(self, seed: int) -> List[List[int]]:
        """
        Генерация обратимой матрицы 5x5 из seed.

        Args:
            seed: 32-битное число для генерации

        Returns:
            Обратимая матрица 5x5 по модулю 256
        """
        # Используем детерминированный алгоритм для генерации матрицы
        matrix = [[0 for _ in range(5)] for _ in range(5)]

        # Инициализируем генератор псевдослучайных чисел на основе seed
        # Простой линейный конгруэнтный генератор
        a = 1664525
        c = 1013904223
        m = 2 ** 32

        current = seed

        for i in range(5):
            for j in range(5):
                current = (a * current + c) % m
                matrix[i][j] = current % 256

        # Делаем матрицу обратимой (гарантируем, что определитель нечетный)
        # Добавляем 1 к диагональным элементам для увеличения вероятности обратимости
        for i in range(5):
            matrix[i][i] = (matrix[i][i] + 1) % 256

        return matrix

    def _matrix_determinant(self, matrix: List[List[int]]) -> int:
        """
        Вычисление определителя матрицы 5x5 по модулю 256.

        Args:
            matrix: Матрица 5x5

        Returns:
            Определитель по модулю 256
        """

        # Реализация через разложение по строке (простой метод для 5x5)
        def det_2x2(a, b, c, d):
            return (a * d - b * c) % 256

        def det_3x3(m):
            return (m[0][0] * det_2x2(m[1][1], m[1][2], m[2][1], m[2][2]) -
                    m[0][1] * det_2x2(m[1][0], m[1][2], m[2][0], m[2][2]) +
                    m[0][2] * det_2x2(m[1][0], m[1][1], m[2][0], m[2][1])) % 256

        def det_4x4(m):
            return (m[0][0] * det_3x3([[m[1][1], m[1][2], m[1][3]],
                                       [m[2][1], m[2][2], m[2][3]],
                                       [m[3][1], m[3][2], m[3][3]]]) -
                    m[0][1] * det_3x3([[m[1][0], m[1][2], m[1][3]],
                                       [m[2][0], m[2][2], m[2][3]],
                                       [m[3][0], m[3][2], m[3][3]]]) +
                    m[0][2] * det_3x3([[m[1][0], m[1][1], m[1][3]],
                                       [m[2][0], m[2][1], m[2][3]],
                                       [m[3][0], m[3][1], m[3][3]]]) -
                    m[0][3] * det_3x3([[m[1][0], m[1][1], m[1][2]],
                                       [m[2][0], m[2][1], m[2][2]],
                                       [m[3][0], m[3][1], m[3][2]]])) % 256

        # Разложение по первой строке для матрицы 5x5
        determinant = 0
        for j in range(5):
            # Создаем минор 4x4
            minor = []
            for i in range(1, 5):
                row = []
                for k in range(5):
                    if k != j:
                        row.append(matrix[i][k])
                minor.append(row)

            minor_det = det_4x4(minor)
            cofactor = (-1) ** j * matrix[0][j] * minor_det
            determinant = (determinant + cofactor) % 256

        return determinant

    def _matrix_mod_inverse(self, a: int, m: int = 256) -> int:
        """
        Нахождение обратного числа по модулю.

        Args:
            a: Число
            m: Модуль

        Returns:
            Обратное число по модулю m
        """

        # Расширенный алгоритм Евклида
        def egcd(a, b):
            if a == 0:
                return (b, 0, 1)
            else:
                g, y, x = egcd(b % a, a)
                return (g, x - (b // a) * y, y)

        g, x, _ = egcd(a, m)
        if g != 1:
            raise ValueError("Обратного элемента не существует")
        else:
            return x % m

    def _matrix_cofactor(self, matrix: List[List[int]], i: int, j: int) -> int:
        """
        Вычисление кофактора (алгебраического дополнения) элемента матрицы.

        Args:
            matrix: Матрица 5x5
            i: Строка элемента
            j: Столбец элемента

        Returns:
            Кофактор элемента
        """
        # Создаем минор 4x4
        minor = []
        for row_idx in range(5):
            if row_idx != i:
                row = []
                for col_idx in range(5):
                    if col_idx != j:
                        row.append(matrix[row_idx][col_idx])
                minor.append(row)

        # Определитель минора
        return ((-1) ** (i + j)) * self._matrix_determinant(minor) % 256

    def _calculate_inverse_matrix(self, matrix: List[List[int]]) -> List[List[int]]:
        """
        Вычисление обратной матрицы по модулю 256.

        Args:
            matrix: Исходная матрица 5x5

        Returns:
            Обратная матрица по модулю 256

        Raises:
            ValueError: Если матрица необратима
        """
        det = self._matrix_determinant(matrix)

        # Проверяем обратимость матрицы
        if det % 2 == 0:  # Определитель должен быть нечетным для обратимости по модулю 256
            # Делаем матрицу обратимой, добавляя 1 к диагональным элементам
            for i in range(5):
                matrix[i][i] = (matrix[i][i] + 1) % 256
            det = self._matrix_determinant(matrix)

            # Если все еще необратима, выбрасываем исключение
            if det % 2 == 0:
                raise ValueError("Не удалось создать обратимую матрицу")

        det_inv = self._matrix_mod_inverse(det)

        # Вычисляем союзную матрицу (матрицу алгебраических дополнений)
        adjugate = [[0 for _ in range(5)] for _ in range(5)]

        for i in range(5):
            for j in range(5):
                adjugate[j][i] = (self._matrix_cofactor(matrix, i, j) * det_inv) % 256

        return adjugate

    def _generate_iv_from_seed(self, seed: int) -> bytes:
        """
        Генерация вектора инициализации (IV) из seed.

        Args:
            seed: 32-битное число для генерации

        Returns:
            IV размером 5 байт
        """
        # Преобразуем seed в 5 байт
        iv_bytes = bytearray(5)

        for i in range(5):
            # Используем разные сдвиги для каждого байта
            shift = i * 6  # 0, 6, 12, 18, 24
            byte_val = (seed >> shift) & 0xFF
            iv_bytes[i] = byte_val

        # Если какие-то байты нулевые, заменяем их
        for i in range(5):
            if iv_bytes[i] == 0:
                iv_bytes[i] = ((seed >> (i * 7)) & 0xFF) + 1

        return bytes(iv_bytes)

    def encrypt_block(self, block: bytes, matrix: List[List[int]]) -> bytes:
        """
        Шифрование одного блока (5 байт) с помощью матрицы.

        Args:
            block: Блок данных (5 байт)
            matrix: Матрица 5x5

        Returns:
            Зашифрованный блок (5 байт)
        """
        if len(block) != 5:
            raise ValueError(f"Размер блока должен быть 5 байт, получено {len(block)}")

        # Преобразуем блок в вектор (список чисел)
        vector = [block[i] for i in range(5)]
        result = [0] * 5

        # Матричное умножение: result = matrix * vector (mod 256)
        for i in range(5):
            sum_val = 0
            for j in range(5):
                sum_val = (sum_val + matrix[i][j] * vector[j]) % 256
            result[i] = sum_val

        return bytes(result)

    def decrypt_block(self, block: bytes, inverse_matrix: List[List[int]]) -> bytes:
        """
        Дешифрование одного блока (5 байт) с помощью обратной матрицы.

        Args:
            block: Зашифрованный блок (5 байт)
            inverse_matrix: Обратная матрица 5x5

        Returns:
            Расшифрованный блок (5 байт)
        """
        # Дешифрование аналогично шифрованию, но с обратной матрицей
        return self.encrypt_block(block, inverse_matrix)

    def pad_data(self, data: bytes) -> bytes:
        """
        Дополнение данных до размера кратного 5 байтам.

        Args:
            data: Исходные данные

        Returns:
            Дополненные данные
        """
        padding_len = (BLOCK_SIZE - len(data) % BLOCK_SIZE) % BLOCK_SIZE
        if padding_len == 0:
            padding_len = BLOCK_SIZE

        # PKCS#7 подобное дополнение
        padding = bytes([padding_len] * padding_len)
        return data + padding

    def unpad_data(self, padded_data: bytes) -> bytes:
        """
        Удаление дополнения из данных.

        Args:
            padded_data: Дополненные данные

        Returns:
            Исходные данные без дополнения
        """
        if len(padded_data) == 0:
            return padded_data

        padding_len = padded_data[-1]

        # Проверяем корректность padding
        if padding_len < 1 or padding_len > BLOCK_SIZE:
            return padded_data

        # Проверяем, что все байты padding одинаковы
        padding = padded_data[-padding_len:]
        if all(byte == padding_len for byte in padding):
            return padded_data[:-padding_len]
        else:
            return padded_data

    def encrypt_cbc(self, data: bytes) -> bytes:
        """
        Шифрование данных в режиме CBC.

        Args:
            data: Исходные данные

        Returns:
            Зашифрованные данные
        """
        # Дополняем данные
        padded_data = self.pad_data(data)

        # Инициализируем предыдущий блок как IV
        prev_block = self.iv
        encrypted_blocks = []

        # Обрабатываем блоки
        for i in range(0, len(padded_data), BLOCK_SIZE):
            block = padded_data[i:i + BLOCK_SIZE]

            # XOR с предыдущим зашифрованным блоком
            xored_block = bytes(block[j] ^ prev_block[j] for j in range(BLOCK_SIZE))

            # Шифруем блок
            encrypted_block = self.encrypt_block(xored_block, self.matrix)
            encrypted_blocks.append(encrypted_block)

            # Обновляем предыдущий блок
            prev_block = encrypted_block

        # Объединяем все блоки
        return b''.join(encrypted_blocks)

    def decrypt_cbc(self, encrypted_data: bytes) -> bytes:
        """
        Дешифрование данных в режиме CBC.

        Args:
            encrypted_data: Зашифрованные данные

        Returns:
            Расшифрованные данные
        """
        if len(encrypted_data) % BLOCK_SIZE != 0:
            raise ValueError(f"Размер зашифрованных данных должен быть кратен {BLOCK_SIZE}")

        # Инициализируем предыдущий блок как IV
        prev_block = self.iv
        decrypted_blocks = []

        # Обрабатываем блоки
        for i in range(0, len(encrypted_data), BLOCK_SIZE):
            block = encrypted_data[i:i + BLOCK_SIZE]

            # Дешифруем блок
            decrypted_block = self.decrypt_block(block, self.inverse_matrix)

            # XOR с предыдущим зашифрованным блоком
            xored_block = bytes(decrypted_block[j] ^ prev_block[j] for j in range(BLOCK_SIZE))
            decrypted_blocks.append(xored_block)

            # Обновляем предыдущий блок
            prev_block = block

        # Объединяем все блоки и удаляем дополнение
        decrypted_data = b''.join(decrypted_blocks)
        return self.unpad_data(decrypted_data)


# Функции для работы с файлами
def encrypt_file(input_path: str, output_path: str, password: str,
                 hash_type: str = "MD5", progress_callback: Optional[Callable] = None) -> dict:
    """
    Шифрование файла с использованием матричного шифрования CBC.

    Args:
        input_path: Путь к входному файлу
        output_path: Путь для сохранения зашифрованного файла
        password: Пароль для шифрования
        hash_type: Тип хеш-функции ("MD5" или "MaHash8")
        progress_callback: Функция для отслеживания прогресса

    Returns:
        Словарь с результатами операции
    """
    try:
        # 1. Валидация входных параметров
        if not os.path.exists(input_path):
            return {
                'success': False,
                'error': f"Входной файл не найден: {input_path}"
            }

        if not password:
            return {
                'success': False,
                'error': "Пароль не может быть пустым"
            }

        if hash_type not in ["MD5", "MaHash8"]:
            return {
                'success': False,
                'error': f"Неподдерживаемый тип хеш-функции: {hash_type}"
            }

        # 2. Получение seed из пароля
        seed = hashes.hash_password(password, hash_type)

        # 3. Создание шифра
        cipher = MatrixCipher(seed)

        # 4. Определение размера файла для отслеживания прогресса
        total_size = os.path.getsize(input_path)
        processed = 0

        # 5. Открытие файлов в бинарном режиме
        with open(input_path, 'rb') as fin, open(output_path, 'wb') as fout:
            # 6. Чтение всего файла (для матричного шифрования проще читать целиком)
            data = fin.read()

            # 7. Шифрование данных
            encrypted_data = cipher.encrypt_cbc(data)

            # 8. Запись зашифрованных данных
            fout.write(encrypted_data)

            # 9. Обновление прогресса
            processed = len(data)
            if progress_callback:
                progress_callback(100)

        # 10. Формирование отчёта об успешном выполнении
        return {
            'success': True,
            'input_path': input_path,
            'output_path': output_path,
            'input_size': total_size,
            'output_size': len(encrypted_data),
            'hash_type': hash_type,
            'seed_hex': f"0x{seed:08x}",
            'seed_decimal': seed,
            'iv_hex': cipher.iv.hex(),
            'message': f"Файл успешно зашифрован. Размер: {total_size} байт"
        }

    except PermissionError as e:
        return {
            'success': False,
            'error': f"Ошибка доступа к файлу: {str(e)}"
        }
    except MemoryError as e:
        return {
            'success': False,
            'error': f"Недостаточно памяти для обработки файла: {str(e)}"
        }
    except Exception as e:
        return {
            'success': False,
            'error': f"Непредвиденная ошибка: {str(e)}"
        }


def decrypt_file(input_path: str, output_path: str, password: str,
                 hash_type: str = "MD5", progress_callback: Optional[Callable] = None) -> dict:
    """
    Дешифрование файла с использованием матричного шифрования CBC.

    Args:
        input_path: Путь к зашифрованному файлу
        output_path: Путь для сохранения расшифрованного файла
        password: Пароль для дешифрования
        hash_type: Тип хеш-функции ("MD5" или "MaHash8")
        progress_callback: Функция для отслеживания прогресса

    Returns:
        Словарь с результатами операции
    """
    try:
        # 1. Валидация входных параметров
        if not os.path.exists(input_path):
            return {
                'success': False,
                'error': f"Входной файл не найден: {input_path}"
            }

        if not password:
            return {
                'success': False,
                'error': "Пароль не может быть пустым"
            }

        if hash_type not in ["MD5", "MaHash8"]:
            return {
                'success': False,
                'error': f"Неподдерживаемый тип хеш-функции: {hash_type}"
            }

        # 2. Получение seed из пароля
        seed = hashes.hash_password(password, hash_type)

        # 3. Создание шифра
        cipher = MatrixCipher(seed)

        # 4. Определение размера файла для отслеживания прогресса
        total_size = os.path.getsize(input_path)
        processed = 0

        # 5. Открытие файлов в бинарном режиме
        with open(input_path, 'rb') as fin, open(output_path, 'wb') as fout:
            # 6. Чтение всего файла
            encrypted_data = fin.read()

            # Проверяем размер данных
            if len(encrypted_data) % BLOCK_SIZE != 0:
                return {
                    'success': False,
                    'error': f"Некорректный размер зашифрованного файла. Должен быть кратен {BLOCK_SIZE}"
                }

            # 7. Дешифрование данных
            decrypted_data = cipher.decrypt_cbc(encrypted_data)

            # 8. Запись расшифрованных данных
            fout.write(decrypted_data)

            # 9. Обновление прогресса
            processed = len(encrypted_data)
            if progress_callback:
                progress_callback(100)

        # 10. Формирование отчёта об успешном выполнении
        return {
            'success': True,
            'input_path': input_path,
            'output_path': output_path,
            'input_size': total_size,
            'output_size': len(decrypted_data),
            'hash_type': hash_type,
            'seed_hex': f"0x{seed:08x}",
            'seed_decimal': seed,
            'message': f"Файл успешно дешифрован. Размер: {total_size} байт"
        }

    except PermissionError as e:
        return {
            'success': False,
            'error': f"Ошибка доступа к файлу: {str(e)}"
        }
    except MemoryError as e:
        return {
            'success': False,
            'error': f"Недостаточно памяти для обработки файла: {str(e)}"
        }
    except Exception as e:
        return {
            'success': False,
            'error': f"Непредвиденная ошибка: {str(e)}"
        }


def generate_encrypted_filename(input_path: str) -> str:
    """
    Формирует имя файла для шифрования.

    Args:
        input_path: Путь к исходному файлу

    Returns:
        Имя зашифрованного файла
    """
    base_name = os.path.basename(input_path)
    encrypted_name = f"{base_name}_matrix_encrypted.enc"
    return encrypted_name


def generate_decrypted_filename(input_path: str) -> str:
    """
    Формирует имя файла для дешифрования.

    Args:
        input_path: Путь к зашифрованному файлу

    Returns:
        Имя дешифрованного файла
    """
    base_name = os.path.basename(input_path)

    # Убираем суффикс _matrix_encrypted.enc
    if base_name.endswith("_matrix_encrypted.enc"):
        base_name = base_name[:-len("_matrix_encrypted.enc")]

    # Разделяем имя и расширение
    name_part, ext = os.path.splitext(base_name)

    # Формируем новое имя: имя_matrix_decrypted.расширение
    decrypted_name = f"{name_part}_matrix_decrypted{ext}"
    return decrypted_name


def validate_password(password: str) -> Tuple[bool, str]:
    """
    Проверяет минимальные требования к паролю.

    Args:
        password: Пароль для проверки

    Returns:
        Кортеж (успех, сообщение)
    """
    if not password:
        return False, "Пароль не может быть пустым"

    if len(password) < 1:
        return False, "Введите хотя бы один символ"

    return True, "Пароль корректен"


def get_file_info(file_path: str) -> dict:
    """
    Получает информацию о файле.

    Args:
        file_path: Путь к файлу

    Returns:
        Словарь с информацией о файле
    """
    try:
        if not os.path.exists(file_path):
            return {'success': False, 'error': 'Файл не существует'}

        size = os.path.getsize(file_path)

        # Определение типа файла по расширению
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()

        file_types = {
            '.txt': 'Текстовый файл',
            '.doc': 'Документ Word',
            '.docx': 'Документ Word',
            '.pdf': 'PDF документ',
            '.jpg': 'Изображение JPEG',
            '.jpeg': 'Изображение JPEG',
            '.png': 'Изображение PNG',
            '.bmp': 'Изображение BMP',
            '.gif': 'Изображение GIF',
            '.mp4': 'Видео MP4',
            '.avi': 'Видео AVI',
            '.mov': 'Видео MOV',
            '.mp3': 'Аудио MP3',
            '.wav': 'Аудио WAV',
            '.enc': 'Зашифрованный файл',
            '.bin': 'Бинарный файл',
            '.exe': 'Исполняемый файл',
            '.zip': 'Архив ZIP',
            '.rar': 'Архив RAR'
        }

        file_type = file_types.get(ext, 'Неизвестный тип файла')

        return {
            'success': True,
            'path': file_path,
            'name': os.path.basename(file_path),
            'size': size,
            'size_human': format_file_size(size),
            'extension': ext,
            'type': file_type,
            'exists': True
        }

    except Exception as e:
        return {'success': False, 'error': str(e)}


def format_file_size(size_in_bytes: int) -> str:
    """
    Форматирует размер файла в удобочитаемый вид.

    Args:
        size_in_bytes: Размер в байтах

    Returns:
        Форматированная строка
    """
    if size_in_bytes < 1024:
        return f"{size_in_bytes} Б"
    elif size_in_bytes < 1024 * 1024:
        return f"{size_in_bytes / 1024:.2f} КБ"
    elif size_in_bytes < 1024 * 1024 * 1024:
        return f"{size_in_bytes / (1024 * 1024):.2f} МБ"
    else:
        return f"{size_in_bytes / (1024 * 1024 * 1024):.2f} ГБ"


# Тестирование модуля
if __name__ == "__main__":
    print("Тестирование модуля matrix_cipher.py")
    print("=" * 50)

    # Создаем тестовый файл
    test_content = b"Hello, World! This is a test file for matrix cipher testing with CBC mode."
    test_file = "test_input.txt"
    encrypted_file = "test_matrix_encrypted.enc"
    decrypted_file = "test_matrix_decrypted.txt"

    try:
        # Записываем тестовый файл
        with open(test_file, 'wb') as f:
            f.write(test_content)

        print(f"Создан тестовый файл: {test_file} ({len(test_content)} байт)")

        # Тестируем генерацию имен файлов
        print("\n1. Тестирование генерации имен файлов:")
        print(f" Исходный файл: test_video.MP4")
        print(f" Зашифрованный: {generate_encrypted_filename('test_video.MP4')}")
        print(f" Дешифрованный: {generate_decrypted_filename('test_video.MP4_matrix_encrypted.enc')}")

        # Тестируем шифрование
        print("\n2. Тестирование шифрования с MD5:")
        result = encrypt_file(
            input_path=test_file,
            output_path=encrypted_file,
            password="test_password",
            hash_type="MD5"
        )

        if result['success']:
            print(f" Успешно! Зашифрованный файл: {encrypted_file}")
            print(f" Seed: {result['seed_hex']}")
            print(f" IV: {result['iv_hex']}")
        else:
            print(f" Ошибка: {result['error']}")

        # Тестируем дешифрование
        print("\n3. Тестирование дешифрования с MD5:")
        result = decrypt_file(
            input_path=encrypted_file,
            output_path=decrypted_file,
            password="test_password",
            hash_type="MD5"
        )

        if result['success']:
            print(f" Успешно! Дешифрованный файл: {decrypted_file}")

            # Проверяем содержимое
            with open(decrypted_file, 'rb') as f:
                decrypted_content = f.read()

            if decrypted_content == test_content:
                print(" ✓ Содержимое файла восстановлено корректно")
            else:
                print(" ✗ Содержимое файла не совпадает с исходным")
                print(f"  Длина исходного: {len(test_content)}")
                print(f"  Длина дешифрованного: {len(decrypted_content)}")
        else:
            print(f" Ошибка: {result['error']}")

        # Тестируем с MaHash8
        print("\n4. Тестирование шифрования с MaHash8:")
        encrypted_file2 = "test_matrix_encrypted2.enc"
        decrypted_file2 = "test_matrix_decrypted2.txt"

        result = encrypt_file(
            input_path=test_file,
            output_path=encrypted_file2,
            password="another_password",
            hash_type="MaHash8"
        )

        if result['success']:
            print(f" Успешно! Зашифрованный файл: {encrypted_file2}")
            print(f" Seed: {result['seed_hex']}")

            result = decrypt_file(
                input_path=encrypted_file2,
                output_path=decrypted_file2,
                password="another_password",
                hash_type="MaHash8"
            )

            if result['success']:
                print(f" Успешно! Дешифрованный файл: {decrypted_file2}")

                with open(decrypted_file2, 'rb') as f:
                    decrypted_content = f.read()

                if decrypted_content == test_content:
                    print(" ✓ Содержимое файла восстановлено корректно")
                else:
                    print(" ✗ Содержимое файла не совпадает с исходным")
            else:
                print(f" Ошибка при дешифровании: {result['error']}")
        else:
            print(f" Ошибка при шифровании: {result['error']}")

        # Тестируем функцию получения информации о файле
        print("\n5. Тестирование get_file_info:")
        info = get_file_info(test_file)
        if info['success']:
            print(f" Имя: {info['name']}")
            print(f" Размер: {info['size_human']}")
            print(f" Тип: {info['type']}")

        print("\n" + "=" * 50)
        print("Тестирование завершено.")

    except Exception as e:
        print(f"Ошибка при тестировании: {e}")
        import traceback

        traceback.print_exc()

    finally:
        # Удаляем тестовые файлы
        for file in [test_file, encrypted_file, decrypted_file,
                     encrypted_file2, decrypted_file2]:
            if os.path.exists(file):
                try:
                    os.remove(file)
                except:
                    pass