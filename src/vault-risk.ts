import BigNumber from 'bignumber.js';
import axios from 'axios';
import { Yearn, Vault } from '@yfi/sdk';
import { getStrategiesByVaults } from './subgraph';
import { getStrategies } from './multicall';
import {
  StrategyContext,
  VaultContext,
  StrategyScores,
  VaultScores,
  Strategy,
  Grouping,
  GroupingsList,
} from './types';
import { toArray, isValidTimestamp, getTokenPrice, amountToMMs } from './utils';
import { aggregateScores } from './aggregation';

/**
 * Wrapper class for the vault-level risk project
 */
export class VaultRisk {
  sdk: Yearn<1>; // FIXME: currently the following only works for the mainnet
  url: string;

  /**
   * Create a VaultRisk instance
   * @param sdk - the Yearn SDK for the mainnet
   * @param riskFrameworkUrl - the url address of the Risk Framework scoring (json) file
   */
  constructor(sdk: Yearn<1>, riskFrameworkUrl: string) {
    this.sdk = sdk;
    this.url = riskFrameworkUrl;
  }

  /** Returns the list of scores from the Risk Framework */
  async getRiskFrameworkScores(): Promise<GroupingsList> {
    const response = await axios(this.url);
    const groupData = response.data['groups'];
    return groupData.filter((group: Grouping) => group.network === 'ethereum');
  }

  /**
   * Returns the list of strategies from the subgraph
   * @param context - query params for the strategy
   * @returns the list of strategy params relevant to the risk framework
   */
  async getStrategies(context?: StrategyContext): Promise<Strategy[]> {
    let vaults: Vault[] = [];
    if (context) {
      if (context.vaultAddress) {
        const addresses = toArray(context.vaultAddress);
        vaults = await this.sdk.vaults.get(addresses);
      } else {
        vaults = await this.sdk.vaults.get();
      }
      if (context.vaultName) {
        const vaultNames = toArray(context.vaultName);
        vaults = vaults.filter((vault) =>
          vaultNames.some((name) =>
            vault.name.toLowerCase().includes(name.toLowerCase())
          )
        );
      }
    } else {
      vaults = await this.sdk.vaults.get();
    }

    const vaultStrategies = await getStrategiesByVaults(
      vaults.map((vault) => vault.address)
    );
    let result = Object.keys(vaultStrategies)
      .map((key) => vaultStrategies[key])
      .flat();

    // filter by name if provided
    if (context && context.nameLike) {
      const names = toArray(context.nameLike);
      result = result.filter((strat) =>
        names.some((name) =>
          strat.name.toLowerCase().includes(name.toLowerCase())
        )
      );
    }

    return getStrategies(result.map((strat) => strat.address));
  }

  /**
   * Returns the scores for each strategy
   * @param context - query params for the strategy
   * @returns the list of risk scores for each strategy
   */
  async getStrategyScores(context: StrategyContext): Promise<StrategyScores[]> {
    // get group scores from the risk framework
    const groups = await this.getRiskFrameworkScores();

    // get list of strategies
    let strategies: Strategy[] = [];
    if (context.address) {
      const addresses = toArray(context.address);
      strategies = await getStrategies(addresses);
    } else if (context.nameLike) {
      strategies = await this.getStrategies({
        nameLike: context.nameLike,
      });
    } else if (context.groupId) {
      const groupIds = toArray(context.groupId);
      const nameLike: string[] = groupIds
        .map(
          (groupId) =>
            groups.filter((group) => group.id === groupId)[0].criteria.nameLike
        )
        .flat();
      strategies = await this.getStrategies({
        nameLike: nameLike,
      });
    } else if (context.vaultAddress) {
      strategies = await this.getStrategies({
        vaultAddress: context.vaultAddress,
      });
    } else if (context.vaultName) {
      strategies = await this.getStrategies({
        vaultName: context.vaultName,
      });
    } else {
      return [];
    }

    // get TVL and longevity from each strategy
    const strategyScores: StrategyScores[] = [];
    for (var strategy of strategies) {
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
      loop: for (var group of groups) {
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
            strategyScores.push({
              name: strategy.name,
              ...metrics,
              longevityScore,
              TVL: amountToMMs(estimatedUSDC),
            });
            break loop;
          }
        }
      }
    }
    return strategyScores;
  }

  /**
   * Returns the scores for each vault
   * @param context - query params for the strategy
   * @returns the list of risk scores for each vault
   */
  async getVaultScores(context: VaultContext): Promise<VaultScores> {
    let strategyContext: StrategyContext = {
      vaultAddress: context.address,
      vaultName: context.nameLike,
    };
    const strategyScores: StrategyScores[] = await this.getStrategyScores(
      strategyContext
    );
    return aggregateScores(strategyScores);
  }
}
