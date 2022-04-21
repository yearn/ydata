import BigNumber from 'bignumber.js';
import { Contract, providers, BigNumberish } from 'ethers';
import TokenABI from '../contracts/ABI/Token.json';
import OracleABI from '../contracts/ABI/Oracle.json';
import { Strategy, Token } from '../types';

export const USDC_DECIMALS = 6;

const ETH_ORACLE_CONTRACT_ADDRESS =
    '0x83d95e0d5f402511db06817aff3f9ea88224b030';

export const getDust = async (strategy: Strategy) => {
    const provider = new providers.AlchemyProvider(
        'homestead',
        process.env.ALCHEMY_KEY
    );
    const token = new Contract(strategy.token.address, TokenABI.abi, provider);
    return await token.balanceOf(strategy.address);
};

export const getOracleInstance = (): Contract => {
    const address = ETH_ORACLE_CONTRACT_ADDRESS;
    const provider = new providers.AlchemyProvider(
        'homestead',
        process.env.ALCHEMY_KEY
    );
    return new Contract(address, OracleABI, provider);
};

export const toUnits = (amount: BigNumberish, decimals: number): BigNumber => {
    return new BigNumber(amount.toString()).div(
        new BigNumber(10).pow(decimals)
    );
};

export const getTokenPrice = async (
    token: Token,
    amount: BigNumberish
): Promise<BigNumber> => {
    try {
        const oracle = getOracleInstance();
        const result = await oracle['getNormalizedValueUsdc(address,uint256)'](
            token.address,
            amount.toString()
        );
        return toUnits(result, USDC_DECIMALS);
    } catch (error) {
        console.error(error);
        return new BigNumber(0);
    }
};

export const amountToMMs = (amount: BigNumber): number => {
    return amount.div(new BigNumber(1000000)).toNumber();
};
