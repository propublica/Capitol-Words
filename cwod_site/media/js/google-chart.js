(function() {
  window.GoogleChart = (function() {
    function GoogleChart(width, height) {
      this.width = width;
      this.height = height;
      this.encoded = [];
      this.data = [];
      this.chg = '';
      this.chf = '';
      this.chco = '';
      this.chdl = '';
      this.chxl = [];
      this.chxp = [];
    }
    GoogleChart.prototype.types = {
      'line': 'lc'
    };
    GoogleChart.prototype.base_url = 'http://chart.apis.google.com/chart?';
    GoogleChart.prototype.add_data = function(values) {
      return this.data.push(values);
    };
    GoogleChart.prototype.set_axis_labels = function(index, labels) {
      return this.chxl.push([index, labels]);
    };
    GoogleChart.prototype.set_axis_positions = function(index, positions) {
      return this.chxp.push([index, positions]);
    };
    GoogleChart.prototype.set_grid = function(x_step, y_step, dash_length, space_length, x_offset, y_offset) {
      return this.chg = x_step + ',' + y_step + ',' + dash_length + ',' + space_length + ',' + x_offset + ',' + y_offset;
    };
    GoogleChart.prototype.set_fill = function(fill_type, s, color) {
      return this.chf = fill_type + ',' + s + ',' + color;
    };
    GoogleChart.prototype.set_colors = function(colors) {
      return this.chco = colors.join(',');
    };
    GoogleChart.prototype.set_legend = function(legend) {
      return this.chdl = legend.join('|');
    };
    GoogleChart.prototype.chs = function() {
      return [this.width, this.height].join('x');
    };
    GoogleChart.prototype.cht = function() {
      return this.types['line'];
    };
    GoogleChart.prototype.chd = function() {
      var maxValue, values;
      maxValue = this.max(_(this.data).flatten());
      return this.encoding() + ((function() {
        var _i, _len, _ref, _results;
        _ref = this.data;
        _results = [];
        for (_i = 0, _len = _ref.length; _i < _len; _i++) {
          values = _ref[_i];
          _results.push(this.encode(values, maxValue));
        }
        return _results;
      }).call(this)).join(',');
    };
    GoogleChart.prototype.url = function() {
      var axis_labels, axis_positions, index, key, labels, pieces, positions, value, _i, _j, _len, _len2, _ref, _ref2;
      pieces = {
        'cht': this.cht(),
        'chs': this.chs(),
        'chd': this.chd(),
        'chg': this.chg,
        'chf': this.chf,
        'chco': this.chco,
        'chdlp': 't|l'
      };
      if (this.chdl !== '') {
        pieces['chdl'] = this.chdl;
      }
      if (this.chxl) {
        pieces['chxt'] = [];
        pieces['chxl'] = [];
        _ref = this.chxl;
        for (_i = 0, _len = _ref.length; _i < _len; _i++) {
          axis_labels = _ref[_i];
          index = axis_labels[0], labels = axis_labels[1];
          pieces['chxl'].push(_i + ':|' + labels.join('|'));
          pieces['chxt'].push(index);
        }
        pieces['chxl'] = pieces['chxl'].join('|');
        pieces['chxt'] = pieces['chxt'].join(',');
        if (this.chxp) {
          pieces['chxp'] = '';
          _ref2 = this.chxp;
          for (_j = 0, _len2 = _ref2.length; _j < _len2; _j++) {
            axis_positions = _ref2[_j];
            index = axis_positions[0], positions = axis_positions[1];
            index = {
              y: 0,
              x: 1
            }[index];
            pieces['chxp'] = index + ',' + positions.join(',');
          }
        }
      }
      return this.base_url + ((function() {
        var _results;
        _results = [];
        for (key in pieces) {
          value = pieces[key];
          _results.push("" + key + "=" + value);
        }
        return _results;
      })()).join('&');
    };
    GoogleChart.prototype.max = function(values) {
      return Math.max.apply(Math, values);
    };
    GoogleChart.prototype.encoding = function() {
      if (this.height > 100) {
        return 'e:';
      } else {
        return 's:';
      }
    };
    GoogleChart.prototype.encode = function(values, maxValue) {
      if (this.height > 100) {
        return this.extendedEncode(values, maxValue);
      } else {
        return this.simpleEncode(values, maxValue);
      }
    };
    GoogleChart.prototype.simpleEncoding = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    GoogleChart.prototype.simpleEncode = function(values, maxValue) {
      var chartData, currentValue, val, _i, _len;
      chartData = [];
      for (_i = 0, _len = values.length; _i < _len; _i++) {
        currentValue = values[_i];
        if (!isNaN(currentValue && currentValue >= 0)) {
          val = Math.round((this.simpleEncoding.length - 1) * (currentValue / maxValue));
          chartData.push(this.simpleEncoding.charAt(val));
        } else {
          chartData.push('_');
        }
      }
      return chartData.join('');
    };
    GoogleChart.prototype.extendedMap = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-.';
    GoogleChart.prototype.extendedEncode = function(values, maxValue) {
      var chartData, currentValue, mapLength, numericalVal, quotient, remainder, scaledVal, _i, _len;
      chartData = '';
      mapLength = this.extendedMap.length;
      for (_i = 0, _len = values.length; _i < _len; _i++) {
        currentValue = values[_i];
        numericalVal = new Number(currentValue);
        scaledVal = Math.floor(mapLength * mapLength * numericalVal / maxValue);
        if (scaledVal > (mapLength * mapLength) - 1) {
          chartData += '..';
        } else if (scaledVal < 0) {
          chartData += '__';
        } else {
          quotient = Math.floor(scaledVal / mapLength);
          remainder = scaledVal - mapLength * quotient;
          chartData += this.extendedMap.charAt(quotient) + this.extendedMap.charAt(remainder);
        }
      }
      return chartData;
    };
    return GoogleChart;
  })();
}).call(this);
