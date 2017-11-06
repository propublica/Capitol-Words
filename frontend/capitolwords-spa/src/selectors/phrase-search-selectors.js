import { createSelector } from 'reselect';

const getPhraseSearch = state => state.phraseSearch;

const phraseSearchResults = createSelector(
  getPhraseSearch,
  phraseSearch => phraseSearch.results
);

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
  phraseSearchResults,
  results => results && results.current_period.total_count
);

export const searchResultDocs = createSelector(
  phraseSearchResults,
  results => results && results.docs
);

export const searchDelta = createSelector(
  phraseSearchResults,
  results => results && results.delta
);

export const dailyBreakdown = createSelector(
  phraseSearchResults,
  results => results && results.current_period.daily_breakdown
);

function processSpeaker(s) {
  return {
    url: s.bio_page_url,
    imageUrl: s.im_url,
    party: s.party,
  };
}

function docToSearchResultItem(doc) {
  return {
    id: doc._id,
    displayDate: doc.human_date,
    mentionCount: doc.mentions,
    title: doc._source.title,
    docUrl: doc._source.html_url,
    snippet: doc.snippet,
    speakers: doc.speakers.map(processSpeaker)
  };
}

// export const searchSpeakersList = createSelector(
//   getPhraseSearch,
//   phraseSearch => phraseSearch.results && phraseSearch.results.)

export const searchResultList = createSelector(
  searchResultDocs,
  docs => docs && docs.map(docToSearchResultItem)
);
