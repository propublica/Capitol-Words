import React, { Component } from 'react';
import { connect } from 'react-redux';
import PropTypes from 'prop-types';

import { routeToPhraseSearch } from '../../actions/search-actions';

import SearchInput from '../SearchInput/SearchInput';

import './HomePage.css';

import {
  isSearching,
  isSearchFailure,
  isSearchSuccess,
  searchResultList,
  searchDelta
} from '../../selectors/phrase-search-selectors';


class HomePage extends Component {
  static propTypes = {
    isSearching: PropTypes.bool.isRequired,
    isSearchFailure: PropTypes.bool.isRequired,
    isSearchSuccess: PropTypes.bool.isRequired,
    searchResultList: PropTypes.array,
    searchDelta: PropTypes.number
  };

  render() {
    const { routeToPhraseSearch } = this.props;

    return (
      <div className="HomePage-container">
        <div className="Title">
          <h3>Capitol Words</h3>
          <p>Dig up some data on the words our legislators use every day.</p>
        </div>
        <div className="HomePage-searchInput">
          <SearchInput variant="blue" onSubmit={routeToPhraseSearch}/>
        </div>
        <div className="QuickOptions-container">
          <div className="QuickOption" onClick={() => {routeToPhraseSearch('Poverty')}}>Poverty</div>
          <div className="QuickOption" onClick={() => {routeToPhraseSearch('Russian Interference')}}>Russian Interference</div>
          <div className="QuickOption" onClick={() => {routeToPhraseSearch('Education')}}>Education</div>
          <div className="QuickOption" onClick={() => {routeToPhraseSearch('Tax Cuts')}}>Tax Cuts</div>
        </div>
      </div>
    );
  }

}


export default connect(state => ({
  isSearching: isSearching(state),
  isSearchFailure: isSearchFailure(state),
  isSearchSuccess: isSearchSuccess(state),
  searchDelta: searchDelta(state),
  searchResultList: searchResultList(state),
}),
{
  routeToPhraseSearch,
})(HomePage);
