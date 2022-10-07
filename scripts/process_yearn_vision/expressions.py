from process_yearn_vision.typings import NetworkStr


def gen_share_price_expr() -> dict[NetworkStr, str]:
    return {
        NetworkStr.Mainnet: 'yearn_vault{param="pricePerShare", experimental="false", network="ETH"}',
        NetworkStr.Fantom: 'yearn_vault{param="pricePerShare", experimental="false", network="FTM"}',
    }


def gen_aum_expr() -> dict[NetworkStr, str]:
    return {
        NetworkStr.Mainnet: 'yearn_vault{param="tvl", experimental="false", network="ETH"}',
        NetworkStr.Fantom: 'yearn_vault{param="tvl", experimental="false", network="FTM"}',
    }


def gen_total_debt_expr() -> dict[NetworkStr, str]:
    return {
        NetworkStr.Mainnet: 'yearn_vault{param="totalDebt", experimental="false", network="ETH"}',
        NetworkStr.Fantom: 'yearn_vault{param="totalDebt", experimental="false", network="FTM"}',
    }


def gen_total_gains_expr(vault: str) -> dict[NetworkStr, str]:
    return {
        NetworkStr.Mainnet: f"""sum(yearn_strategy{{param=\"totalGain\", experimental=\"false\", network=\"ETH\", vault=~\"{vault}\"}}) - sum(yearn_strategy{{param=\"totalLoss\", experimental=\"false\", network=\"ETH\", vault=~\"{vault}\"}})""",
        NetworkStr.Fantom: f"""sum(yearn_strategy{{param=\"totalGain\", experimental=\"false\", network=\"FTM\", vault=~\"{vault}\"}}) - sum(yearn_strategy{{param=\"totalLoss\", experimental=\"false\", network=\"FTM\", vault=~\"{vault}\"}})""",
    }
