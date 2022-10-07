from decimal import Decimal
from typing import Optional

from helpers.constants import Network
from helpers.network import client, parse_json
from helpers.web3 import Web3Provider
from process_yearn_vision.typings import Address, Block, Vault
from web3 import exceptions


def get_vault(vault_address: Address, network: Network) -> Optional[Vault]:
    ydaemon = "https://ydaemon.yearn.finance"
    endpoint = f"{ydaemon}/{network}/vaults/{vault_address}"
    response = client("get", endpoint)
    vault: Optional[Vault] = parse_json(response)
    return vault


def get_delegated_assets(w3: Web3Provider, vault: Vault, block: int) -> float:
    strategies = vault["strategies"]
    token_denom = Decimal(10 ** vault["token"]["decimals"])
    delegatedAssets = Decimal(0)

    for strategy in strategies:
        try:
            asset = w3.call(strategy["address"], "delegatedAssets", block=block)
            asset = Decimal(asset) if asset else Decimal(0)
        except (exceptions.BadFunctionCallOutput, ValueError):
            asset = Decimal(0)
        delegatedAssets += asset
    delegatedAssets /= token_denom
    return float(delegatedAssets)


def timestamp_to_block(
    w3: Web3Provider,
    ts: int,
    left_block: Optional[Block] = None,
    right_block: Optional[Block] = None,
) -> int:
    left_block = left_block if left_block else w3.provider.eth.get_block("earliest")
    right_block = right_block if right_block else w3.provider.eth.get_block("latest")
    earliest_block_num = left_block["number"]
    earliest_ts = left_block["timestamp"]
    latest_block_num = right_block["number"]
    latest_ts = right_block["timestamp"]

    if earliest_block_num == latest_block_num:
        return earliest_block_num
    # Return the closer one, if we're already between blocks
    if (
        earliest_block_num == latest_block_num - 1
        or ts <= earliest_ts
        or ts >= latest_ts
    ):
        return (
            earliest_block_num
            if abs(ts - earliest_ts) < abs(ts - latest_ts)
            else latest_block_num
        )

    # K is how far in between left and right we're expected to be
    k = (ts - earliest_ts) / (latest_ts - earliest_ts)
    # We are ensured logarithmic time even when guesses aren't great
    k = min(max(k, 0.05), 0.95)
    # We get the expected block number from K
    expected_block = round(
        earliest_block_num + k * (latest_block_num - earliest_block_num)
    )
    # Make sure to make some progress
    expected_block = min(
        max(expected_block, earliest_block_num + 1), latest_block_num - 1
    )

    # Get the actual timestamp for that block
    expected_block_timestamp = w3.provider.eth.get_block(expected_block)["timestamp"]

    # Adjust bound using our estimated block
    if expected_block_timestamp < ts:
        earliest_block_num = expected_block
        earliest_ts = expected_block_timestamp
    elif expected_block_timestamp > ts:
        latest_block_num = expected_block
        latest_ts = expected_block_timestamp
    else:
        # Return the perfect match
        return expected_block

    # Recurse using tightened bounds
    return timestamp_to_block(
        w3,
        ts,
        {"number": earliest_block_num, "timestamp": earliest_ts},
        {"number": latest_block_num, "timestamp": latest_ts},
    )
