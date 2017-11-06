import React, { Component } from 'react';
import PropTypes from 'prop-types';

import g from 'glamorous';
import * as s from '../../styles';

import logo from './logo-propublica.svg';
import SearchInput from '../SearchInput/SearchInput';

const Container = g.div({
  display: 'flex',
  flexWrap: 'wrap',
  flexDirection: 'row',
  justifyContent: 'space-between',
  alignItems: 'center',
  padding: '1rem',
  backgroundColor: 'rgba(255, 255, 255, 0.02)',
});

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
      <Container>
        <g.Div display="flex" justifyContent="flex-start" alignItems="center">
          <g.Img src={logo} width="150px" marginLeft="1rem"/>
          <g.Span margin="0 1rem 0" {...s.sansBold} {...s.fontSize12} textTransform="uppercase" lineHeight="32px" position="relative" top="3px">
            |&nbsp;&nbsp;&nbsp;&nbsp;Capitol Words
          </g.Span>
        </g.Div>
        <div>
          <SearchInput defaultValue={defaultValue} onSubmit={onSearchSubmit} />
        </div>
      </Container>
    );
  }
}

export default HeaderBar;
