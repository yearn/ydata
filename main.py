import os
import sys
import time
from web3 import Web3
import logging
from dotenv import load_dotenv
from sqlmodel import create_engine, SQLModel, Session

from yearn_data import Network, Yearn
from yearn_data.models import Vault, Strategy

load_dotenv()

w3 = Web3(Web3.HTTPProvider(os.environ['WEB3_PROVIDER']))
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
logger = logging.getLogger(__name__)

# create database engine
engine = create_engine(os.environ['DATABASE_URI'])
SQLModel.metadata.create_all(engine)


if __name__ == '__main__':
    # initialize Yearn instance
    logger.info(f"Initializing Yearn for chain - {Network(w3.eth.chain_id).name}")
    yearn = Yearn()

    # main loop
    logger.info("Entering main loop")
    start_time = time.time()
    while True:
        try:
            # refresh data
            logger.info("Refreshing data for all vaults")
            yearn.load_vaults()
            for vault in yearn.vaults:
                logger.info(f"Updating vault {vault.name}")

                # vault-level data
                vault_info = yearn.describe(vault)
                with Session(engine) as session:
                    _vault = session.get(Vault, vault.address.lower())
                    if _vault is None:
                        session.add(
                            Vault(
                                address=vault.address.lower(),
                                name=vault.name,
                                info=vault_info,
                            )
                        )
                    else:
                        _vault.info = vault_info
                        session.add(_vault)
                    session.commit()

                # strategy-level data
                for strategy in vault.strategies:
                    strategy_info = yearn.describe(strategy)
                    with Session(engine) as session:
                        _strategy = session.get(Strategy, strategy.address.lower())
                        if _strategy is None:
                            session.add(
                                Strategy(
                                    address=strategy.address.lower(),
                                    name=strategy.name,
                                    info=strategy_info,
                                )
                            )
                        else:
                            _strategy.info = strategy_info
                            session.add(_strategy)
                        session.commit()

        except KeyboardInterrupt:
            logger.error("Interrupted by user")
            sys.exit()

        except Exception as e:
            logger.error(e, exc_info=True)
