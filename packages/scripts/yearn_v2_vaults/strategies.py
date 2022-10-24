import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from pandas.tseries.offsets import MonthEnd
from process_yearn_vision.main import CSV_DATE_FORMAT, fetch_yearn_vision
from process_yearn_vision.typings import NetworkStr


total_assets_expr = (
    '(yearn_vault{{network="{0}", param="totalAssets", experimental="false"}})'
)
token_price_expr = (
    '(yearn_vault{{network="{0}", param="token price", experimental="false"}})'
)

total_gain_expr = (
    '(yearn_strategy{{network="{0}", param="totalGain", experimental="false"}})'
)
total_loss_expr = (
    '(yearn_strategy{{network="{0}", param="totalLoss", experimental="false"}})'
)
total_debt_expr = (
    '(yearn_strategy{{network="{0}", param="totalDebt", experimental="false"}})'
)


def fetch_vault_values(expr, start_dt, end_dt):
    # get query expression
    exprs = {network: expr.format(network) for network in NetworkStr}
    result = fetch_yearn_vision(exprs, start_dt, end_dt)["results"]

    # parse query data
    data = []
    for network in result.keys():
        frames = result[network]["frames"]
        for frame in frames:
            vault = frame["schema"]["name"]
            address = frame["schema"]["fields"][1]["labels"]["address"]

            ts = frame["data"]["values"][0]
            values = frame["data"]["values"][1]
            values = pd.Series(values, index=ts)
            values.index = pd.to_datetime(values.index, unit='ms')

            # monthly samples
            values = values.resample('1M').last().dropna()
            values.name = (vault, address)
            data.append(values)

    data = pd.DataFrame(data).T
    data.index = pd.to_datetime(data.index, unit="ms")
    data.sort_index(inplace=True)
    return data


def fetch_strategy_values(expr, start_dt, end_dt):
    # get query expression
    exprs = {network: expr.format(network) for network in NetworkStr}
    result = fetch_yearn_vision(exprs, start_dt, end_dt)["results"]

    # parse query data
    data = []
    for network in result.keys():
        frames = result[network]["frames"]
        for frame in frames:
            vault = frame["schema"]["name"]
            strategy = frame['schema']['fields'][1]['labels']['strategy']
            address = frame["schema"]["fields"][1]["labels"]["address"]

            ts = frame["data"]["values"][0]
            values = frame["data"]["values"][1]
            values = pd.Series(values, index=ts)
            values.index = pd.to_datetime(values.index, unit='ms')

            # monthly samples
            values = values.resample('1M').last().dropna()
            values.name = (vault, strategy, address)
            data.append(values)

    data = pd.DataFrame(data).T
    data.index = pd.to_datetime(data.index, unit="ms")
    data.sort_index(inplace=True)
    return data


def main() -> None:
    file_dir = Path(__file__).parent.resolve()
    output_file_path = (
        file_dir / ".." / ".." / ".." / "data" / "yearn_v2_strategies.csv"
    )

    start_dt = datetime.strptime("01/12/2020", "%d/%m/%Y").replace(tzinfo=timezone.utc)
    end_dt = datetime.now(timezone.utc) + MonthEnd(-1)

    # fetch vault level data
    data_vault = [
        fetch_vault_values(total_assets_expr, start_dt, end_dt),
        fetch_vault_values(token_price_expr, start_dt, end_dt),
    ]

    # fetch strategy level data
    data_strat = [
        fetch_strategy_values(total_debt_expr, start_dt, end_dt),
        fetch_strategy_values(total_gain_expr, start_dt, end_dt),
        fetch_strategy_values(total_loss_expr, start_dt, end_dt),
    ]

    indices = set(data_strat[0].index).intersection(
        *[d.index for d in data_vault + data_strat]
    )

    # rearrange columns into fields
    output = []
    columns = set(data_strat[0].columns).intersection(*[d.columns for d in data_strat])
    for col in columns:
        vault_name, strategy_name, address = col
        chain = vault_name[-3:]

        total_assets = data_vault[0][vault_name]
        token_price = data_vault[1][vault_name]
        if vault_name == 'st-yCRV 0.4.3 - ETH':
            vault_address = "0x27B5739e22ad9033bcBf192059122d163b60349D"
        else:
            vault_address = total_assets.columns[0]

        for idx in indices:
            price = token_price[vault_address][idx]
            output.append(
                (
                    idx,
                    vault_name,
                    strategy_name,
                    chain,
                    address,
                    idx.strftime(CSV_DATE_FORMAT).lower(),
                    data_strat[0][col][idx],
                    data_strat[1][col][idx] - data_strat[2][col][idx],
                    total_assets[vault_address][idx],
                    data_strat[0][col][idx] * price,
                    (data_strat[1][col][idx] - data_strat[2][col][idx]) * price,
                    total_assets[vault_address][idx] * price,
                )
            )

    output = pd.DataFrame(
        output,
        columns=[
            "Timestamp",
            "Vault",
            "Strategy",
            "Chain",
            "Address",
            "Month",
            "TotalDebt",
            "TotalGain",
            "TotalAssets",
            "TotalDebtUSD",
            "TotalGainUSD",
            "TotalAssetsUSD",
        ],
    )

    # save output
    output.to_csv(output_file_path, index=False)


if __name__ == "__main__":
    main()
