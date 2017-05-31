const API_MULTI_SEARCH = '/cwapi/search/multi/';

export function fetchPhraseSearch(phrase) {
  const encodedPhrase = encodeURIComponent(phrase);
  return fetch(`${API_MULTI_SEARCH}?content=${encodedPhrase}`)
    .then(response => {
      if (response.status >= 400) {
        throw new Error("Bad response from server");
      }
      return response.json();
    });
}
