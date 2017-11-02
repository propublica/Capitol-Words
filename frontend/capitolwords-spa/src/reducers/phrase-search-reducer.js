import {
  PHRASE_SEARCH_REQUESTED,
  PHRASE_SEARCH_FETCH_SUCCEEDED,
  PHRASE_SEARCH_FETCH_FAILED,
} from '../actions/search-actions';

/**
 * This reducer is used to store information about a term or phrase search.
 */
const initialState = {
  isSearching: false,
  isSearchFailure: false,
  phrase: null,
  results: null,
  isModal: false,
};

export default function phraseSearch(state=initialState, action) {
  const {
    payload,
    type
  } = action;
  switch (type) {
    case PHRASE_SEARCH_REQUESTED:
      return {
        ...state,
        isSearching: true,
        isSearchFailure: false,
        phrase: payload.phrase,
        results: null,
      };
    case PHRASE_SEARCH_FETCH_SUCCEEDED:
      return {
        ...state,
        isSearching: false,
        isSearchFailure: false,
        results: payload,
      };
    case PHRASE_SEARCH_FETCH_FAILED:
      return {
        ...state,
        isSearching: false,
        isSearchFailure: true,
        results: null,
      };
    default:
      return state;
  }
};
