from enum import Enum
import requests
import os
import time
import pandas as pd

YDAEMON = "https://ydaemon.yearn.finance"
BASE_URL = "https://yearn.vision"

url = f'{BASE_URL}/api/ds/query'
headers = {
    'Accept': 'application/json, text/plain, */*',
    'Content-Type': 'application/json',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache'
}
to_millis = int(time.time() * 1e3)
from_millis = int(to_millis - 365 * 24 * 60 * 60 * 1e3)


class Network(Enum):
    ETH = 1
    OPT = 10
    FTM = 250


def get_tvl(network, vault):
    query = f"""
        yearn_vault{{
            network=\"{network}\",
            param=\"tvl\",
            vault=~\"{vault}\",
            experimental=\"false\",
        }}
    """
    data = {
        "queries": [
            {
                "expr": query,
                "utcOffsetSec": 0,
                "datasourceId": 1
            }
        ],
        "from": str(from_millis), "to": str(to_millis)
    }
    with requests.Session() as session:
        response = session.post(
            url = url,
            headers = headers,
            json = data
        )
    result = response.json()['results']['A']['frames'][0]['data']['values']

    df = pd.DataFrame(result).T
    df.columns = ['timestamp', 'tvl']
    df.timestamp = pd.to_datetime(df.timestamp, unit='ms')   
    df.set_index('timestamp', inplace=True)
    df = df.resample('1M').last()
    return df

def get_debt_ratio(network, vault):
    query = f"""
        sum(
            yearn_strategy{{
                network=\"{network}\",
                param=\"totalDebt\",
                vault=~\"{vault}\",
                experimental=\"false\"
            }}
        ) / on(vault, version) sum(
            yearn_vault{{
                network=\"{network}\",
                param=\"totalAssets\",
                vault=~\"{vault}\",
                experimental=\"false\"
            }}
        )
    """
    data = {
        "queries": [
            {
                "expr": query,
                "utcOffsetSec": 0,
                "datasourceId": 1
            }
        ],
        "from": str(from_millis), "to": str(to_millis)
    }
    with requests.Session() as session:
        response = session.post(
            url = url,
            headers = headers,
            json = data
        )
    result = response.json()['results']['A']['frames'][0]['data']['values']

    df = pd.DataFrame(result).T
    df.columns = ['timestamp', 'debtRatio']
    df.timestamp = pd.to_datetime(df.timestamp, unit='ms')   
    df.set_index('timestamp', inplace=True)
    df = df.resample('1M').last()
    return df

def get_gain(network, vault):
    query = f"""
        (sum(
            yearn_strategy{{
                network=\"{network}\",
                param=\"totalGain\",
                vault=~\"{vault}\",
                experimental=\"false\"
            }}
        ) - sum(
                yearn_strategy{{
                    network=\"{network}\",
                    param=\"totalLoss\",
                    vault=~\"{vault}\",
                    experimental=\"false\"
                }}
        )) * yearn_vault{{
            network=\"{network}\",
            param=\"token price\",
            experimental=\"false\",
            vault=\"{vault}\"
        }}
    """
    data = {
        "queries": [
            {
                "expr": query,
                "utcOffsetSec": 0,
                "datasourceId": 1
            }
        ],
        "from": str(from_millis), "to": str(to_millis)
    }
    with requests.Session() as session:
        response = session.post(
            url = url,
            headers = headers,
            json = data
        )
    result = response.json()['results']['A']['frames'][0]['data']['values']

    df = pd.DataFrame(result).T
    df.columns = ['timestamp', 'totalGain']
    df.timestamp = pd.to_datetime(df.timestamp, unit='ms')
    df.set_index('timestamp', inplace=True)
    df = df.resample('1M').last()
    return df

def get_apy(network, vault):
    query = f"""
        yearn_vault{{
            network=\"{network}\",
            param=\"pricePerShare\",
            experimental=\"false\",
            vault=\"{vault}\"
        }}
    """
    data = {
        "queries": [
            {
                "expr": query,
                "utcOffsetSec": 0,
                "datasourceId": 1
            }
        ],
        "from": str(from_millis), "to": str(to_millis)
    }
    with requests.Session() as session:
        response = session.post(
            url = url,
            headers = headers,
            json = data
        )
    result = response.json()['results']['A']['frames'][0]['data']['values']

    df = pd.DataFrame(result).T
    df.columns = ['timestamp', 'apy']
    df.timestamp = pd.to_datetime(df.timestamp, unit='ms')
    df.set_index('timestamp', inplace=True)
    df = df.resample('1M').last()

    days = df.index.to_series().diff().dt.days
    df.apy = (df.apy.pct_change() + 1) ** (365.2425 / days) - 1
    return df


dfs, names = [], []
for network in Network:
    # fetch all DAI, USDT, USDC vaults in network
    vaults = requests.get(os.path.join(YDAEMON, str(network.value), "vaults", "all")).json()
    usd_vaults = [
        vault for vault in vaults
        if vault['display_name'] in ['DAI', "USDT", "USDC"]
    ]
    for vault in usd_vaults:
        # FIXME: find out why the versions have a mismatch
        if vault['version'] == "0.4.2":
            vault['version'] = "0.4.3"

    usd_vaults = [vault['symbol'] + ' ' + vault['version'] for vault in usd_vaults]
    for vault in usd_vaults:
        # fetch totalGain and TVL
        try:
            df = pd.concat([
                get_gain(network.name, vault),
                get_tvl(network.name, vault),
                get_debt_ratio(network.name, vault),
                get_apy(network.name, vault),
            ], axis=1)
        except:
            print(f"skipping {network.name} {vault}")
            continue
        df.name = network.name + ' ' + vault
        dfs.append(df)
        names.append(df.name)

data = pd.concat(dfs, axis=1, keys=names).fillna(0.0)
data.to_csv('../data/stablecoin_vision_individual.csv')
print(data)

dai_data = pd.concat([
    sum([data[col[0], 'totalGain'] for col in data.columns if 'DAI' in col[0]]),
    sum([data[col[0], 'tvl'] for col in data.columns if 'DAI' in col[0]]),
], axis=1)
dai_data.columns = ['totalGain', 'tvl']

usdt_data = pd.concat([
    sum([data[col[0], 'totalGain'] for col in data.columns if 'USDT' in col[0]]),
    sum([data[col[0], 'tvl'] for col in data.columns if 'USDT' in col[0]]),
], axis=1)
usdt_data.columns = ['totalGain', 'tvl']

usdc_data = pd.concat([
    sum([data[col[0], 'totalGain'] for col in data.columns if 'USDC' in col[0]]),
    sum([data[col[0], 'tvl'] for col in data.columns if 'USDC' in col[0]]),
], axis=1)
usdc_data.columns = ['totalGain', 'tvl']

data = pd.concat([dai_data, usdt_data, usdc_data], axis=1, keys=('DAI', 'USDT', 'USDC'))
data.to_csv('../data/stablecoin_vision_combined.csv')
print(data)
