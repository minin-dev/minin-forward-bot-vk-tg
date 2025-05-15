FROM python:3.10-slim

WORKDIR /app

RUN mkdir -p /app/data /app/logs

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV TZ=Europe/Moscow

RUN mkdir -p data

COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('https://api.telegram.org/bot{token}/getMe')" || exit 1

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["python", "main.py"]
