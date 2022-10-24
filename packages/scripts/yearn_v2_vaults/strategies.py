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

share_price_expr = (
    '(yearn_vault{{network="{0}", param="pricePerShare", experimental="false"}})'
)
tvl_expr = '(yearn_vault{{network="{0}", param="tvl", experimental="false"}})'


def fetch_apy(start_dt, end_dt):
    # get query expression
    expr = {network: share_price_expr.format(network) for network in NetworkStr}
    result = fetch_yearn_vision(expr, start_dt, end_dt)["results"]

    # parse query data
    data = []
    for network in result.keys():
        frames = result[network]["frames"]
        for frame in frames:
            vault = frame["schema"]["name"]
            address = frame["schema"]["fields"][1]["labels"]["address"]

            ts = frame["data"]["values"][0]
            prices = frame["data"]["values"][1]

            # detect change in share price
            prices = pd.Series(prices, index=ts)
            prices.index = pd.to_datetime(prices.index, unit="ms")
            prices = prices[prices.diff() > 0]

            # monthly samples
            prices = prices.resample("1M").last().dropna()
            days = prices.index.to_series().diff().dt.days
            apys = (1 + prices.pct_change()) ** (365.2425 / days) - 1

            apys.name = (vault, address)
            data.append(apys)

    data = pd.DataFrame(data).T
    data.index = pd.to_datetime(data.index, unit="ms")
    data.sort_index(inplace=True)
    data.dropna(axis=0, how="all", inplace=True)
    data = data.ffill().where(data.bfill().notna())
    return data


def fetch_tvl(start_dt, end_dt):
    # get query expression
    expr = {network: tvl_expr.format(network) for network in NetworkStr}
    result = fetch_yearn_vision(expr, start_dt, end_dt)["results"]

    # parse query data
    data = []
    for network in result.keys():
        frames = result[network]["frames"]
        for frame in frames:
            vault = frame["schema"]["name"]
            address = frame["schema"]["fields"][1]["labels"]["address"]

            ts = frame["data"]["values"][0]
            tvls = frame["data"]["values"][1]
            tvls = pd.Series(tvls, index=ts)
            tvls.index = pd.to_datetime(tvls.index, unit="ms")

            # monthly samples
            tvls = tvls.resample('1M').last().dropna()

            tvls.name = (vault, address)
            data.append(tvls)

    data = pd.DataFrame(data).T
    data.index = pd.to_datetime(data.index, unit="ms")
    data.sort_index(inplace=True)
    data.dropna(axis=0, how="all", inplace=True)
    data = data.ffill().where(data.bfill().notna())
    return data


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
    vault_info_file_path = file_dir / ".." / "vault_info.json"

    start_dt = datetime.strptime("01/12/2020", "%d/%m/%Y").replace(tzinfo=timezone.utc)
    end_dt = datetime.now(timezone.utc) + MonthEnd(-1)

    # get vault info
    with open(vault_info_file_path, "r") as f:
        vault_info = json.load(f)

    # fetch vault level data
    data_vault = [
        fetch_vault_values(total_assets_expr, start_dt, end_dt),
        fetch_vault_values(token_price_expr, start_dt, end_dt),
        fetch_apy(start_dt, end_dt),
        fetch_tvl(start_dt, end_dt),
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

        vault_debt = data_strat[0][vault_name].sum(axis=1)
        if vault_debt[-1] == 0:
            continue

        total_assets = data_vault[0][vault_name]
        token_price = data_vault[1][vault_name]
        vault_apy = data_vault[2][vault_name]
        vault_tvl = data_vault[3][vault_name]
        if vault_name == 'st-yCRV 0.4.3 - ETH':
            vault_address = "0x27B5739e22ad9033bcBf192059122d163b60349D"
        else:
            vault_address = total_assets.columns[0]
        vault_gain = (data_strat[1][vault_name] - data_strat[2][vault_name]).sum(axis=1)
        vault_type = vault_info.get(vault_name, {}).get("assetType", "Other")

        for idx in indices:
            price = token_price[vault_address][idx]
            total_debt = data_strat[0][col][idx]
            net_gain = (data_strat[1][col] - data_strat[2][col]).diff()[idx]
            if total_debt == 0:
                strat_apy = 0.0
            else:
                strat_apy = net_gain / total_debt

            output.append(
                (
                    idx,
                    vault_name,
                    strategy_name,
                    chain,
                    address,
                    idx.strftime(CSV_DATE_FORMAT).lower(),
                    # vault info
                    vault_type,
                    vault_apy[vault_address][idx],
                    vault_tvl[vault_address][idx],
                    # strategy apy
                    strat_apy,
                    # amounts in WANT
                    total_debt,
                    data_strat[1][col][idx] - data_strat[2][col][idx],
                    vault_gain[idx],
                    total_assets[vault_address][idx],
                    # amounts in USD
                    total_debt * price,
                    (data_strat[1][col][idx] - data_strat[2][col][idx]) * price,
                    vault_gain[idx] * price,
                    total_assets[vault_address][idx] * price,
                    # monthly diffs
                    net_gain,
                    vault_gain.diff()[idx],
                    net_gain * price,
                    vault_gain.diff()[idx] * price,
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

            "Type",
            "VaultAPY",
            "VaultTVL",

            "StratAPY",

            "TotalDebt",
            "TotalGainStrat",
            "TotalGainVault",
            "TotalAssets",

            "TotalDebtUSD",
            "TotalGainStratUSD",
            "TotalGainVaultUSD",
            "TotalAssetsUSD",

            "MonthlyGainStrat",
            "MonthlyGainVault",
            "MonthlyGainStratUSD",
            "MonthlyGainVaultUSD",
        ],
    )

    # save output
    output.to_csv(output_file_path, index=False)


if __name__ == "__main__":
    main()
