# main.py
import base64
import os

import redis as redis_lib
from flask import Flask, Response, jsonify, request

from tasks import celery_app, upscale_task

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

app = Flask(__name__)
redis_client = redis_lib.Redis.from_url(REDIS_URL)


@app.post("/upscale")
def upscale_route():
    """Принимает файл изображения, возвращает id задачи."""
    if "file" not in request.files:
        return jsonify({"error": "Пришли файл в поле 'file'"}), 400

    file = request.files["file"]
    data = file.read()
    if not data:
        return jsonify({"error": "Пустой файл"}), 400

    task = upscale_task.delay(base64.b64encode(data).decode("utf-8"))
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