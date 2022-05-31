
from src.yearn import Network, Strategy,Yearn
from src.risk_framework.scores import StrategyRiskScores, VaultRiskScores

#imported into test_analysis
YEARN_MAINNET = Yearn(Network.Mainnet)

YEARN_FANTOM = Yearn(Network.Fantom)

STRAT1 = Strategy(
    Network.Mainnet, "0x1676055fE954EE6fc388F9096210E5EbE0A9070c", "GenLevCompV3"
)
STRAT2 = Strategy(
    Network.Fantom,
    "0x695A4a6e5888934828Cb97A3a7ADbfc71A70922D",
    "StrategyLenderYieldOptimiser",
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

#import into test_scores
STRAT_SCORE = StrategyRiskScores(1, 2, 1, 2, 1, 2, 1, 2)
VAULT_SCORE = VaultRiskScores(1, 1, 1, 1, 1, 5)

