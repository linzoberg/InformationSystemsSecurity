import os
import json
from typing import Dict, Any, Optional
from elgamal import ElGamal

class AsymmetricCryptoApp:
    """Ядро приложения для асимметричного шифрования."""

    def __init__(self, prime_bits: int = 32):
        self.prime_bits = prime_bits
        self.elgamal = ElGamal(prime_bits)
        self.public_key = None
        self.private_key = None
        self.keys_generated = False

    def generate_key_pair(self) -> Dict[str, Any]:
        """Генерация пары ключей."""
        try:
            self.public_key = self.elgamal.generate_keys()[0]
            self.private_key = self.elgamal.get_private_key()
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
                'message': f'Ключи сгенерированы (p: {self.public_key[0].bit_length()} бит)'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def encrypt_file(self, input_path: str, output_path: str,
                    public_key_json: str = None) -> Dict[str, Any]:
        """Шифрование файла открытым ключом."""
        try:
            if not os.path.exists(input_path):
                return {'success': False, 'error': f'Файл не найден: {input_path}'}

            # Загружаем открытый ключ
            if public_key_json:
                key_data = json.loads(public_key_json)
                public_key = (int(key_data['p'], 16), key_data['g'], int(key_data['y'], 16))
            elif self.public_key:
                public_key = self.public_key
            else:
                return {'success': False, 'error': 'Не указан открытый ключ'}

            # Читаем файл
            with open(input_path, 'rb') as f:
                plaintext = f.read()

            # Шифруем
            ciphertext = self.elgamal.encrypt_bytes(plaintext, public_key)

            # Сохраняем
            with open(output_path, 'wb') as f:
                f.write(ciphertext)

            return {
                'success': True,
                'input_size': len(plaintext),
                'output_size': len(ciphertext),
                'input_path': input_path,
                'output_path': output_path,
                'message': f'Файл зашифрован. Размер: {len(plaintext)} → {len(ciphertext)} байт'
            }

        except Exception as e:
            return {'success': False, 'error': f'Ошибка шифрования: {str(e)}'}

    def decrypt_file(self, input_path: str, output_path: str,
                    private_key_json: str = None) -> Dict[str, Any]:
        """Дешифрование файла закрытым ключом."""
        try:
            if not os.path.exists(input_path):
                return {'success': False, 'error': f'Файл не найден: {input_path}'}

            # Загружаем закрытый ключ
            if private_key_json:
                key_data = json.loads(private_key_json)
                private_key = (int(key_data['p'], 16), int(key_data['x'], 16))
            elif self.private_key:
                private_key = self.private_key
            else:
                return {'success': False, 'error': 'Не указан закрытый ключ'}

            # Читаем зашифрованный файл
            with open(input_path, 'rb') as f:
                ciphertext = f.read()

            # Дешифруем
            plaintext = self.elgamal.decrypt_bytes(ciphertext, private_key)

            # Сохраняем
            with open(output_path, 'wb') as f:
                f.write(plaintext)

            return {
                'success': True,
                'input_size': len(ciphertext),
                'output_size': len(plaintext),
                'input_path': input_path,
                'output_path': output_path,
                'message': f'Файл дешифрован. Размер: {len(ciphertext)} → {len(plaintext)} байт'
            }

        except Exception as e:
            return {'success': False, 'error': f'Ошибка дешифрования: {str(e)}'}

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