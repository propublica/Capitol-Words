import React, { Component } from 'react';
import { connect } from 'react-redux';
import PropTypes from 'prop-types';
import Highlighter from 'react-highlight-words'

import TimeSeries from '../TimeSeries/TimeSeries';

import './PhraseSearchResults.css';

import {
  isSearching,
  isSearchFailure,
  isSearchSuccess,
  searchResultCount,
  searchContent,
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
    searchContent: PropTypes.string,
    searchDelta: PropTypes.number
  };

  renderSpeakerThumb(item){
    return (
      <img className="PhraseSearchResults-speaker-im-r" src={ item.im_url } alt={ item.im_url } />
    );
  }

  renderResultItem(item) {
    // var searchTerms = [searchContent];
    // var images = [];
    // for (var i=0; i < item.speakers.length; i++) {
    //   if (item.party === "Republican") {
    //      images.push(<img key={item.im_url} className="PhraseSearchResults-speaker-im-r" src={ item.im_url } alt={ item.im_url } />);
    //   }
    //   else if (item.party === "Democrat") {
    //      images.push(<img key={item.im_url} className="PhraseSearchResults-speaker-im-d" src={ item.im_url } alt={ item.im_url } />);
    //   }
    //   else {
    //      images.push(<img key={item.im_url} className="PhraseSearchResults-speaker-im-i" src={ item.im_url } alt={ item.im_url } />);
    //   }
    // }
    return (
      <li className="PhraseSearchResults-item" key={item._id}>
        <div className="PhraseSearchResults-item-date">
          { item.human_date }
        </div>
        <div className="PhraseSearchResults-item-mention-count">{ item.mentions } mentions</div>
        <a href={ item._source.html_url } className="PhraseSearchResults-item-title">{ item._source.title }</a>
        <div className="PhraseSearchResults-item-snippet">
          <Highlighter
            highlightClassName="snippetHighlight"
            searchWords={[item.search_phrase]}
            textToHighlight={ item.snippet }
          />
        </div>
        { item.speakers.map(function (speaker){
          return (
            <a href={ speaker.bio_page_url }>
            <img data-party={speaker.party} className="PhraseSearchResults-speaker-im" src={ speaker.im_url } alt={ speaker.im_url } />
            </a>
          );
          })}
      </li>
    );
  }

  renderResultList() {
    const { searchResultList } = this.props;

    return (
      <ul className="PhraseSearchResults-list">
        { searchResultList.map(this.renderResultItem) }
      </ul>
    );
  }

  renderContents() {
    const {
      isSearching,
      isSearchFailure,
      isSearchSuccess,
      searchResultCount,
      searchContent,
      searchDelta
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
          <div className="PhraseSearchResults-phrase"> {searchContent} </div>
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
          {this.renderResultList()}
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
  searchContent: searchContent(state),
  searchDelta: searchDelta(state),
  searchResultCount: searchResultCount(state),
  searchResultList: searchResultList(state),
  dailyBreakdown: dailyBreakdown(state),
}))(PhraseSearchResults);
