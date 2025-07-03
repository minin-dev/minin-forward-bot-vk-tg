from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram, Summary, Info, Enum, start_http_server
import threading
import logging
import time

class BirthdayMetricsClass:
    def __init__(self):
        self.BIRTHDAY_REGISTRY = CollectorRegistry()
        self.UPTIME = Gauge('uptime_seconds', 'Uptime in seconds', registry=self.BIRTHDAY_REGISTRY)
        self.STATUS = Enum('status', 'Status of the birthday module', states=['running', 'error'], registry=self.BIRTHDAY_REGISTRY)
        self.BIRTHDAY_SENT = Counter('birthday_sent', 'Number of birthdays processed', registry=self.BIRTHDAY_REGISTRY)

        self.ERROR_COUNT = Counter('event_errors_total', 'Ошибок при обработке событий',
                        registry=self.BIRTHDAY_REGISTRY)
        self.LAST_ERROR = Info('last_error', 'Последняя ошибка в обработке событий',
                        registry=self.BIRTHDAY_REGISTRY)

        self.start_time = time.time()

    def update_uptime(self):
        while True:
            self.UPTIME.set(time.time() - self.start_time)
            time.sleep(1)

    def update_status(self, status='running'):
        if status in self.STATUS._states:
            while(True):
                self.STATUS.state(status)
                time.sleep(100)
        else:
            raise ValueError(f"Invalid status: {status}")

    def handle_error(self, error_message):
        self.ERROR_COUNT.inc()
        self.LAST_ERROR.info({'message': error_message, 'time': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())})
        self.STATUS.state('error')

    def start_metrics(self):
        start_http_server(8001, registry=self.BIRTHDAY_REGISTRY)
        threading.Thread(target=self.update_uptime, daemon=True).start()
        threading.Thread(target=self.update_status, daemon=True).start()


class EventMetricsClass:

    def __init__(self):
        self.EVENTS_REGISTRY = CollectorRegistry()

        self.UPTIME = Gauge('event_uptime_seconds', 'Время работы event-сервиса',
                        registry=self.EVENTS_REGISTRY)
        self.RECONNECTS = Counter('vk_reconnects_total', 'Переподключения к VK API',
                        registry=self.EVENTS_REGISTRY)
        self.STATUS = Enum('event_status', 'Статус event-сервиса',
                        states=['running', 'error'],
                        registry=self.EVENTS_REGISTRY)

        self.EVENT_COUNT = Counter('event_processed_total', 'Обработано событий',
                        registry=self.EVENTS_REGISTRY)
        self.PROCESSING_TIME = Histogram('event_processing_seconds', 'Время обработки события',
                        ['function'],
                        registry=self.EVENTS_REGISTRY)
        self.TG_MESSAGES_SENT = Counter('tg_messages_sent_total', 'Отправлено сообщений в Telegram',
                        registry=self.EVENTS_REGISTRY)
        self.ATTACHMENTS = Counter('attachments_total', 'Вложения по типу', ['type'],
                        registry=self.EVENTS_REGISTRY)


        self.ERROR_COUNT = Counter('event_errors_total', 'Ошибок при обработке событий',
                        registry=self.EVENTS_REGISTRY)
        self.LAST_ERROR = Info('last_error', 'Последняя ошибка в обработке событий',
                        registry=self.EVENTS_REGISTRY)

        self.start_time = time.time()

    def update_uptime(self):
        while True:
            self.UPTIME.set(time.time() - self.start_time)
            time.sleep(1)

    def update_status(self, status='running'):
        if status in self.STATUS._states:
            while(True):
                self.STATUS.state(status)
                time.sleep(100)
        else:
            raise ValueError(f"Invalid status: {status}")

    def handle_error(self, error_message):
        self.ERROR_COUNT.inc()
        self.LAST_ERROR.info({'message': error_message, 'time': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())})
        self.STATUS.state('error')

    def histogram_timer(self):
        def decorator(func):
            def wrapper(*args, **kwargs):
                start = time.time()
                try:
                    return func(*args, **kwargs)
                finally:
                    self.PROCESSING_TIME.labels(function=func.__name__).observe(time.time() - start)
            return wrapper
        return decorator

    def start_metrics(self):
        start_http_server(8000, registry=self.EVENTS_REGISTRY)
        self.RECONNECTS.inc()
        threading.Thread(target=self.update_uptime, daemon=True).start()
        threading.Thread(target=self.update_status, daemon=True).start()


BirthdayMetrics = BirthdayMetricsClass()
EventMetrics = EventMetricsClass()