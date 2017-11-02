// const API_MULTI_SEARCH = '/cwapi/search/multi/';
const API_COUNT_TERM = '/cwapi/count/';

export function fetchPhraseSearch(phrase) {
  const encodedPhrase = encodeURIComponent(phrase);
  return fetch(`${API_COUNT_TERM}${encodedPhrase}`)
    .then(response => {
      if (response.status >= 400) {
        throw new Error("Bad response from server");
      }
      return response.json();
    });
}
