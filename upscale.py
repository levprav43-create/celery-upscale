# upscale.py
import os

import cv2
import numpy as np
from cv2 import dnn_superres

# Путь к модели рядом с этим файлом
MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "EDSR_x2.pb")

# Глобальный кеш: модель загрузится только ОДИН раз
_scaler = None


def get_scaler() -> dnn_superres.DnnSuperResImpl:
    """Создаёт и загружает модель единожды (singleton)."""
    global _scaler
    if _scaler is None:
        _scaler = dnn_superres.DnnSuperResImpl_create()
        _scaler.readModel(MODEL_PATH)
        _scaler.setModel("edsr", 2)
    return _scaler


def upscale(image_bytes: bytes) -> bytes:
    """
    Принимает байты изображения, возвращает байты увеличенного (x2) изображения.
    Файлы на диск НЕ сохраняются — всё в памяти.
    """
    scaler = get_scaler()

    # Байты -> картинка OpenCV
    arr = np.frombuffer(image_bytes, dtype=np.uint8)
    image = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("Не удалось распознать изображение")

    # Апскейл x2 через ИИ-модель
    result = scaler.upsample(image)

    # Картинка -> байты PNG
    ok, encoded = cv2.imencode(".png", result)
    if not ok:
        raise ValueError("Не удалось закодировать результат")
    return encoded.tobytes()


def example():
    """Пример использования (как в оригинале)."""
    with open("lama_300px.png", "rb") as f:
        data = f.read()
    result = upscale(data)
    with open("lama_600px.png", "wb") as f:
        f.write(result)
    print("Готово: lama_600px.png")


if __name__ == "__main__":
    example()