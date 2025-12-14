import numpy as np
from generators import ParkMillerGenerator, BBSGenerator

class MatrixCipher:
    def __init__(self, seed):
        """
        Инициализация матричного шифра
        seed: целое число для инициализации генератора ПСЧ
        """
        self.block_size = 5  # Размер блока 5 байт согласно заданию
        self.seed = seed
        self.generator = ParkMillerGenerator(seed)  # Используем генератор из ЛР№3
        self.key_matrix = self._generate_key_matrix()
        self.inverse_matrix = self._generate_inverse_matrix()
    
    def _generate_key_matrix(self):
        """
        Генерация матрицы-ключа 5x5 на основе seed
        Все элементы матрицы генерируются с помощью ПСЧ
        Гарантируется, что матрица будет обратимой (определитель != 0)
        """
        while True:
            # Генерируем матрицу 5x5 с элементами от 0 до 255
            matrix = np.zeros((self.block_size, self.block_size), dtype=np.uint8)
            
            for i in range(self.block_size):
                for j in range(self.block_size):
                    # Генерируем случайный байт (0-255)
                    byte_val = 0
                    for bit_num in range(8):
                        byte_val = (byte_val << 1) | (self.generator.next() & 1)
                    matrix[i, j] = byte_val
            
            # Проверяем, что матрица обратима (определитель не равен 0 по модулю 256)
            if self._is_invertible(matrix):
                return matrix
    
    def _is_invertible(self, matrix):
        """
        Проверка, является ли матрица обратимой по модулю 256
        Матрица обратима, если её определитель взаимно прост с модулем 256
        """
        # Вычисляем определитель матрицы
        det = int(round(np.linalg.det(matrix)))
        det = det % 256
        
        # Матрица обратима, если определитель нечетный (взаимно прост с 256)
        return det % 2 != 0 and det != 0
    
    def _generate_inverse_matrix(self):
        """
        Генерация обратной матрицы по модулю 256
        Используется метод нахождения матрицы алгебраических дополнений
        """
        matrix = self.key_matrix.copy()
        
        # Вычисляем определитель
        det = int(round(np.linalg.det(matrix)))
        det = det % 256
        
        # Находим обратный элемент для определителя по модулю 256
        det_inv = self._modular_inverse(det, 256)
        if det_inv is None:
            raise ValueError("Матрица необратима")
        
        # Находим матрицу алгебраических дополнений
        adjugate = np.zeros((self.block_size, self.block_size), dtype=np.uint8)
        
        for i in range(self.block_size):
            for j in range(self.block_size):
                # Создаем подматрицу без i-й строки и j-го столбца
                submatrix = np.delete(np.delete(matrix, i, axis=0), j, axis=1)
                # Вычисляем определитель подматрицы
                minor_det = int(round(np.linalg.det(submatrix)))
                # Алгебраическое дополнение с учетом знака
                sign = (-1) ** (i + j)
                adjugate[j, i] = (sign * minor_det) % 256
        
        # Обратная матрица = (1/det) * adjugate
        inverse_matrix = (det_inv * adjugate) % 256
        return inverse_matrix.astype(np.uint8)
    
    def _modular_inverse(self, a, m):
        """
        Нахождение обратного элемента по модулю m
        Возвращает x такое, что (a * x) % m = 1
        """
        a = a % m
        for x in range(1, m):
            if ((a * x) % m == 1):
                return x
        return None
    
    def encrypt_block(self, block):
        """
        Шифрование одного блока данных (5 байт)
        block: байтовая строка длиной 5 байт
        Возвращает: байтовую строку длиной 5 байт
        """
        if len(block) != self.block_size:
            raise ValueError(f"Размер блока должен быть {self.block_size} байт")
        
        # Преобразуем блок в вектор
        vector = np.array([b for b in block], dtype=np.uint8)
        
        # Выполняем матричное умножение: matrix × vector
        result = np.zeros(self.block_size, dtype=np.uint8)
        for i in range(self.block_size):
            sum_val = 0
            for j in range(self.block_size):
                sum_val = (sum_val + self.key_matrix[i, j] * vector[j]) % 256
            result[i] = sum_val
        
        # Преобразуем результат обратно в байты
        return bytes(result.tolist())
    
    def decrypt_block(self, block):
        """
        Дешифрование одного блока данных (5 байт)
        block: байтовая строка длиной 5 байт
        Возвращает: байтовую строку длиной 5 байт
        """
        if len(block) != self.block_size:
            raise ValueError(f"Размер блока должен быть {self.block_size} байт")
        
        # Преобразуем блок в вектор
        vector = np.array([b for b in block], dtype=np.uint8)
        
        # Выполняем матричное умножение с обратной матрицей: inverse_matrix × vector
        result = np.zeros(self.block_size, dtype=np.uint8)
        for i in range(self.block_size):
            sum_val = 0
            for j in range(self.block_size):
                sum_val = (sum_val + self.inverse_matrix[i, j] * vector[j]) % 256
            result[i] = sum_val
        
        # Преобразуем результат обратно в байты
        return bytes(result.tolist())
    
    def get_key_matrix(self):
        """Возвращает матрицу-ключ для отображения в интерфейсе"""
        return self.key_matrix.copy()
    
    def get_inverse_matrix(self):
        """Возвращает обратную матрицу для отображения в интерфейсе"""
        return self.inverse_matrix.copy()