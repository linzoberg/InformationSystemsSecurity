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