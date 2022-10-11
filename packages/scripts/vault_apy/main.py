import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from helpers.constants import Network
from helpers.network import client, parse_json
from helpers.web3 import Web3Provider

CSV_DATE_FORMAT = "%b/%y"
YDAEMON = "https://ydaemon.yearn.finance/{0}/vaults/all"

NETWORK_NAME = {
    Network.Mainnet: "ETH",
    Network.Fantom: "FTM",
    Network.Optimism: "OPT",
    Network.Arbitrum: "ARB",
}


def main() -> None:
    file_dir = Path(__file__).parent.resolve()
    output_file_path = file_dir / ".." / ".." / ".." / "data" / "apy.csv"
    vault_info_file_path = file_dir / ".." / "vault_info.json"

    data = pd.read_csv(output_file_path, index_col=0)
    if len(data) == 0:
        start_dt = datetime.strptime("01/12/2020", "%d/%m/%Y").replace(
            tzinfo=timezone.utc
        )
    else:
        data.index = data.index.to_series().apply(pd.to_datetime)
        start_dt = (data.index[-1] + timedelta(days=40)).replace(day=1)
    end_dt = datetime.now(timezone.utc)
    dt_rng = pd.date_range(start_dt, end_dt, freq="MS", tz=timezone.utc)

    # fetch vault info
    vaults = {
        network: parse_json(client("get", YDAEMON.format(network.value)))
        for network in Network
    }
    with open(vault_info_file_path, "r") as f:
        vaults["info"] = json.load(f)

    # fetch web3 providers
    w3_providers = {network: Web3Provider(network) for network in Network}

    # collect share prices
    for dt in dt_rng:
        for network in Network:
            w3 = w3_providers[network]
            network_name = NETWORK_NAME[network]

            try:
                block = w3.get_closest_block(dt)
            except ValueError:
                continue

            for vault in vaults[network]:
                inception = vault["inception"]
                if dt.value / 1e9 < inception:
                    continue

                vault_id = " ".join(
                    [vault["symbol"], vault["version"], "- {}".format(network_name)]
                )
                share_price = w3.call(vault["address"], "pricePerShare", block=block)
                share_price /= 10 ** vault["decimals"]

                row = pd.DataFrame(
                    [
                        [
                            vault_id,  # Vault
                            network_name,  # Chain
                            vaults["info"]
                            .get(vault_id, {})
                            .get("assetType", "Other"),  # Type
                            dt.strftime(CSV_DATE_FORMAT).lower(),  # Month
                            share_price,  # SharePrice
                            np.nan,  # APY
                        ]
                    ],
                    index=[dt],
                    columns=data.columns,
                )
                if len(data) == 0:
                    data = row
                else:
                    data = pd.concat([data, row], axis=0)

    # calculate apy from monthly data
    data.columns = ["Vault", "Chain", "Type", "Month", "SharePrice", "APY"]
    data.index.name = "Timestamp"
    for vault_name, df in data.groupby("Vault"):
        days = df.index.to_series().diff().dt.days
        df.APY = (1 + df.SharePrice.pct_change()) ** (365.2425 / days) - 1
        data.loc[data.Vault == vault_name] = df

    # save output
    data.to_csv(output_file_path)


if __name__ == "__main__":
    main()
