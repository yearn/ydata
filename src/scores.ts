import BigNumber from 'bignumber.js';
import { Strategy, RiskFrameworkScores, GroupingsList } from './types';
import { isValidTimestamp, getTokenPrice, amountToMMs } from './utils';

export const getRiskFrameworkScores = (
  strategy: Strategy,
  groupScores: GroupingsList
): RiskFrameworkScores => {
  loop: for (var group of groupScores) {
    // exclude
    for (var name of group.criteria.exclude) {
      if (strategy.name.toLowerCase().includes(name)) {
        continue loop;
      }
    }
    // include
    for (var name of group.criteria.nameLike) {
      if (strategy.name.toLowerCase().includes(name) || name === 'all') {
        const { id, network, label, criteria, ...metrics } = group;
        return metrics;
      }
    }
  }
  const { id, network, label, criteria, ...metrics } =
    groupScores[groupScores.length - 1];
  return metrics;
};

export const getLongevityScore = (strategy: Strategy): number => {
  const activation = Date.parse(strategy.params.activation);
  let diffDays = 0;
  if (activation && isValidTimestamp(activation.toString())) {
    const diffMs = Date.now() - activation;
    diffDays = diffMs / 1000 / 60 / 60 / 24;
  }
  let longevityScore;
  if (diffDays < 7) {
    longevityScore = 5;
  } else if (diffDays <= 30) {
    longevityScore = 4;
  } else if (diffDays < 120) {
    longevityScore = 3;
  } else if (diffDays <= 240) {
    longevityScore = 2;
  } else {
    longevityScore = 1;
  }
  return longevityScore;
};

export const getTVL = async (strategy: Strategy): Promise<number> => {
  let estimatedUSDC = new BigNumber(0);
  if (strategy.estimatedTotalAssets) {
    estimatedUSDC = await getTokenPrice(
      strategy.token,
      strategy.estimatedTotalAssets
    );
  }
  return amountToMMs(estimatedUSDC);
};
