import os
import json
from typing import Dict, Any, Optional
from elgamal import ElGamal

class AsymmetricCryptoApp:
    """Ядро приложения для асимметричного шифрования."""

    def __init__(self, prime_bits: int = 32):
        self.prime_bits = prime_bits
        self.elgamal = None  # Будет создан при генерации ключей
        self.public_key = None
        self.private_key = None
        self.keys_generated = False

    def generate_key_pair(self) -> Dict[str, Any]:
        """Генерация пары ключей."""
        try:
            # Создаем объект ElGamal и генерируем ключи
            self.elgamal = ElGamal(prime_bits=self.prime_bits)
            self.public_key, self.private_key = self.elgamal.generate_keys()
            self.keys_generated = True

            return {
                'success': True,
                'public_key': {
                    'p': hex(self.public_key[0]),
                    'g': self.public_key[1],
                    'y': hex(self.public_key[2]),
                    'bits': self.public_key[0].bit_length()
                },
                'private_key': {
                    'p': hex(self.private_key[0]),
                    'x': hex(self.private_key[1])
                },
                'message': 'Ключи сгенерированы'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def encrypt_file(self, input_path: str, output_path: str,
                    public_key_json: str = None, progress_callback=None) -> Dict[str, Any]:
        """Шифрование файла открытым ключом."""
        try:
            if not os.path.exists(input_path):
                return {'success': False, 'error': f'Файл не найден: {input_path}'}

            # Загружаем открытый ключ
            if public_key_json:
                key_data = json.loads(public_key_json)
                public_key = (int(key_data['p'], 16), key_data['g'], int(key_data['y'], 16))
            else:
                return {'success': False, 'error': 'Не указан открытый ключ'}

            # Создаем временный объект ElGamal для шифрования
            temp_elgamal = ElGamal(prime_bits=public_key[0].bit_length())
            temp_elgamal.p = public_key[0]
            temp_elgamal.g = public_key[1]
            temp_elgamal.y = public_key[2]

            # Читаем файл
            with open(input_path, 'rb') as f:
                plaintext = f.read()

            # Обновляем прогресс (25%)
            if progress_callback:
                progress_callback(25)

            # Шифруем
            ciphertext = temp_elgamal.encrypt_bytes(plaintext, public_key)

            # Обновляем прогресс (75%)
            if progress_callback:
                progress_callback(75)

            # Сохраняем
            with open(output_path, 'wb') as f:
                f.write(ciphertext)

            # Обновляем прогресс (100%)
            if progress_callback:
                progress_callback(100)

            return {
                'success': True,
                'input_size': len(plaintext),
                'output_size': len(ciphertext),
                'input_path': input_path,
                'output_path': output_path,
                'message': f'Файл успешно зашифрован. Размер: {len(plaintext)} байт'
            }

        except Exception as e:
            return {'success': False, 'error': f'Ошибка при шифровании: {str(e)}'}

    def decrypt_file(self, input_path: str, output_path: str,
                    private_key_json: str = None, progress_callback=None) -> Dict[str, Any]:
        """Дешифрование файла закрытым ключом."""
        try:
            if not os.path.exists(input_path):
                return {'success': False, 'error': f'Файл не найден: {input_path}'}

            # Загружаем закрытый ключ
            if private_key_json:
                key_data = json.loads(private_key_json)
                private_key = (int(key_data['p'], 16), int(key_data['x'], 16))
            else:
                return {'success': False, 'error': 'Не указан закрытый ключ'}

            # Создаем временный объект ElGamal для дешифрования
            temp_elgamal = ElGamal(prime_bits=private_key[0].bit_length())
            temp_elgamal.p = private_key[0]
            temp_elgamal.x = private_key[1]

            # Читаем зашифрованный файл
            with open(input_path, 'rb') as f:
                ciphertext = f.read()

            # Обновляем прогресс (25%)
            if progress_callback:
                progress_callback(25)

            # Дешифруем
            plaintext = temp_elgamal.decrypt_bytes(ciphertext, private_key)

            # Обновляем прогресс (75%)
            if progress_callback:
                progress_callback(75)

            # Сохраняем
            with open(output_path, 'wb') as f:
                f.write(plaintext)

            # Обновляем прогресс (100%)
            if progress_callback:
                progress_callback(100)

            return {
                'success': True,
                'input_size': len(ciphertext),
                'output_size': len(plaintext),
                'input_path': input_path,
                'output_path': output_path,
                'message': f'Файл успешно дешифрован. Размер: {len(plaintext)} байт'
            }

        except Exception as e:
            return {'success': False, 'error': f'Ошибка при дешифровании: {str(e)}'}

    def save_key_to_file(self, key_data: Dict[str, Any], file_path: str) -> bool:
        """Сохранение ключа в JSON файл."""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(key_data, f, indent=2)
            return True
        except:
            return False

    def load_key_from_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Загрузка ключа из JSON файла."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return None

    def get_key_info(self) -> Dict[str, Any]:
        """Возвращает информацию о текущих ключах."""
        if not self.keys_generated:
            return {'has_keys': False}

        return {
            'has_keys': True,
            'public_key': {
                'p': f'{self.public_key[0]:#x}',
                'g': self.public_key[1],
                'y': f'{self.public_key[2]:#x}',
                'bits': self.public_key[0].bit_length()
            },
            'private_key': {
                'p': f'{self.private_key[0]:#x}',
                'x': f'{self.private_key[1]:#x}'
            }
        }