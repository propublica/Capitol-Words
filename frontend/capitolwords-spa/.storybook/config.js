import React from 'react';
import g from 'glamorous';

import {
  configure,
  addDecorator
} from '@storybook/react';

import '../src/index.css';


// All stories should be in the same directory in which the target of the
// stories (the React Component) is defined. The story filenames are expected to
// be in the format `<name>.story.js`.
const req = require.context('../src', true, /\.story\.js$/);

// Add global stories decorator.
addDecorator((story) => (
  <g.Div padding="16px">
    {story()}
  </g.Div>
));

function loadStories() {
  req.keys().forEach(req)
}

configure(loadStories, module);
