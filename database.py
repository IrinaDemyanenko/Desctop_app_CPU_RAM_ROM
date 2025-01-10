import sqlite3


# Модуль содержит функционал для работы с базой данных
class Database:
    """Класс для работы с базой данных."""
    def __init__(self, db_name='app_monitoring_data.db'):
        """Подключение к базе данных SQLite.

        Если базы нет, она создаётсям автоматически.
        """
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self._create_table()

    def _create_table(self):
        """Создает таблицу для записи данных мониторинга,
        если её ещё нет.
        """
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS monitor_data (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            time TEXT,
                            cpu_usage REAL,
                            ram_usage REAL,
                            disc_usage REAL
                            )
        """)
        self.conn.commit()

    def insert_data(self, time, cpu, ram, disk):
        """Метод отвечает за добавление новых записей в таблицу.
        Параметры соответствуют данным, которые передаются для записи.
        """
        self.cursor.execute("""
        INSERT INTO monitor_data (time, cpu_usage, ram_usage, disc_usage)
        VALUES (?, ?, ?, ?)
        """, (time, cpu, ram, disk))
        self.conn.commit()

    def close(self):
        """Завершает соединение с базой данных, очищая память
        и освобождая ресурсы.
        """
        self.conn.close()
