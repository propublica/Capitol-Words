var $j = jQuery.noConflict();

var CapitolWords = CapitolWords || {};

CapitolWords.states = {
    "WA": "Washington", "VA": "Virginia", "DE": "Delaware", 
    "DC": "District of Columbia", "WI": "Wisconsin", "WV": "West Virginia", 
    "HI": "Hawaii", "CO": "Colorado", "FL": "Florida", "WY": "Wyoming", 
    "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico", "TX": "Texas", 
    "LA": "Louisiana", "NC": "North Carolina", "ND": "North Dakota", "NE": "Nebraska", 
    "TN": "Tennessee", "NY": "New York", "PA": "Pennsylvania", "CA": "California", 
    "NV": "Nevada", "AA": "Armed Forces Americas", "PR": "Puerto Rico", "GU": "Guam", 
    "AE": "Armed Forces Europe", "VI": "Virgin Islands", "AK": "Alaska", "AL": "Alabama", 
    "AP": "Armed Forces Pacific", "AS": "American Samoa", "AR": "Arkansas", "VT": "Vermont", 
    "IL": "Illinois", "GA": "Georgia", "IN": "Indiana", "IA": "Iowa", "OK": "Oklahoma", 
    "AZ": "Arizona", "ID": "Idaho", "CT": "Connecticut", "ME": "Maine", "MD": "Maryland", 
    "MA": "Massachusetts", "OH": "Ohio", "UT": "Utah", "MO": "Missouri", "MN": "Minnesota", 
    "MI": "Michigan", "RI": "Rhode Island", "KS": "Kansas", "MT": "Montana", 
    "MP": "Northern Mariana Islands", "MS": "Mississippi", "SC": "South Carolina", 
    "KY": "Kentucky", "OR": "Oregon", "SD": "South Dakota"};

CapitolWords.customizeChart = function () {
    var party = $j("#partySelect").val();
    var state = $j("#stateSelect").val();
    var url = 'http://capitolwords.org/api/chart/timeline.json';
    $j.ajax({
        dataType: 'jsonp',
        url: url,
        data: {'party': party,                                                                            
               'state': state,                                                                            
               'phrase': $j("#term").val(),                                                                   
               'granularity': 'month',
               'percentages': 'true',
               'legend': 'false',
               'mincount': 0},
        success: function (data) {
            var results = data['results'];
            var imgUrl = results['url'];
            var imgTag = '<img src="' + imgUrl + '"/>';
            $j("#customChart").attr('src', imgUrl);
        }
    });
};

CapitolWords.getGraph = function (term) {
    url = 'http://capitolwords.org/api/chart/timeline.json'
    $j.ajax({
        dataType: 'jsonp',
        url: url,
        data: {
            'phrase': term,
            'granularity': 'month',
            'percentages': true,
            'mincount': 0,
            'legend': false
        },
        success: function (data) {
            var results = data['results'];
            var imgUrl = results['url'];
            var overallImgTag = '<img src="' + imgUrl + '" alt="Timeline of occurrences of ' + term + '"/>';
            var customImgTag = '<img id="customChart" src="' + imgUrl + '" alt="Custom timeline of occurrences of ' + term + '"/>';
            $j("#overallTimeline").html(overallImgTag);
            $j("#customTimeline").append(customImgTag);
        }
    });
};

CapitolWords.getPartyGraph = function (term) {
    url = 'http://capitolwords.org/api/chart/timeline.json'
    $j.ajax({
        dataType: 'jsonp',
        url: url,
        data: {
            'phrase': term,
            'granularity': 'month',
            'percentages': true,
            'mincount': 0,
            'legend': true,
            'split_by_party': true,
        },
        success: function (data) {
            var results = data['results'];
            var imgUrl = results['url'];
            var imgTag = '<img src="' + imgUrl + '" alt="Timeline of occurrences of ' + term + '"/>';
            $j("#partyTimeline").html(imgTag);
        }
    });
};

CapitolWords.getPartyPieChart = function (term, div, width, height, callback) {
    if (typeof width === 'undefined') {
        width = '';
    }
    if (typeof height === 'undefined') {
        height = '';
    }
    url = 'http://capitolwords.org/api/chart/pie.json';
    $j.ajax({
        dataType: 'jsonp',
        url: url,
        data: {
            'phrase': term,
            'entity_type': 'party',
            'width': width,
            'height': height
        },
        success: function (data) {
            var results = data['results'];
            var imgUrl = results['url'];
            div.find('.default').fadeOut('slow', function () {
                div
                    .find('.realChart')
                    .attr("src", imgUrl)
                    .attr("alt", "Pie chart of occurrences of " + term + " by party")
                    .fadeIn('slow', function () {
                        if (typeof callback !== 'undefined') {
                            callback(term, div);
                        }
                     });
            });

        }
    });
};

CapitolWords.addLegislatorToChart = function (result, maxcount, div) {
    url = 'http://capitolwords.org/api/legislators.json';
    var bioguide_id = result['legislator'];
    var pct = (result['count'] / maxcount) * 100;
    $j.ajax({
        dataType: 'jsonp',
        url: url,
        async: false,
        data: {
            'bioguide_id': bioguide_id
        },
        success: function (data) {
            var url = '/legislator/' + bioguide_id + '-' + data['slug'];
            var html = '';
            html += '<li>';
            html += '<span class="tagValue" style="width:' + pct + '%;">';
            html += '<span class="tagPercent">' + pct + '%</span>';
            html += '<span class="tagNumber"></span>';
            html += '</span>';
            html += '<span class="barChartTitle"><a href="' + url + '">';
            html += data['honorific'] + ' ';
            html += data['full_name'] + ', ';
            html += data['party'] + '-' + data['state'];
            html += '</a></span>';
            html += '</li>';
            div.append(html);
        }
    });
};

CapitolWords.getLegislatorPopularity = function (term, div) {
    url = 'http://capitolwords.org/api/phrases/legislator.json';
    $j.ajax({
        dataType: 'jsonp',
        url: url,
        data: {
            'phrase': term,
            'sort': 'relative',
            'per_page': 10
        },
        success: function (data) {
            var results = data['results'];
            var maxcount = results[0]['count'];
            div.html('');
            for (i in results) {
                var result = results[i];
                CapitolWords.addLegislatorToChart(result, maxcount, div);
            }
        }
    });
};

CapitolWords.getStatePopularity = function (term, div) {
    url = 'http://capitolwords.org/api/phrases/state.json';
    $j.ajax({
        dataType: 'jsonp',
        url: url,
        data: {
            'phrase': term,
            'sort': 'relative',
            'per_page': 10
        },
        success: function (data) {
            div.html('');
            var results = data['results'];
            var maxcount = results[0]['count']
            for (i in results) {
                var result = results[i];
                var abbrev = result.state;
                var state = abbrev;
                if (CapitolWords.states.hasOwnProperty(state)) {
                    state = CapitolWords.states[state];
                }
                var url = '/state/' + abbrev;
                var pct = (result['count'] / maxcount) * 100;
                var html =  '';
                html += '<li>';
                html += '<span class="tagValue" style="width:' + pct + '%;">';
                html += '<span class="tagPercent">' + pct + '%</span>';
                html += '<span class="tagNumber"></span>';
                html += '</span>';
                html += '<span class="barChartTitle"><a href="' + url + '">' + state + '</a></span>';
                html += '</li>';
                div.append(html);
            }
        }
    });
};

CapitolWords.populateTermDetailPage = function (term) {
    this.getGraph(term);
    this.getStatePopularity(term, $j("#stateBarChart"));
    this.getPartyPieChart(term, $j("#partyPieChart"));
    this.getLegislatorPopularity(term, $j("#legislatorBarChart"));
    this.getPartyGraph(term);
};

var spinner;

CapitolWords.compare = function (toCompare) {
    var url = 'http://capitolwords.org/api/chart/timeline.json';
    var terms = [];
    var parties = [];
    var states = [];
    var item;
    for (i in toCompare.slice(0, 3)) {
        item = toCompare[i];
        terms.push(item.term || '');
        parties.push(item.party || '');
        states.push(item.states || '');
    }
    terms = terms.join(',');
    parties = parties.join(',');
    states = states.join(',');
    $j.ajax({
        dataType: 'jsonp',
        url: url,
        data: {
            'phrases': terms,
            'parties': parties,
            'states': states,
            'granularity': 'month',
            'percentages': true,
            'mincount': 0,
            'compare': true,
            'width': 860,
            'height': 340,
            'smoothing': 0,
            'start_date': this.startDate(),
            'end_date': this.endDate(),
            'trim': this.trimGraph()
        },
        success: function (data) {
            var results = data['results'];
            var imgUrl = results['url'];

            $j("#chart img.default, #compareGraphic img.default").fadeOut('fast', function () {
                $j("#chart img.realChart, #compareGraphic img.default").attr("src", imgUrl).fadeIn('fast');
            });
            spinner.stop();
        }
    });
};


CapitolWords.populateLegislatorList = function (legislators) {
    var buildTable = function () {
        $j("table#legislatorList tbody").empty();
        var legislator;
        var tr;
        var klass;
        for (i in legislators) {
            legislator = legislators[i];
            if (i % 2 == 0) {
                klass = 'even';
            } else {
                klass = 'odd';
            }
            tr = '';
            tr += '<tr class="' + klass + '">';
            tr += '<td><img class="legislatorImage" alt="legislator photo" src="http://assets.sunlightfoundation.com/moc/40x50/' + legislator.bioguide_id + '.jpg" /></td>';
            tr += '<td><a href="/legislator/' + legislator.bioguide_id + '-' + legislator.slug + '">' + legislator.name + '</a></td>';
            tr += '<td>' + legislator.state + '</td>';
            tr += '<td>' + legislator.party + '</td>';
            tr += '<td>' + legislator.chamber + '</td>';
            tr += '</tr>';
            $j("table#legislatorList tbody").append(tr);
        }
        $j("table#legislatorList tbody").fadeIn('fast', function () {
            $j("img").error(function(){
                $j(this).hide();
            });
        });
    }
    $j("table#legislatorList tbody").fadeOut('fast', buildTable);
}

CapitolWords.itemsToCompare = [];

CapitolWords.a = {}, 
    CapitolWords.b = {}, 
    CapitolWords.minMonth, 
    CapitolWords.maxMonth;

CapitolWords.limit = function () {
    var func;
    if (this.minMonth && this.maxMonth) {
        func = function (v) {
            return v['month'] >= CapitolWords.minMonth && v['month'] <= CapitolWords.maxMonth;
        }
    } else {
        func = function () {
            return true;
        }
    }
    var aVals = _(this.a['all']).select(func);
    var bVals = _(this.b['all']).select(func);

    var labelPositions = this.buildXLabels(aVals);
    var labels = labelPositions[0];
    var positions = labelPositions[1];
    this.showChart([_(aVals).pluck('percentage'), _(bVals).pluck('percentage')], labels, positions);
}

CapitolWords.buildXLabels = function (values) {
    var years = _(_(values).pluck('month'))
                    .select(function (x) {
                        return x.match(/01$/);
                    });
    var positions = [], year, numYears = years.length;
    for (i in years) {
        year = years[i];
        positions.push(Math.round((years.indexOf(year) / numYears) * 100));
    }
    var labels = _(years).map(function (x) {
                        return "1/" + x.slice(2, 4);
                    });
    return [labels, positions];

    /*
    return _(_(values).pluck('month'))
                    .select(function (x) { 
                        return x.match(/01$/); 
                    })
                    .map(function (x) { 
                        return "'" + x.slice(2, 4); 
                    });
    */
}


CapitolWords.submitHomepageCompareForm = function () {

    // spinner options.
    var opts = {
      lines: 12, // The number of lines to draw
      length: 7, // The length of each line
      width: 4, // The line thickness
      radius: 10, // The radius of the inner circle
      color: '#000', // #rbg or #rrggbb
      speed: 1, // Rounds per second
      trail: 100, // Afterglow percentage
      shadow: true // Whether to render a shadow
    };
    var target = document.getElementById('compareGraphic');
    spinner = new Spinner(opts).spin(target);

    var item;
    var items = [];
    var div;
    var url = 'http://capitolwords.org/api/dates.json';

    var phraseA = $j("#terma").val();
    if (phraseA == 'Word or phrase') {
        phraseA = '';
    }
    var phraseB = $j("#termb").val();
    if (phraseB == 'Word or phrase') {
        phraseB = '';
    }

    $j.ajax({
        dataType: 'jsonp',
        url: url,
        data:
        {
            phrase: phraseA,
            state: $j("#stateA").val() || '',
            party: $j($j(".partyA input:checked")[0]).val(),
            granularity: 'month',
            percentages: true,
            mincount: 0,
        },
        success: function (data) {
            var aResults = data['results'];
            CapitolWords.a['all'] = aResults;
            CapitolWords.a['counts'] = _(aResults).pluck('count');
            CapitolWords.a['percentages'] = _(aResults).pluck('percentage');

            $j.ajax({
                dataType: 'jsonp',
                url: url,
                data: {
                    phrase: phraseB,
                    state: $j("#stateB").val() || '',
                    party: $j($j(".partyB input:checked")[0]).val(),
                    granularity: 'month',
                    percentages: true,
                    mincount: 0,
                },
                success: function (data) {
                    var bResults = data['results'];
                    CapitolWords.b['all'] = bResults;
                    CapitolWords.b['counts'] = _(bResults).pluck('count');
                    CapitolWords.b['percentages'] = _(bResults).pluck('percentage');
                    if (CapitolWords.minMonth || CapitolWords.maxMonth) {
                        CapitolWords.limit(CapitolWords.minMonth, CapitolWords.maxMonth);
                    } else {
                        var labelPositions = CapitolWords.buildXLabels(CapitolWords.a['all']);
                        var labels = labelPositions[0];
                        var positions = labelPositions[1];
                        CapitolWords.showChart([CapitolWords.a['percentages'], CapitolWords.b['percentages']], labels, positions);
                    }
                    if (spinner) {
                        spinner.stop();
                    }
                }
            });

        }
    });

}

CapitolWords.smoothing = 0;

CapitolWords.build_legend = function () {
    var termA = $j("#terma").val();
    var partyA = $j($j(".partyA input:checked")[0]).val();
    var stateA = $j("#stateA").val();

    var legend = [];

    var legendA = termA;
    if (termA != 'Word or phrase') {
        if (partyA && stateA) {
            legendA += ' [' + partyA + '-' + stateA + ']';
        } else if (partyA) {
            legendA += ' [' + partyA + ']';
        } else if (stateA) {
            legendA += ' [' + stateA + ']';
        }
        legend.push(legendA);
    }

    var termB = $j("#termb").val();
    var partyB = $j($j(".partyB input:checked")[0]).val()
    var stateB = $j("#stateB").val();

    var legendB = termB;
    if (termB != 'Word or phrase') {
        if (partyB && stateB) {
            legendB += ' [' + partyB + '-' + stateB + ']';
        } else if (partyB) {
            legendB += ' [' + partyB + ']';
        } else if (stateB) {
            legendB += ' [' + stateB + ']';
        }
        legend.push(legendB);
    }

    return legend;
    //return [legendA, legendB];
}

CapitolWords.showChart = function (data, x_labels, x_label_positions) {
    var chart = new GoogleChart(860, 340);
    var values, max = 0, maxValue;
    for (i in data) {
        values = this.smooth(data[i], Number(this.smoothing) || 1);
        maxValue = Math.round(_(values).max()*10000)/10000;
        if (maxValue > max) {
            max = Math.round(maxValue*10000)/10000;
        }
        chart.add_data(values);
    }
    chart.set_grid(0, 50, 2, 5);
    chart.set_fill('bg', 's', '00000000');
    colors = ['8E2844', 'A85B08', 'AF9703'];
    var legend = this.build_legend();
    chart.set_legend(legend);
    chart.set_colors(colors.slice(0, legend.length));

    chart.set_axis_labels('y', ['', max+'%']);
    if (x_labels) {
        chart.set_axis_labels('x', x_labels);
    }
    if (x_label_positions) {
        chart.set_axis_positions('x', x_label_positions);
    }

    //$j("#chart img.default, #compareGraphic img.default").fadeOut(100, function () {
        $j("#chart img.realChart, #compareGraphic img.default").attr("src", chart.url()).fadeIn(100);
    //});
    if (spinner) {
        spinner.stop();
    }

}


CapitolWords.submitCompareForm = function () {

    // spinner options.
    var opts = {
      lines: 12, // The number of lines to draw
      length: 7, // The length of each line
      width: 5, // The line thickness
      radius: 10, // The radius of the inner circle
      color: '#000', // #rbg or #rrggbb
      speed: 1, // Rounds per second
      trail: 100, // Afterglow percentage
      shadow: true // Whether to render a shadow
    };
    var target = document.getElementById('compareGraphic');
    spinner = new Spinner(opts).spin(target);

    var item;
    var items = [];
    var divs = ['a', 'b', 'c'];
    var div;

    for (i=0; i<3; i++) {
        var thisItem = {};
        element = $j("#state" + divs[i]);
        if (element.val() && element.val() != '') {
            thisItem['state'] = element.val();
        }

        element = $j("#party" + divs[i]);
        if (element.val() && element.val() != '') {
            thisItem['party'] = element.val();
        }

        element = $j("#term" + divs[i]);
        if (element.val() && element.val() != 'Word or phrase') {
            thisItem['term'] = element.val();
            items.push(thisItem); // Only use this item if a term is entered.
        }

    }

    if (items.length === 0) {
        if (spinner) {
            spinner.stop();
        }
        return;
    }


    (function (window, undefined) {
        var History = window.History;
        if (!History.enabled) {
            return false;
        }

        var buildUrl = function (items) {
            var urlPieces = [];
            var item;
            var piece;

            for (i in items) {
                item = items[i];
                piece = [];
                piece.push(escape(item.term || ''));
                piece.push(escape(item.party || ''));
                piece.push(escape(item.state || ''));
                urlPieces.push(piece.join(':'));
            }
            return '/compare/' + urlPieces.join('/');
        };
        var terms = [];
        for (i in items) {
            terms.push(items[i].term);
        }
        var title = 'Comparing ' + terms.join(', ') + ' | Capitol Words';
        //History.pushState({}, title, buildUrl(items));

     })(window);


    CapitolWords.compare(items);

    var compareItemHashes = function (a, b) {
        if (typeof a === 'undefined' || typeof b === 'undefined') {
            return false;
        }

        if (a.term != b.term) {
            return false;
        }
        if (a.party != b.party) {
            return false;
        }
        if (a.state != b.state) {
            return false;
        }
        return true;
    }

    for (i in items) {

        // If nothing has changed for this item, skip it.
        if (compareItemHashes(items[i], CapitolWords.itemsToCompare[i]) !== false) {
            continue
        } else {
            CapitolWords.itemsToCompare[i] = items[i];
        }

        item = items[i];
        div = divs[i];

        $j("#" + div + " h4.termLabel'").fadeOut();

        $j("#" + div + " img.realChart").fadeOut('slow', function () { });
        $j("#" + div + " a.moreInfo").attr('href', '').html('');
        $j("#" + div + " img.default").fadeIn('slow', function () { });


        if ($j(".partyPieChart").length != 0) {
            CapitolWords.getPartyPieChart(item['term'], $j("#" + div + " .partyPieChart"), 220, 150, 
                                          function (term, div) {
                                            div.parent().find('h4.termLabel').html(term).fadeIn('slow');
                                            div.parent().find('a.moreInfo').attr('href', '/term/' + term).html('more information on "' + term + '"');
                                          });
        }

    }
};

CapitolWords.legislatorSearch = function () {
    var data = {'chamber': $j("#chamber").val(),
                'party': $j("#party").val(),
                'congress': $j("#congress").val(),
                'state': $j("#state").val()
                };
    $j.ajax({
        dataType: 'jsonp',
        url: 'http://capitolwords.org/api/legislators.json',
        data: data,
        success: function (data) {
            CapitolWords.populateLegislatorList(data['results']);
        }
    });
}

CapitolWords.year_values = [];

$j(document).ready(

        function () {

            if (window.location.pathname.match(/^\/compare/)) {
                var hash = History.getState().hash;
                var comparePath = hash.replace(/^\/compare\//, '').split('?')[0]
                var pieces = comparePath.match(/.*?:.*?:.*?(?:\/|$)/g)
                if (pieces) {

                    var piece,
                        parts,
                        term,
                        party,
                        state,
                        element;
                    var divs = ['a', 'b', 'c'];

                    for (i in pieces) {
                        piece = pieces[i];
                        parts = piece.split(':');
                        term = parts[0];
                        party = parts[1];
                        state = parts[2];
                        $j("#term" + divs[i]).val(term);
                        $j("#party" + divs[i]).val(party);
                        $j("#state" + divs[i]).val(state);
                    }

                    CapitolWords.submitCompareForm();
                }
            }

            if (typeof termDetailTerm !== 'undefined') {
                CapitolWords.populateTermDetailPage(termDetailTerm);
            }

            // Hide broken images.
            $j("img").error(function(){
                $j(this).hide();
            });

            // Change which ngram list is shown.
            $j(".ngramMenu li").bind('click', function (x) {
                var classToShow = $j(this).attr('class');
                $j($j(".barChart:visible")[0]).hide(0, function () {
                    $j("ol#" + classToShow).show(0);
                });
            });

            // Change which timeline is shown.
            $j("#timelineToggle input").bind('click', function () {
                var selectedId = $j('input[name=toggle]:checked', '#timelineToggle').attr('id');
                if (selectedId === 'overallTimelineSelect') {
                    $j("#partyTimeline").hide();
                    $j("#customTimeline").hide();
                    $j("#overallTimeline").show();
                } else if (selectedId === 'partyTimelineSelect') {
                    $j("#overallTimeline").hide();
                    $j("#customTimeline").hide();
                    $j("#partyTimeline").show();
                } else if (selectedId === 'customTimelineSelect') {
                    $j("#overallTimeline").hide();
                    $j("#partyTimeline").hide();
                    $j("#customTimeline").show();
                }
            });

            $j("#partySelect, #stateSelect").change(function () {
                CapitolWords.customizeChart();
            });

            $j(".compareSubmit").bind('click', function () {
                //CapitolWords.submitCompareForm();
                CapitolWords.submitHomepageCompareForm();
            });

            $j("#termSelect input").bind('keyup', function (e) {
                if (e.keyCode === 13) {
                    //CapitolWords.submitCompareForm();
                    CapitolWords.submitHomepageCompareForm();
                }
            });

            $j("#termSelect input").bind('focus', function () {
                if ($j(this).val() == 'Word or phrase') {
                    $j(this).val('');
                }
            });

            $j("#termSelect input").bind('blur', function () {
                if ($j(this).val() == '') {
                    $j(this).val('Word or phrase');
                }
            });

            $j("#searchFilterButton").bind('click', function () {
                    CapitolWords.legislatorSearch();
            });

            if (window.location.pathname.match(/^\/legislator\/?$/)) {
                CapitolWords.legislatorSearch();
            }

            if ($j("#slider-range").length != 0) {
                var d = new Date();
                $j("#slider-range").slider({
                    range: true,
                    min: 1996,
                    max: d.getFullYear(),
                    values: [1996, d.getFullYear()],
                    slide: function(event, ui) {
                        $j("#years").val(ui.values[0] + " - " + ui.values[1]);
                    },
                    stop: function (event, ui) {
                        CapitolWords.minMonth = ui.values[0] + '01';
                        CapitolWords.maxMonth = ui.values[1] + '12';
                        if (_(CapitolWords.a).keys().length > 0 || _(CapitolWords.b).keys().length > 0) {
                            CapitolWords.limit(CapitolWords.minMonth, CapitolWords.maxMonth);
                        }
                    }
                });
                $j("#years").val( $j( "#slider-range" ).slider( "values", 0 ) +
                    " - " + $j( "#slider-range" ).slider( "values", 1 ) );
            }

            $j(".advanced").bind('click', function () {
                var $t = $j(this);
                $j("ul.wordFilter").slideToggle('', function () {
                    if ($j(this).is(":visible")) {
                        $t.addClass('expanded');
                    } else {
                        $t.removeClass('expanded');
                    }
                });
            });
    }

);

CapitolWords.startDate = function () {
    if (this.year_values[0]) {
        return this.year_values[0] + '-01-01';
    }
    return '1996-01-01';
}

CapitolWords.endDate = function () {
    var d = new Date();
    if (this.year_values[1]) {
        return this.year_values[1] + '-12-31';
    }
    return d.getFullYear() + '-12-31';
}

CapitolWords.trimGraph = function () {
    if (this.year_values.length == 2) {
        return true;
    }
    return false;
}

CapitolWords.smooth = function (list, degree) {
    var win = degree*2-1;
    weight = _.range(0, win).map(function (x) { return 1.0; });
    weightGauss = [];
    for (i in _.range(0, win)) {
        i = i-degree+1;
        frac = i/win;
        gauss = 1 / Math.exp((4*(frac))*(4*(frac)));
        weightGauss.push(gauss);
    }
    weight = _(weightGauss).zip(weight).map(function (x) { return x[0]*x[1]; });
    smoothed = _.range(0, (list.length+1)-win).map(function (x) { return 0.0; });
    for (i=0; i < smoothed.length; i++) {
        smoothed[i] = _(list.slice(i, i+win)).zip(weight).map(function (x) { return x[0]*x[1]; }).reduce(function (memo, num){ return memo + num; }, 0) / _(weight).reduce(function (memo, num){ return memo + num; }, 0);
    }
    return smoothed;
}
