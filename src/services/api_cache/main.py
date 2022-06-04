import gc
import logging
import os
import signal
import sys
from typing import Any, List

from dotenv import load_dotenv
from requests.exceptions import HTTPError
from sqlmodel import Session, SQLModel, create_engine

from src.models import RiskGroup, Strategy, Vault, create_id
from src.risk_framework import RiskAnalysis
from src.utils.network import retry
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


@retry(
    retries=0,
    exception=HTTPError,
    exception_handler=lambda strategy: f"Failed to fetch data from strategy {strategy.name}",
)
def __commit_strategy(strategy: TStrategy, risk: RiskAnalysis) -> None:
    strategy_info = risk.describe(strategy)
    strategy_id = create_id(strategy.address, strategy.network)

    with Session(engine) as session:
        _strategy = session.get(Strategy, strategy_id)
        if _strategy is None:
            session.add(
                Strategy(
                    id=strategy_id,
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


@retry(
    retries=0,
    exception=HTTPError,
    exception_handler=lambda vault: f"Failed to fetch data from vault {vault.name}",
)
def __commit_vault(vault: TVault, risk: RiskAnalysis) -> None:
    vault_info = risk.describe(vault)
    vault_id = create_id(vault.address, vault.network)

    with Session(engine) as session:
        _vault = session.get(Vault, vault_id)
        if _vault is None:
            session.add(
                Vault(
                    id=vault_id,
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


@retry(retries=0)
def __commit_risk_group(risk: RiskAnalysis) -> None:
    with Session(engine) as session:
        for group in risk.risk_groups:
            _group = session.get(RiskGroup, group.id)
            if _group is None:
                session.add(
                    RiskGroup(
                        id=group.id,
                        network=group.network,
                        label=group.label,
                        auditScore=group.auditScore,
                        codeReviewScore=group.codeReviewScore,
                        testingScore=group.testingScore,
                        protocolSafetyScore=group.protocolSafetyScore,
                        complexityScore=group.complexityScore,
                        teamKnowledgeScore=group.teamKnowledgeScore,
                        criteria=group.criteria,
                    )
                )
            else:
                _group.network = group.network
                _group.label = group.label
                _group.auditScore = group.auditScore
                _group.codeReviewScore = group.codeReviewScore
                _group.testingScore = group.testingScore
                _group.protocolSafetyScore = group.protocolSafetyScore
                _group.complexityScore = group.complexityScore
                _group.teamKnowledgeScore = group.teamKnowledgeScore
                _group.criteria = group.criteria
                session.add(_group)
            session.commit()


def __refresh(yearn_chains: List[Yearn], risk: RiskAnalysis) -> None:
    logger.info("Refreshing data for all chains")
    for yearn in yearn_chains:
        yearn.refresh()
    risk.refresh()


@retry(retries=0)
def __do_commits(yearn_chains: List[Yearn], risk: RiskAnalysis) -> None:
    # refresh data
    __refresh(yearn_chains, risk)

    # export the risk framework json file
    logger.info(f"Updating risk groups")
    __commit_risk_group(risk)

    for yearn in yearn_chains:
        for vault in yearn.vaults:
            # garbage collection to save memory usage
            gc.collect()

            logger.info(f"Updating vault {vault.name} on {vault.network.name}")

            # vault-level data
            __commit_vault(vault, risk)

            # strategy-level data
            for strategy in vault.strategies:
                __commit_strategy(strategy, risk)


def __get_yearn_chains() -> List[Yearn]:
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
