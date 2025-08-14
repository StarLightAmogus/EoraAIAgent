FROM python:3.13

# Системные зависимости, если нужны
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копируем код и данные
COPY ./app /app
COPY ./data /app/data
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# По умолчанию контейнер показывает версию Python
CMD ["python", "--version"]
