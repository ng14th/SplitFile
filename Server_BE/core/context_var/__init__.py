from contextvars import ContextVar
import uuid


class EventIDContextVar:
    def __init__(self):
        self.eid = ContextVar("event_id", default=None)

    def create_event_id(self):
        eid = str(uuid.uuid4())
        self.eid.set(eid)

    def set_event_id(self, eid):
        self.eid.set(eid)

    def get_event_id(self):
        if not self.eid.get():
            self.create_event_id()
        return self.eid.get()

    def clear_event_id(self):
        self.eid.set(None)


event_id = EventIDContextVar()
