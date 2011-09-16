(function() {
  var spinner;
  jQuery.noConflict();
  spinner = null;
  window.CapitolWords = (function() {
    function CapitolWords() {}
    CapitolWords.prototype.states = {
      "WA": "Washington",
      "VA": "Virginia",
      "DE": "Delaware",
      "DC": "District of Columbia",
      "WI": "Wisconsin",
      "WV": "West Virginia",
      "HI": "Hawaii",
      "CO": "Colorado",
      "FL": "Florida",
      "WY": "Wyoming",
      "NH": "New Hampshire",
      "NJ": "New Jersey",
      "NM": "New Mexico",
      "TX": "Texas",
      "LA": "Louisiana",
      "NC": "North Carolina",
      "ND": "North Dakota",
      "NE": "Nebraska",
      "TN": "Tennessee",
      "NY": "New York",
      "PA": "Pennsylvania",
      "CA": "California",
      "NV": "Nevada",
      "AA": "Armed Forces Americas",
      "PR": "Puerto Rico",
      "GU": "Guam",
      "AE": "Armed Forces Europe",
      "VI": "Virgin Islands",
      "AK": "Alaska",
      "AL": "Alabama",
      "AP": "Armed Forces Pacific",
      "AS": "American Samoa",
      "AR": "Arkansas",
      "VT": "Vermont",
      "IL": "Illinois",
      "GA": "Georgia",
      "IN": "Indiana",
      "IA": "Iowa",
      "OK": "Oklahoma",
      "AZ": "Arizona",
      "ID": "Idaho",
      "CT": "Connecticut",
      "ME": "Maine",
      "MD": "Maryland",
      "MA": "Massachusetts",
      "OH": "Ohio",
      "UT": "Utah",
      "MO": "Missouri",
      "MN": "Minnesota",
      "MI": "Michigan",
      "RI": "Rhode Island",
      "KS": "Kansas",
      "MT": "Montana",
      "MP": "Northern Mariana Islands",
      "MS": "Mississippi",
      "SC": "South Carolina",
      "KY": "Kentucky",
      "OR": "Oregon",
      "SD": "South Dakota"
    };
    CapitolWords.prototype.customizeChart = function() {
      var party, state, url;
      party = jQuery('#partySelect').val();
      state = jQuery('#stateSelect').val();
      url = 'http://capitolwords.org/api/chart/timeline.json';
      return jQuery.ajax({
        dataType: 'jsonp',
        url: url,
        data: {
          'party': party,
          'state': state,
          'phrase': jQuery('#term').val(),
          'granularity': 'month',
          'percentages': 'true',
          'legend': 'false',
          'mincount': 0
        },
        success: function(data) {
          var imgTag, imgUrl, results;
          results = data['results'];
          imgUrl = results['url'];
          imgTag = "<img src=\"" + imgUrl + "\"/>";
          return jQuery('#customChart').attr('src', imgUrl);
        }
      });
    };
    CapitolWords.prototype.getGraph = function(term) {
      var url;
      url = 'http://capitolwords.org/api/chart/timeline.json';
      return jQuery.ajax({
        dataType: 'jsonp',
        url: url,
        data: {
          'phrase': term,
          'granularity': 'month',
          'percentages': 'true',
          'mincount': 0,
          'legend': false
        },
        success: function(data) {
          var customImgTag, imgUrl, overallImgTag, results;
          results = data['results'];
          imgUrl = results['url'];
          overallImgTag = "<img src=\"" + imgUrl + "\" alt=\"Timeline of occurrences of " + term + "\"/>";
          customImgTag = "<img id=\"customChart\" src=\"" + imgUrl + "\" alt=\"Custom timeline of occurrences of \"" + term + "\"/>";
          jQuery('#overallTimeline').html(overallImgTag);
          return jQuery('#customTimeline').append(customImgTag);
        }
      });
    };
    CapitolWords.prototype.getPartyGraph = function(term) {
      var url;
      url = 'http://capitolwords.org/api/chart/timeline.json';
      return jQuery.ajax({
        dataType: 'jsonp',
        url: url,
        data: {
          'phrase': term,
          'granularity': 'month',
          'percentages': 'true',
          'mincount': 0,
          'legend': true,
          'split_by_party': true
        },
        success: function(data) {
          var imgTag, imgUrl, results;
          results = data['results'];
          imgUrl = results['url'];
          imgTag = "<img src=\"" + imgUrl + "\" alt=\"Timeline of occurrences of " + term + "\"/>";
          return jQuery('#partyTimeline').html(imgTag);
        }
      });
    };
    CapitolWords.prototype.getPartyPieChart = function(term, div, width, height, callback) {
      var url;
      if (typeof width === 'undefined') {
        width = '';
      }
      if (typeof width === 'undefined') {
        height = '';
      }
      url = 'http://capitolwords.org/api/chart/pie.json';
      return jQuery.ajax({
        dataType: 'jsonp',
        url: url,
        data: {
          'phrase': term,
          'entity_type': 'party',
          'width': width,
          'height': height
        },
        success: function(data) {
          var imgUrl, results;
          results = data['results'];
          imgUrl = results['url'];
          return div.find('.default').fadeOut('slow', function() {
            return div.find('.realChart').attr('src', imgUrl).attr('alt', "Pie chart of occurrences of " + term + " by party").fadeIn('slow', function() {
              if (typeof callback !== 'undefined') {
                return callback(term, div);
              }
            });
          });
        }
      });
    };
    CapitolWords.prototype.addLegislatorToChart = function(result, maxcount, div) {
      var bioguide_id, pct, url;
      url = 'http://capitolwords.org/api/legislators.json';
      bioguide_id = result['legislator'];
      pct = (result['count'] / maxcount) * 100;
      return jQuery.ajax({
        dataType: 'jsonp',
        url: url,
        async: false,
        data: {
          'bioguide_id': bioguide_id
        },
        success: function(data) {
          var html;
          url = "/legislator/" + bioguide_id + "-" + data['slug'];
          html = "<li>\n    <span class=\"tagValue\" style=\"width:" + pct + "%\">\n        <span class=\"tagPercent\">" + pct + "%</span>\n        <span class=\"tagNumber\"></span>\n    </span>\n    <span class=\"barChartTitle\"><a href=\"" + url + "\">\n        " + data['honorific'] + " " + data['full_name'] + ", " + data['party'] + "-" + data['state'] + "\n    </a>\n    </span>\n    </li>";
          return div.append(html);
        }
      });
    };
    CapitolWords.prototype.getLegislatorPopularity = function(term, div) {
      var url;
      url = 'http://capitolwords.org/api/phrases/legislator.json';
      return jQuery.ajax({
        dataType: 'jsonp',
        url: url,
        data: {
          'phrase': term,
          'sort': 'relative',
          'per_page': 10
        },
        success: function(data) {
          var maxcount, result, results, _i, _len, _results;
          results = data['results'];
          maxcount = results[0]['count'];
          div.html('');
          _results = [];
          for (_i = 0, _len = results.length; _i < _len; _i++) {
            result = results[_i];
            _results.push(this.addLegislatorToChart(result, maxcount, div));
          }
          return _results;
        }
      });
    };
    CapitolWords.prototype.getStatePopularity = function(term, div) {
      var cw, url;
      url = 'http://capitolwords.org/api/phrases/state.json';
      cw = this;
      return jQuery.ajax({
        dataType: 'jsonp',
        url: url,
        data: {
          'phrase': term,
          'sort': 'relative',
          'per_page': 10
        },
        success: function(data) {
          var maxcount, results;
          div.html('');
          results = data['results'];
          maxcount = results[0]['count'];
          return _(results).each(function(result) {
            var abbrev, html, pct, state;
            abbrev = result['state'];
            state = abbrev;
            if (cw.states.hasOwnProperty(state)) {
              state = this.states[state];
            }
            url = "/state/" + abbrev;
            pct = (result['count'] / maxcount) * 100;
            html = "<li>\n    <span class=\"tagValue\" style=\"width: " + pct + "%;\">\n        <span class=\"tagPercent\">" + pct + "%</span>\n        <span class=\"tagNumber\"></span>\n    </span>\n    <span class=\"barChartTitle\"><a href=\"" + url + "\">" + state + "</a></span>\n</li>";
            return div.append(html);
          });
        }
      });
    };
    CapitolWords.prototype.populateTermDetailPage = function(term) {
      this.getGraph(term);
      this.getStatePopularity(term, jQuery('#stateBarChart'));
      this.getPartyPieChart(term, jQuery('#partyPieChart'));
      this.getLegislatorPopularity(term, jQuery('#legislatorBarChart'));
      return this.getPartyGraph(term);
    };
    CapitolWords.prototype.populateLegislatorList = function(legislators) {
      var buildTable;
      return buildTable = function() {
        jQuery('table#legislatorList tbody').empty();
        return _(legislators).each(function(legislator) {
          var klass, tr;
          klass = legislators.indexOf(legislator) % 2 === 0 ? 'even' : 'odd';
          tr = "<tr class=\"" + klass + "\">\n    <td>\n        <img class=\"legislatorImage\" alt=\"legislator photo\" src=\"http://assets.sunlightfoundation.com/moc/40x50/" + legislator['bioguide_id'] + ".jpg\"/>\n    </td>\n    <td>" + legislator['state'] + "</td>\n    <td>" + legislator['party'] + "</td>\n    <td>" + legislator['chamber'] + "</td>\n</tr>";
          return jQuery('table#legislatorList tbody').fadeIn('fast', function() {
            return jQuery('img').error(function() {
              return jQuery(this).hide();
            });
          });
        });
      };
    };
    CapitolWords.prototype.itemsToCompare = [];
    CapitolWords.prototype.a = {};
    CapitolWords.prototype.b = {};
    CapitolWords.prototype.minMonth = void 0;
    CapitolWords.prototype.maxMonth = void 0;
    CapitolWords.prototype.limit = function(minMonth, maxMonth) {
      var aVals, bVals, func, labelPositions, labels, positions;
      if (minMonth && maxMonth) {
        func = function(v) {
          return v['month'] >= minMonth && v['month'] <= maxMonth;
        };
      } else {
        func = function() {
          return true;
        };
      }
      aVals = _(this.a['all']).select(func);
      bVals = _(this.b['all']).select(func);
      labelPositions = this.buildXLabels(aVals);
      labels = labelPositions[0];
      positions = labelPositions[1];
      return this.showChart([_(aVals).pluck('percentage'), _(bVals).pluck('percentage')], labels, positions);
    };
    CapitolWords.prototype.buildXLabels = function(values) {
      var labels, positions, year, years;
      years = _(_(values).pluck('month')).select(function(x) {
        return x.match(/01$/);
      });
      positions = [
        (function() {
          var _i, _len, _results;
          _results = [];
          for (_i = 0, _len = years.length; _i < _len; _i++) {
            year = years[_i];
            _results.push(Math.round((years.indexOf(year) / years.length) * 100));
          }
          return _results;
        })()
      ];
      labels = _(years).map(function(x) {
        return "1/" + (x.slice(2, 4));
      });
      return [labels, positions];
    };
    CapitolWords.prototype.submitHomepageCompareForm = function() {
      var cw, opts, phraseA, phraseB, target, url;
      cw = this;
      opts = {
        lines: 12,
        length: 7,
        width: 4,
        radius: 10,
        color: '#000',
        speed: 1,
        trail: 100,
        shadow: true
      };
      target = document.getElementById('compareGraphic');
      spinner = new Spinner(opts).spin(target);
      url = 'http://capitolwords.org/api/dates.json';
      phraseA = jQuery('#terma').val();
      phraseA = phraseA === 'Word or phrase' ? '' : phraseA;
      phraseB = jQuery('#termb').val();
      phraseB = phraseB === 'Word or phrase' ? '' : phraseB;
      return jQuery.ajax({
        dataType: 'jsonp',
        url: url,
        data: {
          phrase: phraseA,
          state: jQuery('#stateA').val() || '',
          party: jQuery(jQuery('.partyA input:checked')[0]).val(),
          granularity: 'month',
          percentages: true,
          mincount: 0
        },
        success: function(data) {
          var aResults;
          aResults = data['results'];
          cw.a['all'] = aResults;
          cw.a['counts'] = _(aResults).pluck('count');
          cw.a['percentages'] = _(aResults).pluck('percentage');
          return jQuery.ajax({
            dataType: 'jsonp',
            url: url,
            data: {
              phrase: phraseB,
              state: jQuery('#stateB').val() || '',
              party: jQuery(jQuery('.partyB input:checked')[0]).val(),
              granularity: 'month',
              percentages: true,
              mincount: 0
            },
            success: function(data) {
              var bResults, labelPositions, labels, positions;
              bResults = data['results'];
              cw.b['all'] = bResults;
              cw.b['counts'] = _(bResults).pluck('count');
              cw.b['percentages'] = _(bResults).pluck('percentage');
              if (cw.minMonth || cw.maxMonth) {
                cw.limit(cw.minMonth, cw.maxMonth);
              } else {
                labelPositions = cw.buildXLabels(cw.a['all']);
                labels = labelPositions[0];
                positions = labelPositions[1];
                cw.showChart([cw.a['percentages'], cw.b['percentages']], labels, positions);
              }
              if (spinner) {
                return spinner.stop();
              }
            }
          });
        }
      });
    };
    CapitolWords.prototype.smoothing = 0;
    CapitolWords.prototype.build_legend = function() {
      var legend, legendA, legendB, partyA, partyB, stateA, stateB, termA, termB;
      termA = jQuery('#terma').val();
      partyA = jQuery(jQuery('.partyA input:checked')[0]).val();
      stateA = jQuery('#stateA').val();
      legend = [];
      legendA = termA;
      if (termA !== 'Word or phrase') {
        if (partyA && stateA) {
          legendA += " [" + partyA + "-" + stateA + "]";
        } else if (partyA) {
          legendA += " [" + partyA + "]";
        } else if (stateA) {
          legendA += " [" + stateA + "]";
        }
        legend.push(legendA);
      }
      termB = jQuery('#termb').val();
      partyB = jQuery(jQuery('.partyB input:checked')[0]).val();
      stateB = jQuery('#stateB').val();
      legendB = termB;
      if (termB !== 'Word or phrase') {
        if (partyB && stateB) {
          legendB += " [" + partyB + "-" + stateB + "]";
        } else if (partyB) {
          legendB += " [" + partyB + "]";
        } else if (stateB) {
          legendB += " [" + stateB + "]";
        }
        legend.push(legendB);
      }
      return legend;
    };
    CapitolWords.prototype.showChart = function(data, x_labels, x_label_positions) {
      var chart, colors, cw, legend, max, maxValue, values;
      chart = new GoogleChart(860, 340);
      values = [];
      maxValue = 0;
      max = 0;
      cw = this;
      _(data).each(function(item) {
        values = item;
        maxValue = Math.round(_(values).max() * 1000) / 10000;
        if (maxValue > max) {
          max = Math.round(maxValue * 10000) / 10000;
        }
        return chart.add_data(values);
      });
      chart.set_grid(0, 50, 2, 5);
      chart.set_fill('bg', 's', '00000000');
      colors = ['8E2844', 'A85B08', 'AF9703'];
      legend = this.build_legend();
      chart.set_legend(legend);
      chart.set_colors(colors.slice(0, legend.length));
      chart.set_axis_labels('y', ['', "" + max + "%"]);
      if (x_labels) {
        chart.set_axis_labels('x', x_labels);
      }
      if (x_label_positions) {
        chart.set_axis_positions('x', x_label_positions);
      }
      jQuery('#chart img.realChart, #compareGraphic img.default').attr('src', chart.url()).fadeIn(100);
      if (spinner) {
        return spinner.stop();
      }
    };
    CapitolWords.prototype.legislatorSearch = function() {
      var data;
      data = {
        chamber: jQuery('#chamber').val(),
        party: jQuery('#party').val(),
        congress: jQuery('#congress').val(),
        state: jQuery('#state').val()
      };
      return jQuery.ajax({
        dataType: 'jsonp',
        url: 'http://capitolwords.org/api/legislators.json',
        data: data,
        success: function(data) {
          return window.CapitolWords.populateLegislatorList(data['results']);
        }
      });
    };
    CapitolWords.prototype.year_values = [];
    CapitolWords.prototype.startDate = function() {
      if (this.year_values[0]) {
        return "" + this.year_values[0] + "-01-01";
      } else {
        return '1996-01-01';
      }
    };
    CapitolWords.prototype.endDate = function() {
      var d;
      d = new Date();
      if (this.year_values[1]) {
        return "" + this.year_values[1] + "-12-31";
      } else {
        return "" + (d.getFullYear()) + "-12-31";
      }
    };
    CapitolWords.prototype.trimGraph = function() {
      if (this.year_values.length === 2) {
        return true;
      } else {
        return false;
      }
    };
    CapitolWords.prototype.smooth = function(list, degree) {
      var frac, func, gauss, i, smoothed, weight, weightGauss, win, _i, _len, _ref;
      win = degree * 2 - 1;
      weight = _.range(0, win).map(function(x) {
        return 1.0;
      });
      weightGauss = [];
      _ref = _.range(0, win);
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        i = _ref[_i];
        i = i - degree + 1;
        frac = i / win;
        gauss = 1 / Math.exp((4 * frac) * (4 * frac));
        weightGauss.push(gauss);
      }
      weight = _(weightGauss).zip(weight).map(function(x) {
        return x[0] * x[1];
      });
      smoothed = _.range(0, (list.length + 1) - win).map(function(x) {
        return 0.0;
      });
      func = function(memo, num) {
        return memo + num;
      };
      return _(_.range(smoothed.length)).each(function(i) {
        return smoothed[i] = _(list.slice(i, i + win)).zip(weight).map(function(x) {
          return x[0] * x[1];
        }).reduce(func, 0) / _(weight).reduce(func, 0);
      });
    };
    return CapitolWords;
  })();
  jQuery(document).ready(function() {
    var cw, d;
    cw = new window.CapitolWords;
    if (typeof termDetailTerm !== 'undefined') {
      cw.populateTermDetailPage(termDetailTerm);
    }
    jQuery('img').error(function() {
      return jQuery(this).hide();
    });
    jQuery('.ngramMenu li').bind('click', function(x) {
      var classToShow;
      classToShow = jQuery(this).attr('class');
      return jQuery(jQuery('.barChart:visible')[0]).hide(0, function() {
        return jQuery("ol#" + classToShow).show(0);
      });
    });
    jQuery('#timelineToggle input').bind('click', function() {
      var selected, selectedId, timelines;
      selectedId = jQuery('input[name=toggle]:checked', '#timelineToggle').attr('id');
      timelines = {
        party: jQuery('#partyTimeline'),
        custom: jQuery('#customTimeline'),
        overall: jQuery('#overallTimeline')
      };
      selected = {
        overallTimelineSelect: 'overall',
        partyTimelineSelect: 'party',
        customTimelineSelect: 'custom'
      }[selectedId];
      return _(timelines).each(function(k, v) {
        if (k === selected) {
          return v.show();
        } else {
          return v.hide();
        }
      });
    });
    jQuery('#partySelect, #stateSelect').change(function() {
      return cw.customizeChart();
    });
    jQuery('.compareSubmit').bind('click', function() {
      return cw.submitHomepageCompareForm();
    });
    jQuery('#termSelect input').bind('keyup', function(e) {
      if (e.keyCode === 13) {
        return cw.submitHomepageCompareForm();
      }
    });
    jQuery('#termSelect input').bind('focus', function() {
      if (jQuery(this).val() === 'Word or phrase') {
        return jQuery(this).val('');
      }
    });
    jQuery('#termSelect input').bind('blur', function() {
      if (jQuery(this).val() === '') {
        return jQuery(this).val('Word or phrase');
      }
    });
    jQuery('#searchFilterButton').bind('click', function() {
      return cw.legislatorSearch();
    });
    if (jQuery('#slider-range').length !== 0) {
      d = new Date();
      jQuery('#slider-range').slider({
        range: true,
        min: 1996,
        max: d.getFullYear(),
        values: [1996, d.getFullYear()],
        slide: function(event, ui) {
          return jQuery('#years').val("" + ui.values[0] + "-" + ui.values[1]);
        },
        stop: function(event, ui) {
          cw.minMonth = "" + ui.values[0] + "01";
          cw.maxMonth = "" + ui.values[1] + "12";
          if (_(cw.a).keys().length > 0 || _(cw.b).keys().length > 0) {
            return cw.limit(cw.minMonth, cw.maxMonth);
          }
        }
      });
      jQuery('#years').val(jQuery('#slider-range').slider('values', 0) + ' - ' + jQuery('#slider-range').slider('values', 1));
    }
    return jQuery('.advanced').bind('click', function() {
      var t;
      t = jQuery(this);
      return jQuery('ul.wordFilter').slideToggle('', function() {
        if (jQuery(this).is(':visible')) {
          return t.addClass('expanded');
        } else {
          return t.removeClass('expanded');
        }
      });
    });
  });
}).call(this);
