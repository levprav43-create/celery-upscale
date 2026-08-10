# Celery Upscale API

Сервис апскейлинга изображений x2 через ИИ-модель EDSR (OpenCV dnn_superres).

## Архитектура
- **Flask** - принимает HTTP-запросы
- **Celery** - фоновая обработка изображений
- **Redis** - брокер сообщений и хранилище результатов
- **OpenCV** - работа с изображениями и моделью

## Роуты
- POST /upscale - загрузить изображение, получить task_id
- GET /tasks/<task_id> - статус задачи + ссылка на результат
- GET /processed/<file> - скачать обработанное изображение

## Бонусные задачи
- Модель EDSR загружается один раз (singleton)
- Файлы не сохраняются на диск (BytesIO + Redis)
- Полная докеризация (web + worker + redis)
- Тесты: pytest (4 passed)

## Запуск локально
1. docker compose up -d redis
2. celery -A tasks worker --loglevel=info --pool=solo
3. python main.py

## Запуск через Docker
docker compose up -d --build

## Тестирование
pytest -v

## Пример запроса
bash
curl -F file=@image.png http://127.0.0.1:5000/upscale
curl http://127.0.0.1:5000/tasks/<task_id>

Автор: Лев, студент Нетологии
