import requests
import logging

logger = logging.getLogger(__name__)

EXCLUDE = [
    "Token Contract",
    "Proxy Contract",
    "Blocked",
    "Wrapped",
    "Bitfinex",  # USDT
]
HEADERS = {
    'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X x.y; rv:42.0) Gecko/20100101 Firefox/43.4"
}


def get_labels(address: str):
    endpoint = "https://etherscan.io/address/"
    url = endpoint + address
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        logger.debug(f"Failed to get labels from address={address}")
        response.raise_for_status()
    text = response.text

    labels = []
    while True:
        try:
            text = text[text.index("/accounts/label/") :]
            text = text[text.index(">") + 1 :]
            label = text[: text.index("<")].strip()
            if label not in EXCLUDE:
                labels.append(label)
        except:
            break
    return labels
