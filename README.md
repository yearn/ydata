# Yearn Labs

## Vault-level Risk

Currently the most of the code is copypasta from [the yearn-watch repository](https://github.com/yearn/yearn-watch).

Entrypoint is at `src/index.ts`:

```
ts-node src/index.ts
```

when running the above, the expected result is the following:
```
[
  {
    name: 'Curve UST Wormhole Pool yVault',
    codeReviewScore: 2,
    testingScore: 3,
    auditScore: 5,
    protocolSafetyScore: 2,
    complexityScore: 2,
    teamKnowledgeScore: 1,
    longevityScore: 3,
    TVL: 0
  },
  {
    name: 'Curve HUSD Pool yVault',
    codeReviewScore: 3,
    testingScore: 3,
    auditScore: 3.5,
    protocolSafetyScore: 1.5,
    complexityScore: 2,
    teamKnowledgeScore: 1,
    longevityScore: 1,
    TVL: 0
  },
  {
    name: 'Curve EURT Pool yVault',
    codeReviewScore: 2,
    testingScore: 3,
    auditScore: 5,
    protocolSafetyScore: 2,
    complexityScore: 2,
    teamKnowledgeScore: 1,
    longevityScore: 2,
    TVL: 0.032955261095
  },
  {
    name: 'Curve ankrETH Pool yVault',
    codeReviewScore: 2,
    testingScore: 2.9999999999999996,
    auditScore: 5,
    protocolSafetyScore: 2,
    complexityScore: 2,
    teamKnowledgeScore: 1,
    longevityScore: 1,
    TVL: 0.46488896499
  },
```