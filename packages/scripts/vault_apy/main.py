import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from pandas.tseries.offsets import MonthEnd
from process_yearn_vision.main import CSV_DATE_FORMAT, fetch_yearn_vision
from process_yearn_vision.typings import NetworkStr

share_price_expr = (
    '(yearn_vault{{network="{0}", param="pricePerShare", experimental="false"}})'
)


def main() -> None:
    file_dir = Path(__file__).parent.resolve()
    output_file_path = file_dir / ".." / ".." / ".." / "data" / "apy.csv"
    vault_info_file_path = file_dir / ".." / "vault_info.json"

    start_dt = datetime.strptime("01/12/2020", "%d/%m/%Y").replace(tzinfo=timezone.utc)
    end_dt = datetime.now(timezone.utc) + MonthEnd(-1)

    # fetch yearn vision
    expr = {network: share_price_expr.format(network) for network in NetworkStr}
    result = fetch_yearn_vision(expr, start_dt, end_dt)["results"]

    # get vault info
    with open(vault_info_file_path, "r") as f:
        vault_info = json.load(f)

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

    # rearrange columns into fields
    output = []
    for vault_name, address in data.columns:
        chain = vault_name[-3:]
        vault_type = vault_info.get(vault_name, {}).get("assetType", "Other")
        for idx in data.index:
            output.append(
                (
                    idx,
                    vault_name,
                    chain,
                    address,
                    vault_type,
                    idx.strftime(CSV_DATE_FORMAT).lower(),
                    data[vault_name, address].loc[idx],
                )
            )
    output = pd.DataFrame(
        output,
        columns=["Timestamp", "Vault", "Chain", "Address", "Type", "Month", "APY"],
    )

    # save output
    output.to_csv(output_file_path, index=False)


if __name__ == "__main__":
    main()
