import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated, Any, Callable, Optional, Union

import pandas as pd

from scripts.process_yearn_vision.typings import (
    NetworkStr,
    QueryResult,
    QueryResultMap,
    VaultInfo,
)
from scripts.process_yearn_vision.util import (
    add_months,
    append_csv_rows,
    get_csv_row,
    get_start_and_end_of_month,
    to_timestamp,
    update_csv,
)
from src.utils.network import client

CSV_DATE_FORMAT = "%b/%y"


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
                raise ValueError('Header indexes not found')
            name = row[name_index or 0]
            price = float(row[price_index])
            cum_price = cum_price_dict.get(name)
            cum_price_dict[name] = price if cum_price is None else cum_price + price
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
                raise ValueError('Header indexes not found')
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
    parsed_query_results: Annotated[list[dict[str, QueryResultMap]], 2],
    dates: list[tuple[pd.Timestamp, pd.Timestamp]],
    output_file_path: Path,
) -> None:
    arr = []
    for month_start, month_end in dates:
        month_start_ts = to_timestamp(month_start.to_pydatetime())
        month_end_ts = to_timestamp(month_end.to_pydatetime())

        price_data = parsed_query_results[0]
        aum_data = parsed_query_results[1]

        for name, price_query_result_map in price_data.items():

            aum_query_result_map = aum_data.get(name)
            if not aum_query_result_map:
                continue

            network = price_query_result_map["network"]
            price_values = price_query_result_map["values"]
            aum_values = aum_query_result_map["values"]

            price = 0
            price_start = price_values.get(month_start_ts)
            price_end = price_values.get(month_end_ts)
            if price_start is not None and price_end is not None:
                price = (price_end / price_start) - 1

            aum = 0
            if aum_end := aum_values.get(month_end_ts):
                aum = aum_end

            date = f"{month_end.strftime(CSV_DATE_FORMAT).lower()}"
            row = [name, network, "Other", date, price, 0, aum, get_aum_size(aum)]
            arr.append(row)

    append_csv_rows(output_file_path, arr)


def parse_query_results(
    query_results: list[QueryResult],
) -> Annotated[list[dict[str, QueryResultMap]], 2]:
    arr = []
    for query_result in query_results:
        _dict = {}
        for networkStr, frames in query_result["results"].items():
            for frame in frames["frames"]:
                name = frame["schema"]["name"]
                timestamps, prices = frame["data"]["values"]
                _dict[name] = {"name": name, "network": networkStr, "values": {}}

                for timestamp, price in zip(timestamps, prices):
                    _dict[name]["values"][timestamp] = price
        arr.append(_dict)
    return arr


def gen_json_body(
    expr: dict[NetworkStr, str], start_datetime: datetime, end_datetime: datetime
) -> dict[str, Any]:
    return {
        "queries": [
            {
                "expr": expr[NetworkStr.Mainnet],
                "legendFormat": f"{{{{vault}}}} - {NetworkStr.Mainnet}",
                "refId": NetworkStr.Mainnet,
                "utcOffsetSec": 0,
                "datasourceId": 1,
                "intervalMs": 86400000,  # 1 day
                "maxDataPoints": 2000,
            },
            {
                "expr": expr[NetworkStr.Fantom],
                "legendFormat": f"{{{{vault}}}} - {NetworkStr.Fantom}",
                "refId": NetworkStr.Fantom,
                "utcOffsetSec": 0,
                "datasourceId": 1,
                "intervalMs": 86400000,  # 1 day
                "maxDataPoints": 2000,
            },
        ],
        "from": f"{to_timestamp(start_datetime)}",
        "to": f"{to_timestamp(end_datetime)}",
    }


def gen_headers() -> dict[str, str]:
    return {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }


def fetch_yearn_vision(
    expr: dict[NetworkStr, str], start_datetime: datetime, end_datetime: datetime
) -> Optional[QueryResult]:
    headers = gen_headers()
    data = gen_json_body(expr, start_datetime, end_datetime)

    res = client(
        "post", "https://yearn.vision/api/ds/query", headers=headers, json=data
    )
    if res:
        return res.json()
    return None


def get_start_datetime(output_file_path: Path) -> datetime:
    header = get_csv_row(output_file_path, 0)
    date_index = header.index("Month")
    last_row = get_csv_row(output_file_path, -1)
    try:
        naive_dt = datetime.strptime(last_row[date_index], CSV_DATE_FORMAT)
        return add_months(naive_dt.replace(tzinfo=timezone.utc), 1)
    except ValueError:
        return datetime.strptime("01/12/2020", "%d/%m/%Y").replace(tzinfo=timezone.utc)


def main() -> None:
    file_dir = Path(__file__).parent.resolve()
    output_file_path = file_dir / "output.csv"
    vault_info_file_path = file_dir / "vault_info.json"

    share_price_expr = {
        NetworkStr.Mainnet: "yearn_vault{param=\"pricePerShare\", experimental=\"false\", network=\"ETH\"}",
        NetworkStr.Fantom: "yearn_vault{param=\"pricePerShare\", experimental=\"false\", network=\"FTM\"}",
    }
    aum_expr = {
        NetworkStr.Mainnet: "yearn_vault{param=\"tvl\", experimental=\"false\", network=\"ETH\"}",
        NetworkStr.Fantom: "yearn_vault{param=\"tvl\", experimental=\"false\", network=\"FTM\"}",
    }

    start_datetime = get_start_datetime(output_file_path)
    end_datetime = datetime.now(timezone.utc)

    price_data = fetch_yearn_vision(share_price_expr, start_datetime, end_datetime)
    aum_data = fetch_yearn_vision(aum_expr, start_datetime, end_datetime)
    dates = get_start_and_end_of_month(start_datetime, end_datetime)

    if price_data and aum_data:
        parsed_query_results = parse_query_results([price_data, aum_data])
        parse_data_and_append_csv(parsed_query_results, dates, output_file_path)

    update_asset_type_cb = make_update_asset_type_cb(vault_info_file_path)
    update_cum_share_price_cb = make_update_cum_share_price_cb()
    cbs = [update_asset_type_cb, update_cum_share_price_cb]
    update_csv(output_file_path, cbs)


if __name__ == "__main__":
    main()
