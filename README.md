# Celery Upscale API

Сервис апскейлинга изображений x2 через ИИ-модель EDSR (OpenCV dnn_superres).

## Архитектура
- **Flask** - принимает HTTP-запросы
- **Celery** - фоновая обработка (байты напрямую, pickle, без base64)
- **Redis** - брокер и хранилище результатов (TTL 1 час)
- **OpenCV** - работа с изображениями и моделью

## Роуты
- POST /upscale - загрузить изображение (поле image), получить task_id
- GET /tasks/<task_id> - статус задачи + ссылка на результат
- GET /processed/<file> - скачать обработанное изображение

## Особенности
- Модель EDSR загружается один раз (singleton)
- Файлы не сохраняются на диск (bytes + Redis)
- Валидация форматов (png, jpg, jpeg, bmp, tiff)
- TTL результатов в Redis (1 час)
- Полная докеризация (web + worker + redis)
- Тесты: pytest (6 passed), изображение генерируется программно

## Запуск локально (Windows)
1. docker compose up -d redis
2. celery -A tasks worker --loglevel=info --pool=solo
3. python main.py

## Запуск через Docker
docker compose up -d --build

## Тестирование
pytest -v

## Пример запроса
curl -F image=@lama_300px.png http://127.0.0.1:5000/upscale
curl http://127.0.0.1:5000/tasks/<task_id>

Автор: Лев, студент Нетологии
