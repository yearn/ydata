import { Yearn } from '@yfi/sdk';
import { JsonRpcProvider } from '@ethersproject/providers';
import axios from 'axios';
import { expect } from 'chai';
import { getFilteredStrategies, getStrategies } from '../src/strategy';
import { Grouping, GroupingsList } from '../src/types';

import 'dotenv/config';

describe('strategy', () => {
  // Yearn SDK
  const sdk = new Yearn(1, {
    provider: new JsonRpcProvider(process.env.WEB3_PROVIDER),
    subgraph: {
      mainnetSubgraphEndpoint: process.env.SUBGRAPH_URL,
    },
    cache: { useCache: false },
  });

  describe('getFilteredStrategies', () => {
    it('should fetch strategies from vault address', () => {
      // USDC vault
      const USDCVaultAddress = '0xa354F35829Ae975e850e23e9615b11Da1B3dC4DE';
      return getFilteredStrategies(sdk, {
        vaultAddress: USDCVaultAddress,
      }).then((result) => {
        expect(result.length).to.be.above(0);
        const strategies = result.map((strat) => strat.address);
        const GenLevCompV3Address =
          '0x342491C093A640c7c2347c4FFA7D8b9cBC84D1EB';
        expect(strategies).to.include(GenLevCompV3Address.toLowerCase());
      });
    });

    it('should fetch strategies from vault name', () => {
      // DAI vault
      const DAIVaultName = 'DAI yVault';
      return getFilteredStrategies(sdk, {
        vaultName: DAIVaultName,
      }).then((result) => {
        expect(result.length).to.be.above(0);
        const strategies = result.map((strat) => strat.address);
        const StrategyLenderYieldOptimiserAddress =
          '0x3280499298ACe3FD3cd9C2558e9e8746ACE3E52d';
        expect(strategies).to.include(
          StrategyLenderYieldOptimiserAddress.toLowerCase()
        );
      });
    });

    it('should filter strategies by name', () => {
      // Single-sided strategies
      const nameLike = ['singlesided', 'ssc'];
      return getFilteredStrategies(sdk, {
        nameLike: nameLike,
      }).then((result) => {
        expect(result.length).to.be.above(0);
        const strategies = result.map((strat) => strat.address);
        const ssc_dai_ibAddress = '0xa6D1C610B3000F143c18c75D84BaA0eC22681185';
        expect(strategies).to.include(ssc_dai_ibAddress.toLowerCase());
      });
    });
  });

  describe('getStrategies', () => {
    // Risk Framework groups
    let groups: GroupingsList = [];

    before(async () => {
      const response = await axios(process.env.RISK_FRAMEWORK_JSON as string);
      const groupData = response.data['groups'];
      groups = groupData.filter(
        (group: Grouping) => group.network === 'ethereum'
      );
    });

    it('should filter strategies by address', () => {
      // StrategyLenderYieldOptimiser
      const StrategyLenderYieldOptimiserAddress =
        '0x3280499298ACe3FD3cd9C2558e9e8746ACE3E52d';
      return getStrategies(sdk, groups, {
        address: StrategyLenderYieldOptimiserAddress,
      }).then((result) => {
        expect(result.length).to.be.above(0);
      });
    });

    it('should filter strategies by group id', () => {
      // curve and convex
      const groupIds = ['curve', 'convex'];
      return getStrategies(sdk, groups, {
        groupId: groupIds,
      }).then((result) => {
        expect(result.length).to.be.above(0);
      });
    });
  });
});