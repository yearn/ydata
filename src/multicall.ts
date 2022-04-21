import { providers, BigNumber } from 'ethers';
import { get, omit } from 'lodash';
import {
    Multicall,
    ContractCallContext,
    ContractCallResults,
    ContractCallReturnContext,
} from 'ethereum-multicall';
import { Strategy, StrategyParams, StrategyAddressQueueIndex } from './types';
import { isValidTimestamp, toIsoString, toHumanDateText } from './utils';
import { getABI } from './contracts/ABI';
import StratABI from './contracts/ABI/Strategy.json';
import TokenABI from './contracts/ABI/Token.json';

import 'dotenv/config';

interface VaultVersionInfo {
    apiVersion: string;
    want: string;
}

const STRAT_VIEW_METHODS = [
    'apiVersion',
    'emergencyExit',
    'isActive',
    'keeper',
    'rewards',
    'strategist',
    'name',
    'vault',
    'estimatedTotalAssets',
    'delegatedAssets',
    'want',
    'doHealthCheck',
    'healthCheck',
];

const STRAT_PARAM_METHODS: string[] = [
    'debtOutstanding',
    'creditAvailable',
    'expectedReturn',
    'strategies',
];

const TOKEN_VIEW_METHODS: string[] = ['decimals', 'symbol', 'name'];

const STRATEGIES_METHOD = 'strategies';

const STRAT_PARAMS_V030: string[] = [
    'performanceFee',
    'activation',
    'debtRatio',
    'rateLimit',
    'lastReport',
    'totalDebt',
    'totalGain',
    'totalLoss',
];

const STRAT_PARAMS_V032: string[] = [
    'performanceFee',
    'activation',
    'debtRatio',
    'minDebtPerHarvest',
    'maxDebtPerHarvest',
    'lastReport',
    'totalDebt',
    'totalGain',
    'totalLoss',
];

const mapVersions = new Map<string, string[]>();
mapVersions.set('0.3.0', STRAT_PARAMS_V030);
mapVersions.set('0.3.1', STRAT_PARAMS_V030);
mapVersions.set('0.3.2', STRAT_PARAMS_V032);
mapVersions.set('0.3.3', STRAT_PARAMS_V032);
mapVersions.set('0.3.3.Edited', STRAT_PARAMS_V030);

export const getMulticallContract = (): Multicall => {
    const provider = new providers.AlchemyProvider(
        'homestead',
        process.env.ALCHEMY_KEY
    );
    return new Multicall({
        ethersProvider: provider,
        tryAggregate: true,
    });
};

const buildViewMethodsCall = (
    strategies: string[],
    viewMethods: string[] = STRAT_VIEW_METHODS
): ContractCallContext[] => {
    return strategies.map((stratAddres) => {
        const calls = viewMethods.map((method) => ({
            reference: method,
            methodName: method,
            methodParameters: [] as string[],
        }));
        return {
            reference: stratAddres,
            contractAddress: stratAddres,
            abi: StratABI.abi,
            calls,
        };
    });
};

const _handleSingleValue = (value: unknown): unknown => {
    if (get(value, 'type') === 'BigNumber') {
        return BigNumber.from(value).toString();
    }
    return value;
};

const _handleContractValues = (value: unknown): unknown => {
    if (Array.isArray(value)) {
        if (value.length === 1) {
            if (Array.isArray(value[0])) {
                // Preserve array nesting
                return [_handleContractValues(value[0])];
            }
            return _handleSingleValue(value[0]);
        }
        return value.map((v) => _handleContractValues(v));
    }
    return _handleSingleValue(value);
};

const mapContractCalls = (result: ContractCallReturnContext) => {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const mappedObj: any = { errors: [] };
    result.callsReturnContext.forEach(
        ({ methodName, returnValues, success }) => {
            if (success && returnValues && returnValues.length > 0) {
                mappedObj[methodName] = _handleContractValues(returnValues);
            } else {
                mappedObj.errors.push(methodName);
            }
        }
    );
    return mappedObj;
};

const buildParamMethodsCall = (
    strategies: string[],
    strategyMap: Map<string, string>,
    vaultMap: Map<string, VaultVersionInfo>
): ContractCallContext[] => {
    return strategies.map((stratAddres) => {
        const vaultAddress = strategyMap.get(stratAddres) as string;
        const vaultInfo = vaultMap.get(vaultAddress) as VaultVersionInfo;
        const abiParams = getABI(vaultInfo.apiVersion);
        const calls = STRAT_PARAM_METHODS.map((method) => ({
            reference: method === 'strategies' ? 'strategyParams' : method,
            methodName: method,
            methodParameters: [stratAddres],
        }));
        return {
            reference: `${stratAddres}_${vaultAddress}`,
            contractAddress: vaultAddress,
            abi: abiParams,
            calls,
        };
    });
};

const buildTokenCallMethods = (
    strategies: string[],
    strategyMap: Map<string, string>,
    vaultMap: Map<string, VaultVersionInfo>
): ContractCallContext[] => {
    return strategies.map((stratAddres) => {
        const vaultAddress = strategyMap.get(stratAddres) as string;
        const vaultInfo = vaultMap.get(vaultAddress) as VaultVersionInfo;

        const calls = TOKEN_VIEW_METHODS.map((method) => ({
            reference: method,
            methodName: method,
            methodParameters: [] as string[],
        }));
        return {
            reference: `${vaultInfo.want}`,
            contractAddress: vaultInfo.want,
            abi: TokenABI.abi,
            calls,
        };
    });
};

const mapParamDisplayValues = (param: any): StrategyParams => {
    if (param.activation && isValidTimestamp(param.activation)) {
        param.activation = toIsoString(param.activation);
    }
    if (param.lastReport && isValidTimestamp(param.lastReport)) {
        const { lastReport } = param;
        param.lastReport = toIsoString(lastReport);
        param.lastReportText = toHumanDateText(lastReport);
    }

    return param;
};

export const mapStrategyParams = (
    result: ContractCallReturnContext,
    apiVersion: string
): StrategyParams => {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const params: any = { errors: [] };
    result.callsReturnContext.forEach(
        ({ methodName, returnValues, success }) => {
            if (
                success &&
                methodName === STRATEGIES_METHOD &&
                returnValues &&
                returnValues.length > 0
            ) {
                // TODO: resolve version ABI based on vault instead of strategy
                const props = mapVersions.get(apiVersion) || STRAT_PARAMS_V032;

                returnValues.forEach((val, i) => {
                    // eslint-disable-next-line @typescript-eslint/ban-ts-comment
                    // @ts-ignore
                    params[props[i]] = BigNumber.from(val).toString();
                });
            } else {
                params.errors.push(methodName);
            }
        }
    );

    return mapParamDisplayValues(params);
};

export const mapStrategiesCalls = (
    strategies: string[],
    contractCallsResults: ContractCallResults,
    strategiesQueueIndexes: Array<StrategyAddressQueueIndex>,
    strategyMap: Map<string, string>
): Strategy[] => {
    return strategies.map((address) => {
        const stratData = contractCallsResults.results[address];
        const vaultStratData =
            contractCallsResults.results[
                `${address}_${strategyMap.get(address)}`
            ];
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const mappedStrat: any = mapContractCalls(stratData);
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const mappedVaultStratInfo: any = omit(
            mapContractCalls(vaultStratData),
            'strategies'
        );
        const mappedStratParams: StrategyParams = mapStrategyParams(
            vaultStratData,
            mappedStrat.apiVersion
        );
        const tokenData = contractCallsResults.results[mappedStrat.want];
        if (tokenData) {
            const token = mapContractCalls(tokenData);
            mappedStrat.token = {
                ...token,
                address: mappedStrat.want,
            };
        }
        const strategyWithdrawalQueueIndex = strategiesQueueIndexes.find(
            (queueIndex) =>
                queueIndex.address.toLowerCase() === address.toLowerCase()
        );
        const withdrawalQueueIndex =
            strategyWithdrawalQueueIndex === undefined
                ? -1
                : strategyWithdrawalQueueIndex.queueIndex;
        if (!mappedStrat.healthCheck) {
            mappedStrat.healthCheck = null;
        }
        if (!mappedStrat.doHealthCheck) {
            mappedStrat.doHealthCheck = false;
        }
        return {
            ...mappedVaultStratInfo,
            ...mappedStrat,
            address,
            params: mappedStratParams,
            withdrawalQueueIndex,
        };
    });
};

export const getStrategies = async (
    addresses: string[]
): Promise<Strategy[]> => {
    if (addresses.length === 0) {
        throw new Error('Expected a valid strategy address');
    }

    const multicall = getMulticallContract();

    // do call to strategy apiVersion and vault
    const stratCalls: ContractCallContext[] = buildViewMethodsCall(addresses);

    const resultsViewMethods: ContractCallResults = await multicall.call(
        stratCalls
    );
    const vaultMap = new Map<string, VaultVersionInfo>();
    const strategyMap = new Map<string, string>();

    addresses.forEach((address) => {
        const stratData = resultsViewMethods.results[address];
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const mappedStrat: any = mapContractCalls(stratData);
        strategyMap.set(address, mappedStrat.vault);
        vaultMap.set(mappedStrat.vault, {
            apiVersion: mappedStrat.apiVersion,
            want: mappedStrat.want,
        });
    });

    const stratParamCalls = buildParamMethodsCall(
        addresses,
        strategyMap,
        vaultMap
    );
    const tokenMethodCalls = buildTokenCallMethods(
        addresses,
        strategyMap,
        vaultMap
    );

    const stratParamResults: ContractCallResults = await multicall.call(
        stratParamCalls.concat(tokenMethodCalls)
    );

    const mergedResults: ContractCallResults = {
        results: {
            ...resultsViewMethods.results,
            ...stratParamResults.results,
        },
        blockNumber: stratParamResults.blockNumber,
    };

    const mappedStrategies = mapStrategiesCalls(
        addresses,
        mergedResults,
        [],
        strategyMap
    );

    return mappedStrategies;
};
