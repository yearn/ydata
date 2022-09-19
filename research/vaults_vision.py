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


def get_total_assets(network, vault):
    query = f"""
        yearn_vault{{
            network=\"{network}\",
            param=\"totalAssets\",
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
    df.columns = ['timestamp', 'totalAssets']
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
        ) / sum(
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

def get_total_gain(network, vault):
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
        ))
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

def get_token_price(network, vault):
    query = f"""
        yearn_vault{{
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
    df.columns = ['timestamp', 'tokenPrice']
    df.timestamp = pd.to_datetime(df.timestamp, unit='ms')
    df.set_index('timestamp', inplace=True)
    df = df.resample('1M').last()
    return df


dfs, names = [], []
for network in Network:
    # fetch all vaults in network
    query = f"""
        yearn_vault{{
            network=\"{network.name}\",
            experimental=\"false\",
            param=\"activation\",
        }} > 0
    """
    data = {
        "queries": [
            {
                "expr": query,
                "utcOffsetSec": 0,
                "datasourceId": 1
            }
        ],
        "from": str(from_millis), "to": str(to_millis),
    }
    with requests.Session() as session:
        response = session.post(
            url = url,
            headers = headers,
            json = data
        )
    result = response.json()['results']['A']['frames']
    vaults = [frame['schema']['fields'][1]['labels']['vault'] for frame in result]
    for vault in vaults:
        # fetch totalGain and TVL
        try:
            df = pd.concat([
                get_total_gain(network.name, vault),
                get_total_assets(network.name, vault),
                get_tvl(network.name, vault),
                get_debt_ratio(network.name, vault),
                get_apy(network.name, vault),
                get_token_price(network.name, vault),
            ], axis=1)
            df['totalGainDelta'] = df.totalGain.diff()
            df['totalGainDelta/totalAssets'] = df.totalGainDelta / df.totalAssets.shift()
            df['totalGainDeltaUSD'] = df.totalGainDelta * df.tokenPrice
        except Exception as e:
            print(f"skipping {network.name} {vault} due to {e}")
            continue
        df.name = network.name + ' ' + vault
        dfs.append(df)
        names.append(df.name)

data = pd.concat(dfs, axis=1, keys=names).fillna(0.0)
data.to_csv('individual.csv')

print(data)

vaults = list(set(col[0].split(' ')[1] for col in data.columns))

combined = []
for vault in vaults:
    _combined = pd.concat([
        sum([data[col] for col in data.columns if vault in col[0] and col[1] == 'totalGain']),
        sum([data[col] for col in data.columns if vault in col[0] and col[1] == 'totalAssets']),
        sum([data[col] for col in data.columns if vault in col[0] and col[1] == 'tvl']),
        sum([data[col] for col in data.columns if vault in col[0] and col[1] == 'totalGainDeltaUSD']),
    ], axis=1)
    _combined.columns = ['totalGain', 'totalAssets', 'tvl', 'totalGainDeltaUSD']
    _combined['totalGainDelta'] = _combined.totalGain.diff()
    _combined['totalGainDelta/totalAssets'] = _combined.totalGainDelta / _combined.totalAssets.shift()
    combined.append(_combined)
data = pd.concat(combined, axis=1, keys=vaults)

data.to_csv('combined.csv')
print(data)
