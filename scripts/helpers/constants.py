from enum import IntEnum


class Network(IntEnum):
    Mainnet = 1
    Optimism = 10
    Fantom = 250
    Arbitrum = 42161


REQUESTS_RETRY_TIMES = 5
REQUESTS_BACKOFF_FACTOR = 2
REQUESTS_STATUS_FORCELIST = [429, 500, 502, 503, 504]

REQUESTS_TIMEOUT = 10  # seconds

MAX_CALLS_PER_WINDOW = 4
CALL_WINDOW_IN_SECOND = 2
