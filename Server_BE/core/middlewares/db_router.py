from .router import db_selector


class MasterReplicaRouter:
    def db_for_read(self, model, **hints):
        if db_selector.is_write():
            return "master"
        return "replica"  # Use the replica for read operations

    def db_for_write(self, model, **hints):
        return "master"  # Use the master for write operations

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        return db == "master"  # Allow migrations only on the master
