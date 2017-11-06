import React from 'react';
import ReactDOM from 'react-dom';
import App from './App';
import registerServiceWorker from './registerServiceWorker';
import './index.css';

import {
  applyMiddleware,
  combineReducers,
  createStore,
} from 'redux';
import { Provider } from 'react-redux';

import createHistory from 'history/createBrowserHistory';

import {
  ConnectedRouter,
  routerReducer,
  routerMiddleware,
} from 'react-router-redux';

import createSagaMiddleware from 'redux-saga';

import reducers from './reducers';
import searchSaga from './sagas/search-saga';

const history = createHistory();

const sagaMiddleware = createSagaMiddleware();
const store = createStore(
  combineReducers({
    ...reducers,
    router: routerReducer,
  }),
  applyMiddleware(
    routerMiddleware(history),
    sagaMiddleware,
  ),
);

sagaMiddleware.run(searchSaga);

ReactDOM.render(
  <Provider store={store}>
    <ConnectedRouter history={history}>
      <App />
    </ConnectedRouter>
  </Provider>, document.getElementById('root')
);

registerServiceWorker();
