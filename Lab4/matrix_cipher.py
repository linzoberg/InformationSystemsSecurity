import numpy as np
import generators

# Матричный шифр для блоков 5 байт. Использует обратимую матрицу 5x5 по модулю 256.
class MatrixCipher5x5:

    # Инициализация матричного шифра с заданным seed - начальное значение для генератора ПСЧ
    def __init__(self, seed):
        self.prng = generators.ParkMillerGenerator(seed)
        self.matrix = self._generate_invertible_matrix()
        self.matrix_inv = self._calculate_inverse_matrix()

    # Генерирует обратимую матрицу 5x5 по модулю 256. Матрица обратима, если её определитель нечетный.
    def _generate_invertible_matrix(self):
        max_attempts = 1000
        for attempt in range(max_attempts):
            # Генерируем случайную матрицу 5x5
            matrix = np.zeros((5, 5), dtype=np.int32)
            for i in range(5):
                for j in range(5):
                    matrix[i][j] = self.prng.next() % 256
            # Проверяем, что определитель нечетный (матрица обратима по модулю 256)
            det = int(round(np.linalg.det(matrix)))
            if det % 2 == 1:  # Определитель нечетный - матрица обратима
                return matrix
        # Если не удалось сгенерировать - используем единичную матрицу
        print(f"Предупреждение: не удалось сгенерировать обратимую матрицу за {max_attempts} попыток")
        return np.identity(5, dtype=np.int32) * 17  # 17 нечетное

    # Вычисляет обратную матрицу по модулю 256
    def _calculate_inverse_matrix(self):
        # Находим определитель
        det = int(round(np.linalg.det(self.matrix)))
        # Находим обратный элемент для определителя по модулю 256
        # Так как det нечетный, он взаимно прост с 256
        det_inv = self._mod_inverse(det, 256)
        # Вычисляем присоединенную матрицу
        adj = self._adjugate_matrix(self.matrix)
        # Вычисляем обратную матрицу: inv = (det_inv * adj) mod 256
        matrix_inv = (det_inv * adj) % 256
        return matrix_inv.astype(np.int32)

    #Находит обратный элемент a по модулю m. Используется расширенный алгоритм Евклида.
    def _mod_inverse(self, a, m):
        a = a % m # a - число, m - модуль
        for x in range(1, m):
            if (a * x) % m == 1:
                return x
        return 1

    # Вычисляет присоединенную матрицу
    def _adjugate_matrix(self, matrix):
        n = matrix.shape[0]
        adj = np.zeros((n, n), dtype=np.int32)
        for i in range(n):
            for j in range(n):
                # Получаем минор
                minor = np.delete(np.delete(matrix, i, axis=0), j, axis=1)
                # Кофактор
                cofactor = ((-1) ** (i + j)) * int(round(np.linalg.det(minor)))
                # Транспонируем для присоединенной матрицы
                adj[j][i] = cofactor
        return adj

    # Шифрует блок 5 байт
    def encrypt_block(self, block):
        if len(block) != 5:
            raise ValueError(f"Размер блока должен быть 5 байт, получено {len(block)}")
        # Преобразуем блок в вектор
        vec = np.array([b for b in block], dtype=np.int32)
        # Умножаем матрицу на вектор по модулю 256
        result = (self.matrix @ vec) % 256
        # Преобразуем обратно в байты
        return bytes(result.tolist())

    # Дешифрует блок 5 байт
    def decrypt_block(self, block):
        if len(block) != 5:
            raise ValueError(f"Размер блока должен быть 5 байт, получено {len(block)}")
        # Преобразуем блок в вектор
        vec = np.array([b for b in block], dtype=np.int32)
        # Умножаем обратную матрицу на вектор по модулю 256
        result = (self.matrix_inv @ vec) % 256
        # Преобразуем обратно в байты
        return bytes(result.tolist())

    # Возвращает информацию о матрице для отладки
    def get_matrix_info(self):
        det = int(round(np.linalg.det(self.matrix)))
        return {
            'matrix': self.matrix.tolist(),
            'determinant': det,
            'matrix_inv': self.matrix_inv.tolist()
        }

# Тестирование матричного шифра
def test_matrix_cipher():
    print("Тестирование MatrixCipher5x5...")
    # Тестовый seed
    cipher = MatrixCipher5x5(12345)
    # Тестовый блок
    test_block = b"Hello"
    print(f"Исходный блок: {test_block}")
    # Шифрование
    encrypted = cipher.encrypt_block(test_block)
    print(f"Зашифрованный блок: {encrypted}")
    # Дешифрование
    decrypted = cipher.decrypt_block(encrypted)
    print(f"Дешифрованный блок: {decrypted}")
    # Проверка
    if decrypted == test_block:
        print("✓ Тест пройден: блок корректно шифруется и дешифруется")
    else:
        print("✗ Тест не пройден: блок не совпадает")
    # Проверка обратимости матрицы
    info = cipher.get_matrix_info()
    print(f"Определитель матрицы: {info['determinant']}")
    print(f"Определитель нечетный: {info['determinant'] % 2 == 1}")


if __name__ == "__main__":
    test_matrix_cipher()