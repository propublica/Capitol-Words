import { createSelector } from 'reselect';

import { parse } from 'query-string';

const getRouter = state => state.router;

export const searchString = createSelector(
  getRouter,
  ({ location }) => {
    const query = parse(location.search);
    return typeof query.q === 'string' ? query.q : null;
  }
);