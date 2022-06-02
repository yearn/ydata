from src.risk_framework.scores import StrategyRiskScores, VaultRiskScores
from src.yearn import Network, Strategy, Yearn

# imported into test_analysis
YEARN_MAINNET = Yearn(Network.Mainnet)
YEARN_FANTOM = Yearn(Network.Fantom)
YEARN_ARBITRUM = Yearn(Network.Arbitrum)

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

USDC_VAULT = [
    vault
    for vault in YEARN_MAINNET.vaults
    if vault.address == "0xa354F35829Ae975e850e23e9615b11Da1B3dC4DE"
][0]
CRV_VAULT = [
    vault
    for vault in YEARN_FANTOM.vaults
    if vault.address == "0x0446acaB3e0242fCf33Aa526f1c95a88068d5042"
][0]
CRV3_VAULT = [
    vault
    for vault in YEARN_ARBITRUM.vaults
    if vault.address == "0x239e14A19DFF93a17339DCC444f74406C17f8E67"
][0]

# import into test_scores
STRAT_SCORE = StrategyRiskScores(1, 2, 1, 2, 1, 2, 1, 2)
VAULT_SCORE = VaultRiskScores(1, 1, 1, 1, 1, 5)
