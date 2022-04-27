from gql import gql
from graphql.language import DocumentNode


vault_info = """{
        id
        token {
            id
            decimals
            name
            symbol
        }
        shareToken {
            name
        }
        strategies {
            id
            name
        }
    }
}
"""


def query_all_vaults() -> DocumentNode:
    return gql("{ vaults " + vault_info)


def query_vault_by_address(address: str) -> DocumentNode:
    return gql("{ vaults (where: {id: " + f'"{address.lower()}" }})' + vault_info)


strategy_info = """{
        id
        name
    }
}
"""


def query_all_strategies() -> DocumentNode:
    return gql("{ strategies " + strategy_info)


def query_strategy_by_address(address: str) -> DocumentNode:
    return gql(
        "{ strategies (where: {id: " + f'"{address.lower()}" }})' + strategy_info
    )
