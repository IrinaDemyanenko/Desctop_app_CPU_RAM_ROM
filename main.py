import sys
from PyQt5.QtCore import QTimer
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QVBoxLayout,
                             QLabel, QPushButton,
                             QLineEdit, QWidget)
from database import Database
from monitoring import get_system_usage


class SystemMonitorApp(QWidget):
    """Графическое приложение для мониторинга состояния системы
    с возможностью записи данных в базу данных.
    """
    def __init__(self):
        super().__init__()
        self.timer = QTimer()  # Таймер для периодического обновления данных
        self.db = Database()  # Инициализация базы данных
        self.recording = False  # Флаг состояния записи
        self.elapsed_time = 0  # Счётчик времени записи
        self.start_time = None  # Время начала записи

        self.init_ui()  # Инициализация интерфейса
        self.timer.timeout.connect(self.update_data)  # Связь таймера с функцией обновления данных

    def init_ui(self):
        """
        Создаёт графический интерфейс приложения.
        """
        self.setWindowTitle('Уровень загруженности:')
        self.resize(400, 300)
        self.layout = QVBoxLayout()

        # Метки для отображения загрузки системы
        self.cpu_label = QLabel('ЦП: --%')
        self.ram_label = QLabel('ОЗУ: --%')
        self.disk_label = QLabel('ПЗУ: --%')
        self.interval_label = QLabel('Задать интервал обновления (в секундах):')
        self.interval_input = QLineEdit('1')  # Поле ввода интервала обновления

        # Кнопки управления записью
        self.start_button = QPushButton('Начать запись')
        self.stop_button = QPushButton('Остановить запись')
        self.stop_button.hide()  # Скрыта до начала записи

        self.timer_label = QLabel('Время записи: 0с')  # Отображение времени записи

        # Добавление элементов в вертикальный макет
        self.layout.addWidget(self.cpu_label)
        self.layout.addWidget(self.ram_label)
        self.layout.addWidget(self.disk_label)
        self.layout.addWidget(self.interval_label)
        self.layout.addWidget(self.interval_input)
        self.layout.addWidget(self.start_button)
        self.layout.addWidget(self.stop_button)
        self.layout.addWidget(self.timer_label)

        self.setLayout(self.layout)  # Установка макета в окно

        # Подключение кнопок к соответствующим методам
        self.start_button.clicked.connect(self.start_recording)
        self.stop_button.clicked.connect(self.stop_recording)

        # Метод update_data вызывается каждый раз, когда таймер 'тикает'
        #self.timer.timeout.connect(self.update_data)

    def update_data(self):
        """
        Обновляет данные о загрузке системы и записывает их в базу,
        если включена запись.
        """
        usage = get_system_usage()  # Получение текущих данных о системе

        # Обновление интерфейса
        self.cpu_label.setText(f'ЦП: {usage['cpu']}%')
        self.ram_label.setText(f'ОЗУ: {usage['ram']}%')
        self.disk_label.setText(f'ПЗУ: {usage['disk']}%')

        if self.recording:  # Если запись включена
            now = datetime.now()
            self.elapsed_time = (now - self.start_time).seconds
            self.timer_label.setText(f'Время записи: {self.elapsed_time}с')

            # Запись данных в базу
            self.db.insert_data(
                time=now.strftime('%d-%m-%Y %H:%M:%S'),
                cpu=usage['cpu'],
                ram=usage['ram'],
                disk=usage['disk']
            )

    def start_recording(self):
        """
        Запускает процесс записи данных.
        """
        self.recording = True
        self.start_time = datetime.now()
        self.elapsed_time = 0
        self.timer_label.setText('Время записи: 0с')
        self.start_button.hide()
        self.stop_button.show()

        interval = int(self.interval_input.text()) * 1000  # Интервал обновления в миллисекундах
        self.timer.start(interval)

    def stop_recording(self):
        """
        Останавливает процесс записи данных.
        """
        self.recording = False
        self.start_button.show()
        self.stop_button.hide()
        self.timer.stop()
        self.start_time = None
        self.timer_label.setText('Время записи: 0с')

    def closeEvent(self, event):
        """
        Закрывает базу данных при завершении работы приложения.
        """
        self.db.close()
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)  # Создание приложения PyQt
    window = SystemMonitorApp()  # Создание главного окна
    window.show()  # Показ окна на экране
    sys.exit(app.exec_())  # Запуск цикла обработки событий
