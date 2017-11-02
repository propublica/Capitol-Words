import React, { Component } from 'react';
import { connect } from 'react-redux';

import './App.css';

import { phraseSearchRequested } from './actions/search-actions';

import HeaderBar from './components/HeaderBar/HeaderBar';
import PhraseSearchResults from './components/PhraseSearchResults/PhraseSearchResults';

class App extends Component {
  render() {
    return (
      <div className="App-container">
        <HeaderBar onSearchSubmit={this.props.phraseSearchRequested}/>
        <PhraseSearchResults />
      </div>
    );
  }
}

export default connect(
  null,
  {phraseSearchRequested})(App);
