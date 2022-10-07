# Yearn DATA Analytics


## Research Reports

We share the research outputs from the YFI Data Analysis team in [the `research` directory](./research/).


## Vault-level Risk

API endpoint:
https://d3971bp2359cnv.cloudfront.net/api

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

Then run the following command to install the git pre-commit hooks:
```
pre-commit install
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
```

Furthermore, you need to have Docker and Docker Compose that can support compose file format of version 2.0 or higher, see the [documentation](https://docs.docker.com/compose/compose-file/compose-versioning/) for the list of compatible versions and installation guides.


## Usage Examples

### Running the API

To run the API locally at port 80:
```bash
docker-compose up --build
```
Auto-generated docs can be seen at [localhost/docs](http://localhost/docs)

### DevContainer

If you're using VSCode, you can use DevContainer to setup all the required dependencies (almost) automatically.
**But you first need to set up `./.env` file though.**
If you have filled out `./.env`, open cloned dir in VSC and just press `Reopen in Container` button on the right bottom side.  
<img width="459" alt="image" src="https://user-images.githubusercontent.com/103443013/173222631-fa280003-24e2-4f49-85da-dc1d88bc2633.png">  
Or use command palette to search `Remote-Containers: Reopen in Container`.
Then VSC will do the rest. pytest in the integrated terminal after the build process. You'll pass all tests if your DevContainer has no problem and `.env` is set properly.