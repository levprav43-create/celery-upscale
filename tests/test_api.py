# tests/test_api.py
import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import cv2
import numpy as np
import pytest

import main
import upscale


def make_test_image(width: int = 100, height: int = 50) -> bytes:
    """Генерирует PNG-изображение программно — без файла на диске."""
    arr = np.zeros((height, width, 3), dtype=np.uint8)
    arr[:, :, 0] = 120
    arr[:, :, 1] = 200
    arr[:, :, 2] = 80
    ok, encoded = cv2.imencode(".png", arr)
    assert ok
    return encoded.tobytes()


def test_upscale_without_file():
    client = main.app.test_client()
    resp = client.post("/upscale")
    assert resp.status_code == 400


def test_upscale_wrong_extension():
    client = main.app.test_client()
    resp = client.post(
        "/upscale",
        data={"image": (io.BytesIO(b"not an image"), "virus.exe")},
        content_type="multipart/form-data",
    )
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


def test_upscale_doubles_size():
    image = make_test_image(100, 50)
    result = upscale.upscale(image)
    img = cv2.imdecode(np.frombuffer(result, dtype=np.uint8), cv2.IMREAD_COLOR)
    assert img.shape[0] == 100  # высота x2
    assert img.shape[1] == 200  # ширина x2


def test_upscale_invalid_image_raises():
    # Используем только ASCII-байты (иначе SyntaxError)
    # Эти байты не являются валидным изображением — imdecode вернёт None
    with pytest.raises(ValueError):
        upscale.upscale(b"this-is-not-a-valid-image-bytes-0123456789")