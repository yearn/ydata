import os
import requests
import pandas as pd
import numpy as np
import random
import time
from datetime import datetime, timedelta
from joblib import Parallel, delayed

YIELD_URL = "https://yields.llama.fi"
COIN_URL = "https://coins.llama.fi"

MIN_DELAY = 1.0
MAX_DELAY = 3.0
MAX_RETRIES = 3

while True:
    endpoint = os.path.join(YIELD_URL, 'pools')
    response = requests.get(endpoint)
    if response.status_code != 200:
        time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))
        continue
    pools = response.json()['data']
    break

end_date = datetime.combine(datetime.now().date(), datetime.min.time())
start_date = end_date - timedelta(days=365)
index = pd.date_range(start_date, end_date - timedelta(days=1), freq='1D')


def get_pool_returns(pool):
    if pool['project'] == 'yearn-finance':
        if not any(symbol.lower() in pool['symbol'].lower() for symbol in ['USD', 'DAI', 'FRAX', 'MIM', '3Crv']):
            return
    elif not pool['stablecoin']:
        return
    # remove non-USD stablecoins
    if any(symbol.lower() in pool['symbol'].lower() for symbol in ['EUR']):
        return

    # fetch apys
    endpoint = os.path.join(YIELD_URL, 'chart', pool['pool'])
    retries = 0
    while True:
        try:
            response = requests.get(endpoint)
            data = response.json()['data']
            break
        except Exception as e:
            retries += 1
            time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))
            if retries > MAX_RETRIES:
                return
    df = pd.DataFrame(data)

    # check if tvl > 1M
    if df.tvlUsd.iloc[-1] < 1_000_000:
        return

    df.timestamp = df.timestamp.apply(lambda x: datetime.strptime(x[:19], "%Y-%m-%dT%H:%M:%S"))
    df.drop(columns=['apyBase', 'apyReward'], inplace=True)
    df.apy /= 100
    df.set_index('timestamp', inplace=True)
    df.sort_index(inplace=True)
    df = df.resample('1D').last()
    df = df[start_date:end_date]

    # convert to daily returns
    daily_returns = (1 + df.apy) ** (1 / 365.2425) - 1
    name = ':'.join([pool['chain'], pool['project'], pool['symbol']])
    daily_returns = daily_returns.reindex(index)
    return daily_returns.values, name


def update_returns():
    result = Parallel(n_jobs=16)(delayed(get_pool_returns)(pool) for pool in pools)
    result = [x for x in result if x is not None]
    returns, names = map(list, zip(*result))
    returns = np.asarray(returns).T
    return pd.DataFrame(returns, index=index, columns=names)
