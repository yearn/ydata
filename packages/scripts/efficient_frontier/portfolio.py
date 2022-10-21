import numpy as np
from scipy.optimize import minimize
from tqdm import tqdm


def efficient_frontier(mu, cov, num_samples=100, threshold=0.1):
    # maximize return given the target std
    def efficient_return(target_std):
        N = len(mu)

        def neg_portfolio_return(weights):
            return -(mu * weights).sum()

        def portfolio_std(weights):
            return np.sqrt(
                (weights[np.newaxis, :] @ cov @ weights[:, np.newaxis]).sum()
            )

        constraints = (
            {"type": "eq", "fun": lambda x: portfolio_std(x) - target_std},
            {"type": "eq", "fun": lambda x: np.sum(x) - 1},
        )
        bounds = tuple((0, 1) for _ in range(N))
        result = minimize(
            neg_portfolio_return, N * [1 / N], bounds=bounds, constraints=constraints
        )
        return -result.fun, result.x

    sigma = np.sqrt(np.diag(cov))
    sigma_min = min_volatility_portfolio(mu, cov)[1][0]
    xs = np.linspace(sigma_min, sigma.max(), num_samples)
    ys, nonzero = [], set({})
    last_y = -np.inf

    count = 0
    for idx in tqdm(range(num_samples), desc="Efficient Frontier"):
        new_y, weights = efficient_return(xs[idx])
        nonzero.update(set(*np.nonzero(weights > threshold)))
        if new_y >= last_y:
            last_y = new_y
            ys.append(new_y)
            count = 0
        else:  # early stopping
            count += 1
            ys.append(last_y)
            if count >= 5:
                break
    ys += [last_y] * (len(xs) - len(ys))

    return xs, ys, nonzero


def tangency_portfolio(mu, cov):
    # maximize sharpe ratio
    def neg_sharpe_ratio(weights):
        # assuming risk-free rate of 3%
        rf = 0.03
        portfolio_return = (mu * weights).sum()
        portfolio_std = np.sqrt(
            (weights[np.newaxis, :] @ cov @ weights[:, np.newaxis]).sum()
        )
        return -(portfolio_return - rf) / portfolio_std

    N = len(mu)
    constraints = ({"type": "eq", "fun": lambda x: np.sum(x) - 1},)
    bounds = tuple((0, 1) for _ in range(N))
    result = minimize(
        neg_sharpe_ratio, N * [1 / N], bounds=bounds, constraints=constraints
    )
    weights = result.x
    portfolio_return = (mu * weights).sum()
    portfolio_std = np.sqrt(
        (weights[np.newaxis, :] @ cov @ weights[:, np.newaxis]).sum()
    )
    return portfolio_return, portfolio_std, weights


def min_volatility_portfolio(mu, cov):
    # minimize volatility
    def volatility(weights):
        return np.sqrt((weights[np.newaxis, :] @ cov @ weights[:, np.newaxis]).sum())

    N = len(mu)
    constraints = ({"type": "eq", "fun": lambda x: np.sum(x) - 1},)
    bounds = tuple((0, 1) for _ in range(N))
    result = minimize(volatility, N * [1 / N], bounds=bounds, constraints=constraints)
    weights = result.x
    portfolio_return = (mu * weights).sum()
    portfolio_std = np.sqrt(
        (weights[np.newaxis, :] @ cov @ weights[:, np.newaxis]).sum()
    )
    return portfolio_return, portfolio_std, weights


def risk_parity_portfolio(mu, cov):
    sigma = np.sqrt(np.diag(cov))
    weights = 1 / sigma
    weights /= weights.sum()
    portfolio_return = (mu * weights).sum()
    portfolio_std = np.sqrt(
        (weights[np.newaxis, :] @ cov @ weights[:, np.newaxis]).sum()
    )
    return portfolio_return, portfolio_std, weights
