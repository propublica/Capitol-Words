import {combineReducers} from 'redux';

import phraseSearch from './phrase-search-reducer';

import { dialogReducer } from 'redux-dialog';
// const reducers = {
//   // Other reducers here
//   phraseSearch: phraseSearch,
//   dialogReducer: dialogReducer
// }

export default combineReducers({
  phraseSearch,
  dialogReducer
});
