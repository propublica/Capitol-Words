import React, { Component } from 'react';
import { connect } from 'react-redux';
import PropTypes from 'prop-types';

import g from 'glamorous';
import { ClipLoader } from 'react-spinners';

import * as s from '../../styles/base';
import {
  phraseSearchRequested,
  routeToPhraseSearch
} from '../../actions/search-actions';

import HeaderBar from '../HeaderBar/HeaderBar';
import SearchResultItem from '../SearchResultItem/SearchResultItem';
import TimeSeries from '../TimeSeries/TimeSeries';

import './PhraseSearchResults.css';

import {
  isSearching,
  isSearchFailure,
  isSearchSuccess,
  searchResultCount,
  searchResultList,
  searchDelta,
  dailyBreakdown
} from '../../selectors/phrase-search-selectors';

import  {
  searchString
} from '../../selectors/router-selectors';

class PhraseSearchResults extends Component {
  static propTypes = {
    isSearching: PropTypes.bool.isRequired,
    isSearchFailure: PropTypes.bool.isRequired,
    isSearchSuccess: PropTypes.bool.isRequired,
    searchResultCount: PropTypes.number,
    searchResultList: PropTypes.array,
    searchString: PropTypes.string,
    searchDelta: PropTypes.number
  };

  constructor(props) {
    super(props);

    props.phraseSearchRequested(props.searchString);
  }

  componentWillReceiveProps(nextProps) {
    if (nextProps.searchString !== this.props.searchString) {
      this.props.phraseSearchRequested(nextProps.searchString);
    }
  }

  renderLoader() {
    return (
      <div className="Loader-container">
        <ClipLoader color="#9CAB4C"/>
      </div>
    );
  }

  renderResultList(searchResultList) {
    console.log(JSON.stringify(searchResultList));
    return (
      <g.Ul listStyle="none" padding="0" margin="2rem 0 0 0">
        { searchResultList.map(item =>
          <SearchResultItem
            key={item.id}
            item={item} />
        )}
      </g.Ul>
    );
  }

  renderContents() {
    const {
      isSearching,
      isSearchFailure,
      isSearchSuccess,
      searchResultCount,
      searchString,
      searchDelta,
      searchResultList,
    } = this.props;

    if (isSearching) {
      return this.renderLoader();
    }

    if (isSearchFailure) {
      return (<div>Search failed. Please try again.</div>);
    }

    if (isSearchSuccess) {
      return (
        <g.Div margin="2em auto" maxWidth="640px">

          <div className="PhraseSearchResults-results-for">Search results for:</div>
          <div className="PhraseSearchResults-phrase"> {searchString} </div>
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
          {this.renderResultList(searchResultList, searchString)}
        </g.Div>
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
    const {
      routeToPhraseSearch,
      searchString,
    } = this.props;

    return (
      <g.Div
        maxWidth={s.contentMaxWidth}
        margin="0 auto"
        >
        <HeaderBar defaultValue={searchString} onSearchSubmit={routeToPhraseSearch} />
        { this.renderContents() }
      </g.Div>
    );
  }

}


export default connect(state => ({
  isSearching: isSearching(state),
  isSearchFailure: isSearchFailure(state),
  isSearchSuccess: isSearchSuccess(state),
  searchString: searchString(state),
  searchDelta: searchDelta(state),
  searchResultCount: searchResultCount(state),
  searchResultList: searchResultList(state),
  dailyBreakdown: dailyBreakdown(state),
}), {
  phraseSearchRequested,
  routeToPhraseSearch,
})(PhraseSearchResults);
