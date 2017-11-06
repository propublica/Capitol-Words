import React from 'react';

import { storiesOf } from '@storybook/react';

import g from 'glamorous';

import SearchInput from './SearchInput';

storiesOf('SearchInput', module)
  .add('normal', () => (
    <SearchInput />
  ))
  .add('blue', () => (
    <SearchInput variant="blue"/>
  ));