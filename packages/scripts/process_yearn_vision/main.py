import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Optional, Union

import pandas as pd
from expressions import (
    gen_aum_expr,
    gen_share_price_expr,
    gen_total_debt_expr,
    gen_total_gains_expr,
)

from helpers.constants import Network
from helpers.web3 import Web3Provider
from process_yearn_vision.queries import parse_strategy_exprs, parse_vault_exprs
from process_yearn_vision.typings import NetworkStr, QueryResultMap, VaultInfo
from process_yearn_vision.utils.common import (
    append_csv_rows,
    get_start_and_end_of_month,
    get_start_datetime,
    to_timestamp,
    update_csv,
)
from process_yearn_vision.utils.yearn import (
    get_delegated_assets,
    get_vault,
    timestamp_to_block,
)

CSV_DATE_FORMAT = "%b/%y"

network_mapping = {
    NetworkStr.Mainnet: Network.Mainnet,
    NetworkStr.Fantom: Network.Fantom,
}


def make_update_cum_share_price_cb() -> Callable[[int, list[str]], list]:
    name_index: Optional[int] = None
    price_index: Optional[int] = None
    cum_price_index: Optional[int] = None
    cum_price_dict: dict[str, float] = {}

    def update_cum_share_price_cb(line_num: int, row: list[str]) -> list:
        nonlocal name_index
        nonlocal price_index
        nonlocal cum_price_index
        nonlocal cum_price_dict

        if line_num == 0:
            name_index = row.index("Vault")
            price_index = row.index("Month Return (%)")
            cum_price_index = row.index("Cumulative Return (%)")
        else:
            if name_index is None or price_index is None or cum_price_index is None:
                raise ValueError("Header indexes not found")
            name = row[name_index or 0]
            price = float(row[price_index])
            cum_price = cum_price_dict.get(name)
            cum_price_dict[name] = (
                price if cum_price is None else (1 + cum_price) * (1 + price) - 1
            )
            row[cum_price_index] = str(cum_price_dict[name])
        return row

    return update_cum_share_price_cb


def make_update_asset_type_cb(
    vault_info_file_path: Path,
) -> Callable[[int, list[str]], list]:
    vault_info: dict[str, VaultInfo]
    with open(vault_info_file_path, "r") as f:
        vault_info = json.load(f)
    name_index: Optional[int] = None
    type_index: Optional[int] = None

    def update_asset_type_cb(line_num: int, row: list[str]) -> list:
        nonlocal name_index
        nonlocal type_index

        if line_num == 0:
            name_index = row.index("Vault")
            type_index = row.index("Type")
        else:
            if name_index is None or type_index is None:
                raise ValueError("Header indexes not found")
            name = row[name_index]
            asset_type = vault_info.get(name, {}).get("assetType", "Other")
            row[type_index] = asset_type
        return row

    return update_asset_type_cb


def get_aum_size(aum: Union[int, float]) -> str:
    if aum < 10_000_000:
        return "Under $10 million"
    if aum >= 10_000_000 and aum <= 50_000_000:
        return "Between $10 million and $50 million"
    if aum > 50_000_000:
        return "Over $50 million"
    return ""


def parse_data_and_append_csv(
    parsed_query_results: list[dict[str, QueryResultMap]],
    dates: list[tuple[pd.Timestamp, pd.Timestamp]],
    output_file_path: Path,
) -> None:
    arr = []
    for month_start, month_end in dates:
        month_start_ts = to_timestamp(month_start.to_pydatetime())
        month_end_ts = to_timestamp(month_end.to_pydatetime())

        price_data = parsed_query_results[0]
        aum_data = parsed_query_results[1]
        debt_data = parsed_query_results[2]
        gains_data = parsed_query_results[3]

        for name, price_query_result_map in price_data.items():
            network_str = price_query_result_map["network"]
            address = price_query_result_map["address"]
            price_values = price_query_result_map["values"]
            aum_values = aum_data.get(name, {}).get("values", {})
            debt_values = debt_data.get(name, {}).get("values", {})
            gains_values = gains_data.get(name, {}).get("values", {})

            price = 0
            price_start = price_values.get(month_start_ts)
            price_end = price_values.get(month_end_ts)
            if price_start is not None and price_end is not None:
                price = (price_end / price_start) - 1

            aum = 0
            if aum_end := aum_values.get(month_end_ts):
                aum = aum_end

            debt = 0
            if debt_end := debt_values.get(month_end_ts):
                network_int = network_mapping[network_str]
                vault = get_vault(address, network_int)
                w3 = Web3Provider(network_int)
                block = timestamp_to_block(w3, month_end_ts // 10**3)
                delegated_assets = get_delegated_assets(w3, vault, block)
                debt = max(debt_end - delegated_assets, 0)

            gains = 0
            if gains_end := gains_values.get(month_end_ts):
                gains = gains_end

            row = []
            row.append(name)  # Vault
            row.append(network_str)  # Chain
            row.append("Other")  # Type
            row.append(f"{month_end.strftime(CSV_DATE_FORMAT).lower()}")  # Month
            row.append(f"{price}")  # Month Return (%)
            row.append(f"{0}")  # Cumulative Return (%)
            row.append(f"{aum}")  # AUM ($)
            row.append(get_aum_size(aum))  # AUM Size
            row.append(f"{debt}")  # Total Debt
            row.append(f"{gains}")  # Total Gains
            arr.append(row)

    append_csv_rows(output_file_path, arr)


def main() -> None:
    file_dir = Path(__file__).parent.resolve()
    output_file_path = file_dir / ".." / ".." / ".." / "data" / "output.csv"
    vault_info_file_path = file_dir / "vault_info.json"

    # Getting the start datetime will require looping all rows in csv file to get the last row
    start_dt = get_start_datetime(output_file_path)
    end_dt = datetime.now(timezone.utc)
    dates = get_start_and_end_of_month(start_dt, end_dt)

    # Vault-level results
    exprs = [gen_share_price_expr, gen_aum_expr, gen_total_debt_expr]
    vault_query_results = parse_vault_exprs(exprs, start_dt, end_dt)

    # Strategy-level queries parsed to vault-level results
    exprs = [gen_total_gains_expr]
    vaults = list(vault_query_results[0].keys())
    strategy_query_results = parse_strategy_exprs(exprs, vaults, start_dt, end_dt)

    # Process and append data to the csv file
    vault_query_results.extend(strategy_query_results)
    parse_data_and_append_csv(vault_query_results, dates, output_file_path)

    # Loop all rows in csv file again to update other data
    update_asset_type_cb = make_update_asset_type_cb(vault_info_file_path)
    update_cum_share_price_cb = make_update_cum_share_price_cb()
    cbs = [update_asset_type_cb, update_cum_share_price_cb]
    update_csv(output_file_path, cbs)


if __name__ == "__main__":
    main()
