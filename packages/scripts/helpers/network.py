import json
import logging
import time
from functools import wraps
from http import HTTPStatus
from typing import Any, Callable, Literal, Optional, Type

import requests
from helpers.constants import (
    CALL_WINDOW_IN_SECOND,
    MAX_CALLS_PER_WINDOW,
    REQUESTS_BACKOFF_FACTOR,
    REQUESTS_RETRY_TIMES,
    REQUESTS_STATUS_FORCELIST,
    REQUESTS_TIMEOUT,
)
from requests.adapters import HTTPAdapter, Retry

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
    method: Literal["get", "options", "head", "post", "put", "patch", "delete"],
    url: str,
    **kwargs,
) -> Optional[requests.Response]:
    try:
        response = session.request(
            method=method.upper(),
            url=url,
            timeout=REQUESTS_TIMEOUT,
            **kwargs,
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
                    msg_with_retry = f"{msg}; Retrying in {backoff_time} seconds ({fn_call_count}/{retries})"
                    if is_not_last_call:
                        logger.error(msg_with_retry)
                        time.sleep(backoff_time)
                    else:
                        logger.error(msg)

            return None

        return wrapper

    return decorator


def rate_limit(
    max_calls_per_window: int = MAX_CALLS_PER_WINDOW,
    call_window: int = CALL_WINDOW_IN_SECOND,
) -> Callable:
    def decorator(fn: Callable) -> Callable:
        calls: list[float] = []

        @wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            def check_is_over_limit() -> tuple[bool, Optional[float]]:
                call_len = len(calls)
                if not call_len:
                    return False, None
                is_max_len = call_len >= max_calls_per_window
                delta_time = time.time() - calls[0]
                in_call_window = delta_time < call_window
                is_over_limit = is_max_len and in_call_window
                sleep_time = call_window - delta_time if is_over_limit else None
                return is_over_limit, sleep_time

            def add_to_limit() -> None:
                nonlocal calls
                calls = [*calls, time.time()][-max_calls_per_window:]

            is_over_limit, sleep_time = check_is_over_limit()
            if is_over_limit:
                time.sleep(sleep_time or 0)
            add_to_limit()
            return fn(*args, **kwargs)

        return wrapper

    return decorator
