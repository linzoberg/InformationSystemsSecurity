import os
import hashes
import generators

# Размер блока для обработки файлов (8 КБ)
BLOCK_SIZE = 8192


# Шифрует или дешифрует файл с использованием потокового шифрования
def encrypt_decrypt_file(input_path, output_path, password, hash_type="MD5",
                         generator_type="Парка-Миллера", progress_callback=None):
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

        if generator_type not in ["Парка-Миллера", "BBS"]:
            return {
                'success': False,
                'error': f"Неподдерживаемый тип генератора: {generator_type}"
            }

        # 2. Получение seed из пароля с помощью выбранной хеш-функции
        seed = hashes.hash_password(password, hash_type)

        # 3. Инициализация генератора псевдослучайных чисел
        if generator_type == "Парка-Миллера":
            generator = generators.ParkMillerGenerator(seed)
        elif generator_type == "BBS":
            generator = generators.BBSGenerator(seed)

        # 4. Определение размера файла для отслеживания прогресса
        total_size = os.path.getsize(input_path)
        processed = 0

        # 5. Открытие файлов в бинарном режиме
        with open(input_path, 'rb') as fin, open(output_path, 'wb') as fout:
            # 6. Обработка файла блоками
            while True:
                # Чтение блока данных из входного файла
                data_block = fin.read(BLOCK_SIZE)
                if not data_block:
                    break

                # 7. Генерация ключевого блока той же длины
                key_block = generator.random_bytes(len(data_block))

                # 8. Применение операции XOR к каждому байту
                result_block = bytes(a ^ b for a, b in zip(data_block, key_block))

                # 9. Запись результата в выходной файл
                fout.write(result_block)

                # 10. Обновление прогресса выполнения
                processed += len(data_block)
                if progress_callback:
                    progress = int((processed / total_size) * 100)
                    progress_callback(progress)

        # 11. Формирование отчёта об успешном выполнении
        return {
            'success': True,
            'input_path': input_path,
            'output_path': output_path,
            'input_size': total_size,
            'output_size': processed,
            'hash_type': hash_type,
            'generator_type': generator_type,
            'seed_hex': f"0x{seed:08x}",
            'seed_decimal': seed,
            'message': f"Файл успешно обработан. Размер: {total_size} байт"
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


# Шифрует файл
def encrypt_file(input_path, output_path, password, hash_type="MD5",
                 generator_type="Парка-Миллера", progress_callback=None):
    return encrypt_decrypt_file(input_path, output_path, password,
                                hash_type, generator_type, progress_callback)


# Дешифрует файл
def decrypt_file(input_path, output_path, password, hash_type="MD5",
                 generator_type="Парка-Миллера", progress_callback=None):
    return encrypt_decrypt_file(input_path, output_path, password,
                                hash_type, generator_type, progress_callback)


# Проверяет минимальные требования к паролю
def validate_password(password):
    if not password:
        return False, "Пароль не может быть пустым"

    if len(password) < 1:
        return False, "Введите хотя бы один символ"

    return True, "Пароль корректен"


# Формирует имя файла для шифрования
def generate_encrypted_filename(input_path):
    base_name = os.path.basename(input_path)
    encrypted_name = f"{base_name}_encrypted.enc"
    return encrypted_name


# Формирует имя файла для дешифрования
def generate_decrypted_filename(input_path):
    base_name = os.path.basename(input_path)

    # Убираем суффикс _encrypted.enc
    if base_name.endswith("_encrypted.enc"):
        base_name = base_name[:-len("_encrypted.enc")]

    # Разделяем имя и расширение
    name_part, ext = os.path.splitext(base_name)

    # Формируем новое имя: имя_decrypted.расширение
    decrypted_name = f"{name_part}_decrypted{ext}"
    return decrypted_name


# Получает информацию о файле
def get_file_info(file_path):
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


# Форматирует размер файла в удобочитаемый вид
def format_file_size(size_in_bytes):
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
    print("Тестирование модуля cipher.py")
    print("=" * 50)

    # Создаем тестовый файл
    test_content = b"Hello, World! This is a test file for stream cipher testing."
    test_file = "test_input.txt"
    encrypted_file = "test_encrypted.bin"
    decrypted_file = "test_decrypted.txt"

    try:
        # Записываем тестовый файл
        with open(test_file, 'wb') as f:
            f.write(test_content)

        print(f"Создан тестовый файл: {test_file} ({len(test_content)} байт)")

        # Тестируем генерацию имен файлов
        print("\n1. Тестирование генерации имен файлов:")
        print(f"   Исходный файл: test_video.MP4")
        print(f"   Зашифрованный: {generate_encrypted_filename('test_video.MP4')}")
        print(f"   Дешифрованный: {generate_decrypted_filename('test_video.MP4_encrypted.enc')}")

        # Тестируем шифрование
        print("\n2. Тестирование шифрования с MD5 и Парка-Миллера:")
        result = encrypt_file(
            input_path=test_file,
            output_path=encrypted_file,
            password="test_password",
            hash_type="MD5",
            generator_type="Парка-Миллера"
        )

        if result['success']:
            print(f"   Успешно! Зашифрованный файл: {encrypted_file}")
            print(f"   Seed: {result['seed_hex']}")
        else:
            print(f"   Ошибка: {result['error']}")

        # Тестируем дешифрование
        print("\n3. Тестирование дешифрования с MD5 и Парка-Миллера:")
        result = decrypt_file(
            input_path=encrypted_file,
            output_path=decrypted_file,
            password="test_password",
            hash_type="MD5",
            generator_type="Парка-Миллера"
        )

        if result['success']:
            print(f"   Успешно! Дешифрованный файл: {decrypted_file}")

            # Проверяем содержимое
            with open(decrypted_file, 'rb') as f:
                decrypted_content = f.read()

            if decrypted_content == test_content:
                print("   ✓ Содержимое файла восстановлено корректно")
            else:
                print("   ✗ Содержимое файла не совпадает с исходным")
        else:
            print(f"   Ошибка: {result['error']}")

        # Тестируем с MaHash8 и BBS
        print("\n4. Тестирование шифрования с MaHash8 и BBS:")
        encrypted_file2 = "test_encrypted2.bin"
        decrypted_file2 = "test_decrypted2.txt"

        result = encrypt_file(
            input_path=test_file,
            output_path=encrypted_file2,
            password="another_password",
            hash_type="MaHash8",
            generator_type="BBS"
        )

        if result['success']:
            print(f"   Успешно! Зашифрованный файл: {encrypted_file2}")
            print(f"   Seed: {result['seed_hex']}")

            result = decrypt_file(
                input_path=encrypted_file2,
                output_path=decrypted_file2,
                password="another_password",
                hash_type="MaHash8",
                generator_type="BBS"
            )

            if result['success']:
                print(f"   Успешно! Дешифрованный файл: {decrypted_file2}")

                with open(decrypted_file2, 'rb') as f:
                    decrypted_content = f.read()

                if decrypted_content == test_content:
                    print("   ✓ Содержимое файла восстановлено корректно")
                else:
                    print("   ✗ Содержимое файла не совпадает с исходным")
            else:
                print(f"   Ошибка при дешифровании: {result['error']}")
        else:
            print(f"   Ошибка при шифровании: {result['error']}")

        # Тестируем функцию получения информации о файле
        print("\n5. Тестирование get_file_info:")
        info = get_file_info(test_file)
        if info['success']:
            print(f"   Имя: {info['name']}")
            print(f"   Размер: {info['size_human']}")
            print(f"   Тип: {info['type']}")

        print("\n" + "=" * 50)
        print("Тестирование завершено.")

    except Exception as e:
        print(f"Ошибка при тестировании: {e}")

    finally:
        # Удаляем тестовые файлы
        for file in [test_file, encrypted_file, decrypted_file,
                     encrypted_file2, decrypted_file2]:
            if os.path.exists(file):
                try:
                    os.remove(file)
                except:
                    pass