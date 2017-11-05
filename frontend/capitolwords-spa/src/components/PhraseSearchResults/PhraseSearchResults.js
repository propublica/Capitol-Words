import React, { Component } from 'react';
import { connect } from 'react-redux';
import PropTypes from 'prop-types';
import Highlighter from 'react-highlight-words'

import TimeSeries from '../TimeSeries/TimeSeries';
import SearchResultItem from '../SearchResultItem/SearchResultItem';

import './PhraseSearchResults.css';

import {
  isSearching,
  isSearchFailure,
  isSearchSuccess,
  searchResultCount,
  searchTerms,
  searchResultList,
  searchDelta,
  dailyBreakdown
} from '../../selectors/phrase-search-selectors';

class PhraseSearchResults extends Component {
  static propTypes = {
    isSearching: PropTypes.bool.isRequired,
    isSearchFailure: PropTypes.bool.isRequired,
    isSearchSuccess: PropTypes.bool.isRequired,
    searchResultCount: PropTypes.number,
    searchResultList: PropTypes.array,
    searchTerms: PropTypes.string,
    searchDelta: PropTypes.number
  };

  renderSpeakerThumb(item){
    return (
      <img className="PhraseSearchResults-speaker-im-r" src={ item.im_url } alt={ item.im_url } />
    );
  }

  renderResultList(searchResultList) {
    console.log(JSON.stringify(searchResultList));
    return (
      <ul className="PhraseSearchResults-list">
        { searchResultList.map(item =>
          <SearchResultItem
            key={item.id}
            item={item} />
        )}
      </ul>
    );
  }

  renderContents() {
    const {
      isSearching,
      isSearchFailure,
      isSearchSuccess,
      searchResultCount,
      searchTerms,
      searchDelta,
      searchResultList,
    } = this.props;

    if (isSearching) {
      return (<div>Searching...</div>);
    }

    if (isSearchFailure) {
      return (<div>Search failed. Please try again.</div>);
    }

    if (isSearchSuccess) {
      return (
        <div>

          <div className="PhraseSearchResults-results-for">Search results for:</div>
          <div className="PhraseSearchResults-phrase"> {searchTerms} </div>
          <div className="PhraseSearchResults-date-selector-container">
            <div className="PhraseSearchResults-date-selector">
              <div>30 days</div>
              <div>3 months</div>
              <div>6 months</div>
            </div>
          </div>
          <div className="PhraseSearchResults-metrics-container">
            <div className="PhraseSearchResults-metric-box">
              <div className="PhraseSearchResults-metric-box-value">
                { searchResultCount }
              </div>
              <div className="PhraseSearchResults-metric-box-label">
                Total Mentions
              </div>
            </div>
            <div className="PhraseSearchResults-metric-box">
              <div className="PhraseSearchResults-metric-box-value">
                 { searchDelta }%
              </div>
              <div className="PhraseSearchResults-metric-box-label">
                Compared to previous 30 days
              </div>
            </div>
          </div>
          {this.renderTimeSeries()}
          {this.renderResultList(searchResultList, searchTerms)}
        </div>
      )
    }

    return (<div />);
  }

  renderTimeSeries() {
    return (
      <div>
        <h3 className="PhraseSearchResults-timeseries-title">Mentions Over Time</h3>
          <TimeSeries data={this.props.dailyBreakdown}/>
      </div>
    );
  }

  render() {
    return (
      <div className="PhraseSearchResults-container">
        { this.renderContents() }
      </div>
    );
  }

}


export default connect(state => ({
  isSearching: isSearching(state),
  isSearchFailure: isSearchFailure(state),
  isSearchSuccess: isSearchSuccess(state),
  searchTerms: searchTerms(state),
  searchDelta: searchDelta(state),
  searchResultCount: searchResultCount(state),
  searchResultList: searchResultList(state),
  dailyBreakdown: dailyBreakdown(state),
}))(PhraseSearchResults);
