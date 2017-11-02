import React, { Component } from 'react';
import { connect } from 'react-redux';

import './App.css';

import { phraseSearchRequested } from './actions/search-actions';

import { searchContent, isSearching } from './selectors/phrase-search-selectors';

import HeaderBar from './components/HeaderBar/HeaderBar';
import PhraseSearchResults from './components/PhraseSearchResults/PhraseSearchResults';
import HomePage from './components/HomePage/HomePage';

import { ClipLoader } from 'react-spinners';

class App extends Component {

  renderMainContent() {
    const { searchContent, isSearching } = this.props;
    const mainContent = searchContent ? <PhraseSearchResults /> : <HomePage />;
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
    searchContent: searchContent(state),
    isSearching: isSearching(state),
  }),
  {
    phraseSearchRequested,
  })(App);
