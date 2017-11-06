import React, { Component } from 'react';
import { connect } from 'react-redux';
import { Route } from 'react-router';

import g from 'glamorous';
import * as s from './styles';

import PhraseSearchResults from './components/PhraseSearchResults/PhraseSearchResults';
import HomePage from './components/HomePage/HomePage';

const AppContainer = g.div({
  margin: '0 auto',
  maxWidth: s.contentMaxWidth,
  minHeight: '100%',
})

class App extends Component {
  render() {
    return (
      <AppContainer>
        <Route exact path="/" component={HomePage}/>
        <Route path="/search" component={PhraseSearchResults}/>
      </AppContainer>
    );
  }
}

export default App;
