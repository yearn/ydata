# Yearn DATA Analytics


## Research Reports

We share the research outputs from the YFI Data Analysis team in [the `research` directory](./research/).


## Vault-level Risk

API endpoint (Test):
http://yearn-data-test.us-west-2.elasticbeanstalk.com/api

This project aims to provide additional quantitative metrics on top of the existing [Risk Framework](https://github.com/yearn/yearn-watch/blob/main/utils/risks.json), to help discover informative risk measures and collect the data necessary to build the metrics. 
Furthermore, the project also aims to provide aggregated views for Yearn's Vaults and associated DeFi protocols.
See [the project README](./src/risk_framework/README.md) for more details.

~~Usage examples for this project can be seen in [`examples/risk.ipynb`](./examples/risk.ipynb).~~

TODO: need to rewrite examples for the new structure


## Prerequisites

This project uses Poetry for dependency management.
Please refer to the [documentation](https://python-poetry.org/docs/master/) for installing Poetry.

Run the following command to install the dependencies:
```
poetry install
```

You will also need to set up the Web3 provider endpoints and chain explorers in the environment file `.env`.
The necessary variables and some of their default values are shown in [`.env.example`](./.env.example):
```
# Mainnet
ETH_PROVIDER=
ETHERSCAN_TOKEN=

# Fantom
FTM_PROVIDER=https://rpc.ftm.tools/
FTMSCAN_TOKEN=

# Arbitrum
ARB_PROVIDER=https://arb1.arbitrum.io/rpc
ARBISCAN_TOKEN=

# Database
DATABASE_URI=sqlite:////data/api_cache.sqlite3
```

Furthermore, you need to have Docker and Docker Compose that can support compose file format of version 2.0 or higher, see the [documentation](https://docs.docker.com/compose/compose-file/compose-versioning/) for the list of compatible versions and installation guides.


## Usage Examples

### Running the API

To run the API locally at port 80:
```bash
docker-compose up --build
```
Auto-generated docs can be seen at [localhost/docs](http://localhost/docs)
