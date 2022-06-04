import json
import logging
import time
from functools import wraps
from http import HTTPStatus
from typing import Any, Callable, Literal, Optional, Type

import requests
from requests.adapters import HTTPAdapter, Retry

from src.constants import (
    REQUESTS_BACKOFF_FACTOR,
    REQUESTS_RETRY_TIMES,
    REQUESTS_STATUS_FORCELIST,
    REQUESTS_TIMEOUT,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s.%(msecs)03d %(levelname)s %(module)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

retry_strategy = Retry(
    total=REQUESTS_RETRY_TIMES,
    backoff_factor=REQUESTS_BACKOFF_FACTOR,
    status_forcelist=REQUESTS_STATUS_FORCELIST,
)

session = requests.Session()

adapter = HTTPAdapter(max_retries=retry_strategy)

session.mount("https://", adapter)
session.mount("http://", adapter)


def client(
    method: Literal['get', 'options', 'head', 'post', 'put', 'patch', 'delete'],
    url: str,
    **kwargs,
) -> Optional[requests.Response]:
    try:
        response = session.request(
            method=method.upper(),
            url=url,
            timeout=REQUESTS_TIMEOUT,
            params=kwargs.get("params"),
        )
        response.raise_for_status()
        return response
    except requests.exceptions.HTTPError as err_http:
        logger.error(f"Http error: {err_http}")
    except requests.exceptions.ConnectionError as err_connection:
        logger.error(f"Error connecting: {err_connection}")
    except requests.exceptions.Timeout as err_timeout:
        logger.error(f"Timeout error: {err_timeout}")
    except requests.exceptions.RequestException as err:
        logger.error(f"Something went wrong: {err}")
    return None


def parse_json(response: Optional[requests.Response]) -> Optional[Any]:
    if response is None or response.status_code != HTTPStatus.OK:
        return None
    try:
        return response.json()
    except json.decoder.JSONDecodeError as err:
        logger.error(f"JSON decode error: {err}")
    return None


def get_backoff_time(retries: int, backoff_factor=REQUESTS_BACKOFF_FACTOR) -> float:
    return backoff_factor * (2 ** (retries - 1))


def retry(
    retries: int = REQUESTS_RETRY_TIMES,
    backoff_factor: float = REQUESTS_BACKOFF_FACTOR,
    exception: Type[Exception] = Exception,
    exception_handler: Optional[Callable[..., str]] = None,
) -> Callable:
    def decorator(fn: Callable) -> Callable:
        @wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Optional[Any]:
            fn_call_count = 0

            while fn_call_count <= retries:
                try:
                    return fn(*args, **kwargs)
                except exception as e:
                    is_not_last_call = fn_call_count < retries
                    backoff_time = get_backoff_time(fn_call_count, backoff_factor)
                    fn_call_count += 1

                    msg = exception_handler(*args, **kwargs) if exception_handler else e
                    msg = f"{msg}; Retrying in {backoff_time} seconds ({fn_call_count}/{retries})"
                    if is_not_last_call:
                        logger.error(msg, exc_info=True)
                        time.sleep(backoff_time)

            return None

        return wrapper

    return decorator
