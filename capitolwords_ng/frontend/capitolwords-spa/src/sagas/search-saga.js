import {
  call,
  put,
  takeLatest
} from 'redux-saga/effects';

import {
  PHRASE_SEARCH_REQUESTED,
  phraseSearchFetchSucceeded,
  phraseSearchFetchFailed,
} from '../actions/search-actions';

import { fetchPhraseSearch } from '../api/api';

function* requestPhraseSearch(action) {
   try {
      const result = yield call(fetchPhraseSearch, action.payload.phrase);
      yield put(phraseSearchFetchSucceeded(result));
   } catch (e) {
      yield put(phraseSearchFetchFailed());
   }
}

/**
 * Fetch term/phrase search results whenever requested.
 */
function* searchSaga() {
  yield takeLatest(PHRASE_SEARCH_REQUESTED, requestPhraseSearch);
}

export default searchSaga;
