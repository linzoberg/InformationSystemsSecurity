import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog, ttk
import os
import block_cipher


class BlockCipherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Блочные шифры, режимы использования блочных шифров")
        self.root.geometry("700x700")

        # Центрируем окно
        self.center_window()

        # Создание интерфейса
        self.create_widgets()

    def center_window(self):
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
            text="Блочные шифры, режимы использования блочных шифров",
            font=("Arial", 14, "bold"),
            justify="center"
        )
        title_label.pack(pady=10)

        # === БЛОК 1: ВЫБОР ФАЙЛА ===
        file_frame = tk.Frame(self.root, padx=10, pady=10)
        file_frame.pack(fill="x", padx=20, pady=5)

        # Поле для пути к файлу
        tk.Label(file_frame, text="Путь к файлу:", font=("Arial", 10)).pack(anchor="w")

        # Фрейм для строки ввода и кнопки
        file_input_frame = tk.Frame(file_frame)
        file_input_frame.pack(fill="x", pady=(5, 0))

        self.file_path_var = tk.StringVar()
        file_entry = tk.Entry(file_input_frame, textvariable=self.file_path_var,
                              width=60, font=("Arial", 9))
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

        # Информация о файле (ниже поля ввода)
        self.file_info_label = tk.Label(
            file_frame,
            text="Файл не выбран",
            font=("Arial", 9),
            fg="gray"
        )
        self.file_info_label.pack(anchor="w", pady=(5, 0))

        # === БЛОК 2: ПАРАМЕТРЫ ШИФРОВАНИЯ ===
        params_frame = tk.Frame(self.root, padx=10, pady=10)
        params_frame.pack(fill="x", padx=20, pady=5)

        # Пароль
        tk.Label(params_frame, text="Пароль:", font=("Arial", 10)).grid(row=0, column=0, sticky="w", pady=5)
        self.password_entry = tk.Entry(params_frame, width=30, font=("Arial", 10), show="*")
        self.password_entry.grid(row=0, column=1, sticky="w", padx=(10, 20), pady=5)

        # Хеш-функция
        tk.Label(params_frame, text="Хеш-функция:", font=("Arial", 10)).grid(row=0, column=2, sticky="w", pady=5)
        self.hash_var = tk.StringVar(value="MD5")
        hash_combo = ttk.Combobox(
            params_frame,
            textvariable=self.hash_var,
            values=["MD5", "MaHash8"],
            state="readonly",
            width=10,
            font=("Arial", 9)
        )
        hash_combo.grid(row=0, column=3, sticky="w", pady=5)

        # === БЛОК 3: КНОПКИ ДЕЙСТВИЙ ===
        buttons_frame = tk.Frame(self.root)
        buttons_frame.pack(pady=10)

        # Кнопка "Зашифровать"
        self.encrypt_btn = tk.Button(
            buttons_frame,
            text="Зашифровать файл",
            command=self.encrypt_file,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=20,
            pady=10,
            width=15
        )
        self.encrypt_btn.pack(side="left", padx=10)

        # Кнопка "Дешифровать"
        self.decrypt_btn = tk.Button(
            buttons_frame,
            text="Дешифровать файл",
            command=self.decrypt_file,
            bg="#FF9800",
            fg="white",
            font=("Arial", 11),
            padx=20,
            pady=10,
            width=15
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

        # === БЛОК 5: ИНФОРМАЦИЯ О СЕАНСЕ ===
        info_frame = tk.Frame(self.root, padx=10, pady=10)
        info_frame.pack(fill="both", expand=True, padx=20, pady=5)

        # Текстовое поле для информации
        self.info_text = scrolledtext.ScrolledText(
            info_frame,
            width=80,
            height=10,
            wrap=tk.WORD,
            font=("Courier", 9)
        )
        self.info_text.pack(fill="both", expand=True)
        self.info_text.insert("end", "Для начала работы выберите файл и введите пароль.\n")

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

    def browse_file(self):
        """Открыть диалог выбора файла"""
        filepath = filedialog.askopenfilename(
            title="Выберите файл для шифрования/дешифрования",
            filetypes=[
                ("Все файлы", "*.*"),
                ("Текстовые файлы", "*.txt"),
                ("Документы", "*.docx *.pdf *.doc"),
                ("Изображения", "*.jpg *.png *.bmp *.gif"),
                ("Архивы", "*.zip *.rar"),
                ("Исполняемые файлы", "*.exe *.msi"),
                ("Зашифрованные файлы", "*.bcipher")
            ]
        )

        if filepath:
            self.file_path_var.set(filepath)
            info = block_cipher.get_file_info(filepath)

            if info['success']:
                self.file_info_label.config(
                    text=f"{info['name']} • {info['type']} • {info['size_human']}",
                    fg="black"
                )
                self.log_info(f"Выбран файл: {info['name']} ({info['size_human']})")

    def encrypt_file(self):
        """Зашифровать файл"""
        self.process_file("encrypt")

    def decrypt_file(self):
        """Дешифровать файл"""
        self.process_file("decrypt")

    def process_file(self, operation):
        """Выполнить шифрование или дешифрование"""
        # 1. Проверка входных данных
        input_file = self.file_path_var.get()
        password = self.password_entry.get()

        if not input_file:
            messagebox.showerror("Ошибка", "Выберите файл!")
            return

        if not os.path.exists(input_file):
            messagebox.showerror("Ошибка", "Файл не существует!")
            return

        if not password:
            messagebox.showerror("Ошибка", "Введите пароль!")
            return

        # 2. Определение расширения для выходного файла
        if operation == "encrypt":
            # Используем функцию для генерации имени зашифрованного файла
            default_name = block_cipher.generate_encrypted_filename(input_file)
            default_ext = ".bcipher"
            file_types = [("Зашифрованные файлы (блочный шифр)", "*.bcipher"), ("Все файлы", "*.*")]
            operation_name = "зашифрованный"
        else:
            # Используем функцию для генерации имени дешифрованного файла
            default_name = block_cipher.generate_decrypted_filename(input_file)
            default_ext = ""
            file_types = [("Все файлы", "*.*")]
            operation_name = "дешифрованный"

        # 3. Диалог сохранения
        output_file = filedialog.asksaveasfilename(
            title=f"Сохранить {operation_name} файл",
            defaultextension=default_ext,
            initialfile=default_name,
            filetypes=file_types
        )

        if not output_file:
            return  # Пользователь отменил

        # 4. Проверка перезаписи
        if os.path.exists(output_file):
            if not messagebox.askyesno("Подтверждение",
                                       f"Файл '{os.path.basename(output_file)}' уже существует.\nПерезаписать?"):
                return

        # 5. Выполнение операции
        self.set_ui_state(False)
        self.progress_label.config(text="Подготовка...")

        if operation == "encrypt":
            self.log_info(f"Начато шифрование файла: {os.path.basename(input_file)}")
        else:
            self.log_info(f"Начато дешифрование файла: {os.path.basename(input_file)}")

        try:
            if operation == "encrypt":
                result = block_cipher.encrypt_file(
                    input_path=input_file,
                    output_path=output_file,
                    password=password,
                    hash_type=self.hash_var.get(),
                    progress_callback=self.update_progress
                )
            else:
                result = block_cipher.decrypt_file(
                    input_path=input_file,
                    output_path=output_file,
                    password=password,
                    hash_type=self.hash_var.get(),
                    progress_callback=self.update_progress
                )

            # 6. Обработка результата
            if result['success']:
                self.progress_label.config(text="Готово!", fg="green")

                if operation == "encrypt":
                    self.log_info(f"Файл успешно зашифрован")
                    self.status_label.config(text=f"Файл зашифрован: {os.path.basename(output_file)}", fg="green")
                else:
                    self.log_info(f"Файл успешно дешифрован")
                    self.status_label.config(text=f"Файл дешифрован: {os.path.basename(output_file)}", fg="green")

                self.log_info(f"  Выходной файл: {os.path.basename(output_file)}")
                self.log_info(f"  Размер: {block_cipher.format_file_size(result['output_size'])}")
                self.log_info(f"  Хеш-функция: {result['hash_type']}")
                self.log_info(f"  Seed: {result['seed_hex']}")

                if operation == "encrypt":
                    self.log_info(f"  IV: {result['iv']}")
                else:
                    self.log_info(f"  IV: {result['iv_used']}")

                messagebox.showinfo("Успех",
                                    f"Файл успешно {'зашифрован' if operation == 'encrypt' else 'дешифрован'}!\n\n"
                                    f"Сохранён как: {os.path.basename(output_file)}\n"
                                    f"Размер: {block_cipher.format_file_size(result['output_size'])}")
            else:
                self.progress_label.config(text="Ошибка", fg="red")
                self.log_info(f"Ошибка: {result['error']}")
                messagebox.showerror("Ошибка", result['error'])
                self.status_label.config(text="Ошибка при обработке файла", fg="red")

        except Exception as e:
            error_msg = f"Непредвиденная ошибка: {str(e)}"
            self.log_info(f"Критическая ошибка: {error_msg}")
            messagebox.showerror("Ошибка", error_msg)
            self.status_label.config(text="Критическая ошибка", fg="red")

        finally:
            self.set_ui_state(True)
            self.progress_var.set(0)

    def update_progress(self, percent):
        """Обновить прогресс-бар"""
        self.progress_var.set(percent)
        self.progress_label.config(text=f"Выполнено: {percent}%")
        self.root.update_idletasks()

    def set_ui_state(self, enabled):
        """Включить/выключить элементы интерфейса"""
        state = "normal" if enabled else "disabled"
        self.encrypt_btn.config(state=state)
        self.decrypt_btn.config(state=state)

    def log_info(self, message):
        """Добавить сообщение в информационное поле"""
        self.info_text.insert("end", f"{message}\n")
        self.info_text.see("end")


def main():
    root = tk.Tk()
    app = BlockCipherApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()