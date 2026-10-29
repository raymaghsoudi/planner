"""نقطه شروع برنامه: ساخت پایگاه داده و پنجره."""
import tkinter as tk
from tkinter import messagebox
from database import TaskDatabase
from ui import TodoApp


def main():
    database = TaskDatabase()  # مشخصات PostgreSQL را در database.py تغییر دهید.
    try:
        database.setup()
    except Exception as error:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror('خطای پایگاه داده', f'اتصال PostgreSQL برقرار نشد:\n{error}')
        root.destroy()
        return

    app = TodoApp(database)  # تزریق وابستگی: رابط کاربری SQL نمی‌نویسد.
    app.mainloop()


if __name__ == '__main__':
    main()
