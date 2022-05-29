import os
import sys
import time
import signal
import logging
from requests.exceptions import HTTPError
from sqlmodel import create_engine, SQLModel, Session

from src.yearn import Network, Yearn
from src.risk_framework import RiskAnalysis
from src.models import Vault, Strategy

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s.%(msecs)03d %(levelname)s %(module)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# create database engine
engine = create_engine(os.environ["DATABASE_URI"])
SQLModel.metadata.create_all(engine)


def handle_signal(*args):
    logger.error("Interrupted by user")
    sys.exit()


if __name__ == "__main__":
    # handle signals
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    # initialize Yearn instances
    yearn_chains = []
    for network in Network:
        logger.info(f"Initializing Yearn for {network.name}")
        yearn_chains.append(Yearn(network))

    # initialize Risk Analysis
    logger.info("Initializing Risk Analysis")
    risk = RiskAnalysis()

    # main loop
    logger.info("Entering main loop")
    start_time = time.time()
    while True:
        try:
            # refresh data
            logger.info("Refreshing data for all chains")
            for yearn in yearn_chains:
                yearn.refresh()
            risk.refresh()

            for yearn in yearn_chains:
                for vault in yearn.vaults:
                    logger.info(f"Updating vault {vault.name} on {vault.network.name}")

                    # ====================
                    # Risk Framework
                    # ====================
                    # vault-level data
                    try:
                        vault_info = risk.describe(vault)
                        with Session(engine) as session:
                            _vault = session.get(Vault, vault.address.lower())
                            if _vault is None:
                                session.add(
                                    Vault(
                                        address=vault.address.lower(),
                                        network=vault.network,
                                        name=vault.name,
                                        info=vault_info,
                                    )
                                )
                            else:
                                _vault.info = vault_info
                                session.add(_vault)
                            session.commit()
                    except HTTPError:
                        logger.error(
                            f"Failed to fetch data from vault {vault.name}",
                            exc_info=True,
                        )

                    # strategy-level data
                    for strategy in vault.strategies:
                        try:
                            strategy_info = risk.describe(strategy)
                            with Session(engine) as session:
                                _strategy = session.get(
                                    Strategy, strategy.address.lower()
                                )
                                if _strategy is None:
                                    session.add(
                                        Strategy(
                                            address=strategy.address.lower(),
                                            network=strategy.network,
                                            name=strategy.name,
                                            info=strategy_info,
                                        )
                                    )
                                else:
                                    _strategy.info = strategy_info
                                    session.add(_strategy)
                                session.commit()
                        except HTTPError:
                            logger.error(
                                f"Failed to fetch data from strategy {strategy.name}",
                                exc_info=True,
                            )

        except Exception as e:
            logger.error(e, exc_info=True)
