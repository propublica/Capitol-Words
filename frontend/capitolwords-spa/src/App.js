import React, { Component } from 'react';
import { connect } from 'react-redux';

import './App.css';

import { phraseSearchRequested } from './actions/search-actions';

import { searchTerms, isSearching } from './selectors/phrase-search-selectors';

import HeaderBar from './components/HeaderBar/HeaderBar';
import PhraseSearchResults from './components/PhraseSearchResults/PhraseSearchResults';
import HomePage from './components/HomePage/HomePage';

import { ClipLoader } from 'react-spinners';

class App extends Component {

  renderMainContent() {
    const { searchTerms, isSearching } = this.props;
    const mainContent = searchTerms ? <PhraseSearchResults /> : <HomePage />;
    const content = isSearching ? this.renderLoader() : mainContent;
    return (
      <div className="Main-container">
        {content}
      </div>
    );
  }

  renderLoader() {
    return (
      <div className="Loader-container">
        <ClipLoader color="#9CAB4C"/>
      </div>
    );
  }

  render() {
    return (
      <div className="App-container">
        <HeaderBar onSearchSubmit={this.props.phraseSearchRequested}/>
        {this.renderMainContent()}
      </div>
    );
  }
}

export default connect(state => ({
    searchTerms: searchTerms(state),
    isSearching: isSearching(state),
  }),
  {
    phraseSearchRequested,
  })(App);
