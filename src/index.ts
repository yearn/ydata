import axios from 'axios';
import BigNumber from 'bignumber.js';
import { Yearn } from '@yfi/sdk';
import { JsonRpcProvider } from '@ethersproject/providers';
import { getStrategiesByVaults } from './subgraph';
import { getStrategies } from './multicall';
import { isValidTimestamp } from './date_utils';
import { getTokenPrice, amountToMMs } from './price';
import { Grouping } from './types/grouping';

import 'dotenv/config';

type StrategyScores = {
    name: string;
    vaultName: string;
    codeReviewScore: number;
    testingScore: number;
    auditScore: number;
    protocolSafetyScore: number;
    complexityScore: number;
    teamKnowledgeScore: number;
    longevityScore: number;
    TVL: number;
};

type VaultScores = {
    name: string;
    codeReviewScore: number;
    testingScore: number;
    auditScore: number;
    protocolSafetyScore: number;
    complexityScore: number;
    teamKnowledgeScore: number;
    longevityScore: number;
    TVL: number;
};

// FIXME: currently the following only works for the mainnet
const getStrategyScores = async () => {
    // super cool Yearn SDK
    const chainId = 1;
    const yearn = new Yearn(chainId, {
        provider: new JsonRpcProvider(process.env.WEB3_PROVIDER),
        subgraph: {
            mainnetSubgraphEndpoint: process.env.SUBGRAPH_URL,
        },
        cache: { useCache: false },
    });

    // get list of strategies from the subgraph
    const vaults = await yearn.vaults.get();
    const vaultStrategies = await getStrategiesByVaults(
        vaults.map((vault) => vault.address)
    );
    const addresses = Object.keys(vaultStrategies)
        .map((key) => vaultStrategies[key])
        .flat()
        .map((strat) => strat.address);
    const strategies = await getStrategies(addresses);

    // get the risk-framework json file
    const file_url = process.env.RISK_FRAMEWORK_JSON as string;
    const response = await axios(file_url);
    const groupData = response.data['groups'];
    const groupMainnet = groupData.filter(
        (group: Grouping) => group.network === 'ethereum'
    );

    // get TVL and longevity from each strategy
    const strategyScores: StrategyScores[] = [];
    for (var strategy of strategies) {
        // get vault name
        let vaultName = '';
        for (var vault of vaults) {
            if (vault.address === strategy.vault) {
                vaultName = vault.name;
                break;
            }
        }
        // get longevity score
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

        // get TVL in USDC
        let estimatedUSDC = new BigNumber(0);
        if (strategy.estimatedTotalAssets) {
            estimatedUSDC = await getTokenPrice(
                strategy.token,
                strategy.estimatedTotalAssets
            );
        }

        // Risk Framework scores
        loop: for (var group of groupMainnet) {
            // exclude
            for (var name of group.criteria.exclude) {
                if (strategy.name.toLowerCase().includes(name)) {
                    continue loop;
                }
            }
            // include
            for (var name of group.criteria.nameLike) {
                if (strategy.name.toLowerCase().includes(name)) {
                    break loop;
                }
            }
        }
        const { id, network, label, criteria, ...metrics } = group;

        strategyScores.push({
            name: strategy.name,
            vaultName,
            ...metrics,
            longevityScore,
            TVL: amountToMMs(estimatedUSDC),
        });
    }
    return strategyScores;
};

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

const aggregateScores = (scores: StrategyScores[]): VaultScores => {
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
    const teamKnowledgeScore = weightedAverage(
        scores,
        'teamKnowledgeScore',
        tvl
    );

    // maximum value
    const longevityScore = Math.max.apply(
        Math,
        scores.map((score) => score.longevityScore)
    );

    return {
        name: scores[0].vaultName,
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

const main = async () => {
    // fetch the metrics for individual strategies
    const strategyScores = await getStrategyScores();

    // group them by vaults
    const vaultStrategyScores = strategyScores.reduce((previous, current) => {
        if (!previous[current.vaultName]) {
            previous[current.vaultName] = [] as StrategyScores[];
        }
        previous[current.vaultName].push(current);
        return previous;
    }, {} as any);

    // aggregate!
    const vaults = Object.keys(vaultStrategyScores);
    const result = vaults.map((key) =>
        aggregateScores(vaultStrategyScores[key])
    );
    console.log(result);
};

main();
