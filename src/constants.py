# imported into yearn/yearn.py
YEARN_V1_API_ENDPOINT = "https://api.yearn.finance/v1/chains"
META_ENDPOINT = "https://meta.yearn.network"

# imported into yearn/vaults.py
ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"

# imported into yearn/network.py
BLOCK_SIZE = 100000
MAX_BLOCK = 99999999
USDC_DECIMALS = 6

# imported into risk_framework/defi_safety.py
DSAFETY_API_ENDPOINT = (
    "https://www.defisafety.com/api/pqrs?status=Active&reviewStatus=Completed"
)

# imported into risk_framework/scores.py
DAYS = 60 * 60 * 24

# imported into utils/network.py
REQUESTS_RETRY_TIMES = 5
REQUESTS_BACKOFF_FACTOR = 2
REQUESTS_STATUS_FORCELIST = [429, 500, 502, 503, 504]

REQUESTS_TIMEOUT = 10  # seconds
