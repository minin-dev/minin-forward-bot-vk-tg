from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram, Summary, Info, Enum, start_http_server
import threading
import time

class BirthdayMetricsClass:
    def __init__(self):
        self.BIRTHDAY_REGISTRY = CollectorRegistry()
        self.UPTIME = Gauge('uptime', 'Время работы birthday-сервиса', ['type'], registry=self.BIRTHDAY_REGISTRY)
        self.STATUS = Enum('status', 'Статус birthday-сервиса', states=['running', 'error'], registry=self.BIRTHDAY_REGISTRY)
        self.BIRTHDAY_SENT = Counter('birthday_sent', 'Количество отправленных поздравлений', registry=self.BIRTHDAY_REGISTRY)

        self.ERROR_COUNT = Counter('errors_count', 'Ошибок при обработке событий', registry=self.BIRTHDAY_REGISTRY)
        self.LAST_ERROR = Info('last_error', 'Последняя ошибка в обработке событий', registry=self.BIRTHDAY_REGISTRY)

        self.start_time = time.time()

    def update_uptime(self):
        while True:
            elapsed = int(time.time() - self.start_time)
            seconds = elapsed % 60
            minutes = (elapsed // 60) % 60
            hours = (elapsed // 3600) % 24
            days = elapsed // 86400
            self.UPTIME.labels('seconds').set(seconds)
            self.UPTIME.labels('minutes').set(minutes)
            self.UPTIME.labels('hours').set(hours)
            self.UPTIME.labels('days').set(days)
            time.sleep(5)

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

        self.UPTIME = Gauge('uptime', 'Время работы event-сервиса',
                        ['type'],
                        registry=self.EVENTS_REGISTRY)
        self.STATUS = Enum('status', 'Статус event-сервиса',
                        states=['running', 'error'],
                        registry=self.EVENTS_REGISTRY)

        self.EVENT_COUNT = Counter('event_processed_total', 'Обработано событий всего',
                        registry=self.EVENTS_REGISTRY)
        self.METHOD_PROCESSING_TIME = Gauge('method_processing_average_time_seconds', 'Среднее время обработки метода',
                        ['method'],
                        registry=self.EVENTS_REGISTRY)
        self.EVENT_PROCESSING_TIME = Gauge('event_processing_average_time_seconds', 'Среднее время обработки события',
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
        self._timing_data = {}

    def update_uptime(self):
        while True:
            elapsed = int(time.time() - self.start_time)
            seconds = elapsed % 60
            minutes = (elapsed // 60) % 60
            hours = (elapsed // 3600) % 24
            days = elapsed // 86400
            self.UPTIME.labels('seconds').set(seconds)
            self.UPTIME.labels('minutes').set(minutes)
            self.UPTIME.labels('hours').set(hours)
            self.UPTIME.labels('days').set(days)
            time.sleep(5)

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

    def average_processing_time_decorator(self):
        def decorator(func):
            def wrapper(*args, **kwargs):
                start = time.time()
                try:
                    return func(*args, **kwargs)
                finally:
                    elapsed = time.time() - start
                    fname = func.__name__
                    if fname not in self._timing_data:
                        self._timing_data[fname] = [0.0, 0]
                    self._timing_data[fname][0] += elapsed
                    self._timing_data[fname][1] += 1
                    avg = self._timing_data[fname][0] / self._timing_data[fname][1]
                    self.METHOD_PROCESSING_TIME.labels(method=fname).set(avg)
            return wrapper
        return decorator

    def start_metrics(self):
        start_http_server(8000, registry=self.EVENTS_REGISTRY)
        threading.Thread(target=self.update_uptime, daemon=True).start()
        threading.Thread(target=self.update_status, daemon=True).start()


BirthdayMetrics = BirthdayMetricsClass()
EventMetrics = EventMetricsClass()
