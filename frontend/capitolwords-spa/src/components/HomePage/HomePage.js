import React, { Component } from 'react';
import { connect } from 'react-redux';
import PropTypes from 'prop-types';
import Highlighter from 'react-highlight-words'

import { phraseSearchRequested } from '../../actions/search-actions';

import SearchInput from '../SearchInput/SearchInput';

import './HomePage.css';

import {
  isSearching,
  isSearchFailure,
  isSearchSuccess,
  searchContent,
  searchResultList,
  searchDelta
} from '../../selectors/phrase-search-selectors';

class HomePage extends Component {
  static propTypes = {
    isSearching: PropTypes.bool.isRequired,
    isSearchFailure: PropTypes.bool.isRequired,
    isSearchSuccess: PropTypes.bool.isRequired,
    searchResultList: PropTypes.array,
    searchContent: PropTypes.string,
    searchDelta: PropTypes.number
  };


  render() {
    return (
      <div className="HomePage-container">
        <div className="Title">
          <h3>Capitol Words</h3>
          <p>Dig up some data on the words our legislators use every day.</p>
        </div>
        <div className="HomePage-searchInput">
          <SearchInput onSubmit={this.props.phraseSearchRequested}/>
        </div>
        <div className="QuickOptions-container">
          <div className="QuickOption" onClick={() => {this.props.phraseSearchRequested('Poverty')}}>Poverty</div>
          <div className="QuickOption" onClick={() => {this.props.phraseSearchRequested('Russian Interference')}}>Russian Interference</div>
          <div className="QuickOption" onClick={() => {this.props.phraseSearchRequested('Education')}}>Education</div>
          <div className="QuickOption" onClick={() => {this.props.phraseSearchRequested('Tax Cuts')}}>Tax Cuts</div>
        </div>
      </div>
    );
  }

}


export default connect(state => ({
  isSearching: isSearching(state),
  isSearchFailure: isSearchFailure(state),
  isSearchSuccess: isSearchSuccess(state),
  searchContent: searchContent(state),
  searchDelta: searchDelta(state),
  searchResultList: searchResultList(state),
}),
{
  phraseSearchRequested,
})(HomePage);
