# Pim_VK_to_TG

Масштабируемый сервис для пересылки сообщений из VK в Telegram.

## Запуск с помощью Docker

### Предварительные требования
- Установленный Docker
- Установленный Docker Compose

### Настройка окружения
1. Создайте файл `.env` в корне проекта со следующими параметрами:
```
VK_TOKEN=your_vk_token_here
TG_BOT_TOKEN=your_telegram_bot_token_here
VK_CHAT_ID=your_vk_chat_id_here
TG_CHAT_ID=your_telegram_chat_id_here
```

2. Создайте необходимые директории:
```bash
mkdir -p data logs
```

### Сборка и запуск
```bash
docker-compose build
docker-compose up -d
```

### Запускаемые модули
Проект запускает два отдельных модуля в отдельных контейнерах:
- `birthday_module.py` - модуль обработки дней рождения
- `event_module.py` - модуль обработки событий

### Структура проекта
```
/
├── data/                  # Директория для хранения данных
├── logs/                  # Директория для логов
├── src/                   # Исходный код
│   ├── config/            # Конфигурационные файлы
│   ├── console/           # Модули для работы с консолью
│   └── modules/           # Основные модули приложения
├── .env                   # Файл с переменными окружения
├── Dockerfile             # Файл для сборки Docker образа
├── docker-compose.yml     # Конфигурация Docker Compose
├── requirements.txt       # Зависимости Python
└── README.md              # Документация проекта
```

### Просмотр логов
```bash
docker-compose logs -f
docker-compose logs -f birthday_service
docker-compose logs -f event_service
```

### Обновление контейнеров
```bash
docker-compose down
docker-compose up -d --build
```

### Остановка контейнеров
```bash
docker-compose down
```

## Разработка

### Установка зависимостей
```bash
pip install -r requirements.txt
```

### Запуск локально
```bash
python -m src.birthday_module

python -m src.event_module

python main.py
```

## Лицензия

Проект распространяется под лицензией MIT.