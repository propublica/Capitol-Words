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
  phraseSearch => phraseSearch.results && phraseSearch.results.current_period.total_count
);

export const searchResultList = createSelector(
  getPhraseSearch,
  phraseSearch => phraseSearch.results && phraseSearch.results.docs
);

export const searchContent = createSelector(
  getPhraseSearch,
  phraseSearch => phraseSearch.results && phraseSearch.results.term
);

export const searchDelta = createSelector(
  getPhraseSearch,
  phraseSearch => phraseSearch.results && phraseSearch.results.delta
);

export const dailyBreakdown = createSelector(
  getPhraseSearch,
  phraseSearch => phraseSearch.results && phraseSearch.results.current_period.daily_breakdown
);

// export const searchSpeakersList = createSelector(
//   getPhraseSearch,
//   phraseSearch => phraseSearch.results && phraseSearch.results.)
