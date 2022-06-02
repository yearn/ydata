import json
import logging
from http import HTTPStatus
from typing import Any, Literal, Optional

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
    total=3,
    backoff_factor=2,
    status_forcelist=[429, 500, 502, 503, 504],
)

session = requests.Session()

adapter = HTTPAdapter(max_retries=retry_strategy)

session.mount("https://", adapter)
session.mount("http://", adapter)


def client(
    method: Literal['get', 'options', 'head', 'post', 'put', 'patch', 'delete'],
    url: str,
    *args,
    **kwargs,
) -> Optional[requests.Response]:
    try:
        response = session.request(
            method=method.upper(), url=url, timeout=5, *args, **kwargs
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


def parse_json(response: Optional[requests.Response]) -> Optional[Any]:
    if response is None or response.status_code != HTTPStatus.OK:
        return None
    try:
        return response.json()
    except json.decoder.JSONDecodeError as err:
        logger.error(f"JSON decode error: {err}")
    return None
