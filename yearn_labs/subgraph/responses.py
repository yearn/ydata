from typing import Dict, Union
from yearn_labs.strategy import Strategy
from yearn_labs.vault import Vault, Token


def parse_vaults(result: Dict) -> Union[Vault, None]:
    if "vaults" not in result:
        return
    vaults = result["vaults"]
    if len(vaults) == 0:
        return

    result = []
    for vault in vaults:
        address = vault["id"]
        name = vault["shareToken"]["name"]

        _token = vault["token"]
        token = Token(
            address=_token["id"],
            decimals=_token["decimals"],
            name=_token["name"],
            symbol=_token["symbol"],
        )
        strategies = [
            Strategy(
                address=strat["id"],
                name=strat["name"],
            )
            for strat in vault["strategies"]
        ]
        result.append(Vault(address, name, token, strategies))
    return result


def parse_strategies(result: Dict) -> Union[Strategy, None]:
    if "strategies" not in result:
        return
    strategies = result["strategies"]
    if len(strategies) == 0:
        return

    result = []
    for strategy in strategies:
        address = strategy["id"]
        name = strategy["name"]
        result.append(Strategy(address, name))
    return result
