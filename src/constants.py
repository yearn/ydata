
#import into yearn/yearn.py
YEARN_V1_API_ENDPOINT = "https://api.yearn.finance/v1/chains"
META_ENDPOINT = "https://meta.yearn.network"

#import into yearn/vaults.py
ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"

#imported into yearn/network.py
BLOCK_SIZE = 100000
MAX_BLOCK = 99999999
USDC_DECIMALS = 6
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X x.y; rv:42.0) Gecko/20100101 Firefox/43.4"
}

# imported into risk_framework/analysis.py
RISK_FRAMEWORK = (
    "https://raw.githubusercontent.com/yearn/yearn-watch/main/utils/risks.json"
)

# imported into risk_framework/defi_safety.py
DSAFETY_API_ENDPOINT = (
    "https://www.defisafety.com/api/pqrs?status=Active&reviewStatus=Completed"
)

#import into risk_framework/scores.py
DAYS = 60 * 60 * 24


