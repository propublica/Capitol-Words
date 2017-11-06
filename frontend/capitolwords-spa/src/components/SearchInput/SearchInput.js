import React, { Component } from 'react';
import PropTypes from 'prop-types';

import g from 'glamorous';
import * as s from '../../styles/base';

const InputField = g.input({
  ...s.sansRegular,
  ...s.fontSize16,
  color: s.textColor,
  height: '48px',
  lineHeight: '24px',
  padding: '12px 0',
  minWidth: '320px',
  border: 'none',
  outline: 'none',
  backgroundColor: 'transparent',
  boxShadow: 'inset 0 -1px 0 0 #757575',
});

const SearchButton = g.button({
  ...s.sansRegular,
  ...s.fontSize16,
  color: s.textColor,
  cursor: 'pointer',
  width: '48px',
  height: '48px',
  padding: '12px',
  marginLeft: '8px',
  border: 'none',
  outline: 'none',
  borderRadius: '2',
  opacity: '0.75',
  boxShadow: '0 1px 1px 0 rgba(0, 0, 0, 0.5)',
  ':focus': {
    outline: 'none',
  },
},
({ variant }) => ({
  // The weird template string stuff here turns our rgb hex color strings into
  // rgba hex color strings with 50% opacity (80 in hex is 128 or 50% of 255)
  backgroundColor: variant === 'blue' ? `${s.blue600}80` : s.bluegray800b,
  ':hover': {
    backgroundColor: variant === 'blue' ? `${s.blue500}80` : s.bluegray700,
  },
}));

const SearchSvg = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" version="1.1" xmlns="http://www.w3.org/2000/svg">
    <g transform="translate(1 2)" strokeWidth="2" stroke="#FFF" fill="none" fillRule="evenodd">
      <circle cx="15.5" cy="6.5" r="6.5"/>
      <path d="M10.45 11.5L1.08 20" strokeLinecap="square"/>
    </g>
  </svg>
);

class SearchInput extends Component {
  static propTypes = {
    defaultValue: PropTypes.string,
    onSubmit: PropTypes.func.isRequired,
    variant: PropTypes.oneOf([
      'normal',
      'blue',
    ]),
  };

  static defaultProps = {
    defaultValue: '',
    variant: 'normal',
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
    const { defaultValue, variant } = this.props;

    return (
      <g.Div display="flex">
        <InputField
          placeholder="Search for a word or phrase"
          innerRef={ input => { this.textInput = input; }}
          onKeyDown={this.handleKeyDown}
          defaultValue={defaultValue}
          >
        </InputField>
        <SearchButton onClick={this.handleSearchRequested} variant={variant}><SearchSvg /></SearchButton>
      </g.Div>
    );
  }
}

export default SearchInput;
