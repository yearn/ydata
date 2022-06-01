import gc
import logging
import os
import signal
import sys
from functools import wraps
from typing import Any, Callable, Optional, Type

from dotenv import load_dotenv
from requests.exceptions import HTTPError
from sqlmodel import Session, SQLModel, create_engine

from src.models import Strategy, Vault
from src.risk_framework import RiskAnalysis
from src.yearn import Network
from src.yearn import Strategy as TStrategy
from src.yearn import Vault as TVault
from src.yearn import Yearn

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s.%(msecs)03d %(levelname)s %(module)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

load_dotenv()

# create database engine
engine = create_engine(os.environ["DATABASE_URI"])
SQLModel.metadata.create_all(engine)


def handle_signal(*args: Any) -> None:
    logger.error("Interrupted by user")
    sys.exit()


def handle_exception(
    exception: Type[Exception] = Exception,
    handler: Optional[Callable[[Any], str]] = None,
) -> Callable:
    def decorator(fn: Callable) -> Callable:
        @wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return fn(*args, **kwargs)
            except exception as e:
                msg = handler(*args, **kwargs) if handler else e
                logger.error(msg, exc_info=True)

        return wrapper

    return decorator


@handle_exception(
    HTTPError, lambda strategy: f"Failed to fetch data from strategy {strategy.name}"
)
def __commit_strategy(strategy: TStrategy, risk: RiskAnalysis) -> None:
    strategy_info = risk.describe(strategy)

    with Session(engine) as session:
        _strategy = session.get(Strategy, strategy.address.lower())
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


@handle_exception(
    HTTPError, lambda vault: f"Failed to fetch data from vault {vault.name}"
)
def __commit_vault(vault: TVault, risk: RiskAnalysis) -> None:
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


def __refresh(yearn_chains: list[Yearn], risk: RiskAnalysis) -> None:
    logger.info("Refreshing data for all chains")
    for yearn in yearn_chains:
        yearn.refresh()
    risk.refresh()


@handle_exception()
def __do_commits(yearn_chains: list[Yearn], risk: RiskAnalysis) -> None:
    # refresh data
    __refresh(yearn_chains, risk)

    for yearn in yearn_chains:
        for vault in yearn.vaults:
            # garbage collection to save memory usage
            gc.collect()

            logger.info(f"Updating vault {vault.name} on {vault.network.name}")

            # ====================
            # Risk Framework
            # ====================
            # vault-level data
            __commit_vault(vault, risk)

            # strategy-level data
            for strategy in vault.strategies:
                __commit_strategy(strategy, risk)


def __get_yearn_chains() -> list[Yearn]:
    yearn_chains = []
    for network in Network:
        logger.info(f"Initializing Yearn for {network.name}")
        yearn_chains.append(Yearn(network))
    return yearn_chains


def main() -> None:
    # handle signals
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    # initialize Yearn instances
    yearn_chains = __get_yearn_chains()

    # initialize Risk Analysis
    logger.info("Initializing Risk Analysis")
    risk = RiskAnalysis()

    # main loop
    logger.info("Entering main loop")
    while True:
        # garbage collection to save memory usage
        gc.collect()

        __do_commits(yearn_chains, risk)


if __name__ == "__main__":
    main()
