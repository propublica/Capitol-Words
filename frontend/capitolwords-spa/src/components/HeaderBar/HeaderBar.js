import React, { Component } from 'react';
import PropTypes from 'prop-types';

import './HeaderBar.css';

import SearchInput from '../SearchInput/SearchInput';

class HeaderBar extends Component {
  static propTypes = {
    onSearchSubmit: PropTypes.func.isRequired,
  };

  render() {
    return (
      <div className="HeaderBar-container">
        <div>
          <h1 className="HeaderBar-title">Capitol Words</h1>
        </div>
        <div>
          <SearchInput onSubmit={this.props.onSearchSubmit}/>
        </div>
      </div>
    );
  }
}

export default HeaderBar;
