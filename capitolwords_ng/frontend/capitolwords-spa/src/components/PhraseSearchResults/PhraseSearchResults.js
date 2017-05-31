import React, { Component } from 'react';
import { connect } from 'react-redux';
import PropTypes from 'prop-types';

import './PhraseSearchResults.css';

import {
  isSearching,
  isSearchFailure,
  isSearchSuccess,
  searchResultCount,
  searchResultList,
} from '../../selectors/phrase-search-selectors';

class PhraseSearchResults extends Component {
  static propTypes = {
    isSearching: PropTypes.bool.isRequired,
    isSearchFailure: PropTypes.bool.isRequired,
    isSearchSuccess: PropTypes.bool.isRequired,
    searchResultCount: PropTypes.number,
    searchResultList: PropTypes.array,
  };

  renderResultItem(item) {
    return (
      <li className="PhraseSearchResults-item" key={item._id}>
        <div className="PhraseSearchResults-item-id">{ item._source.ID }</div>
        <div className="PhraseSearchResults-item-title">{ item._source.title }</div>
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
          <div>Search returned { searchResultCount } results.</div>
          { searchResultCount && this.renderResultList() }
        </div>
      )
    }

    return (<div />);
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
  searchResultCount: searchResultCount(state),
  searchResultList: searchResultList(state),
}))(PhraseSearchResults);
