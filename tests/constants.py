from src.networks import Network
from src.risk_framework.scores import StrategyRiskScores, VaultRiskScores
from src.yearn import Strategy, Yearn
from src.yearn.protocols import Protocol, ProtocolList

# imported into utils/test_web3
USDC_VAULT_ADDRESS = (Network.Mainnet, "0xa354F35829Ae975e850e23e9615b11Da1B3dC4DE")
WFTM_VAULT_ADDRESS = (Network.Fantom, "0x0DEC85e74A92c52b7F708c4B10207D9560CEFaf0")
CRV3_VAULT_ADDRESS = (Network.Arbitrum, "0x239e14A19DFF93a17339DCC444f74406C17f8E67")

USDC_MAINNET = (Network.Mainnet, "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48")
USDC_FANTOM = (Network.Fantom, "0x04068da6c83afcfa0e13ba15a6696662335d5b75")
USDC_ARBITRUM = (Network.Arbitrum, "0xff970a61a04b1ca14834a43f5de4533ebddb5cc8")

# imported into yearn/test_protocols
AAVE_V3 = ProtocolList[ProtocolList.index(Protocol("Aave"))]
AAVE_V2 = ProtocolList[ProtocolList.index(Protocol("Aave V2"))]

# imported into yearn/test_strategies
STRAT1 = Strategy(
    Network.Mainnet, "0x1676055fE954EE6fc388F9096210E5EbE0A9070c", "GenLevCompV3"
)
STRAT2 = Strategy(
    Network.Fantom,
    "0x695A4a6e5888934828Cb97A3a7ADbfc71A70922D",
    "StrategyLenderYieldOptimiser",
)
STRAT3 = Strategy(
    Network.Arbitrum,
    "0xcDD989d84f9B63D2f0B1906A2d9B22355316dE31",
    "StrategyCurveTricrypto",
)
DAYS = 60 * 60 * 24

# imported into yearn/test_vaults, risk_framework/test_analysis
YEARN_MAINNET = Yearn(Network.Mainnet)
USDC_VAULT = [
    vault
    for vault in YEARN_MAINNET.vaults
    if vault.address == "0xa354F35829Ae975e850e23e9615b11Da1B3dC4DE"
][0]

YEARN_FANTOM = Yearn(Network.Fantom)
CRV_VAULT = [
    vault
    for vault in YEARN_FANTOM.vaults
    if vault.address == "0x0446acaB3e0242fCf33Aa526f1c95a88068d5042"
][0]

YEARN_ARBITRUM = Yearn(Network.Arbitrum)
CRV3_VAULT = [
    vault
    for vault in YEARN_ARBITRUM.vaults
    if vault.address == "0x239e14A19DFF93a17339DCC444f74406C17f8E67"
][0]

# imported into risk_framework/test_scores
STRAT_SCORE = StrategyRiskScores(1, 2, 1, 2, 1, 2, 1, 2)
VAULT_SCORE = VaultRiskScores(1, 1, 1, 1, 1, 5)
