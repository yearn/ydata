# yData

<div align="center"><img src="https://i.imgur.com/0c0VUEH.png" /></div>
<br/>

Explore yearn through the realm of data analysis

- Live Link: https://ydata.vercel.app/

# About

yData is a web app with analytics for the yearn ecosystem. These are the available visualizations:

## Yearn V2 Vaults

You can scroll through many views in this section, including:

- Group vaults by many factors like Chain, Assets Under Management (AUM) size, Cumulative Return, Asset Type, and others.
- Daily Variation of Deposits and Withdraws, helps you track how much Total Value Locked (TVL) is entering and leaving the yearn protocol.
- Overview of cumulative return since inception plotted against monthly returns.

## Efficient Frontier

An overview of yearn's vaults performance that considers risk factors so you can compare them with other DeFi assets. This table will plot yield options in the following axes:

- **Return:** How much yield does this option generates (higher is better)
- **Volatility:** How much does the yield vary over time (lower means less risk)

In this graph you will find a region where the most risk-efficient assets are, that is the "Efficient Frontier" (highlighted with the red crayon square):

![](https://i.imgur.com/USsUmqB.png)

# Set up and run
1) Clone this repo: `git clone git@github.com:yearn/ydata.git`
2) Install dependencies: `yarn`
3) Run dev environment: `yarn dev`

## Available scripts
- `yarn dev`: start dev environment
- `yarn build`: build for production
- `yarn format`: apply prettier formatting
- `yarn lint`: run linter

# More data resources

- [Yearn official docs](https://docs.yearn.finance/)
- [About yVaults V2](https://docs.yearn.finance/getting-started/products/yvaults/overview)
- [About yearn risk scores](https://docs.yearn.finance/resources/risks/risk-score)
- [yDaemon: unified yearn data API](https://medium.com/@marcoworms/ydaemon-one-api-to-unify-all-yearn-data-4fc74dc9a33b)


<br/>
<div align="center"><img height=700px" src="https://i.imgur.com/9oRSSXn.jpg" /></div>
<br/>
