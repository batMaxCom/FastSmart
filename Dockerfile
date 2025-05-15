# Используем официальный образ Python 3.11 slim
FROM python:3.11-slim

# Устанавливаем системные зависимости, которые могут понадобиться для приложения
RUN apt-get update && apt-get install -y \
    libicu72 \
    libssl3 \
    && rm -rf /var/lib/apt/lists/*

# Копируем только requirements.txt (для кэширования зависимостей)
COPY requirements.txt /app/requirements.txt

# Обновляем pip и устанавливаем зависимости из requirements.txt
RUN pip install --upgrade pip && \
    pip install -r /app/requirements.txt --no-cache-dir

# Копируем исходный код приложения в контейнер
COPY . /app
WORKDIR /app

# Копируем и даем права на исполнение xTunnel
COPY xTunnel /usr/local/bin/xTunnel
RUN chmod +x /usr/local/bin/xTunnel

# Открываем порт для приложения
EXPOSE 4647

# Запускаем FastAPI через uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "4647"]
