import logging
import sys
from datetime import datetime
from functools import wraps
from typing import Dict
from pythonjsonlogger import jsonlogger
from collections import OrderedDict
from core.context_var import event_id


class JsonLogFormatter(jsonlogger.JsonFormatter):
    def __init__(self, *args, **kwargs):
        to_rename = {
            "asctime": "time",
            "levelname": "level"
        }
        if 'rename_fields' in kwargs:
            kwargs['rename_fields'].update(to_rename)
        else:
            kwargs['rename_fields'] = to_rename
        super().__init__(*args, **kwargs)
        self.datefmt = '[%d/%b/%Y:%H:%M:%S +0000]'

    def format(self, record):
        record.timestamp = int(datetime.now().timestamp())
        return super().format(record)

    def process_log_record(self, record):
        if not isinstance(record, OrderedDict):
            record = OrderedDict(record)

        # move time to first
        if 'eid' in record:
            record.move_to_end('eid', last=False)
        if 'timestamp' in record:
            record.move_to_end('timestamp', last=False)
        if 'time' in record:
            record.move_to_end('time', last=False)

        return super().process_log_record(record)


def restruct_log_method(func, exc_info: bool = None):
    @wraps(func)
    def structured_method(
        message,
        exc_info: bool = exc_info,
        extra: Dict = None,
        stack_info=False,
        stacklevel=1,
        **kwargs
    ):
        if not extra:
            extra = {}

        eid = extra.get('eid') or kwargs.get('eid')
        if not eid:
            eid = event_id.get_event_id()
        if not 'eid' in extra:
            extra.update({'eid': eid})
        if not message:
            message = f'{eid=}'

        for k, v in kwargs.items():
            if k in ('req_headers', 'resp_headers'):
                extra[k] = v
            elif isinstance(v, (str, int, float)):
                extra[k] = v
            else:
                extra[k] = str(v)
        try:
            return func(message, exc_info=exc_info, extra=extra, stack_info=stack_info, stacklevel=stacklevel)
        except Exception as e:
            new_extra = {'loc': '0cor0000', 'exc_extra': str(extra)}
            return func(message, exc_info=exc_info, extra=new_extra, stack_info=stack_info, stacklevel=stacklevel)
    return structured_method


def create_console_logger(
    name: str,
    level: int = logging.INFO,
    **kwargs
) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False

    logger.handlers = []

    console_handler = logging.StreamHandler(stream=sys.stdout)
    console_handler.setLevel(level)

    format_type = kwargs.get('format_type', 'json')
    if format_type == 'json':
        console_handler.setFormatter(JsonLogFormatter(
            fmt="%(asctime)s %(name)s %(levelname)s %(message)s",
            # <--- added this line
            rename_fields={"asctime": "time", "levelname": "level"},
        ))
    else:
        console_handler.setFormatter(logging.Formatter(
            "%(asctime)s [%(levelname)-4.4s] [%(name)-5.15s]: %(message)s"
        ))

    logger.addHandler(console_handler)

    logger.debug = restruct_log_method(logger.debug)
    logger.info = restruct_log_method(logger.info)
    logger.warn = restruct_log_method(logger.warn)
    logger.error = restruct_log_method(logger.error)
    logger.critical = restruct_log_method(logger.critical)
    logger.exception = restruct_log_method(logger.exception, True)
    logger.warning = restruct_log_method(logger.warning)

    print('created logger', logger)
    return logger
