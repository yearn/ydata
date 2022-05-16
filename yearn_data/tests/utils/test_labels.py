from ...utils.labels import get_labels

USDC = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
yvDAI = "0xda816459f1ab5631232fe5e97a05bbbb94970c95"


def test_get_labels_USDC():
    labels = get_labels(USDC)
    assert 'USDC' in labels
