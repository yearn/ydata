from typing import Literal

from gql import gql

from src.constants import MAX_BLOCK


def vault_transfers_query(
    transfer_type: Literal["withdrawals", "deposits"],
    vault_address: str,
    query_len: int = 1000,
    skip_id: str = "",
    from_block: int = 0,
    to_block: int = MAX_BLOCK,
):
    from_block = 0 if from_block == "first" else from_block
    to_block = MAX_BLOCK if to_block == "latest" else to_block
    shares_minted_or_burnt = (
        "sharesBurnt" if transfer_type == "withdrawals" else "sharesMinted"
    )
    return (
        gql(
            f"""
        {{
            {transfer_type}(first: {query_len},
                where: {{
                    id_gt: "{skip_id}",
                    vault: "{vault_address}",
                    blockNumber_gte: {from_block},
                    blockNumber_lte: {to_block}
                }}) {{
                id
                blockNumber
                timestamp
                transaction {{
                    id
                }}
                account {{
                    id
                }}
                {shares_minted_or_burnt}
            }}
        }}
        """
        ),
        shares_minted_or_burnt,
    )
