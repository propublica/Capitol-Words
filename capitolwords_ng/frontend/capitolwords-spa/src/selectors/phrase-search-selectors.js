import { createSelector } from 'reselect';

const getPhraseSearch = state => state.phraseSearch;

export const isSearching = createSelector(
  getPhraseSearch,
  phraseSearch => phraseSearch.isSearching
);

export const isSearchFailure = createSelector(
  getPhraseSearch,
  phraseSearch => phraseSearch.isSearchFailure
);

export const isSearchSuccess = createSelector(
  getPhraseSearch,
  phraseSearch => !!phraseSearch.results
);

export const searchResultCount = createSelector(
  getPhraseSearch,
  phraseSearch => phraseSearch.results && phraseSearch.results.hits.total,
);

export const searchResultList = createSelector(
  getPhraseSearch,
  phraseSearch => phraseSearch.results && phraseSearch.results.hits.hits
);
