from src.yearn.protocols import Protocol, ProtocolList
from src.yearn import Network, Strategy, Yearn



#import into test_networks
USDC_VAULT = (Network.Mainnet, "0xa354F35829Ae975e850e23e9615b11Da1B3dC4DE")
WFTM_VAULT = (Network.Fantom, "0x0DEC85e74A92c52b7F708c4B10207D9560CEFaf0")

USDC_MAINNET = (Network.Mainnet, "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48")
USDC_FANTOM = (Network.Fantom, "0x04068da6c83afcfa0e13ba15a6696662335d5b75")

#imported into test_protocols
AAVE_V3 = ProtocolList[ProtocolList.index(Protocol("Aave"))]
AAVE_V2 = ProtocolList[ProtocolList.index(Protocol("Aave V2"))]

#import into test_strategies
STRAT1 = Strategy(
    Network.Mainnet, "0x1676055fE954EE6fc388F9096210E5EbE0A9070c", "GenLevCompV3"
)
STRAT2 = Strategy(
    Network.Fantom,
    "0x695A4a6e5888934828Cb97A3a7ADbfc71A70922D",
    "StrategyLenderYieldOptimiser",
)
DAYS = 60 * 60 * 24

#imported into test_vaults
YEARN_MAINNET = Yearn(Network.Mainnet)
VLT_USDC_VAULT = [
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

#imported into test_yearn
YEARN_MAINNET = Yearn(Network.Mainnet)
YEARN_FANTOM = Yearn(Network.Fantom)


