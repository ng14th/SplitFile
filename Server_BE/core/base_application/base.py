
# import uvicorn

from gunicorn.app.base import BaseApplication
import multiprocessing


class _BaseApplication(BaseApplication):

    def __init__(self, app, **kwargs):
        self.application = app
        self.options = self._build_options(**kwargs)
        super().__init__()  # gọi sau khi self.options được gán

    def _build_options(
        self,
        host='0.0.0.0',
        port=4000,
        num_workers=multiprocessing.cpu_count() * 2,
        type_worker='async',
        accesslog='/dev/null',
        timeout=120,
        keepalive=5,
        my_worker=None,
    ):
        options = {
            "bind": f"{host}:{port}",
            "workers": num_workers,
            "accesslog": "-",
            "errorlog": "-",
            "timeout": timeout,
            "keepalive": keepalive,
        }

        if my_worker:
            options["worker_class"] = my_worker
        elif type_worker == "async":
            options["worker_class"] = "uvicorn.workers.UvicornWorker"
        elif type_worker == "sync":
            options["worker_class"] = "gunicorn.workers.sync.SyncWorker"
        else:
            raise ValueError("type_worker must be 'async' or 'sync'")

        return options

    def load_config(self):
        config = {
            key: value for key, value in self.options.items()
            if key in self.cfg.settings and value is not None
        }
        for key, value in config.items():
            self.cfg.set(key, value)

    def load(self):
        return self.application
