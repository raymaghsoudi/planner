"""رابط کاربری ساده با Tkinter استاندارد؛ بدون قالب و فایل ترجمه."""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

PRIORITIES = {'کم': 'Low', 'متوسط': 'Medium', 'زیاد': 'High'}
PRIORITY_TEXT = {value: key for key, value in PRIORITIES.items()}


class TaskForm(tk.Toplevel):
    """یک پنجره برای افزودن و ویرایش: نمونه‌ای از استفاده مجدد از کلاس."""
    def __init__(self, parent, save_callback, task=None):
        super().__init__(parent)
        self.save_callback = save_callback
        self.task = task
        self.title('ویرایش کار' if task else 'کار جدید')
        self.geometry('490x440')
        self.configure(bg='#F3F5F9')
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.title_var = tk.StringVar(value=task['title'] if task else '')
        self.priority_var = tk.StringVar(value=PRIORITY_TEXT.get(task['priority'], 'متوسط') if task else 'متوسط')
        self.date_var = tk.StringVar(value=task['due_date'].strftime('%Y-%m-%d %H:%M')
                                     if task and task['due_date'] else '')

        content = ttk.Frame(self, padding=24, style='Card.TFrame')
        content.pack(fill='both', expand=True)
        ttk.Label(content, text='عنوان کار').pack(anchor='e')
        ttk.Entry(content, textvariable=self.title_var, justify='right').pack(fill='x', pady=5)
        ttk.Label(content, text='توضیحات').pack(anchor='e')
        self.description = tk.Text(content, height=3, wrap='word')
        self.description.pack(fill='x', pady=5)
        if task:
            self.description.insert('1.0', task['description'] or '')
        ttk.Label(content, text='اولویت').pack(anchor='e')
        ttk.Combobox(content, textvariable=self.priority_var,
                     values=list(PRIORITIES), state='readonly').pack(fill='x', pady=5)
        ttk.Label(content, text='موعد (میلادی: 2026-10-15 14:30) — اختیاری').pack(anchor='e')
        ttk.Entry(content, textvariable=self.date_var, justify='right').pack(fill='x', pady=5)
        ttk.Button(content, text='ذخیره تغییرات' if task else 'افزودن کار',
                   style='Primary.TButton', command=self.save).pack(fill='x', pady=14)

    def save(self):
        title = self.title_var.get().strip()
        if not title:
            messagebox.showwarning('خطا', 'عنوان کار را وارد کنید.', parent=self)
            return
        if len(title) > 200:
            messagebox.showwarning('خطا', 'عنوان باید حداکثر ۲۰۰ نویسه باشد.', parent=self)
            return
        date_text = self.date_var.get().strip()
        try:
            due_date = datetime.strptime(date_text, '%Y-%m-%d %H:%M') if date_text else None
        except ValueError:
            messagebox.showwarning('خطا', 'تاریخ را مثل 2026-10-15 14:30 بنویسید.', parent=self)
            return
        data = (title, self.description.get('1.0', 'end-1c').strip(),
                PRIORITIES[self.priority_var.get()], due_date)
        if self.save_callback(data):
            self.destroy()


class TodoApp(tk.Tk):
    """کنترل پنجره، انتخاب کار و رویدادهای دکمه‌ها."""
    def __init__(self, database):
        super().__init__()
        self.database = database
        self.tasks = {}
        self.category = 'همه'
        self.search_var = tk.StringVar()
        self.title('مدیریت کارها — نسخه آموزشی')
        self.geometry('1050x690')
        self.minsize(850, 540)
        self.configure(bg='#F3F5F9')
        self.setup_style()
        self.build_screen()
        self.refresh()

    def setup_style(self):
        """چند تنظیم ظاهری ساده، بدون کتابخانه یا فایل استایل جداگانه."""
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('.', font=('Tahoma', 10), background='#F3F5F9', foreground='#1E293B')
        style.configure('Card.TFrame', background='#FFFFFF')
        style.configure('Card.TLabel', background='#FFFFFF', foreground='#1E293B')
        style.configure('Muted.TLabel', background='#FFFFFF', foreground='#64748B')
        style.configure('Heading.TLabel', background='#F3F5F9', foreground='#1E293B',
                        font=('Tahoma', 17, 'bold'))
        style.configure('Stat.TLabel', background='#FFFFFF', foreground='#2563EB',
                        font=('Tahoma', 17, 'bold'))
        style.configure('TButton', padding=(12, 9), background='#E8EDF6',
                        foreground='#1E293B', borderwidth=0)
        style.map('TButton', background=[('active', '#DDE5F2')])
        style.configure('Primary.TButton', background='#2563EB', foreground='#FFFFFF')
        style.map('Primary.TButton', background=[('active', '#1D4ED8')],
                  foreground=[('active', '#FFFFFF')])
        style.configure('Danger.TButton', background='#FEE2E2', foreground='#B91C1C')
        style.map('Danger.TButton', background=[('active', '#FECACA')])
        style.configure('Treeview', rowheight=38, background='#FFFFFF',
                        fieldbackground='#FFFFFF', foreground='#1E293B', borderwidth=0)
        style.map('Treeview', background=[('selected', '#DBEAFE')],
                  foreground=[('selected', '#1E293B')])
        style.configure('Treeview.Heading', padding=(7, 11), background='#E9EEF6',
                        foreground='#334155', font=('Tahoma', 10, 'bold'))
        style.configure('TEntry', padding=7)

    def build_screen(self):
        sidebar = ttk.Frame(self, padding=16, style='Card.TFrame', width=180)
        sidebar.pack(side='right', fill='y', padx=(0, 15), pady=16)
        sidebar.pack_propagate(False)
        ttk.Label(sidebar, text='مدیریت کارها', style='Card.TLabel',
                  font=('Tahoma', 12, 'bold')).pack(anchor='e', pady=(8, 25))
        ttk.Label(sidebar, text='فیلتر کارها', style='Muted.TLabel').pack(anchor='e', pady=(0, 12))
        for category in ('همه', 'انجام‌نشده', 'انجام‌شده', 'اولویت بالا', 'حذف‌شده‌ها'):
            ttk.Button(sidebar, text=category,
                       command=lambda c=category: self.set_category(c)).pack(fill='x', pady=5)

        main = ttk.Frame(self, padding=16)
        main.pack(side='left', fill='both', expand=True)
        ttk.Label(main, text='کارهای من', style='Heading.TLabel').pack(anchor='e', pady=(2, 2))
        ttk.Label(main, text='برنامه‌ریزی و پیگیری کارهای روزانه',
                  foreground='#64748B').pack(anchor='e', pady=(0, 14))

        stats = ttk.Frame(main)
        stats.pack(fill='x', pady=(0, 14))
        self.stat_labels = {}
        for label, key in (('کل کارها', 'total'), ('در انتظار', 'pending'),
                           ('انجام‌شده', 'done')):
            frame = ttk.Frame(stats, padding=12, style='Card.TFrame')
            frame.pack(side='right', expand=True, fill='x', padx=4)
            self.stat_labels[key] = ttk.Label(frame, text='۰', style='Stat.TLabel')
            self.stat_labels[key].pack(anchor='e')
            ttk.Label(frame, text=label, style='Muted.TLabel').pack(anchor='e')

        content = ttk.Frame(main, padding=15, style='Card.TFrame')
        content.pack(fill='both', expand=True)
        ttk.Label(content, text='فهرست کارها', style='Card.TLabel',
                  font=('Tahoma', 12, 'bold')).pack(anchor='e', pady=(0, 8))
        search = ttk.Entry(content, textvariable=self.search_var, justify='right')
        search.pack(fill='x', pady=(0, 5))
        self.search_var.trace_add('write', lambda *_: self.refresh())
        ttk.Label(content, text='جستجو در عنوان و توضیحات',
                  style='Muted.TLabel').pack(anchor='e', pady=(0, 12))

        table_area = ttk.Frame(content, style='Card.TFrame')
        table_area.pack(fill='both', expand=True)
        columns = ('status', 'priority', 'date', 'title')
        self.table = ttk.Treeview(table_area, columns=columns,
                                  show='headings', selectmode='browse')
        for col, heading, width in (('status', 'وضعیت', 100), ('priority', 'اولویت', 90),
                                    ('date', 'موعد', 155), ('title', 'عنوان کار', 250)):
            self.table.heading(col, text=heading)
            self.table.column(col, width=width, anchor='center', minwidth=75)
        scroll = ttk.Scrollbar(table_area, orient='vertical', command=self.table.yview)
        self.table.configure(yscrollcommand=scroll.set)
        scroll.pack(side='right', fill='y')
        self.table.pack(side='left', fill='both', expand=True)
        self.table.bind('<Double-1>', lambda event: self.edit_task())
        self.table.tag_configure('done', foreground='#64748B')

        buttons = ttk.Frame(content, style='Card.TFrame')
        buttons.pack(fill='x', pady=(14, 8))
        for title, action, button_style in (
            ('+ افزودن کار', self.new_task, 'Primary.TButton'),
            ('ویرایش', self.edit_task, 'TButton'),
            ('تغییر وضعیت', self.toggle_done, 'TButton'),
            ('حذف', self.delete_task, 'Danger.TButton'),
            ('حذف کامل', self.permanent_delete_task, 'Danger.TButton')):
            ttk.Button(buttons, text=title, command=action,
                       style=button_style).pack(side='right', padx=4)
        self.info = ttk.Label(content, text='', style='Muted.TLabel')
        self.info.pack(anchor='e')

    def set_category(self, category):
        self.category = category
        self.refresh()

    def refresh(self):
        try:
            rows = self.database.all_tasks(self.category, self.search_var.get())
        except Exception as error:
            messagebox.showerror('خطا', str(error), parent=self)
            return
        self.table.delete(*self.table.get_children())
        self.tasks = {str(item['id']): item for item in rows}
        for item in rows:
            date = item['due_date'].strftime('%Y-%m-%d %H:%M') if item['due_date'] else '—'
            self.table.insert('', 'end', iid=str(item['id']), values=(
                'انجام‌شده' if item['completed'] else 'باز',
                PRIORITY_TEXT.get(item['priority'], item['priority']), date, item['title']),
                tags=('done',) if item['completed'] else ())
        self.info.config(text=f'تعداد کارهای نمایش‌داده‌شده: {len(rows)}')
        # آمار کلی مستقل از فیلتر و جستجو است.
        try:
            all_rows = self.database.all_tasks('همه', '')
            done = sum(bool(item['completed']) for item in all_rows)
            self.stat_labels['total'].config(text=str(len(all_rows)))
            self.stat_labels['pending'].config(text=str(len(all_rows) - done))
            self.stat_labels['done'].config(text=str(done))
        except Exception:
            pass

    def selected_task(self):
        selected = self.table.selection()
        if not selected:
            messagebox.showinfo('انتخاب کار', 'ابتدا یک کار را انتخاب کنید.', parent=self)
            return None
        return self.tasks.get(selected[0])

    def run_action(self, action):
        try:
            action()
            self.refresh()
            return True
        except Exception as error:
            messagebox.showerror('خطا', str(error), parent=self)
            return False

    def new_task(self):
        TaskForm(self, lambda values: self.run_action(lambda: self.database.add(*values)))

    def in_trash(self):
        """در لیست حذف‌شده‌ها ویرایش و تغییر وضعیت مجاز نیست."""
        if self.category == 'حذف‌شده‌ها':
            messagebox.showinfo('حذف‌شده‌ها', 'این عملیات روی کارهای حذف‌شده ممکن نیست.', parent=self)
            return True
        return False

    def edit_task(self):
        if self.in_trash():
            return
        task = self.selected_task()
        if task:
            TaskForm(self, lambda values: self.run_action(
                lambda: self.database.update(task['id'], *values)), task)

    def toggle_done(self):
        if self.in_trash():
            return
        task = self.selected_task()
        if task:
            self.run_action(lambda: self.database.mark_done(task['id'], not task['completed']))

    def delete_task(self):
        if self.in_trash():
            return
        task = self.selected_task()
        if task and messagebox.askyesno('حذف', 'این کار حذف شود؟', parent=self):
            self.run_action(lambda: self.database.delete(task['id']))

    def permanent_delete_task(self):
        task = self.selected_task()
        if task and messagebox.askyesno(
                'حذف کامل',
                'این کار برای همیشه از پایگاه داده پاک می‌شود و قابل بازیابی نیست.\nادامه می‌دهید؟',
                icon='warning', parent=self):
            self.run_action(lambda: self.database.permanent_delete(task['id']))
