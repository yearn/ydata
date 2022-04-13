import axios from 'axios';
import { memoize, values } from 'lodash';
import { StrategyApi } from './types';
import 'dotenv/config';

type StrategyBasicData = {
    [vault: string]: StrategyApi[];
};

type VaultGQLResult = {
    id: string;
    strategies: StrategyApi[];
};

type GQLResult = {
    data: {
        vaults: VaultGQLResult[];
    };
};

type SubgraphAPIResponse = {
    data: {
        data?: any;
        errors?: any[];
    };
    status: number;
    statusText: string;
    config: any;
    request: any;
    headers: any;
};

type SubgraphResponse = {
    data: any;
};

const querySubgraph = async (query: string): Promise<SubgraphResponse> => {
    const subgraphUrl = process.env.SUBGRAPH_URL;
    try {
        const response: SubgraphAPIResponse = await axios.post(
            `${subgraphUrl}`,
            {
                query,
            }
        );
        if (
            response.data.errors !== undefined &&
            response.data.errors.length > 0
        ) {
            throw Error(
                response.data.errors[0].message ||
                    'Error: retrieving data from subgraph'
            );
        }
        return {
            data: response.data.data,
        };
    } catch (error) {
        console.error('subgraph error', error);
        throw error;
    }
};

// Functions with more than 2 parameters need a custom key defined for memoization to work correctly.
export const querySubgraphData = memoize(querySubgraph, (...args) =>
    values(args).join('_')
);

export const getStrategiesByVaults = async (
    vaults: string[]
): Promise<StrategyBasicData> => {
    if (!vaults || vaults.length === 0) {
        return {};
    }

    const vaultsLower = vaults.map((vault) => vault.toLowerCase());
    const query = `
        {
            vaults(where:{
                id_in: ${JSON.stringify(vaultsLower)}
            }){
                id
                strategies {
                    name
                    address
                }
            }
        }
    `;

    const results: GQLResult = await querySubgraphData(query);
    const result: StrategyBasicData = {};
    results.data.vaults.forEach(({ id, strategies }) => {
        result[id] = strategies;
    });
    return result;
};
