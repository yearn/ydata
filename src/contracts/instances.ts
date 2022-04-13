import { Contract, providers } from 'ethers';
import OracleABI from './ABI/Oracle.json';

const ETH_ORACLE_CONTRACT_ADDRESS =
    '0x83d95e0d5f402511db06817aff3f9ea88224b030';

export const getOracleInstance = (): Contract => {
    const address = ETH_ORACLE_CONTRACT_ADDRESS;
    const provider = new providers.AlchemyProvider(
        'homestead',
        process.env.ALCHEMY_KEY
    );
    return new Contract(address, OracleABI, provider);
};