# tests/test_api.py
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import main
import upscale


def test_upscale_without_file():
    client = main.app.test_client()
    resp = client.post("/upscale")
    assert resp.status_code == 400


def test_processed_not_found():
    client = main.app.test_client()
    resp = client.get("/processed/unknown.png")
    assert resp.status_code == 404


def test_task_status_returns_200():
    client = main.app.test_client()
    resp = client.get("/tasks/nonexistent-id")
    assert resp.status_code == 200
    assert resp.json["status"] in ("PENDING", "STARTED", "SUCCESS", "FAILURE")


def test_upscale_function_doubles_size():
    import cv2
    import numpy as np

    with open("lama_300px.png", "rb") as f:
        data = f.read()
    result = upscale.upscale(data)
    img = cv2.imdecode(np.frombuffer(result, dtype=np.uint8), cv2.IMREAD_COLOR)
    
    # Проверяем что размер увеличился в 2 раза
    assert img.shape[0] == 600  # высота x2
    assert img.shape[1] == 514  # ширина x2 (лама не квадратная!)