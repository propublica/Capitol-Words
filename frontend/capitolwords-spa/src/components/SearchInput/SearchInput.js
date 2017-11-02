import React, { Component } from 'react';
import PropTypes from 'prop-types';

import './SearchInput.css';

class SearchInput extends Component {
  static propTypes = {
    onSubmit: PropTypes.func.isRequired,
  };

  handleSearchRequested = () => {
    const trimmedSearchTerm = this.textInput.value.trim();
    if (trimmedSearchTerm) {
      this.textInput.value = trimmedSearchTerm;
      this.props.onSubmit(trimmedSearchTerm);
    } else {
      this.textInput.value = '';
    }
  }

  handleKeyDown = (e) => {
    if (e.keyCode === 13) {
      this.handleSearchRequested();
    }
  };

  render() {
    return (
      <div className="SearchInput-container">
        <input className="SearchInput-input"
          placeholder="Search for a word or phrase"
          ref={input => { this.textInput = input; }}
          onKeyDown={this.handleKeyDown}>
        </input>
        <div className="SearchInput-button" onClick={this.handleSearchRequested}>Submit</div>
      </div>
    );
  }
}

export default SearchInput;
