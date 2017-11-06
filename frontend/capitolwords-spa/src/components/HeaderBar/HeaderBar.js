import React, { Component } from 'react';
import PropTypes from 'prop-types';

import './HeaderBar.css';

import SearchInput from '../SearchInput/SearchInput';

class HeaderBar extends Component {
  static propTypes = {
    defaultValue: PropTypes.string,
    onSearchSubmit: PropTypes.func.isRequired,
  };

  render() {
    const {
      defaultValue,
      onSearchSubmit,
    } = this.props;

    return (
      <div className="HeaderBar-container">
        <div>
          <h1 className="HeaderBar-title">Capitol Words</h1>
        </div>
        <div>
          <SearchInput defaultValue={defaultValue} onSubmit={onSearchSubmit} />
        </div>
      </div>
    );
  }
}

export default HeaderBar;
