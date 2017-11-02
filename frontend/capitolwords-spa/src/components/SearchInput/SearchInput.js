import React, { Component } from 'react';
import PropTypes from 'prop-types';

import './SearchInput.css';

class SearchInput extends Component {
  static propTypes = {
    onSubmit: PropTypes.func.isRequired,
  };

  handleKeyDown = (e) => {
    if (e.keyCode === 13) {
      const trimmedSearchTerm = this.textInput.value.trim();
      if (trimmedSearchTerm) {
        this.textInput.value = trimmedSearchTerm;
        this.props.onSubmit(trimmedSearchTerm);
      } else {
        this.textInput.value = '';
      }
    }
  };

  render() {
    return (
      <input className="SearchInput-input"
        placeholder="Search for a word or phrase"
        ref={input => { this.textInput = input; }}
        onKeyDown={this.handleKeyDown}>
      </input>
    );
  }
}

export default SearchInput;
