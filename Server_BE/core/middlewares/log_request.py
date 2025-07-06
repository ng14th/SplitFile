# -*- coding: utf-8 -*-
import ujson
import traceback
import logging
import urllib  # noqa: F401
from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException    # noqa: F401
from fastapi.responses import JSONResponse
from core.constants import AUTH_CONSOLE
from core.context_var import event_id


logger = logging.getLogger(AUTH_CONSOLE)


async def set_body(request: Request, body: bytes):
    async def receive():
        return {"type": "http.request", "body": body}
    request._receive = receive


async def get_body(request: Request) -> bytes:
    body = await request.body()
    await set_body(request, body)
    return body


async def log_requests(request: Request, call_next):
    try:
        try:
            await set_body(request, await request.body())

            new_body = await get_body(request)

            if new_body:
                try:
                    new_body = ujson.loads(new_body)
                except ujson.JSONDecodeError:
                    url_decoded_str = new_body.decode('utf-8')
                    query_dict = dict(urllib.parse.parse_qsl(url_decoded_str))
                    new_body = ujson.dumps(query_dict)
                    new_body = ujson.loads(new_body)
                except:
                    new_body = new_body
        except:
            new_body = None

        msg_request = f"Request : {(request.method)} {str(request.url.path)}"

        logger.info(
            msg_request,
            extra={
                "method": request.method,
                "url_path": request.url.path,
            },
            body=new_body
        )

        response = await call_next(request)

        msg = f"Response : {(request.method)} {str(response.status_code)} {str(request.url.path)}"
        logger.info(
            msg,
            extra={
                "method": request.method,
                "url_path": request.url.path,
                "status_code": response.status_code,
                "exc_infor": None
            },
            body=new_body
        )
        return response
    except HTTPException as e:
        logger.error(
            "HTTPException occurred",
            extra={
                "method": request.method,
                "url_path": request.url.path,
                "status_code": e.status_code,
                "exc_infor": traceback.format_exc()
            },
            body=new_body
        )
        raise e
    except Exception as e:
        logger.error(
            "An error occurred",
            extra={
                "method": request.method,
                "url_path": request.url.path,
                "status_code": 500, "exc_infor": traceback.format_exc()
            },
            body=new_body
        )
        raise e
    finally:
        event_id.clear_event_id()
