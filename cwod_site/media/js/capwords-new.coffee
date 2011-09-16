jQuery.noConflict()
spinner = null

class window.CapitolWords

    states : {
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
            "KY": "Kentucky", "OR": "Oregon", "SD": "South Dakota"
        }

    customizeChart: ->
        party = jQuery('#partySelect').val()
        state = jQuery('#stateSelect').val()
        url = 'http://capitolwords.org/api/chart/timeline.json'
        jQuery.ajax {
            dataType: 'jsonp',
            url: url,
            data: {
                'party': party,
                'state': state,
                'phrase': jQuery('#term').val(),
                'granularity': 'month',
                'percentages': 'true',
                'legend': 'false',
                'mincount': 0,
            },
            success: (data) ->
                results = data['results']
                imgUrl = results['url']
                imgTag = "<img src=\"#{imgUrl}\"/>"
                jQuery('#customChart').attr 'src', imgUrl
        }

    getGraph: (term) ->
        url = 'http://capitolwords.org/api/chart/timeline.json'
        jQuery.ajax {
            dataType: 'jsonp',
            url: url,
            data: {
                'phrase': term,
                'granularity': 'month',
                'percentages': 'true',
                'mincount': 0,
                'legend': false,
            },
            success: (data) ->
                results = data['results']
                imgUrl = results['url']
                overallImgTag = "<img src=\"#{imgUrl}\" alt=\"Timeline of occurrences of #{term}\"/>"
                customImgTag = "<img id=\"customChart\" src=\"#{imgUrl}\" alt=\"Custom timeline of occurrences of \"#{term}\"/>"
                jQuery('#overallTimeline').html overallImgTag
                jQuery('#customTimeline').append customImgTag
        }

    getPartyGraph: (term) ->
        url = 'http://capitolwords.org/api/chart/timeline.json'
        jQuery.ajax {
            dataType: 'jsonp',
            url: url,
            data: {
                'phrase': term,
                'granularity': 'month',
                'percentages': 'true',
                'mincount': 0,
                'legend': true,
                'split_by_party': true,
            },
            success: (data) ->
                results = data['results']
                imgUrl = results['url']
                imgTag = "<img src=\"#{imgUrl}\" alt=\"Timeline of occurrences of #{term}\"/>"
                jQuery('#partyTimeline').html imgTag
        }

    getPartyPieChart: (term, div, width, height, callback) ->
        width = '' if typeof width == 'undefined'
        height = '' if typeof width == 'undefined'
        url = 'http://capitolwords.org/api/chart/pie.json'
        jQuery.ajax {
            dataType: 'jsonp',
            url: url,
            data: {
                'phrase': term,
                'entity_type': 'party',
                'width': width,
                'height': height,
            },
            success: (data) ->
                results = data['results']
                imgUrl = results['url']
                div.find('.default').fadeOut 'slow', ->
                    div
                        .find('.realChart')
                        .attr('src', imgUrl)
                        .attr('alt', "Pie chart of occurrences of #{term} by party")
                        .fadeIn('slow', ->
                            if typeof callback != 'undefined'
                                callback term, div
                        )
        }

    addLegislatorToChart: (result, maxcount, div) ->
        url = 'http://capitolwords.org/api/legislators.json'
        bioguide_id = result['legislator']
        pct = (result['count'] / maxcount) * 100
        jQuery.ajax {
            dataType: 'jsonp',
            url: url,
            async: false,
            data: {
                'bioguide_id': bioguide_id,
            },
            success: (data) ->
                url = "/legislator/#{bioguide_id}-#{data['slug']}"
                html = """
                    <li>
                        <span class="tagValue" style="width:#{pct}%">
                            <span class="tagPercent">#{pct}%</span>
                            <span class="tagNumber"></span>
                        </span>
                        <span class="barChartTitle"><a href="#{url}">
                            #{data['honorific']} #{data['full_name']}, #{data['party']}-#{data['state']}
                        </a>
                        </span>
                        </li>
                """
                div.append html
                
        }

    getLegislatorPopularity: (term, div) ->
        url = 'http://capitolwords.org/api/phrases/legislator.json'
        jQuery.ajax {
            dataType: 'jsonp',
            url: url,
            data: {
                'phrase': term,
                'sort': 'relative',
                'per_page': 10,
            },
            success: (data) ->
                results = data['results']
                maxCount = results[0]['count']
                div.html ''
                this.addLegislatorToChart result, maxcount, div for result in results
        }

    getStatePopularity: (term, div) ->
        url = 'http://capitolwords.org/api/phrases/state.json'
        jQuery.ajax {
            dataType: 'jsonp',
            url: url,
            data: {
                'phrase': term,
                'sort': 'relative',
                'per_page': 10,
            },
            success: (data) ->
                div.html ''
                results = data['results']
                maxcount = results[0]['count']
                _(results).each (result) ->
                    abbrev = result['state']
                    state = abbrev
                    if this.states.hasOwnProperty state
                        state = this.states[state]
                    url = "/state/#{abbrev}"
                    pct = (result['count'] / maxcount) * 100
                    html = """
                        <li>
                            <span class="tagValue" style="width: #{pct}%;">
                                <span class="tagPercent">#{pct}%</span>
                                <span class="tagNumber"></span>
                            </span>
                            <span class="barChartTitle"><a href="#{url}">#{state}</a></span>
                        </li>
                    """
                    div.append html
        }

    populateTermDetailPage: (term) ->
        this.getGraph term
        this.getStatePopularity term, jQuery('#stateBarChart')
        this.getPartyPieChart term, jQuery('#partyPieChart')
        this.getLegislatorPopularity term, jQuery('#legislatorBarChart')
        this.getPartyGraph term


    populateLegislatorList: (legislators) ->
        buildTable = ->
            jQuery('table#legislatorList tbody').empty()
            _(legislators).each (legislator) ->
                klass = if legislators.indexOf(legislator) % 2 == 0 then 'even' else 'odd'
                tr = """
                    <tr class="#{klass}">
                        <td>
                            <img class="legislatorImage" alt="legislator photo" src="http://assets.sunlightfoundation.com/moc/40x50/#{legislator['bioguide_id']}.jpg"/>
                        </td>
                        <td>#{legislator['state']}</td>
                        <td>#{legislator['party']}</td>
                        <td>#{legislator['chamber']}</td>
                    </tr>
                """
                jQuery('table#legislatorList tbody').fadeIn('fast', ->
                    jQuery('img').error( ->
                        jQuery(this).hide()
                    )
                )

    itemsToCompare: []
    a: {}
    b: {}
    minMonth: undefined
    maxMonth: undefined

    limit: (minMonth, maxMonth) ->
        if minMonth and maxMonth
            func = (v) ->
                v['month'] >= minMonth and v['month'] <= maxMonth
        else
            func = ->
                true

        aVals = _(this.a['all']).select func
        bVals = _(this.b['all']).select func

        labelPositions = this.buildXLabels aVals
        labels = labelPositions[0]
        positions = labelPositions[1]
        this.showChart [_(aVals).pluck('percentage'), _(bVals).pluck('percentage')], labels, positions


    buildXLabels: (values) ->
        years = _(_(values).pluck('month')).select((x) ->
            x.match /01$/)

        positions = [Math.round((years.indexOf(year) / years.length) * 100) for year in years]
        labels = _(years).map( (x) ->
            "1/#{x.slice(2,4)}"
        )
        [labels, positions]

    submitHomepageCompareForm: ->
        cw = this
        opts = {
            lines: 12,
            length: 7,
            width: 4,
            radius: 10,
            color: '#000',
            speed: 1,
            trail: 100,
            shadow: true,
        }
        target = document.getElementById 'compareGraphic'
        spinner = new Spinner(opts).spin target

        url = 'http://capitolwords.org/api/dates.json'
        phraseA = jQuery('#terma').val()
        phraseA = if phraseA == 'Word or phrase' then '' else phraseA

        phraseB = jQuery('#termb').val()
        phraseB = if phraseB == 'Word or phrase' then '' else phraseB

        jQuery.ajax {
            dataType: 'jsonp',
            url: url,
            data: {
                phrase: phraseA,
                state: jQuery('#stateA').val() or '',
                party: jQuery(jQuery('.partyA input:checked')[0]).val(),
                granularity: 'month',
                percentages: true,
                mincount: 0,
            },
            success: (data) ->
                aResults = data['results']
                cw.a['all'] = aResults
                cw.a['counts'] = _(aResults).pluck 'count'
                cw.a['percentages'] = _(aResults).pluck 'percentage'

                jQuery.ajax {
                    dataType: 'jsonp',
                    url : url,
                    data: {
                        phrase: phraseB,
                        state: jQuery('#stateB').val() or '',
                        party: jQuery(jQuery('.partyB input:checked')[0]).val(),
                        granularity: 'month',
                        percentages: true,
                        mincount: 0,
                    },
                    success: (data) ->
                        bResults = data['results']
                        cw.b['all'] = bResults
                        cw.b['counts'] = _(bResults).pluck 'count'
                        cw.b['percentages'] = _(bResults).pluck 'percentage'

                        if cw.minMonth or cw.maxMonth
                            cw.limit cw.minMonth, cw.maxMonth

                        else
                            labelPositions = cw.buildXLabels cw.a['all']
                            labels = labelPositions[0]
                            positions = labelPositions[1]
                            cw.showChart [cw.a['percentages'], cw.b['percentages']], labels, positions

                        if spinner
                            spinner.stop()
                }
        }

    smoothing: 0

    build_legend: ->
        termA = jQuery('#terma').val()
        partyA = jQuery(jQuery('.partyA input:checked')[0]).val()
        stateA = jQuery('#stateA').val()

        legend = []

        legendA = termA
        if termA != 'Word or phrase'
            if partyA and stateA
                legendA += " [#{partyA}-#{stateA}]"
            else if partyA
                legendA += " [#{partyA}]"
            else if stateA
                legendA += " [#{stateA}]"

            legend.push(legendA)

        termB = jQuery('#termb').val()
        partyB = jQuery(jQuery('.partyB input:checked')[0]).val()
        stateB = jQuery('#stateB').val()

        legendB = termB
        if termB != 'Word or phrase'
            if partyB and stateB
                legendB += " [#{partyB}-#{stateB}]"
            else if partyB
                legendB += " [#{partyB}]"
            else if stateB
                legendB += " [#{stateB}]"

            legend.push(legendB)

        legend


    showChart: (data, x_labels, x_label_positions) ->
        chart = new GoogleChart 860, 340
        values = []
        maxValue = 0
        max = 0
        cw = this
        _(data).each (item) ->
            #values = cw.smooth(item, Number(cw.smoothing) || 1)
            values = item
            maxValue = Math.round(_(values).max()*1000)/10000
            if maxValue > max
                max = Math.round(maxValue*10000)/10000
            chart.add_data values

        chart.set_grid 0, 50, 2, 5
        chart.set_fill 'bg', 's', '00000000'
        colors = ['8E2844', 'A85B08', 'AF9703']
        legend = this.build_legend()
        chart.set_legend legend
        chart.set_colors(colors.slice(0, legend.length))

        chart.set_axis_labels 'y', ['', "#{max}%"]

        if x_labels
            chart.set_axis_labels 'x', x_labels

        if x_label_positions
            chart.set_axis_positions 'x', x_label_positions

        jQuery('#chart img.realChart, #compareGraphic img.default').attr('src', chart.url()).fadeIn 100

        if spinner
            spinner.stop()

    legislatorSearch: ->
        data = {
            chamber: jQuery('#chamber').val(),
            party: jQuery('#party').val(),
            congress: jQuery('#congress').val(),
            state: jQuery('#state').val(),
        }
        jQuery.ajax {
            dataType: 'jsonp',
            url: 'http://capitolwords.org/api/legislators.json',
            data: data,
            success: (data) ->
                window.CapitolWords.populateLegislatorList data['results']
        }

    year_values: []

    startDate: ->
        if this.year_values[0] then "#{this.year_values[0]}-01-01" else '1996-01-01'

    endDate: ->
        d = new Date()
        if this.year_values[1] then "#{this.year_values[1]}-12-31" else "#{d.getFullYear()}-12-31"

    trimGraph: ->
        if this.year_values.length == 2 then true else false

    smooth: (list, degree) ->
        win = degree * 2 - 1
        weight = _.range(0, win).map( (x) -> 1.0 )
        weightGauss = []

        for i in _.range(0, win)
            i = i-degree+1
            frac = i/win
            gauss = 1 / Math.exp((4*(frac))*(4*(frac)))
            weightGauss.push gauss

        weight = _(weightGauss).zip(weight).map( (x) ->
            x[0]*x[1]
        )
        smoothed = _.range(0, (list.length+1)-win).map( (x) ->
            0.0
        )

        func = (memo, num) ->
            memo + num

        _(_.range(smoothed.length)).each (i) ->
            smoothed[i] = _(list.slice(i, i+win)).zip(weight).map( (x) ->
                x[0]*x[1]
            ).reduce(func, 0) / _(weight).reduce(func, 0)


jQuery(document).ready ->

    cw = new window.CapitolWords

    if typeof termDetailTerm != 'undefined'
        cw.populateTermDetailPage termDetailTerm

    jQuery('img').error( ->
        jQuery(this).hide()
    )

    jQuery('.ngramMenu li').bind('click', (x) ->
        classToShow = jQuery(this).attr 'class'
        jQuery(jQuery('.barChart:visible')[0]).hide(0, ->
            jQuery("ol##{classToShow}").show(0)
        )
    )

    jQuery('#timelineToggle input').bind('click', ->
        selectedId = jQuery('input[name=toggle]:checked', '#timelineToggle').attr 'id'
        timelines = {
            party: jQuery('#partyTimeline'),
            custom: jQuery('#customTimeline'),
            overall: jQuery('#overallTimeline'),
        }
        selected = {
            overallTimelineSelect: 'overall',
            partyTimelineSelect: 'party',
            customTimelineSelect: 'custom',
        }[selectedId]

        _(timelines).each (k, v) ->
            if k == selected
                v.show()
            else
                v.hide()
    )

    jQuery('#partySelect, #stateSelect').change( ->
        cw.customizeChart()
    )

    jQuery('.compareSubmit').bind('click', ->
        cw.submitHomepageCompareForm()
    )

    jQuery('#termSelect input').bind('keyup', (e) ->
        if e.keyCode == 13 then cw.submitHomepageCompareForm()
    )

    jQuery('#termSelect input').bind('focus', ->
        if jQuery(this).val() == 'Word or phrase' then jQuery(this).val ''
    )

    jQuery('#termSelect input').bind('blur', ->
        if jQuery(this).val() == '' then jQuery(this).val 'Word or phrase'
    )

    jQuery('#searchFilterButton').bind('click', ->
        cw.legislatorSearch()
    )

    if jQuery('#slider-range').length != 0
        d = new Date()
        jQuery('#slider-range').slider {
            range: true,
            min: 1996,
            max: d.getFullYear(),
            values: [1996, d.getFullYear()],
            slide: (event, ui) ->
                jQuery('#years').val "#{ui.values[0]}-#{ui.values[1]}"
            stop: (event, ui) ->
                cw.minMonth = "#{ui.values[0]}01"
                cw.maxMonth = "#{ui.values[1]}12"
                if _(cw.a).keys().length > 0 or _(cw.b).keys().length > 0
                    cw.limit cw.minMonth, cw.maxMonth
        }
        jQuery('#years').val jQuery('#slider-range').slider('values', 0) + ' - ' + jQuery('#slider-range').slider('values', 1)

    jQuery('.advanced').bind('click', ->
        t = jQuery(this)
        jQuery('ul.wordFilter').slideToggle('', ->
            if jQuery(this).is ':visible' then t.addClass 'expanded' else t.removeClass 'expanded'
        )
    )

