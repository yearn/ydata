import { VaultRisk } from '../src/index';
import { JsonRpcProvider } from '@ethersproject/providers';
import 'dotenv/config';
import { Yearn } from '@yfi/sdk';

// Yearn SDK
const yearn = new Yearn(1, {
  provider: new JsonRpcProvider(process.env.WEB3_PROVIDER),
  subgraph: {
      mainnetSubgraphEndpoint: process.env.SUBGRAPH_URL,
  },
  cache: { useCache: false },
});

// VaultRisk instance
const vaultRisk = new VaultRisk(
  yearn,
  process.env.RISK_FRAMEWORK_JSON as string
);

async function main() {
  console.log(await vaultRisk.getStrategyScores({groupId: ['singlesided']}));
  console.log(await vaultRisk.getVaultScores({nameLike: ['USDC']}));
}

main();