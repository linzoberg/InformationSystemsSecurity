import tkinter as tk
from tkinter import scrolledtext, messagebox
import secrets


class RandomnessTestApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Тестирование псевдослучайных последовательностей")
        self.root.geometry("900x700")

        # Переменные
        self.sequence = ""  # Здесь будет храниться полная последовательность
        self.full_sequence_displayed = False  # Флаг, показываем ли всю последовательность
        self.preview_length = 100  # Количество бит для предпросмотра в начале и в конце

        # Создание интерфейса
        self.create_widgets()

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
            height=25,
            wrap=tk.NONE,  # Не переносить строки
            font=("Courier", 9)  # Моноширинный шрифт для битов
        )
        self.text_area.pack(fill=tk.BOTH, expand=True)

        # Добавляем горизонтальную прокрутку
        text_scroll_x = tk.Scrollbar(text_frame, orient=tk.HORIZONTAL, command=self.text_area.xview)
        text_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.text_area.config(xscrollcommand=text_scroll_x.set)

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

            # Обновляем статус
            self.status_label.config(text=f"Последовательность из {length} бит успешно сгенерирована", fg="green")

        except ValueError:
            messagebox.showerror("Ошибка", "Пожалуйста, введите корректное число для длины!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка при генерации: {str(e)}")
        finally:
            self.generate_btn.config(state=tk.NORMAL, text="Сгенерировать последовательность")

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
        self.text_area.delete(1.0, tk.END)
        self.info_label.config(text="Последовательность не сгенерирована", fg="blue")
        self.status_label.config(text="Очищено", fg="blue")


def main():
    root = tk.Tk()
    app = RandomnessTestApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()