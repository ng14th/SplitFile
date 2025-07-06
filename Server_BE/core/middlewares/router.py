
from core.abstractions.singeton import Singleton


class DBRouter(Singleton):

    def _singleton_init(self, **kwargs):
        """[summary]
            """
        self._use_write = False

    def is_write(self):
        return self._use_write

    def set_write(self):
        self._use_write = True

    def clear_use_write(self):
        self._use_write = False


db_selector: DBRouter = DBRouter()
