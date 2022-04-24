import axios from 'axios';
import { Yearn } from '@yfi/sdk';
import { getStrategies } from './strategy';
import {
  StrategyContext,
  VaultContext,
  StrategyScores,
  VaultScores,
  Grouping,
  GroupingsList,
} from './types';
import { aggregateScores } from './aggregation';
import { getLongevityScore, getRiskFrameworkScores, getTVL } from './scores';

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
  async getRiskFramework(): Promise<GroupingsList> {
    const response = await axios(this.url);
    const groupData = response.data['groups'];
    return groupData.filter((group: Grouping) => group.network === 'ethereum');
  }

  /**
   * Returns the scores for each strategy
   * @param context - query params for the strategy
   * @returns the list of risk scores for each strategy
   */
  async getStrategyScores(context: StrategyContext): Promise<StrategyScores[]> {
    const groups = await this.getRiskFramework();
    const strategies = await getStrategies(this.sdk, groups, context);

    // get scores for each strategy
    const strategyScores: StrategyScores[] = [];
    for (var strategy of strategies) {
      const longevityScore = getLongevityScore(strategy);
      const TVL = await getTVL(strategy);
      const riskFrameworkScores = getRiskFrameworkScores(strategy, groups);
      strategyScores.push({
        name: strategy.name,
        ...riskFrameworkScores,
        longevityScore,
        TVL,
      });
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
