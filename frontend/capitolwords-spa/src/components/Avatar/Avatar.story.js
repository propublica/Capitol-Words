import React from 'react';

import { storiesOf } from '@storybook/react';

import g from 'glamorous';

import Avatar from './Avatar';

const people = [
  {
    "url": "https://www.congress.gov/member/raja-krishnamoorthi/K000391",
    "imageUrl": "https://theunitedstates.io/images/congress/225x275/K000391.jpg",
    "party": "Democrat"
  },
  {
    "url": "https://www.congress.gov/member/david-young/Y000066",
    "imageUrl": "https://theunitedstates.io/images/congress/225x275/Y000066.jpg",
    "party": "Republican"
  },
  {
    "url": "https://www.congress.gov/member/bernard-sanders/S000033",
    "imageUrl": "https://theunitedstates.io/images/congress/225x275/S000033.jpg",
    "party": "Independent"
  },
  {
    "url": "https://www.congress.gov/member/tim-kaine/K000384",
    "imageUrl": "https://theunitedstates.io/images/congress/225x275/K000384.jpg",
    "party": "Democrat"
  },
  {
    "url": "https://www.congress.gov/member/jared-huffman/H001068",
    "imageUrl": "https://theunitedstates.io/images/congress/225x275/H001068.jpg",
    "party": "Democrat"
  },
  {
    "url": "https://www.congress.gov/member/madeleine-z.-bordallo/B001245",
    "imageUrl": "https://theunitedstates.io/images/congress/225x275/B001245.jpg",
    "party": "Democrat"
  },
  {
    "url": "https://www.congress.gov/member/mark-pocan/P000607",
    "imageUrl": "https://theunitedstates.io/images/congress/225x275/P000607.jpg",
    "party": "Democrat"
  },
  {
    "url": "https://www.congress.gov/member/bennie-g.-thompson/T000193",
    "imageUrl": "https://theunitedstates.io/images/congress/225x275/T000193.jpg",
    "party": "Democrat"
  },
  {
    "url": "https://www.congress.gov/member/cathy-mcmorris-rodgers/M001159",
    "imageUrl": "https://theunitedstates.io/images/congress/225x275/M001159.jpg",
    "party": "Republican"
  }
];

storiesOf('Avatar', module)
  .add('Democrat', () => (
    <Avatar person={people[0]} />
  ))
  .add('Republican', () => (
    <Avatar person={people[1]} />
  ))
  .add('Independent', () => (
    <Avatar person={people[2]} />
  ))
  .add('Large size', () => (
    <Avatar person={people[3]} size="large" />
  ));


