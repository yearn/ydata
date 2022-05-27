# Yearn DATA Analytics


## Research Reports

We share the research outputs from the YFI Data Analysis team in [the `research` directory](./research/).


## Vault-level Risk

This project aims to provide additional quantitative metrics on top of the existing [Risk Framework](https://github.com/yearn/yearn-watch/blob/main/utils/risks.json), to help discover informative risk measures and collect the data necessary to build the metrics. 
Furthermore, the project also aims to provide aggregated views for Yearn's Vaults and associated DeFi protocols.
See [the project README](./src/risk_framework/README.md) for more details.

~~Usage examples for this project can be seen in [`examples/risk.ipynb`](./examples/risk.ipynb).~~

TODO: need to rewrite examples for the new structure


### Prerequisites

This project uses Poetry for dependency management.
Please refer to the [documentation](https://python-poetry.org/docs/master/) for installing Poetry.
```
poetry install
```

You will also need to set up the Web3 provider endpoints and chain explorers in the environment file `.env`.
The necessary variables and some of their default values are shown in `.env.example`:
```
# Mainnet
ETH_PROVIDER=
ETHERSCAN_TOKEN=

# Fantom
FTM_PROVIDER=https://rpc.ftm.tools/
FTMSCAN_TOKEN=

# Database
DATABASE_URI=sqlite:///db.sqlite3
```


### Running the API

To run the API locally at port 8000:
```bash
docker-compose up --build
```
Auto-generated docs can be seen at [localhost:8000/docs](http://localhost:8000/docs)
