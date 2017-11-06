import React from 'react';

import g from 'glamorous';

import * as s from '../../styles';

const AvatarImg = g.a({
  display: 'inline-block',
  borderRadius: '50%',
  borderStyle: 'solid',
  borderWidth: '4px',
  backgroundSize: 'cover',
  backgroundPosition: 'center 20%',
},
({ size, imageUrl, party }) => ({
  width: size === 'large' ? '64px' : '48px',
  height: size === 'large' ? '64px' : '48px',
  borderColor: party === 'Democrat' ? s.demColor : (party === 'Republican' ? s.gopColor : s.indColor),
  backgroundImage: `url(${imageUrl})`,
}));

const Avatar = ({size, person}) => (
  <AvatarImg
    size={size}
    imageUrl={person.imageUrl}
    party={person.party}
    href={person.url}/>
);

export default Avatar;
