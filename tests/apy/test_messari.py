import pytest
from dotenv import load_dotenv

from src.apy.messari import Subgraph
from src.yearn import Network

from src.utils.web3 import Web3Provider  # isort:skip

load_dotenv()


@pytest.mark.parametrize("network", [Network.Mainnet])
@pytest.mark.parametrize("protocol", ['yearn', 'balancer'])
@pytest.mark.parametrize("num_blocks", [1000000])
def test_daily_snapshots(network, protocol, num_blocks):
    w3 = Web3Provider(network)
    current_block = w3.provider.eth.get_block_number()
    from_block = current_block - num_blocks

    subgraph = Subgraph(network, protocol)
    snapshots = subgraph.daily_snapshots(from_block)
    assert len(snapshots) > 0
