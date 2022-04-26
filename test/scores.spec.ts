import axios from 'axios';
import { expect } from 'chai';
import { Grouping, GroupingsList } from '../src/types';

describe('scores', () => {
  describe('getRiskFrameworkScores', () => {
    // Risk Framework groups
    let groups: GroupingsList = [];

    before(async () => {
      const response = await axios(process.env.RISK_FRAMEWORK_JSON as string);
      const groupData = response.data['groups'];
      groups = groupData.filter(
        (group: Grouping) => group.network === 'ethereum'
      );
    });

    it('should return the scores for a given strategy', () => {});
  });

  describe('getLongevityScore', () => {});

  describe('getTVL', () => {
    it('should return the correct TVL for a given strategy', () => {});
  });
});
