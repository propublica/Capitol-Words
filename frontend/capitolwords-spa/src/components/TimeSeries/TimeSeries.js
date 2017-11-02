import React, { Component } from 'react';
import PropTypes from 'prop-types';

import { VictoryChart, VictoryBar } from 'victory';

import './TimeSeries.css';

class TimeSeries extends Component {
  static propTypes = {
    data: PropTypes.object.isRequired,
  };

  render() {
    const data = [
      { x: 1, y: 8, width: 8 },
      { x: 2, y: 2, width: 8 },
      { x: 3, y: 3, width: 8 },
      { x: 4, y: 1, width: 8 },
      { x: 5, y: 10, width: 8 },
      { x: 6, y: 12, width: 8 },
      { x: 7, y: 9, width: 8 },
      { x: 8, y: 2, width: 8 },
      { x: 9, y: 6, width: 8 },
      { x: 10, y: 7, width: 8 },
    ];

    return (
      <div className="TimeSeries-container">
        <VictoryChart>
          <VictoryBar
            style={{ data: { fill: "#029cd0"}}}
            alignment="start"
            data={data}
          />
        </VictoryChart>
      </div>
    );
  }
}

export default TimeSeries;
