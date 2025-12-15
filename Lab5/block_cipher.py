import os
import hashes
from matrix_cipher import MatrixCipher5x5
from cbc_mode import CBCMode


class BlockCipher:
    """
    Блочный шифр с матричным шифрованием 5x5 и режимом CBC.
    """

    def __init__(self, password, hash_type="MD5"):
        """
        Инициализация блочного шифра.

        Args:
            password: Пароль для генерации ключа
            hash_type: Тип хеш-функции ("MD5" или "MaHash8")
        """
        # Получаем seed из пароля
        self.seed = hashes.hash_password(password, hash_type)
        self.hash_type = hash_type

        # Создаем матричный шифр
        self.matrix_cipher = MatrixCipher5x5(self.seed)

        # Создаем режим CBC
        self.cbc = CBCMode(self.matrix_cipher, block_size=5)

        # Генерируем IV из того же seed
        self.iv = self._generate_iv()

    def _generate_iv(self):
        """
        Генерирует начальный вектор (IV) из seed.
        Для согласованности используем тот же PRNG, но с другим начальным значением.

        Returns:
            bytes: IV длиной 5 байт
        """
        # Используем seed + 1 для генерации IV
        from generators import ParkMillerGenerator
        prng = ParkMillerGenerator(self.seed + 1)

        iv_bytes = []
        for i in range(5):
            iv_bytes.append(prng.next() % 256)

        return bytes(iv_bytes)

    def encrypt_file(self, input_path, output_path, progress_callback=None):
        """
        Шифрует файл с использованием матричного шифра и режима CBC.

        Args:
            input_path: Путь к исходному файлу
            output_path: Путь для сохранения зашифрованного файла
            progress_callback: Функция для отображения прогресса (принимает процент)

        Returns:
            dict: Результат операции
        """
        try:
            # Проверка существования файла
            if not os.path.exists(input_path):
                return {
                    'success': False,
                    'error': f"Файл не найден: {input_path}"
                }

            # Определяем размер файла
            total_size = os.path.getsize(input_path)

            # Открываем файлы
            with open(input_path, 'rb') as fin, open(output_path, 'wb') as fout:
                # Записываем IV в начало файла (первые 5 байт)
                fout.write(self.iv)

                # Читаем файл блоками для прогресса
                block_size = 8192  # 8 КБ
                processed = 0

                # Собираем все данные для шифрования
                data = fin.read()

                # Шифруем данные
                encrypted_data = self.cbc.encrypt(data, self.iv)

                # Записываем зашифрованные данные
                fout.write(encrypted_data)
                processed = len(data)

                # Обновляем прогресс
                if progress_callback:
                    progress_callback(100)

            # Формируем результат
            return {
                'success': True,
                'input_path': input_path,
                'output_path': output_path,
                'input_size': total_size,
                'output_size': 5 + len(encrypted_data),  # +5 байт для IV
                'hash_type': self.hash_type,
                'seed': self.seed,
                'seed_hex': f"0x{self.seed:08x}",
                'iv': self.iv.hex(),
                'message': f"Файл успешно зашифрован. Размер: {total_size} байт"
            }

        except Exception as e:
            return {
                'success': False,
                'error': f"Ошибка при шифровании: {str(e)}"
            }

    def decrypt_file(self, input_path, output_path, progress_callback=None):
        """
        Дешифрует файл, зашифрованный матричным шифром в режиме CBC.

        Args:
            input_path: Путь к зашифрованному файлу
            output_path: Путь для сохранения дешифрованного файла
            progress_callback: Функция для отображения прогресса (принимает процент)

        Returns:
            dict: Результат операции
        """
        try:
            # Проверка существования файла
            if not os.path.exists(input_path):
                return {
                    'success': False,
                    'error': f"Файл не найден: {input_path}"
                }

            # Определяем размер файла
            total_size = os.path.getsize(input_path)

            # Открываем файлы
            with open(input_path, 'rb') as fin, open(output_path, 'wb') as fout:
                # Читаем IV из начала файла (первые 5 байт)
                iv_from_file = fin.read(5)

                if len(iv_from_file) != 5:
                    return {
                        'success': False,
                        'error': "Неверный формат зашифрованного файла (отсутствует IV)"
                    }

                # Используем IV из файла (а не сгенерированный)
                iv_to_use = iv_from_file

                # Читаем остальные данные
                encrypted_data = fin.read()

                # Дешифруем данные
                decrypted_data = self.cbc.decrypt(encrypted_data, iv_to_use)

                # Записываем дешифрованные данные
                fout.write(decrypted_data)

                # Обновляем прогресс
                if progress_callback:
                    progress_callback(100)

            # Формируем результат
            return {
                'success': True,
                'input_path': input_path,
                'output_path': output_path,
                'input_size': total_size,
                'output_size': len(decrypted_data),
                'hash_type': self.hash_type,
                'seed': self.seed,
                'seed_hex': f"0x{self.seed:08x}",
                'iv_used': iv_to_use.hex(),
                'message': f"Файл успешно дешифрован. Размер: {len(decrypted_data)} байт"
            }

        except Exception as e:
            return {
                'success': False,
                'error': f"Ошибка при дешифровании: {str(e)}"
            }

    def get_cipher_info(self):
        """
        Возвращает информацию о шифре.

        Returns:
            dict: Информация о шифре
        """
        matrix_info = self.matrix_cipher.get_matrix_info()

        return {
            'seed': self.seed,
            'seed_hex': f"0x{self.seed:08x}",
            'hash_type': self.hash_type,
            'iv': self.iv.hex(),
            'block_size': 5,
            'matrix_determinant': matrix_info['determinant']
        }


def encrypt_file(input_path, output_path, password, hash_type="MD5", progress_callback=None):
    """
    Удобная функция для шифрования файла.

    Args:
        input_path: Путь к исходному файлу
        output_path: Путь для сохранения зашифрованного файла
        password: Пароль
        hash_type: Тип хеш-функции
        progress_callback: Функция для отображения прогресса

    Returns:
        dict: Результат операции
    """
    cipher = BlockCipher(password, hash_type)
    return cipher.encrypt_file(input_path, output_path, progress_callback)


def decrypt_file(input_path, output_path, password, hash_type="MD5", progress_callback=None):
    """
    Удобная функция для дешифрования файла.

    Args:
        input_path: Путь к зашифрованному файлу
        output_path: Путь для сохранения дешифрованного файла
        password: Пароль
        hash_type: Тип хеш-функции
        progress_callback: Функция для отображения прогресса

    Returns:
        dict: Результат операции
    """
    cipher = BlockCipher(password, hash_type)
    return cipher.decrypt_file(input_path, output_path, progress_callback)


def generate_encrypted_filename(input_path):
    """
    Генерирует имя для зашифрованного файла.

    Args:
        input_path: Путь к исходному файлу

    Returns:
        str: Имя зашифрованного файла
    """
    base_name = os.path.basename(input_path)
    encrypted_name = f"{base_name}_encrypted.bcipher"
    return encrypted_name


def generate_decrypted_filename(input_path):
    """
    Генерирует имя для дешифрованного файла.

    Args:
        input_path: Путь к зашифрованному файлу

    Returns:
        str: Имя дешифрованного файла
    """
    base_name = os.path.basename(input_path)

    # Убираем суффикс _encrypted.bcipher
    if base_name.endswith("_encrypted.bcipher"):
        base_name = base_name[:-len("_encrypted.bcipher")]

    # Разделяем имя и расширение
    name_part, ext = os.path.splitext(base_name)

    # Формируем новое имя: имя_decrypted.расширение
    decrypted_name = f"{name_part}_decrypted{ext}"
    return decrypted_name


def get_file_info(file_path):
    """
    Возвращает информацию о файле.

    Args:
        file_path: Путь к файлу

    Returns:
        dict: Информация о файле
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
            '.bcipher': 'Зашифрованный файл (блочный)',
            '.enc': 'Зашифрованный файл (потоковый)',
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


def format_file_size(size_in_bytes):
    """
    Форматирует размер файла в удобочитаемый вид.

    Args:
        size_in_bytes: Размер в байтах

    Returns:
        str: Отформатированный размер
    """
    if size_in_bytes < 1024:
        return f"{size_in_bytes} Б"
    elif size_in_bytes < 1024 * 1024:
        return f"{size_in_bytes / 1024:.2f} КБ"
    elif size_in_bytes < 1024 * 1024 * 1024:
        return f"{size_in_bytes / (1024 * 1024):.2f} МБ"
    else:
        return f"{size_in_bytes / (1024 * 1024 * 1024):.2f} ГБ"


def test_block_cipher():
    """Тестирование блочного шифра"""
    print("Тестирование BlockCipher...")

    # Создаем тестовые файлы
    test_file = "test_block_cipher.txt"
    encrypted_file = "test_encrypted.bcipher"
    decrypted_file = "test_decrypted.txt"

    # Тестовые данные
    test_data = b"Hello World! This is a test of matrix cipher with CBC mode."

    try:
        # Записываем тестовый файл
        with open(test_file, 'wb') as f:
            f.write(test_data)

        print(f"Создан тестовый файл: {test_file} ({len(test_data)} байт)")

        # Тестируем шифрование
        print("\n1. Тестирование шифрования...")
        result = encrypt_file(
            input_path=test_file,
            output_path=encrypted_file,
            password="test_password",
            hash_type="MD5"
        )

        if result['success']:
            print(f"  ✓ Успешно! Зашифрованный файл: {encrypted_file}")
            print(f"    Seed: {result['seed_hex']}")
            print(f"    IV: {result['iv']}")
            print(f"    Размер: {result['input_size']} -> {result['output_size']} байт")
        else:
            print(f"  ✗ Ошибка: {result['error']}")
            return False

        # Тестируем дешифрование
        print("\n2. Тестирование дешифрования...")
        result = decrypt_file(
            input_path=encrypted_file,
            output_path=decrypted_file,
            password="test_password",
            hash_type="MD5"
        )

        if result['success']:
            print(f"  ✓ Успешно! Дешифрованный файл: {decrypted_file}")
            print(f"    IV из файла: {result['iv_used']}")

            # Проверяем содержимое
            with open(decrypted_file, 'rb') as f:
                decrypted_content = f.read()

            if decrypted_content == test_data:
                print("  ✓ Содержимое файла восстановлено корректно")
            else:
                print("  ✗ Содержимое файла не совпадает с исходным")
                print(f"    Ожидалось: {test_data[:50]}...")
                print(f"    Получено: {decrypted_content[:50]}...")
        else:
            print(f"  ✗ Ошибка: {result['error']}")
            return False

        # Тестируем с неправильным паролем
        print("\n3. Тестирование с неправильным паролем...")
        result = decrypt_file(
            input_path=encrypted_file,
            output_path="test_wrong_password.txt",
            password="wrong_password",
            hash_type="MD5"
        )

        if result['success']:
            print("  ✗ Ошибка: файл не должен дешифроваться с неправильным паролем")
        else:
            print("  ✓ Правильно: файл не дешифруется с неправильным паролем")

        # Тестируем с MaHash8
        print("\n4. Тестирование с MaHash8...")
        result = encrypt_file(
            input_path=test_file,
            output_path="test_mahash8.bcipher",
            password="another_password",
            hash_type="MaHash8"
        )

        if result['success']:
            print(f"  ✓ Успешно с MaHash8! Seed: {result['seed_hex']}")
        else:
            print(f"  ✗ Ошибка с MaHash8: {result['error']}")

        # Тестируем генерацию имен файлов
        print("\n5. Тестирование генерации имен файлов:")
        print(f"   Исходный: document.pdf")
        print(f"   Зашифрованный: {generate_encrypted_filename('document.pdf')}")
        print(f"   Дешифрованный: {generate_decrypted_filename('document_encrypted.bcipher')}")

        print("\n" + "=" * 50)
        print("Тестирование завершено успешно!")
        return True

    except Exception as e:
        print(f"Ошибка при тестировании: {e}")
        return False

    finally:
        # Удаляем тестовые файлы
        for file in [test_file, encrypted_file, decrypted_file,
                     "test_wrong_password.txt", "test_mahash8.bcipher"]:
            if os.path.exists(file):
                try:
                    os.remove(file)
                except:
                    pass


if __name__ == "__main__":
    test_block_cipher()