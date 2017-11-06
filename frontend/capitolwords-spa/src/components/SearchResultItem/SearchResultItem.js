import React from 'react';

import g from 'glamorous';

import * as s from '../../styles';

import Avatar from '../Avatar/Avatar';

const ResultListItem = g.li({
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'stretch',
  marginTop: '2rem',
  padding: '0 2rem',
  backgroundColor: s.blockBgColor,
});

const DateDisplay = g.div({
  alignSelf: 'center',
  backgroundColor: s.block2BgColor,
  ...s.sansRegular,
  ...s.fontSize11,
  textTransform: 'uppercase',
  lineHeight: '2rem',
  padding: '0 1rem',
  position: 'relative',
  margin: '-0.5rem 0 1rem',
  color: s.textSecondaryColor,
})

const TitleDocLink = g.a({
  flex: '1 1 100%',
  ...s.serifRegular,
  ...s.fontSize14,
  color: s.textSecondaryColor,
  textDecoration: 'none',
});

const MentionCount = g.div({
  flex: '0 0 auto',
  marginLeft: '2rem',
  ...s.sansRegular,
  ...s.fontSize14,
  color: s.textSecondaryColor,
});

const Snippet = g.div({
  ...s.serifRegular,
  ...s.fontSize18,
  lineHeight: '2rem',
  marginTop: '1rem',

  // elasticsearch highlights matching words within the snippet with <em> tags
  '& em': {
    fontStyle: 'normal',
    display: 'inline-block',
    boxShadow: `inset 0 -3px 0 0 ${s.green500}`,
  },
});

const Speakers = g.div({
  display: 'flex',
  flexWrap: 'wrap',
  margin: '1.5rem 0 2rem -0.5rem',
  '& > *': {
    margin: '0.5rem 0 0 0.5rem',
  },
});


const SearchResultItem = ({ item }) => (
  <ResultListItem key={item.id}>
    <DateDisplay>{ item.displayDate }</DateDisplay>
    <g.Div display="flex" width="100%" justifyContent="space-between" alignItems="baseline">
      <TitleDocLink href={ item.docUrl } className="PhraseSearchResults-item-title">{ item.title }</TitleDocLink>
      <MentionCount>{ item.mentionCount } mentions</MentionCount>
    </g.Div>
    <Snippet dangerouslySetInnerHTML={{__html: item.snippet}} />
    <Speakers>
      { item.speakers.map(speaker => (
        <Avatar key={speaker.url} person={speaker} />
      ))}
    </Speakers>
  </ResultListItem>
);

export default SearchResultItem;
