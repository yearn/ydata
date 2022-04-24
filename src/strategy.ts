import { Yearn, Vault } from '@yfi/sdk';
import { StrategyContext, Strategy, GroupingsList } from './types';
import { getStrategiesMulticall } from './multicall';
import { getStrategiesByVaults } from './subgraph';
import { toArray } from './utils';

const getFilteredStrategies = async (
  sdk: Yearn<1>,
  context?: StrategyContext
): Promise<Strategy[]> => {
  // get vaults from the SDK
  let vaults: Vault[] = [];
  if (context) {
    if (context.vaultAddress) {
      const addresses = toArray(context.vaultAddress);
      vaults = await sdk.vaults.get(addresses);
    } else {
      vaults = await sdk.vaults.get();
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
    vaults = await sdk.vaults.get();
  }
  // get strategies from the subgraph
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
  // get strategy info from the chain
  return getStrategiesMulticall(result.map((strat) => strat.address));
};

export const getStrategies = async (
  sdk: Yearn<1>,
  groups: GroupingsList,
  context?: StrategyContext
): Promise<Strategy[]> => {
  // filter by context
  if (context) {
    if (context.address) {
      const addresses = toArray(context.address);
      return getStrategiesMulticall(addresses);
    } else if (context.nameLike) {
      return getFilteredStrategies(sdk, { nameLike: context.nameLike });
    } else if (context.groupId) {
      const groupIds = toArray(context.groupId);
      const nameLike: string[] = groupIds
        .map(
          (groupId) =>
            groups.filter((group) => group.id === groupId)[0].criteria.nameLike
        )
        .flat();
      return getFilteredStrategies(sdk, { nameLike: nameLike });
    } else if (context.vaultAddress) {
      return getFilteredStrategies(sdk, { vaultAddress: context.vaultAddress });
    } else if (context.vaultName) {
      return getFilteredStrategies(sdk, { vaultName: context.vaultName });
    } else {
      return [];
    }
    // return all strategies
  } else {
    return getFilteredStrategies(sdk);
  }
};
