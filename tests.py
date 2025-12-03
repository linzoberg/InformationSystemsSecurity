"""
Модуль для тестирования псевдослучайных последовательностей
Реализует тесты из набора NIST
"""

import math


def frequency_test(bit_sequence: str) -> dict:
    """
    Частотный тест (Frequency Test)
    Проверяет пропорцию нулей и единиц в последовательности

    Параметры:
        bit_sequence (str): строка из 0 и 1

    Возвращает:
        dict: словарь с результатами теста:
            - 'passed': bool (True/False)
            - 'statistic': float (значение статистики S)
            - 'threshold': float (пороговое значение)
            - 'description': str (описание результата)
    """

    # Проверка входных данных
    if not bit_sequence:
        return {
            'passed': False,
            'statistic': 0.0,
            'threshold': 1.82138636,
            'description': 'Ошибка: пустая последовательность'
        }

    # Проверка корректности символов
    for bit in bit_sequence:
        if bit not in '01':
            return {
                'passed': False,
                'statistic': 0.0,
                'threshold': 1.82138636,
                'description': f'Ошибка: некорректный символ "{bit}"'
            }

    n = len(bit_sequence)

    # 1. Преобразование 0/1 в -1/1
    X = [2 * int(bit) - 1 for bit in bit_sequence]

    # 2. Вычисление суммы Sn
    Sn = sum(X)

    # 3. Вычисление статистики S
    try:
        S = abs(Sn) / math.sqrt(n)
    except ZeroDivisionError:
        S = float('inf')

    # 4. Сравнение с порогом
    threshold = 1.82138636
    passed = S <= threshold

    # Формирование описания
    zeros = bit_sequence.count('0')
    ones = bit_sequence.count('1')
    proportion = zeros / n if n > 0 else 0

    description = (
        f"Частотный тест: {'ПРОЙДЕН' if passed else 'НЕ ПРОЙДЕН'}\n"
        f"Длина последовательности: {n} бит\n"
        f"Количество нулей: {zeros}\n"
        f"Количество единиц: {ones}\n"
        f"Пропорция нулей: {proportion:.6f}\n"
        f"Статистика S = {S:.6f}\n"
        f"Пороговое значение: {threshold}\n"
        f"Условие: S ≤ {threshold} -> {S:.6f} ≤ {threshold} = {passed}"
    )

    return {
        'passed': passed,
        'statistic': S,
        'threshold': threshold,
        'description': description
    }


# Для тестирования модуля
if __name__ == "__main__":
    # Пример использования
    test_sequence = "0101010101" * 1000  # 10000 бит
    result = frequency_test(test_sequence)
    print(result['description'])