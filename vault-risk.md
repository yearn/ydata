# Vault-level Risk

This project aims to provide additional quantitative metrics on top of the existing [Risk Framework](https://github.com/yearn/yearn-watch/blob/main/utils/risks.json), to help discover informative risk measures and collect the data necessary to build the metrics. 
Furthermore, the project also aims to provide aggregated views for Yearn's Vaults and associated DeFi protocols.

## Metrics

Currently the project can provide strategy-level metrics and the vault-level risk metrics for Yearn's V2 vaults.


### Strategy Risk Metrics

* `overallScore` - a profile-specific scalar score representing the risk of the strategy, see Overall Score
  * `high` - profile score for a risk-seeking user
  * `low` - profile score for a risk-averse user
  * `median` - profile score for a median representative user
* `protocols` - associated protocols
  * `name` - name of the protocol shown in [the Process Quality Reviews (PQR) in DeFi Safety](https://www.defisafety.com/pqrs)
  * `DeFiSafetyScores` - PQR scores, the higher the safer
* `riskScores` - breakdown of the `overallScore`. Currently contains only the strategy group scores in the [Risk Framework](https://github.com/yearn/yearn-watch/blob/main/utils/risks.json), the lower the safer
  * `TVLImpact` - amount of TVL
  * `auditScore` - number of auditing firms and recency of the audits
  * `codeReviewScore` - number of reviewers and their expertise
  * `complexityScore` - leverage, external calls, risk of loss
  * `longevityImpact` - how long the code has been live
  * `protocolSafetyScore` - multisig, bug bounties, verified contracts
  * `teamKnowledgeScore` - number of strategists familiar with the strategy
  * `testingScore` - test coverage
* `tokens` - associated ERC20 tokens


### Vault Risk Metrics

* `overallScore` - a profile-specific scalar score representing the risk of the vault, see Overall Score
  * `high` - profile score for a risk-seeking user
  * `low` - profile score for a risk-averse user
  * `median` - profile score for a median representative user
* `protocols` - associated protocols
  * `name` - name of the protocol shown in [the Process Quality Reviews (PQR) in DeFi Safety](https://www.defisafety.com/pqrs)
  * `DeFiSafetyScores` - PQR scores, the higher the safer
  * `TVLRatio` - ratio of the vault TVL that is associated with the protocol
* `riskScores` - breakdown of the `overallScore`. Currently contains only the TVL-weighted averages of the strategy group scores in the [Risk Framework](https://github.com/yearn/yearn-watch/blob/main/utils/risks.json), the lower the safer
  * `auditScore` - TVL-weighted average of the strategy `auditScore`
  * `codeReviewScore` - TVL-weighted average of the strategy `codeReviewScore`
  * `complexityScore` - TVL-weighted average of the strategy `complexityScore`
  * `protocolSafetyScore` - TVL-weighted average of the strategy `protocolSafetyScore`
  * `teamKnowledgeScore` - TVL-weighted average of the strategy `teamKnowledgeScore`
  * `testingScore` - TVL-weighted average of the strategy `testingScore`
* `tokens` - associated ERC20 tokens
  * `name` - symbol of the ERC20 token
  * `TVLRatio` - ratio of the vault TVL that is associated with the token
* `topWallets` - TVL distribution of the top 10 wallets


### Overall Score

We believe that any representation of risk as a single number is going to be highly biased.
Thus we aim to portray a distribution of the scores according to the different risk profiles of our users, which ideally should include our retail customers, contributors and protocol partners.

In this project, the risk profile of a user is depicted as the ordering of the various risk scores, i.e., whether the user thinks that score A is more important than score B.
This information can be collected through surveys or interviews with our users.
The [sample csv](./data/sample_risk_weights.csv) in the repository currently holds some sample orderings (weightings), for the scores shown in the [Risk Framework](https://github.com/yearn/yearn-watch/blob/main/utils/risks.json):

auditScore | codeReviewScore | complexityScore | protocolSafetyScore | teamKnowledgeScore | testingScore | TVLImpact | longevityImpact
:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:
4 | 3 | 5 | 5 | 5 | 3 | 2 | 2
5 | 4 | 2 | 2 | 2 | 3 | 4 | 1
4 | 4 | 3 | 3 | 3 | 3 | 2 | 4
3 | 5 | 4 | 4 | 5 | 3 | 4 | 4
4 | 5 | 5 | 4 | 5 | 3 | 1 | 3

In this case the number 1 stands for having less importance and 5 stands for having more importance.

Once we have the orderings or the weightings, we can assign a ratio to each metric that satisfies the ordering and adds up to 1.0 for each individual.
Then for each entry, we can calculate the weighted average of the metrics for a strategy/vault to obtain a single number (e.g. 3.0).
We repeat this for each entry to get a list of numbers (e.g. [2.7, 3.0, 3.1, ...]) which is now the distribution of the scores according to the different risk profiles of users.

We can choose representatives from this distribution to get a better grasp of our users.
For the illustration we currently calculate the following:
* `median` - the median value from the distribution
* `high` - median + 1.5 IQR
* `low` - median - 1.5 IQR

where IQR stands for the interquartile range of the distribution.


## Examples

Usage examples for this project can be seen in [`examples/risk.ipynb`](./examples/risk.ipynb).


### Strategy Risk Metrics

The following is the output from the PoolTogether USD Coin strategy in the yvWBTC 0.3.5 vault.

```
{'overallScore': {'high': 3.37675585284281,
                  'low': 2.5463210702341135,
                  'median': 2.9615384615384617},
 'protocols': [{'DeFiSafetyScores': {'adminControlsScore': 84.0,
                                     'contractsAndTeamScore': 100.0,
                                     'documentationScore': 94.0,
                                     'oraclesScore': 100.0,
                                     'overallScore': 93.0,
                                     'securityScore': 95.0,
                                     'testingScore': 90.0},
                'Name': 'Compound'},
               {'DeFiSafetyScores': {'adminControlsScore': 91.0,
                                     'contractsAndTeamScore': 100.0,
                                     'documentationScore': 100.0,
                                     'oraclesScore': 100.0,
                                     'overallScore': 95.0,
                                     'securityScore': 95.0,
                                     'testingScore': 86.0},
                'Name': 'PoolTogether'}],
 'riskScores': {'TVLImpact': 0,
                'auditScore': 5,
                'codeReviewScore': 2,
                'complexityScore': 3,
                'longevityImpact': 1,
                'protocolSafetyScore': 3,
                'teamKnowledgeScore': 5,
                'testingScore': 4},
 'tokens': ['PcUSDC', 'COMP', 'yvUSDC', 'POOL']}
```


### Vault Risk Metrics

The following is the output from the yvWBTC 0.3.5 vault.

```
{'overallScore': {'high': 2.2752366800075863,
                  'low': 1.7845149064132193,
                  'median': 2.029875793210403},
 'protocols': [{'DeFiSafetyScores': {'adminControlsScore': 71.0,
                                     'contractsAndTeamScore': 68.0,
                                     'documentationScore': 84.0,
                                     'oraclesScore': None,
                                     'overallScore': 81.0,
                                     'securityScore': 96.0,
                                     'testingScore': 75.0},
                'Name': 'Maker',
                'TVL Ratio': 0.0},
               {'DeFiSafetyScores': {'adminControlsScore': 97.0,
                                     'contractsAndTeamScore': 100.0,
                                     'documentationScore': 94.0,
                                     'oraclesScore': 100.0,
                                     'overallScore': 93.0,
                                     'securityScore': 95.0,
                                     'testingScore': 72.0},
                'Name': 'Curve.fi',
                'TVL Ratio': 0.12377062260389834},
               {'DeFiSafetyScores': {'adminControlsScore': 86.0,
                                     'contractsAndTeamScore': 100.0,
                                     'documentationScore': 95.0,
                                     'oraclesScore': None,
                                     'overallScore': 95.0,
                                     'securityScore': 95.5,
                                     'testingScore': 98.5},
                'Name': 'Aave',
                'TVL Ratio': 0.0},
               {'DeFiSafetyScores': {'adminControlsScore': 89.0,
                                     'contractsAndTeamScore': 100.0,
                                     'documentationScore': 93.0,
                                     'oraclesScore': None,
                                     'overallScore': 96.0,
                                     'securityScore': 95.0,
                                     'testingScore': 100.0},
                'Name': 'Aave V2',
                'TVL Ratio': 0.0},
               {'DeFiSafetyScores': {'adminControlsScore': 84.0,
                                     'contractsAndTeamScore': 100.0,
                                     'documentationScore': 94.0,
                                     'oraclesScore': 100.0,
                                     'overallScore': 93.0,
                                     'securityScore': 95.0,
                                     'testingScore': 90.0},
                'Name': 'Compound',
                'TVL Ratio': 3.6448743907626444e-07},
               {'DeFiSafetyScores': {'adminControlsScore': 82.0,
                                     'contractsAndTeamScore': 100.0,
                                     'documentationScore': 100.0,
                                     'oraclesScore': 100.0,
                                     'overallScore': 94.0,
                                     'securityScore': 100.0,
                                     'testingScore': 90.0},
                'Name': 'Balancer',
                'TVL Ratio': 0.8762290129086625}],
 'riskScores': {'auditScore': 4.123770622603898,
                'codeReviewScore': 2.0,
                'complexityScore': 3.0000007289748782,
                'protocolSafetyScore': 1.0,
                'teamKnowledgeScore': 2.0,
                'testingScore': 2.123770622603898},
 'tokens': [{'Name': 'yvWBTC', 'TVL Ratio': 0.12377098709133741},
            {'Name': 'WBTC', 'TVL Ratio': 1.0},
            {'Name': 'DAI', 'TVL Ratio': 0.0},
            {'Name': 'yvDAI', 'TVL Ratio': 0.0},
            {'Name': 'yvCurve-HBTC', 'TVL Ratio': 0.12377062260389834},
            {'Name': 'hCRV', 'TVL Ratio': 0.12377062260389834},
            {'Name': 'vWBTC', 'TVL Ratio': 0.0},
            {'Name': 'VSP', 'TVL Ratio': 0.0},
            {'Name': 'bBTC/sbtcCRV', 'TVL Ratio': 0.0},
            {'Name': 'yvCurve-BBTC', 'TVL Ratio': 0.0},
            {'Name': 'yvCurve-pBTC', 'TVL Ratio': 0.0},
            {'Name': 'pBTC/sbtcCRV', 'TVL Ratio': 0.0},
            {'Name': 'oBTC/sbtcCRV', 'TVL Ratio': 0.0},
            {'Name': 'yvCurve-oBTC', 'TVL Ratio': 0.0},
            {'Name': 'MM', 'TVL Ratio': 0.0},
            {'Name': 'mWBTC', 'TVL Ratio': 0.0},
            {'Name': 'cETH', 'TVL Ratio': 3.6448743907626444e-07},
            {'Name': 'COMP', 'TVL Ratio': 3.6448743907626444e-07},
            {'Name': 'WETH', 'TVL Ratio': 3.6448743907626444e-07},
            {'Name': 'cWBTC', 'TVL Ratio': 3.6448743907626444e-07},
            {'Name': 'cDAI', 'TVL Ratio': 0.0},
            {'Name': 'staBAL3-BTC', 'TVL Ratio': 0.8762290129086625},
            {'Name': 'BAL', 'TVL Ratio': 0.8762290129086625},
            {'Name': 'staBAL3-BTC-gauge', 'TVL Ratio': 0.8762290129086625}],
 'topWallets': [['0x92Be6ADB6a12Da0CA607F9d87DB2F9978cD6ec3E',
                 0.24285785200456952],
                ['0x4b92d19c11435614CD49Af1b589001b7c08cD4D5',
                 0.23791877080538126],
                ['0x53a393Fbc352fAd69BAEdEFA46C4C1085bb6D707',
                 0.09661537452302911],
                ['0x8D9487b81e0fEdcd2D8Cab91885756742375CDC5',
                 0.06916830311925562],
                ['0xA696a63cc78DfFa1a63E9E50587C197387FF6C7E',
                 0.05578875019901013],
                ['0x13e382dfe53207E9ce2eeEab330F69da2794179E',
                 0.039635294920950734],
                ['0xe215A738C44fFd8E917b78985C5903a20E201683',
                 0.02950394075032685],
                ['0xC4f2498B13780754629e7c82Ac300E6f74603425',
                 0.0227234001247493],
                ['0x5f0845101857d2A91627478e302357860b1598a1',
                 0.02133250387901777],
                ['0xa84c1C4ab43eF351AC60bb1AB08D2BbF76AA2A23',
                 0.020178506718973404]]}
```