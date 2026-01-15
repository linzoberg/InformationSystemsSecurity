import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog, ttk
import os
import json
from app_core import AsymmetricCryptoApp


class AsymmetricCryptoGUI:
    """Графический интерфейс для асимметричного шифрования."""

    def __init__(self, root):
        self.root = root
        self.root.title("Асимметричная криптография")
        self.root.geometry("700x700")  # Изменено на 700x700

        # Инициализация ядра приложения
        self.app = AsymmetricCryptoApp(prime_bits=32)

        # Создание интерфейса
        self.create_widgets()
        self.center_window()

    def center_window(self):
        """Центрирование окна на экране."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def create_widgets(self):
        """Создание всех элементов интерфейса."""
        # Заголовок
        title_label = tk.Label(
            self.root,
            text="Асимметричная криптография",
            font=("Arial", 14, "bold"),
            justify="center"
        )
        title_label.pack(pady=10)

        # Блок 1: Генерация ключей
        key_frame = tk.Frame(self.root, padx=10, pady=10)
        key_frame.pack(fill="x", padx=20, pady=5)

        # Кнопка генерации ключей
        self.generate_btn = tk.Button(
            key_frame,
            text="Сгенерировать пару ключей",
            command=self.generate_keys,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=8
        )
        self.generate_btn.pack(pady=5)

        # === БЛОК 2: ВЫБОР ФАЙЛА ===
        file_frame = tk.Frame(self.root, padx=10, pady=10)
        file_frame.pack(fill="x", padx=20, pady=5)

        # Поле для пути к файлу
        tk.Label(file_frame, text="Путь к файлу:", font=("Arial", 10)).pack(anchor="w")

        # Фрейм для строки ввода и кнопки
        file_input_frame = tk.Frame(file_frame)
        file_input_frame.pack(fill="x", pady=(5, 0))

        self.file_path_var = tk.StringVar()
        file_entry = tk.Entry(file_input_frame, textvariable=self.file_path_var,
                              width=50, font=("Arial", 9))
        file_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        # Кнопка "Обзор"
        browse_btn = tk.Button(
            file_input_frame,
            text="Обзор...",
            command=self.browse_file,
            bg="#2196F3",
            fg="white",
            font=("Arial", 10),
            padx=15
        )
        browse_btn.pack(side="right")

        # Информация о файле
        self.file_info_label = tk.Label(
            file_frame,
            text="Файл не выбран",
            font=("Arial", 9),
            fg="gray"
        )
        self.file_info_label.pack(anchor="w", pady=(5, 0))

        # === БЛОК 3: КНОПКИ ДЕЙСТВИЙ ===
        buttons_frame = tk.Frame(self.root)
        buttons_frame.pack(pady=10)

        # Кнопка "Зашифровать"
        self.encrypt_btn = tk.Button(
            buttons_frame,
            text="Зашифровать (открытым ключом)",
            command=self.encrypt_file,
            bg="#4CAF50",  # Зеленый цвет
            fg="white",
            font=("Arial", 11, "bold"),
            padx=20,
            pady=10,
            width=25
        )
        self.encrypt_btn.pack(side="left", padx=10)

        # Кнопка "Дешифровать"
        self.decrypt_btn = tk.Button(
            buttons_frame,
            text="Дешифровать (закрытым ключом)",
            command=self.decrypt_file,
            bg="#FF9800",  # Оранжевый цвет
            fg="white",
            font=("Arial", 11),
            padx=20,
            pady=10,
            width=25
        )
        self.decrypt_btn.pack(side="left", padx=10)

        # === БЛОК 4: ПРОГРЕСС-БАР ===
        progress_frame = tk.Frame(self.root)
        progress_frame.pack(fill="x", padx=20, pady=10)

        # Прогресс-бар
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=100,
            length=400
        )
        self.progress_bar.pack(pady=(0, 5))

        # Метка прогресса
        self.progress_label = tk.Label(
            progress_frame,
            text="Готов к работе",
            font=("Arial", 9),
            fg="green"
        )
        self.progress_label.pack()

        # === БЛОК 5: ИНФОРМАЦИОННАЯ ПАНЕЛЬ ===
        info_frame = tk.Frame(self.root, padx=10, pady=10)
        info_frame.pack(fill="both", expand=True, padx=20, pady=5)

        self.info_text = scrolledtext.ScrolledText(
            info_frame,
            width=70,
            height=12,
            wrap=tk.WORD,
            font=("Courier", 9)
        )
        self.info_text.pack(fill="both", expand=True)
        self.info_text.insert("end", "Сгенерируйте ключи или выберите файл.\n")

        # === СТАТУСНАЯ СТРОКА ===
        self.status_label = tk.Label(
            self.root,
            text="Готов к работе",
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W,
            font=("Arial", 9)
        )
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

    def generate_keys(self):
        """Генерация пары ключей."""
        self.generate_btn.config(state='disabled', text="Генерация...")
        self.root.update()

        try:
            result = self.app.generate_key_pair()

            if result['success']:
                # Активируем кнопки
                self.encrypt_btn.config(state='normal')
                self.decrypt_btn.config(state='normal')

                # Добавляем информацию о ключах в нижнее поле
                self.log_info("✓ Ключи сгенерированы")
                self.log_info("")

                pub = result['public_key']
                priv = result['private_key']

                # Выводим информацию о ключах с измененными заголовками
                self.log_info("Открытый ключ (для шифрования):")
                self.log_info(f"  p (простое): {pub['p']}")
                self.log_info(f"  g: {pub['g']}")
                self.log_info(f"  y: {pub['y']}")
                self.log_info(f"  Длина: {pub['bits']} бит")
                self.log_info("")

                self.log_info("Закрытый ключ (для дешифрования):")
                self.log_info(f"  p: {priv['p']}")
                self.log_info(f"  x: {priv['x']}")
                self.log_info("")

                self.progress_label.config(text="Ключи сгенерированы", fg="green")
                self.status_label.config(text="Ключи успешно сгенерированы", fg="green")

                # Предлагаем сохранить ключи
                if messagebox.askyesno("Сохранение ключей", "Сохранить ключи в файлы?"):
                    self.save_keys_to_files()
            else:
                messagebox.showerror("Ошибка", result['error'])
                self.progress_label.config(text="Ошибка", fg="red")
                self.status_label.config(text="Ошибка генерации ключей", fg="red")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при генерации ключей: {str(e)}")
            self.progress_label.config(text="Ошибка", fg="red")
            self.status_label.config(text="Ошибка", fg="red")
        finally:
            self.generate_btn.config(state='normal', text="Сгенерировать пару ключей")

    def save_keys_to_files(self):
        """Сохранение ключей в файлы."""
        key_info = self.app.get_key_info()
        if not key_info['has_keys']:
            return

        # Сохранение открытого ключа
        pub_file = filedialog.asksaveasfilename(
            title="Сохранить открытый ключ",
            defaultextension=".json",
            initialfile="public_key.json",
            filetypes=[("JSON файлы", "*.json"), ("Все файлы", "*.*")]
        )
        if pub_file:
            pub_data = {
                'algorithm': 'ElGamal',
                'key_type': 'public',
                'parameters': key_info['public_key']
            }
            if self.app.save_key_to_file(pub_data, pub_file):
                self.log_info(f"✓ Открытый ключ сохранен: {os.path.basename(pub_file)}")

        # Сохранение закрытого ключа
        priv_file = filedialog.asksaveasfilename(
            title="Сохранить закрытый ключ",
            defaultextension=".json",
            initialfile="private_key.json",
            filetypes=[("JSON файлы", "*.json"), ("Все файлы", "*.*")]
        )
        if priv_file:
            priv_data = {
                'algorithm': 'ElGamal',
                'key_type': 'private',
                'parameters': key_info['private_key']
            }
            if self.app.save_key_to_file(priv_data, priv_file):
                self.log_info(f"✓ Закрытый ключ сохранен: {os.path.basename(priv_file)}")

    def browse_file(self):
        """Выбор файла для обработки."""
        filepath = filedialog.askopenfilename(
            title="Выберите файл",
            filetypes=[
                ("Все файлы", "*.*"),
                ("Текстовые файлы", "*.txt"),
                ("Изображения", "*.jpg *.png *.bmp"),
                ("Документы", "*.pdf *.docx")
            ]
        )
        if filepath:
            self.file_path_var.set(filepath)
            size = os.path.getsize(filepath)
            self.file_info_label.config(
                text=f"{os.path.basename(filepath)} • {self.format_size(size)}",
                fg="black"
            )
            self.log_info(f"Выбран файл: {os.path.basename(filepath)} ({self.format_size(size)})")

    def encrypt_file(self):
        """Шифрование файла."""
        input_file = self.file_path_var.get()
        if not input_file or not os.path.exists(input_file):
            messagebox.showerror("Ошибка", "Выберите файл для шифрования!")
            return

        # Запрос открытого ключа
        key_file = filedialog.askopenfilename(
            title="Выберите открытый ключ",
            filetypes=[("JSON файлы", "*.json"), ("Все файлы", "*.*")]
        )
        if not key_file:
            return

        key_data = self.app.load_key_from_file(key_file)
        if not key_data or key_data.get('key_type') != 'public':
            messagebox.showerror("Ошибка", "Некорректный файл открытого ключа!")
            return

        # Выбор места сохранения
        output_file = filedialog.asksaveasfilename(
            title="Сохранить зашифрованный файл",
            defaultextension=".enc",
            initialfile=os.path.basename(input_file) + ".enc"
        )
        if not output_file:
            return

        # Проверка перезаписи
        if os.path.exists(output_file):
            if not messagebox.askyesno("Подтверждение",
                                       f"Файл '{os.path.basename(output_file)}' уже существует.\nПерезаписать?"):
                return

        # Выполнение шифрования
        self.set_ui_state(False)
        self.progress_var.set(0)
        self.progress_label.config(text="Подготовка...", fg="orange")
        self.log_info(f"Начато шифрование файла: {os.path.basename(input_file)}")

        try:
            # Обновляем прогресс
            self.update_progress(25)

            result = self.app.encrypt_file(
                input_file,
                output_file,
                json.dumps(key_data['parameters']),
                progress_callback=self.update_progress  # Добавляем callback для прогресса
            )

            # Завершаем прогресс
            self.update_progress(100)

            if result['success']:
                self.log_info(f"✓ Файл успешно зашифрован")
                self.log_info(f"  Выходной файл: {os.path.basename(output_file)}")
                self.log_info(
                    f"  Размер: {self.format_size(result['input_size'])} → {self.format_size(result['output_size'])}")
                self.log_info(f"  Seed: {result.get('seed_hex', 'N/A')}")

                self.progress_label.config(text="Готово!", fg="green")
                self.status_label.config(text=f"Файл зашифрован: {os.path.basename(output_file)}", fg="green")
                messagebox.showinfo("Успех",
                                    f"Файл успешно зашифрован!\n\n"
                                    f"Сохранён как: {os.path.basename(output_file)}\n"
                                    f"Размер: {self.format_size(result['output_size'])}")
            else:
                self.progress_label.config(text="Ошибка", fg="red")
                self.log_info(f"✗ Ошибка: {result['error']}")
                messagebox.showerror("Ошибка", result['error'])
                self.status_label.config(text="Ошибка шифрования", fg="red")

        except Exception as e:
            self.progress_label.config(text="Ошибка", fg="red")
            self.log_info(f"✗ Критическая ошибка: {str(e)}")
            messagebox.showerror("Ошибка", f"Непредвиденная ошибка: {str(e)}")
            self.status_label.config(text="Критическая ошибка", fg="red")
        finally:
            self.set_ui_state(True)

    def decrypt_file(self):
        """Дешифрование файла."""
        input_file = self.file_path_var.get()
        if not input_file or not os.path.exists(input_file):
            messagebox.showerror("Ошибка", "Выберите файл для дешифрования!")
            return

        # Запрос закрытого ключа
        key_file = filedialog.askopenfilename(
            title="Выберите закрытый ключ",
            filetypes=[("JSON файлы", "*.json"), ("Все файлы", "*.*")]
        )
        if not key_file:
            return

        key_data = self.app.load_key_from_file(key_file)
        if not key_data or key_data.get('key_type') != 'private':
            messagebox.showerror("Ошибка", "Некорректный файл закрытого ключа!")
            return

        # Выбор места сохранения
        default_name = os.path.basename(input_file).replace('.enc', '')
        if default_name == os.path.basename(input_file):
            default_name = default_name + "_decrypted"

        output_file = filedialog.asksaveasfilename(
            title="Сохранить дешифрованный файл",
            defaultextension="",
            initialfile=default_name
        )
        if not output_file:
            return

        # Проверка перезаписи
        if os.path.exists(output_file):
            if not messagebox.askyesno("Подтверждение",
                                       f"Файл '{os.path.basename(output_file)}' уже существует.\nПерезаписать?"):
                return

        # Выполнение дешифрования
        self.set_ui_state(False)
        self.progress_var.set(0)
        self.progress_label.config(text="Подготовка...", fg="orange")
        self.log_info(f"Начато дешифрование файла: {os.path.basename(input_file)}")

        try:
            # Обновляем прогресс
            self.update_progress(25)

            result = self.app.decrypt_file(
                input_file,
                output_file,
                json.dumps(key_data['parameters']),
                progress_callback=self.update_progress  # Добавляем callback для прогресса
            )

            # Завершаем прогресс
            self.update_progress(100)

            if result['success']:
                self.log_info(f"✓ Файл успешно дешифрован")
                self.log_info(f"  Выходной файл: {os.path.basename(output_file)}")
                self.log_info(
                    f"  Размер: {self.format_size(result['input_size'])} → {self.format_size(result['output_size'])}")
                self.log_info(f"  Seed: {result.get('seed_hex', 'N/A')}")

                self.progress_label.config(text="Готово!", fg="green")
                self.status_label.config(text=f"Файл дешифрован: {os.path.basename(output_file)}", fg="green")
                messagebox.showinfo("Успех",
                                    f"Файл успешно дешифрован!\n\n"
                                    f"Сохранён как: {os.path.basename(output_file)}\n"
                                    f"Размер: {self.format_size(result['output_size'])}")
            else:
                self.progress_label.config(text="Ошибка", fg="red")
                self.log_info(f"✗ Ошибка: {result['error']}")
                messagebox.showerror("Ошибка", result['error'])
                self.status_label.config(text="Ошибка дешифрования", fg="red")

        except Exception as e:
            self.progress_label.config(text="Ошибка", fg="red")
            self.log_info(f"✗ Критическая ошибка: {str(e)}")
            messagebox.showerror("Ошибка", f"Непредвиденная ошибка: {str(e)}")
            self.status_label.config(text="Критическая ошибка", fg="red")
        finally:
            self.set_ui_state(True)

    def update_progress(self, percent):
        """Обновить прогресс-бар."""
        self.progress_var.set(percent)
        self.progress_label.config(text=f"Выполнено: {percent}%")
        self.root.update_idletasks()

    def set_ui_state(self, enabled):
        """Включение/отключение элементов интерфейса."""
        state = 'normal' if enabled else 'disabled'
        self.generate_btn.config(state=state)
        self.encrypt_btn.config(state=state)
        self.decrypt_btn.config(state=state)

    def log_info(self, message):
        """Добавление сообщения в информационное поле."""
        self.info_text.config(state='normal')
        self.info_text.insert('end', f"{message}\n")
        self.info_text.see('end')
        self.info_text.config(state='disabled')

    def format_size(self, size):
        """Форматирование размера файла."""
        for unit in ['Б', 'КБ', 'МБ', 'ГБ']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} ТБ"


def main():
    """Запуск приложения."""
    root = tk.Tk()
    app = AsymmetricCryptoGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()