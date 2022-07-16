import logging
from typing import Optional

import brownie

brownie._config.CONFIG.settings["autofetch_sources"] = True

from ypricemagic.magic import magic

from src.utils.network import rate_limit, retry

logging.getLogger("dank_mids").setLevel(logging.WARN)
logging.getLogger("y.prices").setLevel(logging.WARN)
logging.getLogger("y.prices.lending.compound").setLevel(logging.WARN)
logging.getLogger("y.prices.dex.uniswap.v2").setLevel(logging.WARN)


@rate_limit()
@retry()
def get_price(token_address: str, block: int) -> Optional[float]:
    return magic.get_price(token_address, block, fail_to_None=True, silent=False)
