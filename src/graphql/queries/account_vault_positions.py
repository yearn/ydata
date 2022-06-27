from gql import gql


def account_vault_positions_query(
    vault_address: str,
    num_accounts: int = 1000,
):
    return gql(
        f"""
        {{
            accountVaultPositions(first: {num_accounts},
                where:{{vault:"{vault_address}"}},
                orderBy: balanceShares,
                orderDirection: desc) {{
                id
                balanceShares
                account {{
                id
                }}
            }}
        }}
        """
    )
