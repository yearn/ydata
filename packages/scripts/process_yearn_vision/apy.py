import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Optional

import pandas as pd
from expressions import gen_share_price_expr

from process_yearn_vision.queries import parse_vault_exprs
from process_yearn_vision.typings import QueryResultMap, VaultInfo
from process_yearn_vision.utils.common import (
    CSV_DATE_FORMAT,
    append_csv_rows,
    get_start_and_end_of_month,
    get_start_datetime,
    to_timestamp,
    update_csv,
)


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

        for name, price_query_result_map in price_data.items():
            network_str = price_query_result_map["network"]
            price_values = price_query_result_map["values"]

            apy = 0
            price_start = price_values.get(month_start_ts)
            price_end = price_values.get(month_end_ts)
            if price_start is not None and price_end is not None:
                days = (month_end - month_start).days
                apy = (price_end / price_start) ** (365.2425 / days) - 1

            row = []
            row.append(name)  # Vault
            row.append(network_str)  # Chain
            row.append("Other")  # Type
            row.append(f"{month_end.strftime(CSV_DATE_FORMAT).lower()}")  # Month
            row.append(f"{apy}")  # APY (%)
            arr.append(row)

    append_csv_rows(output_file_path, arr)


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


def main() -> None:
    file_dir = Path(__file__).parent.resolve()
    output_file_path = file_dir / ".." / ".." / ".." / "data" / "apy.csv"
    vault_info_file_path = file_dir / "vault_info.json"

    # Getting the start datetime will require looping all rows in csv file to get the last row
    start_dt = get_start_datetime(output_file_path)
    end_dt = datetime.now(timezone.utc)
    dates = get_start_and_end_of_month(start_dt, end_dt)

    # Vault-level results
    exprs = [gen_share_price_expr]
    vault_query_results = parse_vault_exprs(exprs, start_dt, end_dt)

    # Process and append data to the csv file
    parse_data_and_append_csv(vault_query_results, dates, output_file_path)

    # Loop all rows in csv file again to update other data
    update_asset_type_cb = make_update_asset_type_cb(vault_info_file_path)
    update_csv(output_file_path, [update_asset_type_cb])


if __name__ == "__main__":
    main()
