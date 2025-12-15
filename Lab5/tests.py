import math

# Частотный тест
def frequency_test(bit_sequence: str) -> dict:
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

# Тест на последовательность одинаковых бит
def runs_test(bit_sequence: str) -> dict:
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

    # 1. Вычисляем частоту единиц
    ones_count = bit_sequence.count('1')
    pi = ones_count / n

    # 2. Проверяем условие |pi - 0.5| < 2 / sqrt(n)
    if abs(pi - 0.5) >= 2 / math.sqrt(n):
        # Тест не пройден, возвращаем результат с passed=False
        statistic = abs(pi - 0.5) * math.sqrt(n) / 2
        description = (
            f"Длина последовательности: {n} бит\n"
            f"Частота единиц: {pi:.6f}\n"
            f"Условие: |pi - 0.5| < 2/√n -> |{pi:.6f} - 0.5| < {2 / math.sqrt(n):.6f} = {abs(pi - 0.5) < 2 / math.sqrt(n)}\n"
            f"Предварительное условие не выполнено, тест не может быть продолжен."
        )
        return {
            'passed': False,
            'statistic': statistic,
            'threshold': 2 / math.sqrt(n),
            'description': description
        }

    # 3. Вычисляем Vn (число блоков)
    # Инициализируем счетчик блоков
    blocks = 1  # Первый блок начинается с первого бита
    for i in range(1, n):
        if bit_sequence[i] != bit_sequence[i - 1]:
            blocks += 1

    Vn = blocks

    # 4. Вычисляем статистику S
    numerator = abs(Vn - 2 * n * pi * (1 - pi))
    denominator = 2 * math.sqrt(2 * n) * pi * (1 - pi)
    S = numerator / denominator

    # 5. Сравниваем с порогом
    threshold = 1.82138636
    passed = S <= threshold

    # Формируем описание
    zeros_count = bit_sequence.count('0')
    description = (
        f"Длина последовательности: {n} бит\n"
        f"Количество нулей: {zeros_count}\n"
        f"Количество единиц: {ones_count}\n"
        f"Частота единиц (pi): {pi:.6f}\n"
        f"Количество блоков (Vn): {Vn}\n"
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

    print("=== Частотный тест ===")
    result1 = frequency_test(test_sequence)
    print(result1['description'])

    print("\n=== Тест на последовательность одинаковых бит ===")
    result2 = runs_test(test_sequence)
    print(result2['description'])