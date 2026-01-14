import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog, ttk
import os
import json
from app_core import AsymmetricCryptoApp

class AsymmetricCryptoGUI:
    """Графический интерфейс для асимметричного шифрования."""

    def __init__(self, root):
        self.root = root
        self.root.title("Асимметричная криптография - Эль-Гамаль")
        self.root.geometry("800x700")

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
            text="Асимметричная криптография - Криптосистема Эль-Гамаля",
            font=("Arial", 14, "bold"),
            justify="center"
        )
        title_label.pack(pady=10)

        # Блок 1: Генерация ключей
        key_frame = tk.LabelFrame(self.root, text="Генерация ключей", padx=10, pady=10)
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

        # Поле для отображения информации о ключах
        self.key_info_text = scrolledtext.ScrolledText(
            key_frame,
            width=70,
            height=8,
            wrap=tk.WORD,
            font=("Courier", 9)
        )
        self.key_info_text.pack(pady=5)
        self.key_info_text.insert("end", "Ключи не сгенерированы.\nНажмите 'Сгенерировать пару ключей'.")
        self.key_info_text.config(state='disabled')

        # Блок 2: Работа с файлами
        file_frame = tk.LabelFrame(self.root, text="Шифрование/Дешифрование файлов", padx=10, pady=10)
        file_frame.pack(fill="x", padx=20, pady=5)

        # Выбор файла
        tk.Label(file_frame, text="Входной файл:", font=("Arial", 10)).grid(row=0, column=0, sticky="w", pady=5)

        self.file_path_var = tk.StringVar()
        file_entry = tk.Entry(file_frame, textvariable=self.file_path_var, width=50, font=("Arial", 9))
        file_entry.grid(row=0, column=1, padx=5, pady=5)

        browse_btn = tk.Button(
            file_frame,
            text="Обзор...",
            command=self.browse_file,
            bg="#2196F3",
            fg="white",
            font=("Arial", 9)
        )
        browse_btn.grid(row=0, column=2, padx=5, pady=5)

        # Кнопки операций
        btn_frame = tk.Frame(file_frame)
        btn_frame.grid(row=1, column=0, columnspan=3, pady=10)

        self.encrypt_btn = tk.Button(
            btn_frame,
            text="Зашифровать (открытым ключом)",
            command=self.encrypt_file,
            bg="#9C27B0",
            fg="white",
            font=("Arial", 10),
            padx=15,
            pady=8,
            state='disabled'
        )
        self.encrypt_btn.pack(side="left", padx=5)

        self.decrypt_btn = tk.Button(
            btn_frame,
            text="Дешифровать (закрытым ключом)",
            command=self.decrypt_file,
            bg="#3F51B5",
            fg="white",
            font=("Arial", 10),
            padx=15,
            pady=8,
            state='disabled'
        )
        self.decrypt_btn.pack(side="left", padx=5)

        # Блок 3: Прогресс и информация
        info_frame = tk.LabelFrame(self.root, text="Информация о выполнении", padx=10, pady=10)
        info_frame.pack(fill="both", expand=True, padx=20, pady=5)

        self.info_text = scrolledtext.ScrolledText(
            info_frame,
            width=80,
            height=12,
            wrap=tk.WORD,
            font=("Courier", 9)
        )
        self.info_text.pack(fill="both", expand=True, pady=5)
        self.log_info("Готов к работе. Сгенерируйте ключи или выберите файл.")

        # Статусная строка
        self.status_label = tk.Label(
            self.root,
            text="Готов",
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
                # Обновляем текстовое поле с информацией о ключах
                self.key_info_text.config(state='normal')
                self.key_info_text.delete(1.0, tk.END)

                pub = result['public_key']
                priv = result['private_key']

                info = f"""ОТКРЫТЫЙ КЛЮЧ (для шифрования):
p (простое): {pub['p']}
g: {pub['g']}
y: {pub['y']}
Длина: {pub['bits']} бит

ЗАКРЫТЫЙ КЛЮЧ (для дешифрования):
p: {priv['p']}
x: {priv['x']}

Сохраните эти ключи в безопасном месте!"""
                self.key_info_text.insert("end", info)
                self.key_info_text.config(state='disabled')

                # Активируем кнопки
                self.encrypt_btn.config(state='normal')
                self.decrypt_btn.config(state='normal')

                self.log_info(f"✓ {result['message']}")
                self.status_label.config(text="Ключи успешно сгенерированы", fg="green")

                # Предлагаем сохранить ключи
                if messagebox.askyesno("Сохранение ключей", "Сохранить ключи в файлы?"):
                    self.save_keys_to_files()
            else:
                messagebox.showerror("Ошибка", result['error'])
                self.status_label.config(text="Ошибка генерации ключей", fg="red")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при генерации ключей: {str(e)}")
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

        # Выполнение шифрования
        self.set_ui_state(False)
        self.log_info(f"Начато шифрование файла: {os.path.basename(input_file)}")

        try:
            result = self.app.encrypt_file(
                input_file,
                output_file,
                json.dumps(key_data['parameters'])
            )

            if result['success']:
                self.log_info(f"✓ Файл успешно зашифрован")
                self.log_info(f"  Размер: {self.format_size(result['input_size'])} → "
                            f"{self.format_size(result['output_size'])}")
                self.status_label.config(text="Файл зашифрован", fg="green")
                messagebox.showinfo("Успех", "Файл успешно зашифрован!")
            else:
                self.log_info(f"✗ Ошибка: {result['error']}")
                messagebox.showerror("Ошибка", result['error'])
                self.status_label.config(text="Ошибка шифрования", fg="red")

        except Exception as e:
            self.log_info(f"✗ Критическая ошибка: {str(e)}")
            messagebox.showerror("Ошибка", f"Непредвиденная ошибка: {str(e)}")
            self.status_label.config(text="Ошибка", fg="red")
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
        output_file = filedialog.asksaveasfilename(
            title="Сохранить дешифрованный файл",
            defaultextension=".dec",
            initialfile=os.path.basename(input_file).replace('.enc', '.dec')
        )
        if not output_file:
            return

        # Выполнение дешифрования
        self.set_ui_state(False)
        self.log_info(f"Начато дешифрование файла: {os.path.basename(input_file)}")

        try:
            result = self.app.decrypt_file(
                input_file,
                output_file,
                json.dumps(key_data['parameters'])
            )

            if result['success']:
                self.log_info(f"✓ Файл успешно дешифрован")
                self.log_info(f"  Размер: {self.format_size(result['input_size'])} → "
                            f"{self.format_size(result['output_size'])}")
                self.status_label.config(text="Файл дешифрован", fg="green")
                messagebox.showinfo("Успех", "Файл успешно дешифрован!")
            else:
                self.log_info(f"✗ Ошибка: {result['error']}")
                messagebox.showerror("Ошибка", result['error'])
                self.status_label.config(text="Ошибка дешифрования", fg="red")

        except Exception as e:
            self.log_info(f"✗ Критическая ошибка: {str(e)}")
            messagebox.showerror("Ошибка", f"Непредвиденная ошибка: {str(e)}")
            self.status_label.config(text="Ошибка", fg="red")
        finally:
            self.set_ui_state(True)

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