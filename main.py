# main.py
import os

import redis as redis_lib
from flask import Flask, Response, jsonify, request

from tasks import celery_app, upscale_task

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Допустимые форматы изображений
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "bmp", "tiff"}

app = Flask(__name__)
redis_client = redis_lib.Redis.from_url(REDIS_URL)


def allowed_file(filename: str) -> bool:
    """Проверяет расширение файла."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.post("/upscale")
def upscale_route():
    """Принимает файл изображения в поле 'image', возвращает id задачи."""
    if "image" not in request.files:
        return jsonify({"error": "Пришли файл в поле 'image'"}), 400

    file = request.files["image"]
    if not file.filename or not allowed_file(file.filename):
        return jsonify({"error": "Недопустимый формат. Разрешены: png, jpg, jpeg, bmp, tiff"}), 400

    data = file.read()
    if not data:
        return jsonify({"error": "Пустой файл"}), 400

    # Передаём БАЙТЫ напрямую — без base64!
    task = upscale_task.delay(data)
    return jsonify({"task_id": task.id}), 202


@app.get("/tasks/<task_id>")
def task_status(task_id):
    """Возвращает статус задачи и ссылку на готовый файл."""
    result = celery_app.AsyncResult(task_id)
    body = {"task_id": task_id, "status": result.status}

    if result.status == "SUCCESS":
        body["url"] = f"/processed/{result.result['file']}"
    if result.status == "FAILURE":
        body["error"] = str(result.result)

    return jsonify(body)


@app.get("/processed/<path:file>")
def processed_file(file):
    """Возвращает обработанный файл из Redis."""
    data = redis_client.get(f"processed:{file}")
    if data is None:
        return jsonify({"error": "Файл не найден"}), 404
    return Response(data, mimetype="image/png")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)