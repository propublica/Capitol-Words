import React, { Component } from 'react';
import PropTypes from 'prop-types';

import moment from 'moment';

import { VictoryChart, VictoryBar, VictoryAxis } from 'victory';

import './TimeSeries.css';

class TimeSeries extends Component {
  static propTypes = {
    data: PropTypes.array.isRequired,
  };

  formatDate(date) {
    return moment(date).format('MMMM Do');
  }

  render() {

    return (
      <div className="TimeSeries-container">
        <VictoryChart height={300} width={800} paddingLeft={40} paddingRight={40} paddingTop={0}>
          <VictoryBar
            style={{ data: { fill: "#029cd0"}}}
            alignment="start"
            data={this.props.data}
            x={'date'}
            y={'count'}
          />
          <VictoryAxis
            orientation='bottom'
            style={{
              axis: {stroke: "white"},
              axisLabel: {fontSize: 20, padding: 30},
              tickLabels: {fontSize: 20, padding: 5, fill: 'white'},
            }}
            tickCount={4}
            tickFormat={this.formatDate}
          />
          <VictoryAxis
            dependentAxis
            orientation="left"
            style={{
              axis: {stroke: "#404040"},
              axisLabel: {fontSize: 20, padding: 30},
              tickLabels: {fontSize: 20, padding: 5, fill: '#404040'},
              ticks: {stroke: "#404040", size: 5, strokeDasharray: 5},
            }}
            tickCount={3}
            tickFormat={(number) => Math.round(number)}
          />
        </VictoryChart>
      </div>
    );
  }
}

export default TimeSeries;
