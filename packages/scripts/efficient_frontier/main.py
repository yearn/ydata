import os
import numpy as np
import pandas as pd
import altair as alt
import datapane as dp

from efficient_frontier.stablecoins import update_returns
from efficient_frontier.portfolio import efficient_frontier


def plot_data(data, xs, ys, is_yearn=False):
    color = "#0675F9" if is_yearn else "mediumvioletred"
    if is_yearn:
        scatter = (
            alt.Chart(data)
            .mark_circle(size=70, color=color)
            .encode(
                x="Volatility",
                y="Return",
                tooltip=["Return", "Volatility", "Network", "Project", "Symbol"],
            )
        )
    else:
        scatter = (
            alt.Chart(data)
            .mark_circle(size=70)
            .encode(
                x="Volatility",
                y="Return",
                color=alt.Color(
                    "OnFrontier",
                    scale=alt.Scale(
                        domain=[True, False],
                        range=[color, "lightgray"],
                    ),
                    legend=alt.Legend(title="On Frontier"),
                ),
                tooltip=["Return", "Volatility", "Network", "Project", "Symbol"],
            )
        )
    _line = pd.DataFrame(
        {
            "Return": ys,
            "Volatility": xs,
        }
    )
    line = (
        alt.Chart(_line)
        .mark_line(
            color=color
        )
        .encode(
            x="Volatility:Q",
            y="Return:Q",
        )
    )
    return scatter, line


def update_data():
    # get yield data from defi llama
    returns = update_returns().fillna(method='ffill')
    returns = returns.loc[:, (~returns.isna()).sum() > 30].dropna()

    # aggregate to yearly values
    T = 365.2425
    mu = (1 + returns).prod() ** (T / len(returns)) - 1
    cov = returns.cov() * T
    sigma = np.sqrt(np.diag(cov))

    # remove outliers
    mu_iqr = np.quantile(mu, 0.75) - np.quantile(mu, 0.25)
    mu_median = np.median(mu)
    mask = (mu > mu_median + 1.5 * mu_iqr) | (mu < mu_median - 1.5 * mu_iqr)

    sigma_iqr = np.quantile(sigma, 0.75) - np.quantile(sigma, 0.25)
    sigma_median = np.median(sigma)
    mask |= (sigma > sigma_median + 1.5 * sigma_iqr) | (
        sigma < sigma_median - 1.5 * sigma_iqr
    )
    mask |= (sigma < 1e-5)
    returns = returns.loc[:, ~mask]
    return returns


def main_chart(returns):
    # aggregate to yearly values
    T = 365.2425
    mu = (1 + returns).prod() ** (T / len(returns)) - 1
    cov = returns.cov() * T
    sigma = np.sqrt(np.diag(cov))

    # efficient frontier
    xs, ys, nonzero = efficient_frontier(mu, cov)
    data = pd.DataFrame(
        np.stack([mu, sigma]).T, columns=["Return", "Volatility"], index=mu.index
    )
    data["Network"] = [col.split(":")[0] for col in returns.columns]
    data["Project"] = [col.split(":")[1] for col in returns.columns]
    data["Symbol"] = [col.split(":")[2] for col in returns.columns]
    data["OnFrontier"] = False
    for idx in nonzero:
        data.loc[data.index[idx], "OnFrontier"] = True
    scatter, line = plot_data(data, xs, ys, is_yearn=False)

    # list of assets on the frontier
    frontier_data = data[data["OnFrontier"]].reset_index()
    frontier_data = frontier_data[["Network", "Project", "Symbol", "Return", "Volatility"]]

    # Yearn assets
    ycols = [col for col in returns.columns if 'yearn-finance' in col]
    yreturns = returns[ycols]

    mu = (1 + yreturns).prod() ** (T / len(yreturns)) - 1
    cov = yreturns.cov() * T
    sigma = np.sqrt(np.diag(cov))

    # efficient frontier
    xs, ys, nonzero = efficient_frontier(mu, cov)
    data = pd.DataFrame(
        np.stack([mu, sigma]).T, columns=["Return", "Volatility"], index=mu.index
    )
    data["Network"] = [col.split(":")[0] for col in yreturns.columns]
    data["Project"] = [col.split(":")[1] for col in yreturns.columns]
    data["Symbol"] = [col.split(":")[2] for col in yreturns.columns]
    yscatter, yline = plot_data(data, xs, ys, is_yearn=True)

    frontier_chart = (
        alt.layer(
            scatter,
            line,
            yscatter,
            yline,
        )
        .properties(
            width=500,
            height=500,
        )
        .interactive()
    )
    return frontier_chart, frontier_data


def main():
    # fetch daily returns from defillama
    data = update_data()
    frontier_chart, frontier_data = main_chart(data)

    # login to datapane
    dp.login(token=os.environ["DATAPANE_TOKEN"])

    # datapane report
    report = dp.Report(
        dp.Group(
            dp.Text("### Efficient Frontier of Stablecoins"),
            frontier_chart,
            dp.DataTable(frontier_data),
            label="Efficient Frontier"
        ),
    )

    # upload the report
    report.upload(name="DeFi Frontier", publicly_visible=True)


if __name__ == '__main__':
    main()
