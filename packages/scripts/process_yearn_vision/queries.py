from datetime import datetime
from typing import Any, Callable, Optional

from helpers.network import client
from process_yearn_vision.typings import NetworkStr, QueryResult, QueryResultMap
from process_yearn_vision.utils.common import to_timestamp


def gen_json_body(
    expr: dict[NetworkStr, str], start_dt: datetime, end_dt: datetime
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
        "from": f"{to_timestamp(start_dt)}",
        "to": f"{to_timestamp(end_dt)}",
    }


def gen_headers() -> dict[str, str]:
    return {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }


def fetch_yearn_vision(
    expr: dict[NetworkStr, str],
    start_dt: datetime,
    end_dt: datetime,
) -> Optional[QueryResult]:
    headers = gen_headers()
    data = gen_json_body(expr, start_dt, end_dt)

    res = client(
        "post", "https://yearn.vision/api/ds/query", headers=headers, json=data
    )
    if res:
        return res.json()
    return None


def parse_query_results(
    query_results: list[QueryResult],
) -> list[dict[str, QueryResultMap]]:
    arr = []
    for query_result in query_results:
        _dict = {}
        for network_str, frames in query_result["results"].items():
            for frame in frames["frames"]:
                name = frame["schema"]["name"]
                try:
                    address = list(
                        filter(
                            lambda i: i.get("labels", {}).get("address"),
                            frame["schema"]["fields"],
                        )
                    )[0]["labels"]["address"]
                except IndexError:
                    continue
                timestamps, prices = frame["data"]["values"]
                _dict[name] = {
                    "name": name,
                    "network": network_str,
                    "address": address,
                    "values": {},
                }

                for timestamp, price in zip(timestamps, prices):
                    _dict[name]["values"][timestamp] = price
        arr.append(_dict)
    return arr


def parse_vault_exprs(
    gen_expr_cbs: list[Callable[[], dict[NetworkStr, str]]],
    start_dt: datetime,
    end_dt: datetime,
) -> list[dict[str, QueryResultMap]]:
    arr: list[Optional[QueryResult]] = []
    for gen_expr_cb in gen_expr_cbs:
        expr = gen_expr_cb()
        data = fetch_yearn_vision(expr, start_dt, end_dt)
        arr.append(data)
    filtered: list[QueryResult] = list(filter(lambda i: i is not None, arr))
    return parse_query_results(filtered)


def merge_query_result_map(
    query_result_maps: list[dict[str, QueryResultMap]]
) -> dict[str, QueryResultMap]:
    _dict: dict[str, QueryResultMap] = {}
    for query_result_dict in query_result_maps:
        for name, query_result_map in query_result_dict.items():
            _dict[name] = query_result_map
    return _dict


def parse_strategy_exprs(
    gen_expr_cbs: list[Callable[[str], dict[NetworkStr, str]]],
    vaults: list[str],
    start_dt: datetime,
    end_dt: datetime,
) -> list[dict[str, QueryResultMap]]:
    merged_arr: list[dict[str, QueryResultMap]] = []
    vault_networks = list(map(lambda i: i.split(" - "), vaults))
    for gen_expr_cb in gen_expr_cbs:
        arr: list[Optional[QueryResult]] = []

        for vault, _ in vault_networks:
            expr = gen_expr_cb(vault)
            data = fetch_yearn_vision(expr, start_dt, end_dt)
            arr.append(data)
        filtered: list[QueryResult] = list(filter(lambda i: i is not None, arr))
        parsed_query_results = parse_query_results(filtered)
        merged_query_result_map = merge_query_result_map(parsed_query_results)
        merged_arr.append(merged_query_result_map)
    return merged_arr
