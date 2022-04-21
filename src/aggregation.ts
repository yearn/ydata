import { StrategyScores, VaultScores } from './types';

const weightedAverage = (
  scores: StrategyScores[],
  key: string,
  tvl: number
) => {
  if (isNaN(tvl) || tvl === 0) {
    return (
      scores.reduce((previous, current: any) => {
        return previous + current[key];
      }, 0) / scores.length
    );
  } else {
    return (
      scores.reduce((previous, current: any) => {
        return previous + current.TVL * current[key];
      }, 0) / tvl
    );
  }
};

export const aggregateScores = (scores: StrategyScores[]): VaultScores => {
  const tvl = scores.reduce((previous, current) => {
    return previous + current.TVL;
  }, 0);

  // TVL weighted average
  const codeReviewScore = weightedAverage(scores, 'codeReviewScore', tvl);
  const testingScore = weightedAverage(scores, 'testingScore', tvl);
  const auditScore = weightedAverage(scores, 'auditScore', tvl);
  const protocolSafetyScore = weightedAverage(
    scores,
    'protocolSafetyScore',
    tvl
  );
  const complexityScore = weightedAverage(scores, 'complexityScore', tvl);
  const teamKnowledgeScore = weightedAverage(scores, 'teamKnowledgeScore', tvl);

  // maximum value
  const longevityScore = Math.max.apply(
    Math,
    scores.map((score) => score.longevityScore)
  );

  return {
    codeReviewScore,
    testingScore,
    auditScore,
    protocolSafetyScore,
    complexityScore,
    teamKnowledgeScore,
    longevityScore,
    TVL: tvl,
  };
};
