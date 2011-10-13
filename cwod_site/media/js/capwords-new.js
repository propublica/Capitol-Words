(function() {
  var $, spinner;
  var __indexOf = Array.prototype.indexOf || function(item) {
    for (var i = 0, l = this.length; i < l; i++) {
      if (this[i] === item) return i;
    }
    return -1;
  };
  spinner = null;
  $ = jQuery;
  /*
  jQuery.deparam
  reverses jQuery's param() method, converting a querystring back to an object
  */
  $.deparam = function(qs) {
    var params, pieces;
    params = {};
    if (!qs) {
      return params;
    }
    pieces = qs.split(/[&=]/);
    $.each(pieces, function(idx, val) {
      if (idx % 2) {
        return params[pieces[idx - 1]] = val;
      }
    });
    return params;
  };
  /*
  CapitolWords
  main application class
  */
  window.CapitolWords = (function() {
    function CapitolWords() {}
    CapitolWords.prototype.a = {};
    CapitolWords.prototype.b = {};
    CapitolWords.prototype.itemsToCompare = [];
    CapitolWords.prototype.legislatorData = [];
    CapitolWords.prototype.minMonth = void 0;
    CapitolWords.prototype.maxMonth = void 0;
    CapitolWords.prototype.smoothing = 0;
    CapitolWords.prototype.year_values = [];
    CapitolWords.prototype.states = {
      "AL": "Alabama",
      "AK": "Alaska",
      "AZ": "Arizona",
      "AR": "Arkansas",
      "CA": "California",
      "CO": "Colorado",
      "CT": "Connecticut",
      "DE": "Delaware",
      "FL": "Florida",
      "GA": "Georgia",
      "HI": "Hawaii",
      "ID": "Idaho",
      "IL": "Illinois",
      "IN": "Indiana",
      "IA": "Iowa",
      "KS": "Kansas",
      "KY": "Kentucky",
      "LA": "Louisiana",
      "ME": "Maine",
      "MD": "Maryland",
      "MA": "Massachusetts",
      "MI": "Michigan",
      "MN": "Minnesota",
      "MS": "Mississippi",
      "MO": "Missouri",
      "MT": "Montana",
      "NE": "Nebraska",
      "NV": "Nevada",
      "NH": "New Hampshire",
      "NJ": "New Jersey",
      "NM": "New Mexico",
      "NY": "New York",
      "NC": "North Carolina",
      "ND": "North Dakota",
      "OH": "Ohio",
      "OK": "Oklahoma",
      "OR": "Oregon",
      "PA": "Pennsylvania",
      "RI": "Rhode Island",
      "SC": "South Carolina",
      "SD": "South Dakota",
      "TN": "Tennessee",
      "TX": "Texas",
      "UT": "Utah",
      "VT": "Vermont",
      "VA": "Virginia",
      "WA": "Washington",
      "WV": "West Virginia",
      "WI": "Wisconsin",
      "WY": "Wyoming",
      "DC": "District of Columbia",
      "AA": "Armed Forces Americas",
      "AE": "Armed Forces Europe",
      "AP": "Armed Forces Pacific",
      "AS": "American Samoa",
      "GU": "Guam",
      "MP": "Northern Mariana Islands",
      "PR": "Puerto Rico",
      "VI": "Virgin Islands"
    };
    CapitolWords.prototype.addLegislatorToChart = function(result, maxcount, div, callback) {
      var bioguide_id, cw, pct, url;
      url = 'http://capitolwords.org/api/legislators.json';
      bioguide_id = result['legislator'];
      pct = (result['count'] / maxcount) * 100;
      cw = this;
      return $.ajax({
        dataType: 'jsonp',
        url: url,
        async: false,
        data: {
          'bioguide_id': bioguide_id
        },
        success: function(data) {
          data = data['results'];
          url = "/legislator/" + bioguide_id + "-" + data['slug'];
          cw.legislatorData.push({
            url: url,
            data: data,
            result: result,
            pct: pct
          });
          return callback();
        }
      });
    };
    CapitolWords.prototype.build_legend = function() {
      var legend, legendA, legendB, partyA, partyB, stateA, stateB, termA, termB;
      termA = $('#terma').val();
      partyA = $('.partyA input:checked').eq(0).val();
      stateA = $('#stateA').val();
      legend = [];
      legendA = termA;
      if (termA && termA !== 'Word or phrase') {
        if (partyA && stateA) {
          legendA += " [" + partyA + "-" + stateA + "]";
        } else if (partyA) {
          legendA += " [" + partyA + "]";
        } else if (stateA) {
          legendA += " [" + stateA + "]";
        }
        legend.push(legendA);
      }
      termB = $('#termb').val();
      partyB = $('.partyB input:checked').eq(0).val();
      stateB = $('#stateB').val();
      legendB = termB;
      if (termB && termB !== 'Word or phrase') {
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
    CapitolWords.prototype.build_legend_html = function() {
      var legend, partyA, partyB, stateA, stateB, template, termA, termB;
      legend = this.build_legend();
      termA = legend[0] && legend[0].split(' [')[0] || "(no term)";
      partyA = $('.partyA input:checked').eq(0).parent().text().trim();
      if (partyA === 'All') {
        partyA = 'All Parties';
      }
      stateA = $('#stateA');
      stateA = stateA.val() && this.states[stateA.val()] || "All states";
      termB = legend[1] && legend[1].split(' [')[0] || "(no term)";
      partyB = $('.partyB input:checked').eq(0).parent().text().trim();
      if (partyB === 'All') {
        partyB = 'All Parties';
      }
      stateB = $('#stateB');
      stateB = stateB.val() && this.states[stateB.val()] || "All states";
      template = "<div class=\"key\">\n    Comparing\n    <span class=\"wordOne\">\n        <span class=\"color\"></span><a href\"#\"=\"\" class=\"wordOne\">\"" + termA + "\"</a>\n        <span class=\"filters\">[" + stateA + ", " + partyA + "]</span>\n    </span>\n    and\n    <span class=\"wordTwo\">\n        <span class=\"color\"></span><a href\"#\"=\"\" class=\"wordTwo\">\"" + termB + "\"</a>\n        <span class=\"filters\">[" + stateB + ", " + partyB + "]</span>\n    </span>\n</div>";
      return template;
    };
    CapitolWords.prototype.buildPartyGraph = function(minMonth, maxMonth) {
      var colors, func, imgTag, imgUrl, labelPositions, parties, partyAPercentages, partyBPercentages, percentages, vals, x;
      if (minMonth && maxMonth) {
        func = function(v) {
          return v['month'] >= minMonth && v['month'] <= maxMonth;
        };
      } else {
        func = function() {
          return true;
        };
      }
      vals = [
        (function() {
          var _i, _len, _ref, _results;
          _ref = this.partyResults;
          _results = [];
          for (_i = 0, _len = _ref.length; _i < _len; _i++) {
            x = _ref[_i];
            _results.push(_(x[1]).select(func));
          }
          return _results;
        }).call(this)
      ][0];
      labelPositions = this.buildXLabels(vals[0]);
      partyAPercentages = _(vals[0]).pluck('percentage');
      partyBPercentages = _(vals[1]).pluck('percentage');
      percentages = [partyAPercentages, partyBPercentages];
      parties = [
        (function() {
          var _i, _len, _ref, _results;
          _ref = this.partyResults;
          _results = [];
          for (_i = 0, _len = _ref.length; _i < _len; _i++) {
            x = _ref[_i];
            _results.push(x[0]);
          }
          return _results;
        }).call(this)
      ];
      colors = {
        'R': 'bb3110',
        'D': '295e72'
      };
      imgUrl = this.showChart([partyAPercentages, partyBPercentages], labelPositions[0], labelPositions[1], 575, 300, [colors[this.partyResults[0][0]], colors[this.partyResults[1][0]]], [this.partyResults[0][0], this.partyResults[1][0]]);
      imgTag = "<img id=\"partyTermChart\" src=\"" + imgUrl + "\"/>";
      return $('#partyTimeline').html(imgTag);
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
            _results.push(Math.round((($.inArray(year, years)) / years.length) * 100));
          }
          return _results;
        })()
      ];
      labels = _(years).map(function(x) {
        return "1/" + (x.slice(2, 4));
      });
      return [labels, positions];
    };
    CapitolWords.prototype.customizeChart = function() {
      var party, state, url;
      party = $('#partySelect').val();
      state = $('#stateSelect').val();
      url = 'http://capitolwords.org/api/chart/timeline.json';
      return $.ajax({
        dataType: 'jsonp',
        url: url,
        data: {
          'party': party,
          'state': state,
          'phrase': $('#term').val(),
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
          return $('#customChart').attr('src', imgUrl);
        }
      });
    };
    CapitolWords.prototype.dateFromMonth = function(month) {
      var datePieces;
      datePieces = month.match(/(\d{4})(\d{2})/).slice(1, 3);
      datePieces.push('01');
      return datePieces.join('-');
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
    CapitolWords.prototype.getCookie = function(name) {
      var cookie, cookieContent, cookieName, cookies, _i, _len, _ref;
      if (document.cookie && (document.cookie !== '')) {
        cookies = _(document.cookie.split(';')).map((function(x) {
          return $.trim(x);
        }));
        for (_i = 0, _len = cookies.length; _i < _len; _i++) {
          cookie = cookies[_i];
          _ref = cookie.split('=', 2), cookieName = _ref[0], cookieContent = _ref[1];
          if (cookieName === name) {
            return decodeURIComponent(cookieContent);
          }
        }
      }
    };
    CapitolWords.prototype.getCREntries = function(term) {
      var cw, data, url;
      url = 'http://capitolwords.org/api/text.json';
      cw = this;
      data = {
        'phrase': term,
        'bioguide_id': "['' TO *]",
        'start_date': cw.start_date,
        'end_date': cw.end_date,
        'sort': 'date desc,score desc'
      };
      return $.ajax({
        dataType: 'jsonp',
        url: url,
        data: data,
        success: function(data) {
          var entries, html, results, urls;
          results = data['results'];
          entries = [];
          urls = [];
          _(results).each(function(entry) {
            var _ref;
            if (entries.length >= 5) {
              return;
            }
            if (_ref = entry['origin_url'], __indexOf.call(urls, _ref) < 0) {
              urls.push(entry['origin_url']);
              return entries.push(entry);
            }
          });
          entries = cw.highlightEntries(entries, term);
          html = "";
          _(entries).each(function(entry) {
            return html += "<li>\n    <h5><a href=\"\">" + (cw.titleCase(entry['title'])) + "</a></h5>\n    <p>" + entry['speaker_first'] + " " + entry['speaker_last'] + ", " + entry['speaker_party'] + "-" + entry['speaker_state'] + "</p>\n    <p>" + entry.date + "</p>\n    <p>" + entry.match + "</p>\n</li>";
          });
          return $('#crEntries').html(html);
        }
      });
    };
    CapitolWords.prototype.getEmbedCode = function(container) {
      var data, imgSrc;
      if ($('#partyTimeline').is(':visible')) {
        imgSrc = $('#partyTimeline img').attr('src');
      } else {
        imgSrc = $('#overallTimeline img').attr('src');
      }
      data = {
        img_src: imgSrc,
        url: window.location.href,
        title: window.document.title.split(' | ')[0],
        chart_type: $('#embedDark:checked').length === 1 ? 'dark' : 'light'
      };
      $.ajax({
        type: 'POST',
        url: '/embed/',
        data: data,
        success: function(url) {
          var full_url, script;
          full_url = "http://capitolwords.org" + url;
          script = "<script type=\"text/javascript\" src=\"" + full_url + "\"></script>";
          return container.find('textarea').val(script);
        }
      });
      return container.slideDown();
    };
    CapitolWords.prototype.getGraph = function(term) {
      var data, url;
      data = {
        'phrase': term,
        'granularity': 'month',
        'percentages': 'true',
        'mincount': 0,
        'legend': false
      };
      url = 'http://capitolwords.org/api/chart/timeline.json';
      return $.ajax({
        dataType: 'jsonp',
        url: url,
        data: data,
        success: function(data) {
          var imgUrl, overallImgTag, results;
          results = data['results'];
          imgUrl = results['url'];
          overallImgTag = "<img src=\"" + imgUrl + "\" alt=\"Timeline of occurrences of " + term + "\"/>";
          return $('#overallTimeline').html(overallImgTag);
        }
      });
    };
    CapitolWords.prototype.getGraphData = function(term) {
      var cw, data, url;
      data = {
        'phrase': term,
        'granularity': 'month',
        'percentages': 'true',
        'mincount': 0
      };
      url = 'http://capitolwords.org/api/dates.json';
      cw = this;
      return $.ajax({
        dataType: 'jsonp',
        url: url,
        data: data,
        success: function(data) {
          var counts, imgUrl, labelPositions, percentages, results;
          results = data['results'];
          cw.results = results;
          window.cwod_results = results;
          counts = _(results).pluck('count');
          percentages = _(results).pluck('percentage');
          labelPositions = cw.buildXLabels(results);
          imgUrl = cw.showChart([percentages], labelPositions[0], labelPositions[1], 575, 300, ['E0B300']);
          window.cwod_counts = $.extend(true, [], counts);
          $.getJSON(imgUrl + '&chof=json', function(data) {
            var annotation_callback, copy_coords, csj, overallImgTag, _i, _len, _ref;
            copy_coords = function(c) {
              if (c.name === 'line0') {
                return window.cwod_line_coords = $.extend(true, [], c.coords);
              }
            };
            _ref = data.chartshape;
            for (_i = 0, _len = _ref.length; _i < _len; _i++) {
              csj = _ref[_i];
              copy_coords(csj);
            }
            annotation_callback = function() {
              var FUZZ_X, FUZZ_Y, MONTHS, annotation_month, annotation_text, annotation_year, i, plural;
              if (!(window.cwod_inchart && ($('#partyTimelineSelect').attr('checked')) !== 'checked')) {
                return $('#annotation').hide();
              } else {
                $('#annotation').show();
                FUZZ_X = 5;
                FUZZ_Y = 6;
                i = 0;
                while ((window.cwod_line_coords[i] + FUZZ_X) < (window.cwod_pagex - $('#termChart').offset().left) && (i < window.cwod_results.length * 2)) {
                  i += 2;
                }
                if ((i / 2) < window.cwod_results.length) {
                  MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
                  annotation_month = MONTHS[(parseInt(window.cwod_results[i / 2].month.substr(4, 2), 10)) - 1];
                  annotation_year = window.cwod_results[i / 2].month.substr(0, 4);
                  plural = window.cwod_counts[i / 2] !== 1 ? 'mentions' : 'mention';
                  annotation_text = "<span class=\"annotation-count\">" + window.cwod_counts[i / 2] + " " + plural + "</span>\n<br /><span class=\"annotation-date\">in " + annotation_month + " " + annotation_year + "</span>";
                  $('#inner-annotation').html(annotation_text);
                  $('#annotation').css({
                    left: $('#termChart').offset().left + window.cwod_line_coords[i] + FUZZ_X,
                    top: $('#termChart').offset().top + window.cwod_line_coords[i + 1] + FUZZ_Y
                  });
                  return true;
                }
              }
            };
            window.clearInterval(window.cwod_interval);
            window.cwod_interval = window.setInterval(annotation_callback, 50);
            overallImgTag = "<img id=\"termChart\" src=\"" + imgUrl + "\" alt=\"Timeline of occurrences of " + term + "\"/>";
            $('#overallTimeline').html(overallImgTag);
            return $('#termChart').mouseenter(function(event) {
              return window.cwod_inchart = true;
            }).mouseleave(function(event) {
              return window.cwod_inchart = false;
            }).mousemove(function(event) {
              return window.cwod_pagex = event.pageX;
            });
          });
          if (cw.minMonth && cw.maxMonth) {
            return cw.limit(cw.minMonth, cw.maxMonth);
          }
        }
      });
    };
    CapitolWords.prototype.getLegislatorPopularity = function(term, div) {
      var cw, url;
      url = 'http://capitolwords.org/api/phrases/legislator.json';
      cw = this;
      return $.ajax({
        dataType: 'jsonp',
        url: url,
        data: {
          'phrase': term,
          'sort': 'relative',
          'per_page': 10,
          'start_date': cw.start_date,
          'end_date': cw.end_date
        },
        success: function(data) {
          var listItems, maxcount, render, renderWhenDone, result, results, _i, _len, _results;
          results = data['results'];
          maxcount = results[0]['count'];
          listItems = [];
          cw.legislatorData = [];
          render = function() {
            var done;
            listItems = [];
            cw.legislatorData.sort(function(a, b) {
              return b['pct'] - a['pct'];
            });
            done = [];
            _(cw.legislatorData).each(function(legislator) {
              var html, _ref;
              if (_ref = legislator.data.bioguide_id, __indexOf.call(done, _ref) >= 0) {
                return;
              }
              done.push(legislator.data.bioguide_id);
              html = "<li>\n    <span class=\"tagValue\" style=\"width:" + legislator['pct'] + "%\">\n        <span class=\"tagPercent\">" + legislator['pct'] + "%</span>\n        <span class=\"tagNumber\"></span>\n    </span>\n    <span class=\"barChartTitle\"><a href=\"" + legislator['url'] + "\">\n        " + legislator['data']['honorific'] + " " + legislator['data']['full_name'] + ", " + legislator['data']['party'] + "-" + legislator['data']['state'] + "\n    </a>\n    </span>\n    </li>";
              return listItems.push(html);
            });
            return div.html(listItems.join(''));
          };
          renderWhenDone = _(results.length).after(render);
          _results = [];
          for (_i = 0, _len = results.length; _i < _len; _i++) {
            result = results[_i];
            _results.push(cw.addLegislatorToChart(result, maxcount, div, renderWhenDone));
          }
          return _results;
        }
      });
    };
    CapitolWords.prototype.getPartyGraph = function(term) {
      var cw, url;
      url = 'http://capitolwords.org/api/chart/timeline.json';
      cw = this;
      return $.ajax({
        dataType: 'jsonp',
        url: url,
        data: {
          'phrase': term,
          'granularity': 'month',
          'percentages': 'true',
          'mincount': 0,
          'legend': true,
          'split_by_party': true,
          'start_date': cw.start_date,
          'end_date': cw.end_date
        },
        success: function(data) {
          var imgTag, imgUrl, results;
          results = data['results'];
          imgUrl = results['url'];
          imgTag = "<img src=\"" + imgUrl + "\" alt=\"Timeline of occurrences of " + term + "\"/>";
          return $('#partyTimeline').html(imgTag);
        }
      });
    };
    CapitolWords.prototype.getPartyGraphData = function(term) {
      var cw, data, parties, partyData, render, renderWhenDone, url;
      data = {
        'phrase': term,
        'granularity': 'month',
        'percentages': true,
        'mincount': 0
      };
      url = 'http://capitolwords.org/api/dates.json';
      cw = this;
      partyData = [];
      render = function() {
        var chartData, legendItems;
        chartData = [];
        legendItems = [];
        cw.partyResults = [];
        _(partyData).each(function(partyResult) {
          return cw.partyResults.push(partyResult);
        });
        return cw.buildPartyGraph(cw.minMonth, cw.maxMonth);
      };
      parties = ['R', 'D'];
      renderWhenDone = _(parties.length).after(render);
      return _(parties).each(function(party) {
        data = {
          'party': party,
          'phrase': term,
          'granularity': 'month',
          'percentages': true,
          'mincount': 0
        };
        return $.ajax({
          dataType: 'jsonp',
          url: url,
          data: data,
          success: function(data) {
            var results;
            results = data['results'];
            partyData.push([party, results]);
            return renderWhenDone();
          }
        });
      });
    };
    CapitolWords.prototype.getPartyPieChart = function(term, div, width, height, callback) {
      var cw, url;
      if (_(width).isUndefined()) {
        width = '';
      }
      if (_(width).isUndefined()) {
        height = '';
      }
      url = 'http://capitolwords.org/api/chart/pie.json';
      cw = this;
      return $.ajax({
        dataType: 'jsonp',
        url: url,
        data: {
          'phrase': term,
          'entity_type': 'party',
          'width': width,
          'height': height,
          'start_date': cw.start_date,
          'end_date': cw.end_date
        },
        success: function(data) {
          var imgUrl, results;
          results = data['results'];
          imgUrl = results['url'];
          return div.find('.default').fadeOut('slow', function() {
            return div.find('.realChart').attr('src', imgUrl).attr('alt', "Pie chart of occurrences of " + term + " by party").fadeIn('slow', function() {
              if (!_(callback).isUndefined()) {
                return callback(term, div);
              }
            });
          });
        }
      });
    };
    CapitolWords.prototype.getStatePopularity = function(term, div) {
      var cw, url;
      url = 'http://capitolwords.org/api/phrases/state.json';
      cw = this;
      return $.ajax({
        dataType: 'jsonp',
        url: url,
        data: {
          'phrase': term,
          'sort': 'relative',
          'per_page': 10,
          'start_date': cw.start_date,
          'end_date': cw.end_date
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
              state = cw.states[state];
            }
            url = "/state/" + abbrev;
            pct = (result['count'] / maxcount) * 100;
            html = "<li>\n    <span class=\"tagValue\" style=\"width: " + pct + "%;\">\n        <span class=\"tagPercent\">" + pct + "%</span>\n        <span class=\"tagNumber\"></span>\n    </span>\n    <span class=\"barChartTitle\"><a href=\"" + url + "\">" + state + "</a></span>\n</li>";
            return div.append(html);
          });
        }
      });
    };
    CapitolWords.prototype.highlightEntries = function(entries, term) {
      var entry_matches, regexp;
      entry_matches = [];
      regexp = new RegExp(term, "ig");
      _(entries).each(function(entry) {
        var match;
        match = null;
        _(entry['speaking']).each(function(graf) {
          var matcher, versions_of_term;
          graf = graf.replace(/\n/, '');
          versions_of_term = _(graf.match(regexp)).uniq();
          if (!_(versions_of_term).isEmpty()) {
            matcher = new RegExp('(' + versions_of_term.join('|') + ')');
            match = graf.replace(matcher, function(a, b) {
              return "<em>" + b + "</em>";
            });
          }
        });
        entry['match'] = match;
        return entry_matches.push(entry);
      });
      return entry_matches;
    };
    CapitolWords.prototype.legislatorSearch = function(data) {
      var cw;
      cw = this;
      data = {
        chamber: data['chamber'] || $('#chamber').val(),
        party: data['party'] || $('#party').val(),
        congress: data['congress'] || $('#congress').val(),
        state: data['state'] || $('#state').val()
      };
      return $.ajax({
        dataType: 'jsonp',
        url: 'http://capitolwords.org/api/legislators.json',
        data: data,
        success: function(data) {
          return cw.populateLegislatorList(data['results']);
        }
      });
    };
    CapitolWords.prototype.limit = function(minMonth, maxMonth) {
      var aVals, bVals, func, imgUrl, labelPositions, labels, percentages, positions, vals;
      if (minMonth && maxMonth) {
        func = function(v) {
          return v['month'] >= minMonth && v['month'] <= maxMonth;
        };
      } else {
        func = function() {
          return true;
        };
      }
      if (typeof termDetailTerm !== 'undefined') {
        vals = _(this.results).select(func);
        percentages = _(vals).pluck('percentage');
        labelPositions = this.buildXLabels(vals);
        imgUrl = this.showChart([percentages], labelPositions[0], labelPositions[1], 575, 300, ['E0B300']);
        return $('#termChart').attr('src', imgUrl);
      } else {
        aVals = _(this.a['all']).select(func);
        bVals = _(this.b['all']).select(func);
        labelPositions = this.buildXLabels(aVals);
        labels = labelPositions[0];
        positions = labelPositions[1];
        return this.showChart([_(aVals).pluck('percentage'), _(bVals).pluck('percentage')], labels, positions);
      }
    };
    CapitolWords.prototype.makeHomepageHistoryState = function(slid) {
      var hash, params, partyA, partyB, stateA, stateB;
      stateA = $('#stateA').val() || '';
      stateB = $('#stateB').val() || '';
      partyA = $('.partyA input:checked').eq(0).val();
      partyB = $('.partyB input:checked').eq(0).val();
      params = {
        "terma": this.phraseA(),
        "termb": this.phraseB(),
        "statea": stateA,
        "stateb": stateB,
        "partya": partyA,
        "partyb": partyB,
        "start": this.minMonth,
        "end": this.maxMonth
      };
      hash = $.param(params);
      return History.pushState({
        'slid': slid
      }, '', "?" + hash);
    };
    CapitolWords.prototype.phraseA = function() {
      var phraseA;
      phraseA = $('#terma').val();
      if (phraseA === 'Word or phrase') {
        return '';
      } else {
        return phraseA;
      }
    };
    CapitolWords.prototype.phraseB = function() {
      var phraseB;
      phraseB = $('#termb').val();
      if (phraseB === 'Word or phrase') {
        return '';
      } else {
        return phraseB;
      }
    };
    CapitolWords.prototype.populateLegislatorList = function(legislators) {
      var buildTable;
      buildTable = function() {
        var bioguides, n;
        $('table#legislatorList tbody').empty();
        bioguides = [];
        n = 0;
        _(legislators).each(function(legislator) {
          var klass, tr;
          if (!_(bioguides).include(legislator['bioguide_id'])) {
            bioguides.push(legislator['bioguide_id']);
            klass = n % 2 === 0 ? 'even' : 'odd';
            n++;
            tr = "<tr class=\"" + klass + "\">\n    <td>\n        <a href=\"/legislator/" + legislator['bioguide_id'] + "-" + legislator['slug'] + "\">\n        <img class=\"legislatorImage\" alt=\"legislator photo\" src=\"http://assets.sunlightfoundation.com/moc/40x50/" + legislator['bioguide_id'] + ".jpg\"/>\n        </a>\n    </td>\n    <td><a href=\"/legislator/" + legislator['bioguide_id'] + "-" + legislator['slug'] + "\">" + legislator['name'] + "</a></td>\n    <td>" + legislator['state'] + "</td>\n    <td>" + legislator['party'] + "</td>\n    <td>" + legislator['chamber'] + "</td>\n</tr>";
            return $('table#legislatorList tbody').append(tr);
          }
        });
        return $('table#legislatorList tbody').find('img').error(function() {
          return $(this).hide();
        }).end().imagesLoaded(function() {}).fadeIn('fast');
      };
      return $('table#legislatorList tbody').fadeOut('fast', buildTable);
    };
    CapitolWords.prototype.populateTermDetailPage = function(term) {
      if (_(this.results).isUndefined()) {
        this.getGraphData(term);
      }
      this.getStatePopularity(term, $('#stateBarChart'));
      this.getPartyPieChart(term, $('#partyPieChart'));
      this.getLegislatorPopularity(term, $('#legislatorBarChart'));
      if (_(this.partyResults).isUndefined()) {
        this.getPartyGraphData(term);
      }
      if (this.start_date && this.end_date) {
        return this.getCREntries(term);
      }
    };
    CapitolWords.prototype.readHomepageHistory = function(nosubmit) {
      var cw, data, endYear, hash, mapping, pieces, showAdvanced, startYear;
      mapping = {
        'terma': '#terma',
        'termb': '#termb',
        'statea': '#stateA',
        'stateb': '#stateB'
      };
      hash = History.getState().hash.split('?')[1];
      data = {};
      showAdvanced = false;
      cw = this;
      if (hash) {
        pieces = hash.split('&');
        _(pieces).each(function(piece) {
          var id, k, v, _ref;
          _ref = piece.split('='), k = _ref[0], v = _ref[1];
          id = mapping[k];
          $("" + id).val(v);
          if (k === 'partya' || k === 'partyb' || k === 'statea' || k === 'stateb') {
            showAdvanced = true;
          }
          if (k === 'partya' && v) {
            return $("#partyA" + v).attr('checked', true);
          } else if (k === 'partyb' && v) {
            return $("#partyB" + v).attr('checked', true);
          } else if (k === 'start' && v) {
            return cw.minMonth = v;
          } else if (k === 'end' && v) {
            return cw.maxMonth = v;
          }
        });
        if (showAdvanced) {
          $('ul.wordFilter').show();
          $('.advanced').addClass('expanded');
        }
        if (this.minMonth || this.maxMonth) {
          startYear = this.minMonth.slice(0, 4);
          endYear = this.maxMonth.slice(0, 4);
          $("#slider-range").slider("option", "values", [startYear, endYear]);
          this.limit(this.minMonth, this.maxMonth);
        }
        if (!nosubmit) {
          return this.submitHomepageCompareForm(true);
        }
      }
    };
    CapitolWords.prototype.readLegislatorHistory = function() {
      var chamber, congress, data, hash, party, pieces, state;
      hash = History.getState().hash.split('?')[1];
      data = {};
      if (hash) {
        pieces = hash.split('&');
        chamber = party = congress = state = void 0;
        _(pieces).each(function(piece) {
          var k, v, _ref;
          _ref = piece.split('='), k = _ref[0], v = _ref[1];
          $("#" + k).val(v);
          return data[k] = v;
        });
      }
      return this.legislatorSearch(data);
    };
    CapitolWords.prototype.readTermDetailPageHistory = function() {
      var endYear, hash, k, piece, pieces, startYear, v, x, _i, _len;
      if (typeof History.getState().hash === 'undefined') {
        return;
      }
      hash = History.getState().hash.split('?')[1];
      if (!hash) {
        return;
      }
      pieces = [
        (function() {
          var _i, _len, _ref, _results;
          _ref = hash.split('&');
          _results = [];
          for (_i = 0, _len = _ref.length; _i < _len; _i++) {
            x = _ref[_i];
            _results.push(x.split('='));
          }
          return _results;
        })()
      ][0];
      for (_i = 0, _len = pieces.length; _i < _len; _i++) {
        piece = pieces[_i];
        k = piece[0], v = piece[1];
        if (k === 'start') {
          this.minMonth = v;
          this.start_date = this.dateFromMonth(this.minMonth);
        } else if (k === 'end') {
          this.maxMonth = v;
          this.end_date = this.dateFromMonth(this.maxMonth);
        }
      }
      if (this.minMonth || this.maxMonth) {
        startYear = this.minMonth.slice(0, 4);
        endYear = this.maxMonth.slice(0, 4);
        $("#slider-range").slider("option", "values", [startYear, endYear]);
        return this.limit(this.minMonth, this.maxMonth);
      }
    };
    CapitolWords.prototype.sameOrigin = function(url) {
      var host, origin, protocol, sr_origin;
      host = document.location.host;
      protocol = document.location.protocol;
      sr_origin = "//" + host;
      origin = protocol + sr_origin;
      return (url === origin || url.slice(0, origin.length + 1) === origin + '/') || (url === sr_origin || url.slice(0, sr_origin.length + 1) === sr_origin + '/') || !(/^(\/\/|http:|https:).*/.test(url));
    };
    CapitolWords.prototype.showChart = function(data, x_labels, x_label_positions, width, height, colors, legend) {
      var chart, cw, max, maxValue, values;
      width = width || 860;
      height = height || 340;
      chart = new GoogleChart(width, height);
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
      if (!colors) {
        colors = ['8E2844', 'A85B08', 'AF9703'];
      }
      if (!legend) {
        legend = this.build_legend();
      }
      if (!_(legend).isEmpty()) {
        chart.set_legend(legend);
      }
      chart.set_colors(colors.slice(0, legend.length));
      chart.set_axis_labels('y', ['', "" + max + "%"]);
      if (x_labels) {
        chart.set_axis_labels('x', x_labels);
      }
      if (x_label_positions) {
        chart.set_axis_positions('x', x_label_positions);
      }
      if ($('#chart img.realChart, #compareGraphic img.default')) {
        $('#chart img.realChart, #compareGraphic img.default').attr('src', chart.url()).fadeIn(100);
      }
      if (spinner) {
        spinner.stop();
      }
      return chart.url();
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
    CapitolWords.prototype.startDate = function() {
      if (this.year_values[0]) {
        return "" + this.year_values[0] + "-01-01";
      } else {
        return '1996-01-01';
      }
    };
    CapitolWords.prototype.submitHomepageCompareForm = function(skipState) {
      var cw, opts, querya, queryb, target, url;
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
      querya = $.ajax({
        dataType: 'jsonp',
        url: url,
        data: {
          phrase: cw.phraseA(),
          state: $('#stateA').val() || '',
          party: $('.partyA input:checked').eq(0).val(),
          granularity: 'month',
          percentages: true,
          mincount: 0
        },
        success: function(data) {
          var aResults;
          aResults = data['results'];
          cw.a['all'] = aResults;
          cw.a['counts'] = _(aResults).pluck('count');
          return cw.a['percentages'] = _(aResults).pluck('percentage');
        }
      });
      queryb = $.ajax({
        dataType: 'jsonp',
        url: url,
        data: {
          phrase: cw.phraseB(),
          state: $('#stateB').val() || '',
          party: $('.partyB input:checked').eq(0).val(),
          granularity: 'month',
          percentages: true,
          mincount: 0
        },
        success: function(data) {
          var bResults;
          bResults = data['results'];
          cw.b['all'] = bResults;
          cw.b['counts'] = _(bResults).pluck('count');
          return cw.b['percentages'] = _(bResults).pluck('percentage');
        }
      });
      $.when(a, b).done(function() {
        var labelPositions, labels, positions;
        if (cw.minMonth || cw.maxMonth) {
          return cw.limit(cw.minMonth, cw.maxMonth);
        } else {
          labelPositions = cw.buildXLabels(cw.a['all']);
          labels = labelPositions[0];
          positions = labelPositions[1];
          return cw.showChart([cw.a['percentages'], cw.b['percentages']], labels, positions);
        }
      }).then(function() {
        if (spinner) {
          spinner.stop();
        }
        return $('#compareGraphic div.key').eq(0).replaceWith(cw.build_legend_html());
      });
      if (!skipState) {
        return this.makeHomepageHistoryState(true);
      }
    };
    CapitolWords.prototype.titleCase = function(s) {
      return s.replace(/\w\S*/g, function(txt) {
        return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
      });
    };
    CapitolWords.prototype.trimGraph = function() {
      if (this.year_values.length === 2) {
        return true;
      } else {
        return false;
      }
    };
    return CapitolWords;
  })();
  /*
  Add csrf token to ajax POSTs
  */
  $(document).ajaxSend(function(event, xhr, settings) {
    var cw;
    cw = new window.CapitolWords;
    if ((settings.type === 'POST') && cw.sameOrigin(settings.url)) {
      return xhr.setRequestHeader("X-CSRFToken", cw.getCookie('csrftoken'));
    }
  });
  /*
  DomReady Handler
  */
  $(document).ready(function() {
    var area, cw, d, endYear, startYear;
    cw = new window.CapitolWords;
    if (typeof termDetailTerm !== 'undefined') {
      cw.readTermDetailPageHistory();
      cw.populateTermDetailPage(termDetailTerm);
      History.Adapter.bind(window, 'statechange', function() {
        cw.readTermDetailPageHistory();
        return cw.populateTermDetailPage(termDetailTerm);
      });
    }
    $('img').error(function() {
      return $(this).hide();
    });
    $('.ngramMenu span').bind('click', function(x) {
      var classToShow;
      classToShow = $(this).attr('class');
      $('.ngramMenu span').removeAttr('id');
      $(this).attr('id', 'selected');
      return $('.barChart:visible').eq(0).hide(0, function() {
        return $("ol#" + classToShow).show(0);
      });
    });
    $('#timelineToggle input').bind('click', function() {
      var selected, selectedId, timelines;
      selectedId = $('input[name=toggle]:checked', '#timelineToggle').attr('id');
      timelines = [['party', $('#partyTimeline')], ['overall', $('#overallTimeline')]];
      selected = {
        'overallTimelineSelect': 'overall',
        'partyTimelineSelect': 'party'
      }[selectedId];
      return _(timelines).each(function(timeline) {
        var name, obj;
        name = timeline[0];
        obj = timeline[1];
        if (name === selected) {
          return obj.show();
        } else {
          return obj.hide();
        }
      });
    });
    $('#partySelect, #stateSelect').change(function() {
      return cw.customizeChart();
    });
    $('.compareSubmit').bind('click', function() {
      return cw.submitHomepageCompareForm();
    });
    $('#termSelect input').bind('keyup', function(e) {
      if (e.keyCode === 13) {
        return cw.submitHomepageCompareForm();
      }
    });
    $('#termSelect input').bind('focus', function() {
      if ($(this).val() === 'Word or phrase') {
        return $(this).val('');
      }
    });
    $('#termSelect input').bind('blur', function() {
      if ($(this).val() === '') {
        return $(this).val('Word or phrase');
      }
    });
    $('#searchFilterButton').bind('click', function() {
      var hash, pieces;
      pieces = [];
      $('#searchFilter select').each(function(select) {
        var id, val;
        id = $(this).attr('id');
        val = $(this).val();
        return pieces.push("" + id + "=" + val);
      });
      hash = pieces.join('&');
      History.pushState({}, '', "/legislator?" + hash);
      return cw.legislatorSearch({});
    });
    $('#signUp').find('input[type=text]').bind('focus', function() {
      var el;
      el = $(this);
      try {
        return el.parent().find('label[for=' + el.attr('id') + ']').eq(0).addClass('hidden');
      } catch (_e) {}
    }).bind('blur', function() {
      var el;
      el = $(this);
      if (!el.val()) {
        try {
          return el.parent().find('label[for=' + el.attr('id') + ']').eq(0).removeClass('hidden');
        } catch (_e) {}
      }
    });
    if (window.location.pathname.match(/^\/legislator\/?$/)) {
      cw.readLegislatorHistory();
      History.Adapter.bind(window, 'statechange', function() {
        return cw.readLegislatorHistory();
      });
    }
    if (window.location.pathname.match(/^\/?$/)) {
      cw.readHomepageHistory();
      History.Adapter.bind(window, 'statechange', function() {
        if (History.getState()['data']['slid'] !== true) {
          return cw.readHomepageHistory();
        }
      });
    }
    if (!_($('#slider-range')).isEmpty()) {
      d = new Date();
      if (cw.minMonth && cw.maxMonth) {
        startYear = cw.minMonth.slice(0, 4);
        endYear = cw.maxMonth.slice(0, 4);
      } else {
        startYear = 1996;
        endYear = d.getFullYear();
      }
      $('#slider-range').slider({
        range: true,
        min: 1996,
        max: d.getFullYear(),
        values: [startYear, endYear],
        slide: function(event, ui) {
          return $('#years').val("" + ui.values[0] + "-" + ui.values[1]);
        },
        stop: function(event, ui) {
          cw.minMonth = "" + ui.values[0] + "01";
          cw.maxMonth = "" + ui.values[1] + "12";
          if (!_(_(cw.a).keys()).isEmpty() || !_(_(cw.b).keys()).isEmpty()) {
            cw.limit(cw.minMonth, cw.maxMonth);
          } else if (typeof termDetailTerm !== 'undefined') {
            cw.limit(cw.minMonth, cw.maxMonth);
            cw.buildPartyGraph(cw.minMonth, cw.maxMonth);
            cw.start_date = cw.dateFromMonth(cw.minMonth);
            cw.end_date = cw.dateFromMonth(cw.maxMonth);
            cw.populateTermDetailPage(termDetailTerm);
          }
          return cw.makeHomepageHistoryState(true);
        }
      });
    }
    $('.advanced').bind('click', function() {
      var t;
      t = $(this);
      return $('ul.wordFilter').slideToggle('', function() {
        if ($(this).is(':visible')) {
          return t.addClass('expanded');
        } else {
          return t.removeClass('expanded');
        }
      });
    });
    $('#embed span').bind('click', function() {
      var t;
      t = $('.embedContainer');
      if (t.is(':visible')) {
        return t.slideUp();
      } else {
        return cw.getEmbedCode(t);
      }
    });
    $('#customizeEmbed input').change(function() {
      return cw.getEmbedCode($('.embedContainer'));
    });
    (area = $('#rtColumn')) && area.length && area.imagesLoaded(function() {});
    return Emphasis.init();
  });
}).call(this);
