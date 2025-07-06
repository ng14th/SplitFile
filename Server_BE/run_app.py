
import uvloop
from core.base_application.base import _BaseApplication
from uvicorn.workers import UvicornWorker

from src.main import app  # Import FastAPI app từ main.py

uvloop.install()


class MyUvicornWorker(UvicornWorker):
    CONFIG_KWARGS = {
        "loop": "uvloop",         # ✅ cấu hình đúng ở đây
        "http": "httptools",      # (optional) hiệu suất cao hơn h11
        "lifespan": "auto",
    }


if __name__ == "__main__":
    worker_app = _BaseApplication(
        app,
        host="0.0.0.0",
        port=4000,
        num_workers=1,
        type_worker="async",
        my_worker=MyUvicornWorker,
    )
    worker_app.run()
