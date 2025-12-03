import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog
import secrets
import os
import sys
import datetime as dt
import tests  # Импорт нашего модуля тестов


def resource_path(relative_path):
    """Получить абсолютный путь к ресурсу, работает для dev и для PyInstaller"""
    try:
        # PyInstaller создает временную папку и хранит путь в _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class GenerateApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Тестирование псевдослучайных последовательностей")
        self.root.geometry("900x700")

        # Центрируем окно на экране
        self.center_window()

        # Переменные
        self.sequence = ""  # Здесь будет храниться полная последовательность
        self.full_sequence_displayed = False  # Флаг, показываем ли всю последовательность
        self.preview_length = 100  # Количество бит для предпросмотра в начале и в конце
        self.current_file = None  # Текущий открытый файл

        # Создание интерфейса
        self.create_widgets()

    def center_window(self):
        """Центрирование окна на экране"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def create_widgets(self):
        # Заголовок
        title_label = tk.Label(
            self.root,
            text="Тестирование псевдослучайных последовательностей",
            font=("Arial", 14, "bold")
        )
        title_label.pack(pady=10)

        # Фрейм для ввода длины
        length_frame = tk.Frame(self.root)
        length_frame.pack(pady=10)

        tk.Label(
            length_frame,
            text="Длина последовательности (бит):",
            font=("Arial", 10)
        ).pack(side=tk.LEFT, padx=5)

        self.length_entry = tk.Entry(length_frame, width=15, font=("Arial", 10))
        self.length_entry.pack(side=tk.LEFT, padx=5)
        self.length_entry.insert(0, "10000")  # значение по умолчанию

        # Подсказка
        hint_label = tk.Label(
            self.root,
            text="Рекомендуется использовать длину не менее 10 000 бит",
            font=("Arial", 9, "italic"),
            fg="gray"
        )
        hint_label.pack(pady=5)

        # Фрейм для кнопок управления последовательностью
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)

        # Кнопка генерации
        self.generate_btn = tk.Button(
            btn_frame,
            text="Сгенерировать последовательность",
            command=self.generate_sequence,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=10,
            pady=5
        )
        self.generate_btn.pack(side=tk.LEFT, padx=5)

        # Кнопка загрузки из файла
        self.load_btn = tk.Button(
            btn_frame,
            text="Загрузить из файла",
            command=self.load_from_file,
            bg="#2196F3",
            fg="white",
            font=("Arial", 10),
            padx=10,
            pady=5
        )
        self.load_btn.pack(side=tk.LEFT, padx=5)

        # Кнопка сохранения в файл
        self.save_btn = tk.Button(
            btn_frame,
            text="Сохранить в файл",
            command=self.save_to_file,
            bg="#FF9800",
            fg="white",
            font=("Arial", 10),
            padx=10,
            pady=5,
            state=tk.DISABLED  # Изначально неактивна, пока нет последовательности
        )
        self.save_btn.pack(side=tk.LEFT, padx=5)

        # Кнопка очистки
        self.clear_btn = tk.Button(
            btn_frame,
            text="Очистить",
            command=self.clear_display,
            bg="#f44336",
            fg="white",
            font=("Arial", 10),
            padx=10,
            pady=5
        )
        self.clear_btn.pack(side=tk.LEFT, padx=5)

        # Метка для отображения информации о последовательности
        self.info_label = tk.Label(
            self.root,
            text="Последовательность не сгенерирована",
            font=("Arial", 10),
            fg="blue"
        )
        self.info_label.pack(pady=5)

        # Информация о файле
        self.file_info_label = tk.Label(
            self.root,
            text="Файл: не выбран",
            font=("Arial", 9),
            fg="gray"
        )
        self.file_info_label.pack(pady=2)

        # Фрейм для управления отображением
        display_frame = tk.Frame(self.root)
        display_frame.pack(pady=5)

        tk.Label(
            display_frame,
            text="Режим отображения:",
            font=("Arial", 9)
        ).pack(side=tk.LEFT, padx=5)

        # Переключатель режима отображения
        self.display_mode = tk.StringVar(value="preview")

        tk.Radiobutton(
            display_frame,
            text=f"Предпросмотр (первые/последние {self.preview_length} бит)",
            variable=self.display_mode,
            value="preview",
            command=self.update_display,
            font=("Arial", 9)
        ).pack(side=tk.LEFT, padx=5)

        tk.Radiobutton(
            display_frame,
            text="Полная последовательность",
            variable=self.display_mode,
            value="full",
            command=self.update_display,
            font=("Arial", 9)
        ).pack(side=tk.LEFT, padx=5)

        # Текстовое поле для последовательности с прокруткой
        text_frame = tk.Frame(self.root)
        text_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

        tk.Label(
            text_frame,
            text="Последовательность бит:",
            font=("Arial", 10, "bold")
        ).pack(anchor=tk.W)

        # Создаем ScrolledText с вертикальной и горизонтальной прокруткой
        self.text_area = scrolledtext.ScrolledText(
            text_frame,
            width=110,
            height=20,
            wrap=tk.NONE,  # Не переносить строки
            font=("Courier", 9)  # Моноширинный шрифт для битов
        )
        self.text_area.pack(fill=tk.BOTH, expand=True)

        # Добавляем горизонтальную прокрутку
        text_scroll_x = tk.Scrollbar(text_frame, orient=tk.HORIZONTAL, command=self.text_area.xview)
        text_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.text_area.config(xscrollcommand=text_scroll_x.set)

        # Фрейм для кнопок тестирования
        test_frame = tk.Frame(self.root)
        test_frame.pack(pady=10)

        # Кнопка частотного теста
        self.freq_test_btn = tk.Button(
            test_frame,
            text="Частотный тест",
            command=self.run_frequency_test,
            bg="#9C27B0",  # Фиолетовый цвет
            fg="white",
            font=("Arial", 10, "bold"),
            padx=10,
            pady=5,
            state=tk.DISABLED  # Изначально неактивна
        )
        self.freq_test_btn.pack(side=tk.LEFT, padx=5)

        # Кнопка всех тестов (для будущего)
        self.all_tests_btn = tk.Button(
            test_frame,
            text="Все тесты",
            command=self.run_all_tests,
            bg="#673AB7",  # Темно-фиолетовый
            fg="white",
            font=("Arial", 10),
            padx=10,
            pady=5,
            state=tk.DISABLED
        )
        self.all_tests_btn.pack(side=tk.LEFT, padx=5)

        # Кнопка очистки результатов тестов
        self.clear_tests_btn = tk.Button(
            test_frame,
            text="Очистить результаты",
            command=self.clear_test_results,
            bg="#795548",  # Коричневый
            fg="white",
            font=("Arial", 10),
            padx=10,
            pady=5
        )
        self.clear_tests_btn.pack(side=tk.LEFT, padx=5)

        # Фрейм для отображения результатов тестов
        results_frame = tk.Frame(self.root)
        results_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

        tk.Label(
            results_frame,
            text="Результаты тестирования:",
            font=("Arial", 10, "bold")
        ).pack(anchor=tk.W)

        # Текстовое поле для результатов тестов с прокруткой
        self.results_text = scrolledtext.ScrolledText(
            results_frame,
            width=110,
            height=10,
            wrap=tk.WORD,
            font=("Courier", 9),
            state=tk.NORMAL
        )
        self.results_text.pack(fill=tk.BOTH, expand=True)
        self.results_text.insert(1.0, "Здесь будут отображаться результаты тестов...\n")
        self.results_text.config(state=tk.DISABLED)  # Только для чтения

        # Статусная строка
        self.status_label = tk.Label(
            self.root,
            text="Готов к работе",
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W,
            font=("Arial", 9)
        )
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

        # Добавляем теги для цветового форматирования результатов тестов
        self.results_text.tag_config("passed", foreground="green", font=("Courier", 9, "bold"))
        self.results_text.tag_config("failed", foreground="red", font=("Courier", 9, "bold"))

    def generate_sequence(self):
        """Генерация псевдослучайной последовательности 0 и 1"""
        try:
            # Получаем длину из поля ввода
            length = int(self.length_entry.get())

            # Проверяем корректность длины
            if length <= 0:
                messagebox.showerror("Ошибка", "Длина должна быть положительным числом!")
                return

            if length > 1000000:
                response = messagebox.askyesno(
                    "Предупреждение",
                    f"Вы хотите сгенерировать {length} бит. Это может занять некоторое время.\nПродолжить?"
                )
                if not response:
                    return

            # Обновляем статус
            self.status_label.config(text="Генерация последовательности...", fg="orange")
            self.generate_btn.config(state=tk.DISABLED, text="Генерация...")
            self.root.update()  # Обновляем интерфейс

            # Генерация последовательности с использованием secrets (криптографически стойкий)
            self.sequence = ''.join(str(secrets.randbits(1)) for _ in range(length))
            self.current_file = None  # Сбрасываем информацию о файле

            # Отображаем последовательность
            self.update_display()

            # Подсчитываем количество нулей и единиц
            zeros_count = self.sequence.count('0')
            ones_count = self.sequence.count('1')

            # Обновляем информацию в новом формате
            self.info_label.config(
                text=f"Сгенерировано: {length} бит, нулей: {zeros_count}, единиц: {ones_count}",
                fg="green"
            )

            # Обновляем информацию о файле
            self.file_info_label.config(text="Файл: не сохранено", fg="gray")

            # Активируем кнопку сохранения
            self.save_btn.config(state=tk.NORMAL)

            # Активируем кнопки тестов
            self.enable_test_buttons()

            # Обновляем статус
            self.status_label.config(text=f"Последовательность из {length} бит успешно сгенерирована", fg="green")

        except ValueError:
            messagebox.showerror("Ошибка", "Пожалуйста, введите корректное число для длины!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка при генерации: {str(e)}")
        finally:
            self.generate_btn.config(state=tk.NORMAL, text="Сгенерировать последовательность")

    def load_from_file(self):
        """Загрузка последовательности из текстового файла"""
        try:
            # Открываем диалог выбора файла
            filepath = filedialog.askopenfilename(
                title="Выберите файл с последовательностью",
                filetypes=[
                    ("Текстовые файлы", "*.txt"),
                    ("Все файлы", "*.*")
                ]
            )

            if not filepath:  # Пользователь отменил выбор
                return

            # Читаем файл
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read().strip()

            # Удаляем все символы, кроме 0 и 1
            cleaned_content = ''.join(filter(lambda c: c in '01', content))

            if not cleaned_content:
                messagebox.showerror("Ошибка", "Файл не содержит последовательности из 0 и 1!")
                return

            # Сохраняем последовательность
            self.sequence = cleaned_content
            self.current_file = filepath

            # Отображаем
            self.update_display()

            # Обновляем информацию
            zeros_count = self.sequence.count('0')
            ones_count = self.sequence.count('1')
            self.info_label.config(
                text=f"Загружено: {len(self.sequence)} бит, нулей: {zeros_count}, единиц: {ones_count}",
                fg="green"
            )

            # Обновляем информацию о файле
            filename = os.path.basename(filepath)
            self.file_info_label.config(text=f"Файл: {filename}", fg="green")

            # Активируем кнопку сохранения
            self.save_btn.config(state=tk.NORMAL)

            # Активируем кнопки тестов
            self.enable_test_buttons()

            # Обновляем статус
            self.status_label.config(
                text=f"Последовательность из файла '{filename}' успешно загружена ({len(self.sequence)} бит)",
                fg="green"
            )

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить файл: {str(e)}")
            self.status_label.config(text="Ошибка при загрузке файла", fg="red")

    def save_to_file(self):
        """Сохранение последовательности в текстовый файл"""
        if not self.sequence:
            messagebox.showwarning("Предупреждение", "Нет последовательности для сохранения!")
            return

        try:
            # Предлагаем сохранить в текущий файл или новый
            if self.current_file:
                response = messagebox.askyesnocancel(
                    "Сохранение",
                    f"Сохранить в текущий файл?\n{self.current_file}\n\nДа - перезаписать текущий файл\nНет - выбрать новый файл"
                )

                if response is None:  # Отмена
                    return
                elif response:  # Да - сохранить в текущий
                    filepath = self.current_file
                else:  # Нет - выбрать новый
                    filepath = filedialog.asksaveasfilename(
                        title="Сохранить последовательность",
                        defaultextension=".txt",
                        filetypes=[
                            ("Текстовые файлы", "*.txt"),
                            ("Все файлы", "*.*")
                        ]
                    )
            else:
                filepath = filedialog.asksaveasfilename(
                    title="Сохранить последовательность",
                    defaultextension=".txt",
                    filetypes=[
                        ("Текстовые файлы", "*.txt"),
                        ("Все файлы", "*.*")
                    ]
                )

            if not filepath:  # Пользователь отменил
                return

            # Сохраняем в файл
            with open(filepath, 'w', encoding='utf-8') as file:
                file.write(self.sequence)

            self.current_file = filepath
            filename = os.path.basename(filepath)

            # Обновляем информацию
            self.file_info_label.config(text=f"Файл: {filename} (сохранено)", fg="green")
            self.status_label.config(text=f"Последовательность сохранена в файл: {filename}", fg="green")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {str(e)}")
            self.status_label.config(text="Ошибка при сохранении файла", fg="red")

    def update_display(self):
        """Обновление отображения последовательности в зависимости от выбранного режима"""
        if not self.sequence:
            self.text_area.delete(1.0, tk.END)
            return

        mode = self.display_mode.get()

        if mode == "preview":
            # Показываем только начало и конец для длинных последовательностей
            if len(self.sequence) > (2 * self.preview_length):
                preview = (
                        self.sequence[:self.preview_length] +
                        "\n... [пропущено " +
                        str(len(self.sequence) - 2 * self.preview_length) +
                        " бит] ...\n" +
                        self.sequence[-self.preview_length:]
                )
                self.full_sequence_displayed = False
            else:
                preview = self.sequence
                self.full_sequence_displayed = True
        else:  # full mode
            preview = self.sequence
            self.full_sequence_displayed = True

        # Обновляем текстовое поле
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(1.0, preview)

        # Добавляем информацию о длине
        if not self.full_sequence_displayed:
            self.text_area.insert(
                tk.END,
                f"\n\n[Отображено {2 * self.preview_length} из {len(self.sequence)} бит]"
            )

    def clear_display(self):
        """Очистка текстового поля и сброс последовательности"""
        self.sequence = ""
        self.current_file = None
        self.text_area.delete(1.0, tk.END)
        self.info_label.config(text="Последовательность не сгенерирована", fg="blue")
        self.file_info_label.config(text="Файл: не выбран", fg="gray")
        self.save_btn.config(state=tk.DISABLED)

        # Деактивируем кнопки тестов
        self.enable_test_buttons(False)

        # Очищаем результаты тестов
        self.clear_test_results()

        self.status_label.config(text="Очищено", fg="blue")

    def enable_test_buttons(self, enable=True):
        """Активация/деактивация кнопок тестов"""
        state = tk.NORMAL if enable else tk.DISABLED
        self.freq_test_btn.config(state=state)
        self.all_tests_btn.config(state=state)

    def run_frequency_test(self):
        """Выполнение частотного теста"""
        if not self.sequence:
            messagebox.showwarning("Предупреждение", "Нет последовательности для тестирования!")
            return

        try:
            # Обновляем статус
            self.status_label.config(text="Выполняется частотный тест...", fg="orange")
            self.root.update()

            # Выполняем тест
            result = tests.frequency_test(self.sequence)

            # Отображаем результаты
            self.display_test_result(result, "Частотный тест")

            # Обновляем статус
            status_color = "green" if result['passed'] else "red"
            status_text = "Частотный тест пройден" if result['passed'] else "Частотный тест не пройден"
            self.status_label.config(text=status_text, fg=status_color)

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при выполнении теста: {str(e)}")
            self.status_label.config(text="Ошибка при выполнении теста", fg="red")

    def display_test_result(self, result, test_name):
        """Отображение результатов теста в текстовом поле"""
        self.results_text.config(state=tk.NORMAL)

        # Добавляем разделитель и заголовок
        separator = "=" * 80
        timestamp = dt.datetime.now().strftime("%H:%M:%S")
        header = f"\n{separator}\n{test_name} - {timestamp}\n{separator}\n"

        self.results_text.insert(tk.END, header)

        # Добавляем результаты
        self.results_text.insert(tk.END, result['description'] + "\n")

        # Добавляем цветовое выделение
        if result['passed']:
            self.results_text.insert(tk.END, "✓ Тест ПРОЙДЕН успешно\n", "passed")
        else:
            self.results_text.insert(tk.END, "✗ Тест НЕ ПРОЙДЕН\n", "failed")

        # Прокручиваем вниз
        self.results_text.see(tk.END)
        self.results_text.config(state=tk.DISABLED)

    def run_all_tests(self):
        """Выполнение всех тестов (пока только частотный)"""
        self.run_frequency_test()
        # Здесь будут добавляться другие тесты

    def clear_test_results(self):
        """Очистка результатов тестов"""
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(1.0, "Здесь будут отображаться результаты тестов...\n")
        self.results_text.config(state=tk.DISABLED)
        self.status_label.config(text="Результаты тестов очищены", fg="blue")


def main():
    root = tk.Tk()
    app = GenerateApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()