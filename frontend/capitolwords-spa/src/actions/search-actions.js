import { push } from 'react-router-redux';

export const PHRASE_SEARCH_REQUESTED = 'PHRASE_SEARCH_REQUESTED';
export const PHRASE_SEARCH_FETCH_SUCCEEDED = 'PHRASE_SEARCH_FETCH_SUCCEEDED';
export const PHRASE_SEARCH_FETCH_FAILED = 'PHRASE_SEARCH_FETCH_FAILED';
export const PHRASE_SEARCH_MODAL_OPEN = 'PHRASE_SEARCH_MODAL_OPEN'
export const PHRASE_SEARCH_MODAL_CLOSED = 'PHRASE_SEARCH_MODAL_CLOSED'

export function routeToPhraseSearch(searchString) {
  return push(`/search?q=${encodeURIComponent(searchString)}`)
}

export function phraseSearchRequested(phrase) {
  return {
    type: PHRASE_SEARCH_REQUESTED,
    payload: {
      phrase
    },
  };
}

export function phraseSearchFetchSucceeded(result) {
  return {
    type: PHRASE_SEARCH_FETCH_SUCCEEDED,
    payload: result
  }
}

export function phraseSearchFetchFailed() {
  return {
    type: PHRASE_SEARCH_FETCH_FAILED
  }
}

export function phraseSearchModelOpen() {
  return {
    type: PHRASE_SEARCH_MODAL_OPEN
  }
}

export function phraseSearchModelClosed() {
  return {
    type: PHRASE_SEARCH_MODAL_CLOSED
  }
}
