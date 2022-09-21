from decimal import Decimal
from dotenv import load_dotenv
from src.utils.web3 import Web3Provider
from src.utils.network import client, parse_json
import requests
from src.networks import Network
from datetime import datetime
import pandas as pd
from rich.progress import Progress
import time
import os

load_dotenv()
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
    df.tokenPrice = df.tokenPrice.fillna(0.0).apply(Decimal)
    df.set_index('timestamp', inplace=True)
    df = df.resample('1M').last()
    return df


dfs = []
for symbol, network in [
        ('ETH', Network.Mainnet),
        ('OPT', Network.Optimism),
        ('FTM', Network.Fantom),
    ]:
    w3 = Web3Provider(network)

    # fetch vaults from ydaemon
    endpoint = os.path.join(YDAEMON, str(network.value), "vaults", "all")
    response = client('get', endpoint)
    jsoned = parse_json(response)
    vaults = [vault['address'] for vault in jsoned]

    # XXX: version mismatch
    # fetch vault names from vision
    query = f"""
        yearn_vault{{
            network=\"{symbol}\",
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
    vault_names = {
        frame['schema']['fields'][1]['labels']['address']: frame['schema']['fields'][1]['labels']['vault']
        for frame in result
    }
    print(f"Fetched {len(vaults)} vaults on {network.name}")

    # fetch block numbers
    def binary_search(low, high, dt, tol=600):
        if high >= low:
            mid = (high + low) // 2
            block = w3.provider.eth.get_block(mid)
            block_dt = datetime.fromtimestamp(block.timestamp)
            diff = int((dt - block_dt).total_seconds())
            if abs(diff) < tol or high - low == 1:
                return mid
            elif diff > 0:
                return binary_search(mid, high, dt, tol=tol)
            else:
                return binary_search(low, mid, dt, tol=tol)
        else:
            return -1

    first_ts = w3.provider.eth.get_block(1).timestamp
    start_dt = datetime.fromtimestamp(first_ts)
    start_dt = max(datetime.fromtimestamp(from_millis / 1e3), start_dt)
    end_dt = datetime.fromtimestamp(to_millis / 1e3)
    dts = pd.date_range(start=start_dt, end=end_dt, freq='M')

    latest_block = w3.provider.eth.get_block("latest")["number"]
    blocks = []
    with Progress(transient=True) as progress:
        task = progress.add_task("Fetching block numbers...", total=len(dts))
        for dt in dts:
            blocks.append(binary_search(0, latest_block, dt))
            progress.update(task, advance=1)
    print(f"Fetched {len(blocks)} blocks to process")

    # fetch on-chain data
    with Progress(transient=True) as progress:
        points = len(vaults) * len(dts)
        task = progress.add_task("Collecting on-chain data...", total=points)
        for idx, vault in enumerate(vaults):
            df = pd.DataFrame(
                index=dts,
                columns=[
                    'network',
                    'vault',
                    'version',
                    'totalAssets',
                    'totalDebt',
                    'totalGain',
                    'totalLoss',
                    'netTotalGain',
                    'netTotalGainDelta',
                    'tokenPriceUSDC',
                    'totalAssetsUSDC',
                    'totalDebtUSDC',
                    'netTotalGainUSDC',
                    'netTotalGainDeltaUSDC',
                    'pricePerShare',
                    'apy',
                ]
            )
            df['network'] = symbol
            df['vault'] = vault_names[vault].split(' ')[0]
            df['version'] = vault_names[vault].split(' ')[1]

            endpoint = os.path.join(YDAEMON, str(network.value), "vaults", vault)
            response = client('get', endpoint)
            jsoned = parse_json(response)

            token = jsoned['token']['address']
            token_denom = Decimal(10 ** jsoned['token']['decimals'])
            share_denom = Decimal(10 ** jsoned['decimals'])

            inception = datetime.fromtimestamp(jsoned['inception'])

            strategies = [strategy['address'] for strategy in jsoned['strategies']]

            for dt, block in zip(dts, blocks):
                # skip if before inception date
                if dt < inception:
                    progress.update(task, advance=1)
                    points -= 1
                    continue

                # vault-level data
                try:
                    df.loc[dt, 'totalAssets'] = Decimal(w3.call(vault, "totalAssets", block=block)) / token_denom
                    df.loc[dt, 'totalDebt'] = Decimal(w3.call(vault, "totalDebt", block=block)) / token_denom
                    df.loc[dt, 'pricePerShare'] = Decimal(w3.call(vault, "pricePerShare", block=block)) / share_denom
                except:
                    continue

                # strategy-level data
                totalGain, totalLoss = Decimal(0), Decimal(0)
                for strategy in strategies:
                    try:
                        strategy_params = w3.call(vault, "strategies", strategy, block=block)
                        totalGain += Decimal(strategy_params[-2])
                        totalLoss += Decimal(strategy_params[-1])
                    except:
                        pass
                df.loc[dt, 'totalGain'] = totalGain / token_denom
                df.loc[dt, 'totalLoss'] = totalLoss / token_denom
                progress.update(task, advance=1)

            df = df.resample('1M').last()
            token_prices = get_token_price(symbol, vault_names[vault])
            index = token_prices.index.intersection(df.index)
            df.loc[index, 'tokenPriceUSDC'] = token_prices.loc[index].values

            # additional metrics
            df['apy'] = df.pricePerShare.pct_change()
            df['netTotalGain'] = (df.totalGain - df.totalLoss).apply(Decimal)
            df['netTotalGainDelta'] = df.netTotalGain.diff()
            df['totalAssetsUSDC'] = df.totalAssets * df.tokenPriceUSDC
            df['totalDebtUSDC'] = df.totalDebt * df.tokenPriceUSDC
            df['netTotalGainUSDC'] = df.netTotalGain * df.tokenPriceUSDC
            df['netTotalGainDeltaUSDC'] = df.netTotalGainDelta * df.tokenPriceUSDC

            df = df.reset_index().rename(columns={'index': 'timestamp'})
            dfs.append(df)

    print(f"Collected {points} data points")

data = pd.concat(dfs).fillna(Decimal(0.0))
data.index = range(len(data))
data.to_csv('individual.csv')

data = data.groupby(['timestamp', 'vault']).sum().drop(
    columns=['network', 'version', 'tokenPriceUSDC', 'pricePerShare', 'apy']
).reset_index()
data.to_csv('combined.csv')
