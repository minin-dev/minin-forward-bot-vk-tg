# Pim_VK_to_TG

Сервис для передачи сообщений из ВКонтакте в Telegram и отслеживания дней рождения.

## Структура проекта

```
Pim_VK_to_TG/
├── .dockerignore        # Файлы, исключаемые из Docker-образа
├── .gitignore           # Файлы, исключаемые из Git-репозитория
├── LICENSE              # Лицензия MIT
├── README.md            # Документация проекта
├── docker-compose.yml   # Конфигурация Docker Compose
├── Dockerfile           # Инструкции для сборки Docker-образа
├── entrypoint.sh        # Точка входа для Docker-контейнера
├── requirements.txt     # Зависимости Python
├── data/                # Директория для хранения данных
└── src/                 # Исходный код проекта
    ├── __init__.py
    ├── birthday_module.py  # Модуль обработки дней рождения
    ├── event_module.py     # Модуль обработки событий VK
    ├── config/             # Конфигурации приложения
    │   ├── __init__.py
    │   └── config.py       # Настройки токенов и ID чатов
    ├── console/            # Модуль для вывода в консоль
    │   ├── __init__.py
    │   └── console_messages.py
    └── modules/            # Вспомогательные модули
        ├── __init__.py
        └── handle_func.py  # Функции обработки сообщений
```

## Запуск с помощью Docker

### Предварительные требования
- Установленный Docker
- Установленный Docker Compose

### Настройка окружения
1. Создайте файл `.env` в корне проекта со следующими параметрами:
```
VK_TOKEN=your_vk_token_here
TG_BOT_TOKEN=your_telegram_bot_token_here
```

### Сборка и запуск
```bash
# Сборка образа
docker-compose build

# Запуск контейнеров
docker-compose up -d
```

### Запускаемые модули
Проект запускает два отдельных модуля в отдельных контейнерах:
- `birthday_module.py` - модуль обработки дней рождения
- `event_module.py` - модуль обработки событий

### Просмотр логов
```bash
# Логи всех контейнеров
docker-compose logs -f

# Логи конкретного контейнера
docker-compose logs -f birthday_service
docker-compose logs -f event_service
```

### Остановка контейнеров
```bash
docker-compose down
```

## Лицензия

Этот проект распространяется под лицензией MIT. Подробности смотрите в файле [LICENSE](LICENSE).
