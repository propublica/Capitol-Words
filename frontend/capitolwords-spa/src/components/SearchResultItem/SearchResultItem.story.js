import React from 'react';

import { storiesOf } from '@storybook/react';

import g from 'glamorous';

import SearchResultItem from './SearchResultItem';

const ItemList = g.ul({
  listStyle: 'none',
  padding: '0',
  margin: '0 auto',
  maxWidth: '600px',
});

const items = [
  {
    "id": "id-CREC-2017-05-22-pt1-PgH4416-3",
    "displayDate": "May 22, 2017",
    "mentionCount": 6,
    "title": "FUND CAREER AND TECHNICAL EDUCATION",
    "docUrl": "https://www.gpo.gov/fdsys/pkg/CREC-2017-05-22/html/CREC-2017-05-22-pt1-PgH4416-3.htm",
    "snippet": " H4416]\nFrom the Congressional Record Online through the Government Publishing Office [&lt;a href=&quot;http:&#x2F;&#x2F;www.gpo.gov&quot;&gt;www.gpo.gov&lt;&#x2F;a&gt;]\n\n\n\n\n                  FUND CAREER AND TECHNICAL <em>EDUCATION</em>\n\n  (Mr",
    "speakers": [
      {
        "url": "https://www.congress.gov/member/raja-krishnamoorthi/K000391",
        "imageUrl": "https://theunitedstates.io/images/congress/225x275/K000391.jpg",
        "party": "Democrat"
      }
    ]
  },
  {
    "id": "id-CREC-2017-05-15-pt1-PgS2934",
    "displayDate": "May 15, 2017",
    "mentionCount": 9,
    "title": "STATEMENTS ON INTRODUCED BILLS AND JOINT RESOLUTIONS",
    "docUrl": "https://www.gpo.gov/fdsys/pkg/CREC-2017-05-15/html/CREC-2017-05-15-pt1-PgS2934.htm",
    "snippet": "\n\n      By Mr. KAINE (for himself and Mr. Tester):\n  S. 1125. A bill to amend the Higher <em>Education</em> Act of 1965 to provide \nFederal Pell Grants to Iraq and Afghanistan veteran&#x27;s dependents; to \nthe",
    "speakers": [
      {
        "url": "https://www.congress.gov/member/tim-kaine/K000384",
        "imageUrl": "https://theunitedstates.io/images/congress/225x275/K000384.jpg",
        "party": "Democrat"
      },
      {
        "url": "https://www.congress.gov/member/tim-kaine/K000384",
        "imageUrl": "https://theunitedstates.io/images/congress/225x275/K000384.jpg",
        "party": "Republican"
      },
      {
        "url": "https://www.congress.gov/member/tim-kaine/K000384",
        "imageUrl": "https://theunitedstates.io/images/congress/225x275/K000384.jpg",
        "party": "Independent"
      },
      {
        "url": "https://www.congress.gov/member/tim-kaine/K000384",
        "imageUrl": "https://theunitedstates.io/images/congress/225x275/K000384.jpg",
        "party": "Democrat"
      },
      {
        "url": "https://www.congress.gov/member/tim-kaine/K000384",
        "imageUrl": "https://theunitedstates.io/images/congress/225x275/K000384.jpg",
        "party": "Republican"
      },
      {
        "url": "https://www.congress.gov/member/tim-kaine/K000384",
        "imageUrl": "https://theunitedstates.io/images/congress/225x275/K000384.jpg",
        "party": "Independent"
      },
      {
        "url": "https://www.congress.gov/member/tim-kaine/K000384",
        "imageUrl": "https://theunitedstates.io/images/congress/225x275/K000384.jpg",
        "party": "Democrat"
      },
      {
        "url": "https://www.congress.gov/member/tim-kaine/K000384",
        "imageUrl": "https://theunitedstates.io/images/congress/225x275/K000384.jpg",
        "party": "Republican"
      },
      {
        "url": "https://www.congress.gov/member/tim-kaine/K000384",
        "imageUrl": "https://theunitedstates.io/images/congress/225x275/K000384.jpg",
        "party": "Independent"
      },
      {
        "url": "https://www.congress.gov/member/tim-kaine/K000384",
        "imageUrl": "https://theunitedstates.io/images/congress/225x275/K000384.jpg",
        "party": "Democrat"
      },
      {
        "url": "https://www.congress.gov/member/tim-kaine/K000384",
        "imageUrl": "https://theunitedstates.io/images/congress/225x275/K000384.jpg",
        "party": "Republican"
      },
      {
        "url": "https://www.congress.gov/member/tim-kaine/K000384",
        "imageUrl": "https://theunitedstates.io/images/congress/225x275/K000384.jpg",
        "party": "Independent"
      },
      {
        "url": "https://www.congress.gov/member/tim-kaine/K000384",
        "imageUrl": "https://theunitedstates.io/images/congress/225x275/K000384.jpg",
        "party": "Democrat"
      },
      {
        "url": "https://www.congress.gov/member/tim-kaine/K000384",
        "imageUrl": "https://theunitedstates.io/images/congress/225x275/K000384.jpg",
        "party": "Republican"
      },
      {
        "url": "https://www.congress.gov/member/tim-kaine/K000384",
        "imageUrl": "https://theunitedstates.io/images/congress/225x275/K000384.jpg",
        "party": "Independent"
      }
    ]
  },
  {
    "id": "id-CREC-2017-05-25-pt1-PgE720",
    "displayDate": "May 25, 2017",
    "mentionCount": 9,
    "title": "HONORING DR. VALERIE PITTS",
    "docUrl": "https://www.gpo.gov/fdsys/pkg/CREC-2017-05-25/html/CREC-2017-05-25-pt1-PgE720.htm",
    "snippet": " public \n<em>education</em>, most recently as Superintendent of the Larkspur-Corte Madera \nSchool District for the past 12 years. Dr. Pitts dedicated her \nprofessional tenure to supporting and promoting",
    "speakers": [
      {
        "url": "https://www.congress.gov/member/jared-huffman/H001068",
        "imageUrl": "https://theunitedstates.io/images/congress/225x275/H001068.jpg",
        "party": "Democrat"
      }
    ]
  },
  {
    "id": "id-CREC-2017-05-25-pt1-PgE733",
    "displayDate": "May 25, 2017",
    "mentionCount": 8,
    "title": "INTRODUCTION OF THE YOUNG AMERICANS FINANCIAL LITERACY ACT",
    "docUrl": "https://www.gpo.gov/fdsys/pkg/CREC-2017-05-25/html/CREC-2017-05-25-pt1-PgE733.htm",
    "snippet": " Act. Financial \nliteracy is critical to ensuring future financial responsibility. \nStudies have shown that 87 percent of Americans believe finance \n<em>education</em> should be taught in schools and 92 percent",
    "speakers": []
  },
  {
    "id": "id-CREC-2017-05-23-pt1-PgE703",
    "displayDate": "May 23, 2017",
    "mentionCount": 9,
    "title": "RECOGNIZING GUAM DEPARTMENT OF EDUCATION NURSES IN HONOR OF NATIONAL SCHOOL NURSES DAY",
    "docUrl": "https://www.gpo.gov/fdsys/pkg/CREC-2017-05-23/html/CREC-2017-05-23-pt1-PgE703.htm",
    "snippet": " Remarks]\n[Page E703]\nFrom the Congressional Record Online through the Government Publishing Office [&lt;a href=&quot;http:&#x2F;&#x2F;www.gpo.gov&quot;&gt;www.gpo.gov&lt;&#x2F;a&gt;]\n\n\n\n\n RECOGNIZING GUAM DEPARTMENT OF <em>EDUCATION</em> NURSES",
    "speakers": [
      {
        "url": "https://www.congress.gov/member/madeleine-z.-bordallo/B001245",
        "imageUrl": "https://theunitedstates.io/images/congress/225x275/B001245.jpg",
        "party": "Democrat"
      }
    ]
  },
  {
    "id": "id-CREC-2017-05-23-pt1-PgE700-3",
    "displayDate": "May 23, 2017",
    "mentionCount": 7,
    "title": "RECOGNIZING INTERNATIONAL EDUCATION PROGRAMS",
    "docUrl": "https://www.gpo.gov/fdsys/pkg/CREC-2017-05-23/html/CREC-2017-05-23-pt1-PgE700-3.htm",
    "snippet": " Remarks]\n[Page E700]\nFrom the Congressional Record Online through the Government Publishing Office [&lt;a href=&quot;http:&#x2F;&#x2F;www.gpo.gov&quot;&gt;www.gpo.gov&lt;&#x2F;a&gt;]\n\n\n\n\n              RECOGNIZING INTERNATIONAL <em>EDUCATION</em>",
    "speakers": [
      {
        "url": "https://www.congress.gov/member/mark-pocan/P000607",
        "imageUrl": "https://theunitedstates.io/images/congress/225x275/P000607.jpg",
        "party": "Democrat"
      }
    ]
  },
  {
    "id": "id-CREC-2017-05-17-pt1-PgE654-5",
    "displayDate": "May 17, 2017",
    "mentionCount": 7,
    "title": "HONORING LYNN MAURICE STINSON",
    "docUrl": "https://www.gpo.gov/fdsys/pkg/CREC-2017-05-17/html/CREC-2017-05-17-pt1-PgE654-5.htm",
    "snippet": " <em>education</em> was at Grenada Colored \nSchool and Willia Wilson Elementary in Grenada. Stinson graduated from \nCarrie Dotson High School in Grenada, MS in 1966.\n  Stinson&#x27;s desire to continue his <em>education</em> led",
    "speakers": [
      {
        "url": "https://www.congress.gov/member/bennie-g.-thompson/T000193",
        "imageUrl": "https://theunitedstates.io/images/congress/225x275/T000193.jpg",
        "party": "Democrat"
      }
    ]
  },
  {
    "id": "id-CREC-2017-05-18-pt1-PgE666",
    "displayDate": "May 18, 2017",
    "mentionCount": 5,
    "title": "TRIBUTE TO LYNN UBBEN",
    "docUrl": "https://www.gpo.gov/fdsys/pkg/CREC-2017-05-18/html/CREC-2017-05-18-pt1-PgE666.htm",
    "snippet": " the \nend of the 2016-2017 school year.\n  Lynn has been in <em>education</em> for 41 years, starting as a Special \n<em>Education</em> Teacher at Fredericksburg Community School in 1976. Lynn \ntaught as she continued her",
    "speakers": [
      {
        "url": "https://www.congress.gov/member/david-young/Y000066",
        "imageUrl": "https://theunitedstates.io/images/congress/225x275/Y000066.jpg",
        "party": "Republican"
      }
    ]
  },
  {
    "id": "id-CREC-2017-05-22-pt1-PgE688-2",
    "displayDate": "May 22, 2017",
    "mentionCount": 5,
    "title": "HONORING JAMIE MANCHESTER",
    "docUrl": "https://www.gpo.gov/fdsys/pkg/CREC-2017-05-22/html/CREC-2017-05-22-pt1-PgE688-2.htm",
    "snippet": " received the Recognizing Inspirational \nSchool Employees (RISE) Award for her exemplary service to the students \nof Washington State. Sponsored by the National Coalition of Classified \n<em>Education</em>",
    "speakers": [
      {
        "url": "https://www.congress.gov/member/cathy-mcmorris-rodgers/M001159",
        "imageUrl": "https://theunitedstates.io/images/congress/225x275/M001159.jpg",
        "party": "Republican"
      }
    ]
  },
  {
    "id": "id-CREC-2017-05-16-pt1-PgS2964",
    "displayDate": "May 16, 2017",
    "mentionCount": 8,
    "title": "INTRODUCTION OF BILLS AND JOINT RESOLUTIONS",
    "docUrl": "https://www.gpo.gov/fdsys/pkg/CREC-2017-05-16/html/CREC-2017-05-16-pt1-PgS2964.htm",
    "snippet": " \n     price increases, and for other purposes; to the Committee on \n     Health, <em>Education</em>, Labor, and Pensions.\n           By Mr. CASSIDY (for himself, Ms. Klobuchar, and Mr. \n             King",
    "speakers": []
  }
];

storiesOf('SearchResultItem', module)
  .add('with everything', () => (
    <ItemList>
      {items.map(item => (
        <SearchResultItem item={item} />
      ))}
    </ItemList>
  ));


