(function() {
  /*
  CapitolWords
  main application class
  Requires: jQuery, jQuery ui slider, underscore
  */
  var $, currentMonth;
  var __indexOf = Array.prototype.indexOf || function(item) {
    for (var i = 0, l = this.length; i < l; i++) {
      if (this[i] === item) return i;
    }
    return -1;
  };
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
  jQuery.cleanedValue
  decodes uri components and strips html tags
  */
  $.cleanedValue = function(str) {
    if (!str) {
      return '';
    }
    str = decodeURIComponent(str).replace(/\+/g, ' ');
    return $.trim($("<div>" + str + "</div>").text());
  };
  /*
  jQuery.sum
  returns the sum of an array
  */
  $.sum = function(arr) {
    var sum, val, _i, _len;
    sum = 0;
    for (_i = 0, _len = arr.length; _i < _len; _i++) {
      val = arr[_i];
      sum += val;
    }
    return sum;
  };
  currentMonth = function() {
    var d, pad;
    d = new Date();
    pad = d.getMonth() + 1 > 9 ? '' : '0';
    return "" + (d.getFullYear()) + pad + (d.getMonth() + 1);
  };
  window.CapitolWords = (function() {
    function CapitolWords() {}
    CapitolWords.prototype.cw = CapitolWords;
    CapitolWords.prototype.a = {};
    CapitolWords.prototype.b = {};
    CapitolWords.prototype.debug_progress = 0;
    CapitolWords.prototype.homepageDefaults = {
      'terma': 'Word or phrase',
      'termb': 'Word or phrase',
      'statea': '',
      'stateb': '',
      'partya': 'All',
      'partyb': 'All',
      'start': '199601',
      'end': currentMonth()
    };
    CapitolWords.prototype.itemsToCompare = [];
    CapitolWords.prototype.legislatorData = [];
    CapitolWords.prototype.minMonth = void 0;
    CapitolWords.prototype.maxMonth = void 0;
    CapitolWords.prototype.random_phrase_i = void 0;
    CapitolWords.prototype.smoothing = 0;
    CapitolWords.prototype.spinner = null;
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
      var bioguide_id, pct, url;
      url = 'http://capitolwords.org/api/legislators.json';
      bioguide_id = result['legislator'];
      pct = (result['count'] / maxcount) * 100;
      return $.ajax({
        dataType: 'jsonp',
        url: url,
        async: false,
        data: {
          bioguide_id: bioguide_id,
          apikey: window.cwod_apikey
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
      var legend, legendA, legendB, partyA, partyB, stateA, stateB, termA, termB, _ref;
      _ref = cw.phrases(), termA = _ref[0], termB = _ref[1];
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
      partyA = $.trim($('.partyA input:checked').eq(0).parent().text());
      if (partyA === 'All') {
        partyA = 'All Parties';
      }
      stateA = $('#stateA');
      stateA = stateA.val() && this.states[stateA.val()] || "All states";
      termB = legend[1] && legend[1].split(' [')[0] || "(no term)";
      partyB = $.trim($('.partyB input:checked').eq(0).parent().text());
      if (partyB === 'All') {
        partyB = 'All Parties';
      }
      stateB = $('#stateB');
      stateB = stateB.val() && this.states[stateB.val()] || "All states";
      template = "<div class=\"key\">\n    <span class=\"wordOne\">\n        <span class=\"color\"></span><a href=\"/term/" + termA + "\" class=\"wordOne\">" + termA + "</a>\n        <span class=\"filters\">[" + stateA + ", " + partyA + "]</span>\n    </span>\n    <span class=\"wordTwo\">\n        <span class=\"color\"></span><a href=\"/term/" + termB + "\" class=\"wordTwo\">" + termB + "</a>\n        <span class=\"filters\">[" + stateB + ", " + partyB + "]</span>\n    </span>\n</div>";
      return template;
    };
    CapitolWords.prototype.buildPartyGraph = function(minMonth, maxMonth, requestedUrls) {
      var colors, func, i, imgTag, imgUrl, labelPositions, params, parties, partyAPercentages, partyBPercentages, percentages, url, vals, x;
      if (minMonth && maxMonth) {
        func = function(v) {
          return v['month'] >= minMonth && v['month'] <= maxMonth;
        };
      } else {
        func = function() {
          return true;
        };
      }
      if (!requestedUrls) {
        requestedUrls = this.getDataUrlsForImage($('#partyTermChart'));
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
        'D': '295e72',
        'R': 'bb3110'
      };
      params = {
        x_positions: labelPositions[0],
        x_label_positions: labelPositions[1],
        width: 565,
        height: 300,
        colors: [colors[this.partyResults[0][0]], colors[this.partyResults[1][0]]],
        legend: [this.partyResults[0][0], this.partyResults[1][0]]
      };
      imgUrl = this.showChart([partyAPercentages, partyBPercentages], params);
      imgTag = $("<img id=\"partyTermChart\"\nsrc=\"" + imgUrl + "\" />");
      if (typeof requestedUrls !== 'undefined') {
        for (i in requestedUrls) {
          url = requestedUrls[i];
          imgTag.attr('data-dataurl' + i, url);
        }
      }
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
          'mincount': 0,
          'apikey': window.cwod_apikey
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
        'sort': 'date desc,score desc',
        'apikey': window.cwod_apikey
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
    CapitolWords.prototype.getDataUrlsForImage = function(el) {
      var i, requestedUrls, url;
      requestedUrls = [];
      if ((url = $(el).attr('data-dataurl'))) {
        requestedUrls.push(url);
      } else {
        i = 0;
        while ((url = $(el).attr("data-dataurl" + i))) {
          requestedUrls.push(url);
          i++;
        }
      }
      return requestedUrls;
    };
    CapitolWords.prototype.getEmbedCode = function(container) {
      var fields, key, _i, _len, _ref;
      fields = {
        url: window.location.href,
        chart_color: $('#embedDark:checked').length ? 2 : 1,
        title: window.document.title.split(' | ')[0],
        img_src: '',
        by_party_img_src: '',
        overall_img_src: '',
        start_date: $.deparam(location.href.split('?')[1])['start'] || cw.minMonth || cw.homepageDefaults['start'],
        end_date: $.deparam(location.href.split('?')[1])['end'] || cw.maxMonth || cw.homepageDefaults['end'],
        apikey: window.cwod_apikey
      };
      $('#partyTimeline img').each(function() {
        fields['by_party_img_src'] = $('#partyTimeline img').attr('src');
        fields['overall_img_src'] = $('#overallTimeline img').attr('src');
        fields['chart_type'] = $('#partyTimeline img').is(':visible') ? 2 : 1;
        window.termDetailTerm && (fields['extra'] = {
          'term': termDetailTerm
        });
        return fields['extra'] = {
          by_party_dataurls: cw.getDataUrlsForImage($('#partyTimeline img').eq(0)),
          overall_dataurls: cw.getDataUrlsForImage($('#overallTimeline img').eq(0))
        };
      });
      $('#compareGraphic img#compareTimeline').each(function() {
        var terma, termb, _ref;
        fields['img_src'] = $(this).attr('src');
        fields['chart_type'] = 3;
        _ref = cw.phrases(), terma = _ref[0], termb = _ref[1];
        return fields['extra'] = {
          terma: terma,
          termb: termb,
          statea: $('#stateA').val(),
          stateb: $('#stateB').val(),
          partya: $('input[name=partya]').val(),
          partyb: $('input[name=partyb]').val(),
          dataurls: cw.getDataUrlsForImage($(this))
        };
      });
      _ref = ['img_src', 'by_party_img_src', 'overall_img_src'];
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        key = _ref[_i];
        fields[key] = fields[key].replace(/chs=[\dx]+/, 'chs=570x200');
      }
      $.ajax({
        type: 'POST',
        url: '/embed/',
        data: fields,
        enctype: 'miltipart/form-data',
        success: function(url) {
          var full_url, script;
          full_url = "http://capitolwords.org" + url;
          script = "<script type=\"text/javascript\" src=\"" + full_url + "\"></script>";
          return container.find('textarea').val(script);
        }
      });
      return container.slideDown();
    };
    CapitolWords.prototype.getGraphData = function(term) {
      var cw, data, requestedUrl, url;
      data = {
        'phrase': term,
        'granularity': 'month',
        'percentages': 'true',
        'mincount': 0,
        'apikey': window.cwod_apikey
      };
      url = 'http://capitolwords.org/api/dates.json';
      cw = this;
      requestedUrl = "" + url + "?" + ($.param(data));
      return $.ajax({
        dataType: 'jsonp',
        url: url,
        data: data,
        success: function(data) {
          var counts, imgUrl, labelPositions, overallImgTag, percentages, results;
          results = data['results'];
          cw.results = results;
          counts = _(results).pluck('count');
          percentages = _(results).pluck('percentage');
          labelPositions = cw.buildXLabels(results);
          imgUrl = cw.showChart([percentages], {
            x_labels: labelPositions[0],
            x_label_positions: labelPositions[1],
            width: 565,
            height: 300,
            colors: ['E0B300']
          });
          overallImgTag = "<img id=\"termChart\"\nsrc=\"" + imgUrl + "\"\nalt=\"Timeline of occurrences of " + term + "\"\ndata-dataurl=\"" + requestedUrl + "\" />";
          $('#overallTimeline').html(overallImgTag);
          if (cw.minMonth && cw.maxMonth) {
            cw.limit(cw.minMonth, cw.maxMonth);
          }
          return $('#termChart, #partyTermChart').trigger('load.capitolwords');
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
          'end_date': cw.end_date,
          'apikey': window.cwod_apikey
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
    CapitolWords.prototype.getPartyGraphData = function(term) {
      var cw, data, parties, partyData, render, renderWhenDone, requestedUrls, url;
      data = {
        'phrase': term,
        'granularity': 'month',
        'percentages': true,
        'mincount': 0
      };
      url = 'http://capitolwords.org/api/dates.json';
      cw = this;
      partyData = [];
      requestedUrls = [];
      render = function() {
        var chartData, legendItems;
        chartData = [];
        legendItems = [];
        cw.partyResults = [];
        _(partyData).each(function(partyResult) {
          return cw.partyResults.push(partyResult);
        });
        return cw.buildPartyGraph(cw.minMonth, cw.maxMonth, requestedUrls);
      };
      parties = ['D', 'R'];
      renderWhenDone = _(parties.length).after(render);
      return _(parties).each(function(party) {
        data = {
          'party': party,
          'phrase': term,
          'granularity': 'month',
          'percentages': true,
          'mincount': 0,
          'apikey': window.cwod_apikey
        };
        requestedUrls.push("" + url + "?" + ($.param(data)));
        return jQuery.ajax({
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
          'end_date': cw.end_date,
          'apikey': window.cwod_apikey
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
          'end_date': cw.end_date,
          'apikey': window.cwod_apikey
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
        state: data['state'] || $('#state').val(),
        apikey: window.cwod_apikey
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
        imgUrl = this.showChart([percentages], {
          x_labels: labelPositions[0],
          x_label_positions: labelPositions[1],
          width: 565,
          height: 300,
          colors: ['E0B300']
        });
        return $('#termChart').attr('src', imgUrl);
      } else {
        aVals = _(this.a['all']).select(func);
        bVals = _(this.b['all']).select(func);
        labelPositions = this.buildXLabels(aVals);
        labels = labelPositions[0];
        positions = labelPositions[1];
        return this.showChart([_(aVals).pluck('percentage'), _(bVals).pluck('percentage')], {
          x_labels: labels,
          x_label_positions: positions
        });
      }
    };
    CapitolWords.prototype.makeHomepageHistoryState = function(slid) {
      var cw, hash, hashParams, params, partyA, partyB, phraseA, phraseB, stateA, stateB, _ref;
      cw = this;
      stateA = $('#stateA').val() || cw.homepageDefaults['statea'];
      stateB = $('#stateB').val() || cw.homepageDefaults['stateb'];
      partyA = $('.partyA input:checked').eq(0).val() || cw.homepageDefaults['partya'];
      partyB = $('.partyB input:checked').eq(0).val() || cw.homepageDefaults['partyb'];
      _ref = this.phrases(), phraseA = _ref[0], phraseB = _ref[1];
      params = {
        "terma": phraseA,
        "termb": phraseB,
        "statea": stateA,
        "stateb": stateB,
        "partya": partyA,
        "partyb": partyB,
        "start": this.minMonth || cw.homepageDefaults['start'],
        "end": this.maxMonth || cw.homepageDefaults['end']
      };
      hashParams = {};
      _.each(params, function(v, k) {
        if (v !== cw.homepageDefaults[k] && v !== void 0) {
          return hashParams[k] = v;
        }
      });
      hash = $.param(hashParams);
      return History.pushState({
        'slid': slid
      }, '', "?" + hash);
    };
    CapitolWords.prototype.phrases = function() {
      var SAMPLE_PHRASES, params, phraseA, phraseB;
      params = $('#termSelect').serialize();
      phraseA = $('#terma').val();
      if (phraseA === 'Word or phrase') {
        phraseA = '';
      }
      phraseB = $('#termb').val();
      if (phraseB === 'Word or phrase') {
        phraseB = '';
      }
      if ((cw.random_phrase_i !== void 0) || (phraseA === '') && (phraseB === '') && (window.location.pathname.match(/(^\/?$|homepage\.html)/)) && (!(window.location.href.match(/[\?#]/)))) {
        SAMPLE_PHRASES = [['global warming', 'climate change'], ['iraq', 'afghanistan'], ['war', 'peace'], ['ozone', 'carbon dioxide'], ['bailout', 'big banks']];
        if (cw.random_phrase_i === void 0) {
          cw.random_phrase_i = Math.floor(Math.random() * SAMPLE_PHRASES.length);
        }
        return SAMPLE_PHRASES[cw.random_phrase_i];
      }
      return [phraseA, phraseB];
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
          return $(this).attr('src', '/media/img/no_leg_image.gif');
        }).end().imagesLoaded(function() {}).fadeIn('fast');
      };
      return $('table#legislatorList tbody').fadeOut('fast', buildTable);
    };
    CapitolWords.prototype.populateTermDetailPage = function(term) {
      term = unescape(term);
      this.getGraphData(term);
      this.getStatePopularity(term, jQuery('#stateBarChart'));
      this.getPartyPieChart(term, jQuery('#partyPieChart'));
      this.getLegislatorPopularity(term, jQuery('#legislatorBarChart'));
      if (_(this.partyResults).isUndefined()) {
        this.getPartyGraphData(term);
      }
      if (this.start_date && this.end_date) {
        return this.getCREntries(term);
      }
    };
    CapitolWords.prototype.readHomepageHistory = function(nosubmit) {
      var endYear, hash, param_id_map, params, startYear, state;
      cw.minMonth = cw.maxMonth = false;
      param_id_map = {
        'terma': '#terma',
        'termb': '#termb',
        'statea': '#stateA',
        'stateb': '#stateB'
      };
      state = History.getState();
      hash = state.hash.split('?')[1];
      params = $.deparam(hash);
      if (hash) {
        _(_.defaults(params, cw.homepageDefaults)).each(function(v, k) {
          var id;
          id = param_id_map[k];
          $("" + id).val($.cleanedValue(v));
          if (k === 'partya' && v) {
            return $("#partyA" + v).attr('checked', true);
          } else if (k === 'partyb' && v) {
            return $("#partyB" + v).attr('checked', true);
          } else if (k === 'start' && v !== cw.homepageDefaults[k]) {
            return cw.minMonth = v;
          } else if (k === 'end' && v !== cw.homepageDefaults[k]) {
            return cw.maxMonth = v;
          }
        });
        cw.minMonth = cw.minMonth || cw.homepageDefaults['start'];
        cw.maxMonth = cw.maxMonth || cw.homepageDefaults['end'];
        startYear = cw.minMonth.slice(0, 4);
        endYear = cw.maxMonth.slice(0, 4);
        $("#slider-range").slider("option", "values", [startYear, endYear]);
        cw.limit(cw.minMonth, cw.maxMonth);
        if (!nosubmit) {
          return cw.submitHomepageCompareForm(true);
        }
      }
    };
    CapitolWords.prototype.readLegislatorHistory = function() {
      var chamber, congress, data, hash, party, pieces, state;
      hash = History.getState().hash.split('?')[1];
      data = {
        congress: 112
      };
      $("#congress").val(112);
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
      this.minMonth = "199601";
      this.maxMonth = "201112";
      if (typeof History.getState().hash === 'undefined') {
        return;
      }
      hash = History.getState().hash.split('?')[1];
      if (hash) {
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
      }
      if (this.minMonth || this.maxMonth) {
        startYear = this.minMonth.slice(0, 4);
        endYear = this.maxMonth.slice(0, 4);
        $("#slider-range").slider("values", [startYear, endYear]);
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
    CapitolWords.prototype.showChart = function(data, params) {
      var chart, colors, cw, height, i, img, legend, max, maxValue, requestedUrls, url, values, width, x_label_positions, x_labels;
      x_labels = params.x_labels, x_label_positions = params.x_label_positions, width = params.width, height = params.height, colors = params.colors, legend = params.legend, requestedUrls = params.requestedUrls;
      width = width || 880;
      height = height || 340;
      chart = new GoogleChart(width, height);
      values = [];
      maxValue = 0;
      max = 0;
      cw = this;
      _(data).each(function(item) {
        values = item;
        maxValue = Math.round(_(values).max() * 10000) / 10000;
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
      if (!_(legend).isEmpty() && !location.pathname.match(/^\/?$/)) {
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
      img = $('#chart img.realChart, #compareGraphic img#compareTimeline').attr('src', chart.url());
      if (typeof requestedUrls === 'object' && requestedUrls.length) {
        if (requestedUrls.length > 1) {
          for (i in requestedUrls) {
            url = requestedUrls[i];
            img.attr("data-dataurl" + i, url);
          }
        } else {
          img.attr('data-dataurl', requestedUrls[0]);
        }
      }
      img.fadeIn(500);
      img.trigger('load.capitolwords');
      if (cw.spinner) {
        cw.spinner.stop();
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
      var breakdownUrl, breakdowna, breakdownaData, breakdownb, breakdownbData, cw, d, endDate, opts, phraseA, phraseB, querya, queryaData, queryb, querybData, requestedUrls, startDate, target, url, _ref;
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
      cw.spinner && cw.spinner.stop && cw.spinner.stop();
      cw.spinner = new Spinner(opts).spin(target);
      url = 'http://capitolwords.org/api/dates.json';
      breakdownUrl = 'http://capitolwords.org/api/chart/pie.json';
      requestedUrls = [];
      _ref = cw.phrases(), phraseA = _ref[0], phraseB = _ref[1];
      d = new Date;
      startDate = cw.minMonth ? "" + (cw.minMonth.slice(0, 4)) + "-" + (cw.minMonth.slice(4, 6)) + "-01" : "1996-01-01";
      endDate = cw.maxMonth ? "" + (cw.maxMonth.slice(0, 4)) + "-" + (cw.maxMonth.slice(4, 6)) + "-31" : "" + (d.getFullYear()) + "-" + (d.getMonth() + 1) + "-" + (d.getDate());
      queryaData = {
        phrase: phraseA,
        state: $('#stateA').val() || '',
        party: $('.partyA input:checked').eq(0).val(),
        granularity: 'month',
        percentages: true,
        mincount: 0,
        apikey: window.cwod_apikey
      };
      requestedUrls.push("" + url + "?" + ($.param(queryaData)));
      querya = $.ajax({
        dataType: 'jsonp',
        url: url,
        data: queryaData,
        success: function(data) {
          var aResults;
          aResults = data['results'];
          cw.a['all'] = aResults;
          cw.a['counts'] = _(aResults).pluck('count');
          return cw.a['percentages'] = _(aResults).pluck('percentage');
        }
      });
      querybData = {
        phrase: phraseB,
        state: $('#stateB').val() || '',
        party: $('.partyB input:checked').eq(0).val(),
        granularity: 'month',
        percentages: true,
        mincount: 0,
        apikey: window.cwod_apikey
      };
      requestedUrls.push("" + url + "?" + ($.param(querybData)));
      queryb = $.ajax({
        dataType: 'jsonp',
        url: url,
        data: querybData,
        success: function(data) {
          var bResults;
          bResults = data['results'];
          cw.b['all'] = bResults;
          cw.b['counts'] = _(bResults).pluck('count');
          return cw.b['percentages'] = _(bResults).pluck('percentage');
        }
      });
      breakdownaData = {
        phrase: phraseA,
        output: 'data',
        entity_type: 'party',
        start_date: startDate,
        end_date: endDate,
        apikey: window.cwod_apikey
      };
      breakdowna = $.ajax({
        dataType: 'jsonp',
        url: breakdownUrl,
        data: breakdownaData,
        success: function(data) {
          return cw.a['breakdown'] = data.data;
        }
      });
      breakdownbData = {
        phrase: phraseB,
        output: 'data',
        entity_type: 'party',
        start_date: startDate,
        end_date: endDate,
        apikey: window.cwod_apikey
      };
      breakdownb = $.ajax({
        dataType: 'jsonp',
        url: breakdownUrl,
        data: breakdownbData,
        success: function(data) {
          return cw.b['breakdown'] = data.data;
        }
      });
      $.when(querya, queryb, breakdowna, breakdownb).done(function() {
        var labelPositions, labels, positions;
        labelPositions = cw.buildXLabels(cw.a['all']);
        labels = labelPositions[0];
        positions = labelPositions[1];
        cw.showChart([cw.a['percentages'], cw.b['percentages']], {
          x_labels: labels,
          x_label_positions: positions,
          requestedUrls: requestedUrls
        });
        if (cw.minMonth || cw.maxMonth) {
          return cw.limit(cw.minMonth, cw.maxMonth);
        }
      }).then(function() {
        var aTotal, bTotal, i, legend_html, party, _ref2, _ref3;
        if (cw.spinner) {
          cw.spinner.stop();
        }
        legend_html = cw.build_legend_html();
        $('#compareGraphic div.key span.wordOne span.legend-text').eq(0).html($(legend_html).find('span.wordOne').html());
        $('#compareGraphic div.key span.wordTwo span.legend-text').eq(0).html($(legend_html).find('span.wordTwo').html());
        aTotal = $.sum(cw.a.breakdown[1]);
        if (__indexOf.call(cw.a.breakdown[0], 'D') < 0) {
          $("#compareGraphic .key .wordOne .party-breakdown .D").animate({
            'width': 0
          });
          $("#compareGraphic .key .wordOne .party-breakdown-labels .D .percentage").html("0%");
        }
        if (__indexOf.call(cw.a.breakdown[0], 'R') < 0) {
          $("#compareGraphic .key .wordOne .party-breakdown .R").animate({
            'width': 0
          });
          $("#compareGraphic .key .wordOne .party-breakdown-labels .R .percentage").html("0%");
        }
        _ref2 = cw.a.breakdown[0];
        for (i in _ref2) {
          party = _ref2[i];
          $("#compareGraphic .key .wordOne .party-breakdown ." + party).animate({
            'width': "" + (((cw.a.breakdown[1][i] / aTotal) * 100).toFixed(0)) + "%"
          });
          $("#compareGraphic .key .wordOne .party-breakdown-labels ." + party + " .percentage").html("" + (((cw.a.breakdown[1][i] / aTotal) * 100).toFixed(0)) + "%");
        }
        bTotal = $.sum(cw.b.breakdown[1]);
        if (__indexOf.call(cw.b.breakdown[0], 'D') < 0) {
          $("#compareGraphic .key .wordTwo .party-breakdown .D").animate({
            'width': 0
          });
          $("#compareGraphic .key .wordTwo .party-breakdown-labels .D .percentage").html("0%");
        }
        if (__indexOf.call(cw.b.breakdown[0], 'R') < 0) {
          $("#compareGraphic .key .wordTwo .party-breakdown .R").animate({
            'width': 0
          });
          $("#compareGraphic .key .wordTwo .party-breakdown-labels .R .percentage").html("0%");
        }
        _ref3 = cw.b.breakdown[0];
        for (i in _ref3) {
          party = _ref3[i];
          $("#compareGraphic .key .wordTwo .party-breakdown ." + party).animate({
            'width': "" + ((cw.b.breakdown[1][i] / bTotal) * 100) + "%"
          });
          $("#compareGraphic .key .wordTwo .party-breakdown-labels ." + party + " .percentage").html("" + (((cw.b.breakdown[1][i] / bTotal) * 100).toFixed(0)) + "%");
        }
        return cw.random_phrase_i = void 0;
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
}).call(this);
