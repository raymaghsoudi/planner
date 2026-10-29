"""لایه داده: تمام دستورات SQL در یک کلاس قرار دارند."""
import psycopg2
from psycopg2.extras import RealDictCursor


class TaskDatabase:
    def __init__(self, host='localhost', dbname='todo_db', user='postgres', password='postgres'):
        self.config = dict(host=host, dbname=dbname, user=user, password=password)

    def execute(self, sql, params=(), fetch=False):
        # اتصال در پایان هر عملیات به صورت خودکار بسته می‌شود.
        with psycopg2.connect(**self.config) as connection:
            with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(sql, params)
                return [dict(row) for row in cursor.fetchall()] if fetch else None

    def setup(self):
        # همین جدول در پروژه قبلی استفاده شده؛ داده‌های قدیمی حذف نمی‌شوند.
        self.execute('''CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            title VARCHAR(200) NOT NULL,
            description TEXT NOT NULL DEFAULT '',
            priority VARCHAR(16) NOT NULL DEFAULT 'Medium',
            due_date TIMESTAMP NULL,
            created_at TIMESTAMP NOT NULL DEFAULT NOW(),
            completed BOOLEAN NOT NULL DEFAULT FALSE,
            reminder_enabled BOOLEAN NOT NULL DEFAULT TRUE,
            completed_at TIMESTAMP NULL,
            deleted BOOLEAN NOT NULL DEFAULT FALSE
        )''')
        self.execute('ALTER TABLE tasks ADD COLUMN IF NOT EXISTS deleted BOOLEAN NOT NULL DEFAULT FALSE')
        self.execute('ALTER TABLE tasks ADD COLUMN IF NOT EXISTS completed_at TIMESTAMP NULL')

    def all_tasks(self, category='همه', search=''):
        # در دسته «حذف‌شده‌ها» فقط کارهای حذف نرم‌شده نمایش داده می‌شوند.
        sql = 'SELECT * FROM tasks WHERE deleted = ' + ('TRUE' if category == 'حذف‌شده‌ها' else 'FALSE')
        params = []
        if category == 'انجام‌نشده':
            sql += ' AND completed = FALSE'
        elif category == 'انجام‌شده':
            sql += ' AND completed = TRUE'
        elif category == 'اولویت بالا':
            sql += " AND priority = 'High'"
        if search.strip():
            sql += ' AND (title ILIKE %s OR description ILIKE %s)'
            params += [f'%{search.strip()}%'] * 2
        sql += ' ORDER BY completed, created_at DESC, id DESC'
        return self.execute(sql, tuple(params), fetch=True)

    def add(self, title, description, priority, due_date):
        self.execute('''INSERT INTO tasks (title, description, priority, due_date)
                        VALUES (%s, %s, %s, %s)''',
                     (title, description, priority, due_date))

    def update(self, task_id, title, description, priority, due_date):
        self.execute('''UPDATE tasks SET title=%s, description=%s, priority=%s,
                        due_date=%s WHERE id=%s AND deleted=FALSE''',
                     (title, description, priority, due_date, task_id))

    def mark_done(self, task_id, done):
        self.execute('''UPDATE tasks SET completed=%s, completed_at=CASE WHEN %s
                        THEN NOW() ELSE NULL END WHERE id=%s AND deleted=FALSE''',
                     (done, done, task_id))

    def delete(self, task_id):
        # حذف نرم برای سازگاری با پروژه قبلی
        self.execute('UPDATE tasks SET deleted=TRUE WHERE id=%s', (task_id,))

    def permanent_delete(self, task_id):
        # حذف کامل: ردیف به طور کامل از جدول پاک می‌شود و هیچ اطلاعاتی از آن باقی نمی‌ماند.
        self.execute('DELETE FROM tasks WHERE id=%s', (task_id,))
