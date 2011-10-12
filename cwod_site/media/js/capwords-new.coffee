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

    dateFromMonth: (month) ->
        datePieces = month.match(/(\d{4})(\d{2})/).slice(1,3)
        datePieces.push '01'
        datePieces.join '-'

    getGraphData: (term) ->
        data = {
            'phrase': term,
            'granularity': 'month',
            'percentages': 'true',
            'mincount': 0,
        }

        url = 'http://capitolwords.org/api/dates.json'
        cw = this

        jQuery.ajax {
            dataType: 'jsonp',
            url: url,
            data: data,
            success: (data) ->
                results = data['results']
                cw.results = results
                counts = _(results).pluck 'count'
                percentages = _(results).pluck 'percentage'
                labelPositions = cw.buildXLabels results

                imgUrl = cw.showChart [percentages], labelPositions[0], labelPositions[1], 575, 300, ['E0B300',]
                window.cwod_counts = jQuery.extend true, [], counts

                jQuery.getJSON (imgUrl + '&chof=json'), (data) ->

                    copy_coords = (c) ->
                        if c.name is 'line0'
                            window.cwod_line_coords = jQuery.extend true, [], c.coords

                    copy_coords(csj) for csj in data.chartshape

                    annotation_callback = () ->
                        if not (window.cwod_inchart and (jQuery('#partyTimelineSelect').attr 'checked')!='checked')
                            jQuery('#annotation').hide()
                        else
                            jQuery('#annotation').show()
                            FUZZ_X = 5
                            FUZZ_Y = 6
                            i = 0
                            while ((window.cwod_line_coords[i]+FUZZ_X)<(window.cwod_pagex - (jQuery '#termChart').offset().left) and (i<results.length*2))
                                i += 2

                            MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
                            annotation_month = MONTHS[(parseInt (results[i/2].month.substr 4, 2), 10) - 1]
                            annotation_year = results[i/2].month.substr 0, 4
                            annotation_text = ('<span class="annotation-count">' + window.cwod_counts[i/2] + ' mention' + (if window.cwod_counts[i/2]!=1 then 's' else '') + '</span><br /><span class="annotation-date">in ' + annotation_month + ' ' + annotation_year + '</span>')
                            (jQuery '#inner-annotation').html annotation_text
                            (jQuery '#annotation').css {
                                left: jQuery('#termChart').offset().left + window.cwod_line_coords[i] + FUZZ_X, 
                                top: jQuery('#termChart').offset().top + window.cwod_line_coords[i+1] + FUZZ_Y
                            }

                    window.clearInterval window.cwod_interval
                    window.cwod_interval = window.setInterval annotation_callback, 50
                
                    overallImgTag = "<img id=\"termChart\" src=\"#{imgUrl}\" alt=\"Timeline of occurrences of #{term}\"/>"
                    jQuery('#overallTimeline').html overallImgTag

                    (((jQuery '#termChart').mouseenter (event) ->
                       window.cwod_inchart = true).mouseleave (event) ->
                          window.cwod_inchart = false).mousemove (event) ->
                             window.cwod_pagex = event.pageX

                if cw.minMonth and cw.maxMonth
                    cw.limit cw.minMonth, cw.maxMonth
        }


    getGraph: (term) ->
        data = {
            'phrase': term,
            'granularity': 'month',
            'percentages': 'true',
            'mincount': 0,
            'legend': false,
        }

        url = 'http://capitolwords.org/api/chart/timeline.json'
        jQuery.ajax {
            dataType: 'jsonp',
            url: url,
            data: data,
            success: (data) ->
                results = data['results']
                imgUrl = results['url']
                overallImgTag = "<img src=\"#{imgUrl}\" alt=\"Timeline of occurrences of #{term}\"/>"
                #customImgTag = "<img id=\"customChart\" src=\"#{imgUrl}\" alt=\"Custom timeline of occurrences of \"#{term}\"/>"
                jQuery('#overallTimeline').html overallImgTag
                #jQuery('#customTimeline').append customImgTag
        }


    buildPartyGraph: (minMonth, maxMonth) ->
        if minMonth and maxMonth
            func = (v) ->
                v['month'] >= minMonth and v['month'] <= maxMonth
        else
            func = ->
                true

        vals = [_(x[1]).select(func) for x in this.partyResults][0]
        labelPositions = this.buildXLabels vals[0]
        partyAPercentages = _(vals[0]).pluck 'percentage'
        partyBPercentages = _(vals[1]).pluck 'percentage'
        percentages = [partyAPercentages, partyBPercentages, ]
        parties = [x[0] for x in this.partyResults]

        colors = {'R': 'bb3110', 'D': '295e72', }

        imgUrl = this.showChart [partyAPercentages, partyBPercentages,], labelPositions[0], labelPositions[1], 575, 300, [colors[this.partyResults[0][0]], colors[this.partyResults[1][0]],], [this.partyResults[0][0], this.partyResults[1][0],]
        imgTag = "<img id=\"partyTermChart\" src=\"#{imgUrl}\"/>"
        jQuery('#partyTimeline').html imgTag


    getPartyGraphData: (term) ->
        data = {
            'phrase': term,
            'granularity': 'month',
            'percentages': true,
            'mincount': 0,
        }

        url = 'http://capitolwords.org/api/dates.json'
        cw = this

        partyData = []

        render = () ->
            chartData = []
            legendItems = []
            cw.partyResults = []
            _(partyData).each (partyResult) ->
                cw.partyResults.push partyResult

            cw.buildPartyGraph cw.minMonth, cw.maxMonth

        parties = ['R', 'D', ]
        renderWhenDone = _(parties.length).after(render)

        _(parties).each (party) ->
            data = {
                'party': party,
                'phrase': term,
                'granularity': 'month',
                'percentages': true,
                'mincount': 0,
            }
            jQuery.ajax {
                dataType: 'jsonp',
                url: url,
                data: data,
                success: (data) ->
                    results = data['results']
                    partyData.push [party, results]
                    renderWhenDone()
            }


    getPartyGraph: (term) ->
        url = 'http://capitolwords.org/api/chart/timeline.json'
        cw = this
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
                'start_date': cw.start_date,
                'end_date': cw.end_date,
            },
            success: (data) ->
                results = data['results']
                imgUrl = results['url']
                imgTag = "<img src=\"#{imgUrl}\" alt=\"Timeline of occurrences of #{term}\"/>"
                jQuery('#partyTimeline').html imgTag
        }

    titleCase: (s) ->
        s.replace(/\w\S*/g, (txt) ->
            txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase()
        )

    highlightEntries: (entries, term) ->
        entry_matches = []
        regexp = new RegExp(term, "ig")
        _(entries).each (entry) ->
            match = null
            _(entry['speaking']).each (graf) ->
                graf = graf.replace /\n/, ''
                versions_of_term = _(graf.match regexp).uniq()
                if not _(versions_of_term).isEmpty()
                    matcher = new RegExp '(' + versions_of_term.join('|') + ')'
                    match = graf.replace(matcher, (a, b) ->
                        "<em>#{b}</em>"
                    )
                    return
            entry['match'] = match
            entry_matches.push(entry)
        entry_matches


    getCREntries: (term) ->
        url = 'http://capitolwords.org/api/text.json'
        cw = this
        data = {
            'phrase': term,
            'bioguide_id': "['' TO *]",
            'start_date': cw.start_date,
            'end_date': cw.end_date,
            'sort': 'date desc,score desc',
        }
        jQuery.ajax {
            dataType: 'jsonp',
            url: url,
            data: data,
            success: (data) ->
                results = data['results']
                entries = []
                urls = []
                _(results).each (entry) ->
                    if entries.length >= 5
                        return
                    if entry['origin_url'] not in urls
                        urls.push entry['origin_url']
                        entries.push entry

                entries = cw.highlightEntries(entries, term)

                html = ""
                _(entries).each (entry) ->
                    html += """
                        <li>
                            <h5><a href="">#{cw.titleCase(entry['title'])}</a></h5>
                            <p>#{entry['speaker_first']} #{entry['speaker_last']}, #{entry['speaker_party']}-#{entry['speaker_state']}</p>
                            <p>#{entry.date}</p>
                            <p>#{entry.match}</p>
                        </li>
                    """
                jQuery('#crEntries').html(html)
        }

    getPartyPieChart: (term, div, width, height, callback) ->
        width = '' if _(width).isUndefined()
        height = '' if _(width).isUndefined()
        url = 'http://capitolwords.org/api/chart/pie.json'
        cw = this
        jQuery.ajax {
            dataType: 'jsonp',
            url: url,
            data: {
                'phrase': term,
                'entity_type': 'party',
                'width': width,
                'height': height,
                'start_date': cw.start_date,
                'end_date': cw.end_date,
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
                            if not _(callback).isUndefined()
                                callback term, div
                        )
        }


    legislatorData: []


    addLegislatorToChart: (result, maxcount, div, callback) ->
        url = 'http://capitolwords.org/api/legislators.json'
        bioguide_id = result['legislator']
        pct = (result['count'] / maxcount) * 100
        cw = this
        jQuery.ajax {
            dataType: 'jsonp',
            url: url,
            async: false,
            data: {
                'bioguide_id': bioguide_id,
            },
            success: (data) ->
                data = data['results']
                url = "/legislator/#{bioguide_id}-#{data['slug']}"
                cw.legislatorData.push({
                    url: url,
                    data: data,
                    result: result,
                    pct: pct,
                })
                
                callback()
                
        }


    getLegislatorPopularity: (term, div) ->
        url = 'http://capitolwords.org/api/phrases/legislator.json'
        cw = this
        jQuery.ajax {
            dataType: 'jsonp',
            url: url,
            data: {
                'phrase': term,
                'sort': 'relative',
                'per_page': 10,
                'start_date': cw.start_date,
                'end_date': cw.end_date,
            },
            success: (data) ->
                results = data['results']
                maxcount = results[0]['count']
                listItems = []

                cw.legislatorData = []

                render = () ->
                    listItems = []
                    cw.legislatorData.sort( (a, b) ->
                        b['pct'] - a['pct']
                    )
                    done = []

                    _(cw.legislatorData).each (legislator) ->
                        if legislator.data.bioguide_id in done
                            return

                        done.push legislator.data.bioguide_id

                        html = """
                            <li>
                                <span class="tagValue" style="width:#{legislator['pct']}%">
                                    <span class="tagPercent">#{legislator['pct']}%</span>
                                    <span class="tagNumber"></span>
                                </span>
                                <span class="barChartTitle"><a href="#{legislator['url']}">
                                    #{legislator['data']['honorific']} #{legislator['data']['full_name']}, #{legislator['data']['party']}-#{legislator['data']['state']}
                                </a>
                                </span>
                                </li>
                        """
                        listItems.push html

                    div.html(listItems.join(''))

                renderWhenDone = _(results.length).after(render)

                cw.addLegislatorToChart result, maxcount, div, renderWhenDone for result in results
        }

    getStatePopularity: (term, div) ->
        url = 'http://capitolwords.org/api/phrases/state.json'
        cw = this
        jQuery.ajax {
            dataType: 'jsonp',
            url: url,
            data: {
                'phrase': term,
                'sort': 'relative',
                'per_page': 10,
                'start_date': cw.start_date,
                'end_date': cw.end_date,
            },
            success: (data) ->
                div.html ''
                results = data['results']
                maxcount = results[0]['count']
                _(results).each (result) ->
                    abbrev = result['state']
                    state = abbrev
                    if cw.states.hasOwnProperty state
                        state = cw.states[state]
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

        if _(this.results).isUndefined()
            this.getGraphData term

        this.getStatePopularity term, jQuery('#stateBarChart')
        this.getPartyPieChart term, jQuery('#partyPieChart')
        this.getLegislatorPopularity term, jQuery('#legislatorBarChart')

        if _(this.partyResults).isUndefined()
            this.getPartyGraphData term

        if this.start_date and this.end_date
            this.getCREntries term



    populateLegislatorList: (legislators) ->
        buildTable = ->
            jQuery('table#legislatorList tbody').empty()
            bioguides = []
            n=0
            _(legislators).each (legislator) ->
                if not _(bioguides).include legislator['bioguide_id']
                    bioguides.push legislator['bioguide_id']
                    #klass = if legislators.indexOf(legislator) % 2 == 0 then 'even' else 'odd'
                    klass = if n % 2 == 0 then 'even' else 'odd'
                    n++
                    tr = """
                        <tr class="#{klass}">
                            <td>
                                <a href="/legislator/#{legislator['bioguide_id']}-#{legislator['slug']}">
                                <img class="legislatorImage" alt="legislator photo" src="http://assets.sunlightfoundation.com/moc/40x50/#{legislator['bioguide_id']}.jpg"/>
                                </a>
                            </td>
                            <td><a href="/legislator/#{legislator['bioguide_id']}-#{legislator['slug']}">#{legislator['name']}</a></td>
                            <td>#{legislator['state']}</td>
                            <td>#{legislator['party']}</td>
                            <td>#{legislator['chamber']}</td>
                        </tr>
                    """
                    jQuery('table#legislatorList tbody').append tr

            jQuery('table#legislatorList tbody').fadeIn('fast', ->
                jQuery('img').error( ->
                    jQuery(this).hide()
                )
            )

        jQuery('table#legislatorList tbody').fadeOut 'fast', buildTable

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

        if typeof termDetailTerm isnt 'undefined'
            vals = _(this.results).select func
            percentages = _(vals).pluck 'percentage'
            labelPositions = this.buildXLabels vals
            imgUrl = this.showChart [percentages], labelPositions[0], labelPositions[1], 575, 300, ['E0B300',]
            jQuery('#termChart').attr('src', imgUrl)
            #jQuery('#customChart').attr('src', imgUrl)

        else
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

    submitHomepageCompareForm: (skipState) ->
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
        #phraseA = jQuery('#terma').val()
        #phraseA = if phraseA == 'Word or phrase' then '' else phraseA

        #phraseB = jQuery('#termb').val()
        #phraseB = if phraseB == 'Word or phrase' then '' else phraseB

        jQuery.ajax {
            dataType: 'jsonp',
            url: url,
            data: {
                phrase: cw.phraseA(),
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
                        phrase: cw.phraseB(),
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

                }
                if spinner
                    spinner.stop()
        }

        if not skipState
            this.makeHomepageHistoryState(true)


    phraseA: ->
        phraseA = jQuery('#terma').val()
        if phraseA == 'Word or phrase' then '' else phraseA


    phraseB: ->
        phraseB = jQuery('#termb').val()
        if phraseB == 'Word or phrase' then '' else phraseB


    smoothing: 0


    build_legend: ->
        termA = jQuery('#terma').val()
        partyA = jQuery(jQuery('.partyA input:checked')[0]).val()
        stateA = jQuery('#stateA').val()

        legend = []

        legendA = termA
        if termA and termA != 'Word or phrase'
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
        if termB and termB != 'Word or phrase'
            if partyB and stateB
                legendB += " [#{partyB}-#{stateB}]"
            else if partyB
                legendB += " [#{partyB}]"
            else if stateB
                legendB += " [#{stateB}]"

            legend.push(legendB)

        legend


    showChart: (data, x_labels, x_label_positions, width, height, colors, legend) ->

        width = width or 860
        height = height or 340

        chart = new GoogleChart width, height
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
        if not colors
            colors = ['8E2844', 'A85B08', 'AF9703']
        if not legend
            legend = this.build_legend()
        chart.set_legend legend if not _(legend).isEmpty()
        chart.set_colors(colors.slice(0, legend.length))

        chart.set_axis_labels 'y', ['', "#{max}%"]

        if x_labels
            chart.set_axis_labels 'x', x_labels

        if x_label_positions
            chart.set_axis_positions 'x', x_label_positions

        if jQuery('#chart img.realChart, #compareGraphic img.default')
            jQuery('#chart img.realChart, #compareGraphic img.default').attr('src', chart.url()).fadeIn 100

        if spinner
            spinner.stop()

        chart.url()


    legislatorSearch: (data) ->
        cw = this
        data = {
            chamber: data['chamber'] or jQuery('#chamber').val(),
            party: data['party'] or jQuery('#party').val(),
            congress: data['congress'] or jQuery('#congress').val(),
            state: data['state'] or jQuery('#state').val(),
        }
        jQuery.ajax {
            dataType: 'jsonp',
            url: 'http://capitolwords.org/api/legislators.json',
            data: data,
            success: (data) ->
                cw.populateLegislatorList data['results']
        }


    readTermDetailPageHistory: ->
        if typeof History.getState().hash is 'undefined'
            return
        hash = History.getState().hash.split('?')[1]
        if not hash
            return
        pieces = [x.split '=' for x in hash.split '&'][0]
        for piece in pieces
            [k, v] = piece
            if k == 'start'
                this.minMonth = v
                this.start_date = this.dateFromMonth(this.minMonth)

            else if k == 'end'
                this.maxMonth = v
                this.end_date = this.dateFromMonth(this.maxMonth)

#            else if k == 'pt' and v == 'true'
#                jQuery('#overallTimeline').hide(->
#                    jQuery('#partyTimelineSelect').attr('checked', true)
#                    jQuery('#partyTimeline').show()
#                )


        if this.minMonth or this.maxMonth
            startYear = this.minMonth.slice(0, 4)
            endYear = this.maxMonth.slice(0, 4)
            jQuery("#slider-range").slider("option", "values", [startYear, endYear])

            this.limit this.minMonth, this.maxMonth


    readHomepageHistory: (nosubmit) ->
        mapping = {'terma': '#terma', 'termb': '#termb', 'statea': '#stateA', 'stateb': '#stateB', }
        hash = History.getState().hash.split('?')[1]
        data = {}
        showAdvanced = false
        cw = this

        if hash
            pieces = hash.split '&'
            _(pieces).each (piece) ->
                [k, v] = piece.split '='
                id = mapping[k]
                jQuery("#{id}").val(v)

                if k in ['partya', 'partyb', 'statea', 'stateb']
                    showAdvanced = true

                if k == 'partya' and v
                    jQuery("#partyA#{v}").attr('checked', true)

                else if k == 'partyb' and v
                    jQuery("#partyB#{v}").attr('checked', true)

                else if k == 'start' and v
                    cw.minMonth = v

                else if k == 'end' and v
                    cw.maxMonth = v

            if showAdvanced
                jQuery('ul.wordFilter').show()
                jQuery('.advanced').addClass 'expanded'

            if this.minMonth or this.maxMonth
                startYear = this.minMonth.slice(0, 4)
                endYear = this.maxMonth.slice(0, 4)
                jQuery("#slider-range").slider("option", "values", [startYear, endYear])
                this.limit this.minMonth, this.maxMonth

            if not nosubmit
                this.submitHomepageCompareForm(true)


    makeHomepageHistoryState: (slid) ->
        stateA = jQuery('#stateA').val() or ''
        stateB = jQuery('#stateB').val() or ''
        partyA = jQuery(jQuery('.partyA input:checked')[0]).val()
        partyB = jQuery(jQuery('.partyB input:checked')[0]).val()

        pieces = [
            ["terma", this.phraseA(),]
            ["termb", this.phraseB(),]
            ["statea", stateA,]
            ["stateb", stateB,]
            ["partya", partyA,]
            ["partyb", partyB,]
            ["start", this.minMonth,],
            ["end", this.maxMonth,],
            #["pt", jQuery('#partyTimeline:visible').length == 0,],
        ]
        pieces = _(pieces).select( (item) ->
            return item[1]
        ).map( (item) ->
            return "#{item[0]}=#{item[1]}"
        )

        hash = pieces.join '&'
        History.pushState {'slid': slid}, '', "?#{hash}"

    readLegislatorHistory: ->
        hash = History.getState().hash.split('?')[1]
        data = {}
        if hash
            pieces = hash.split '&'
            chamber = party = congress = state = undefined
            _(pieces).each (piece) ->
                [k, v] = piece.split '='
                jQuery("##{k}").val(v)
                data[k] = v

        this.legislatorSearch(data)

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

    if typeof termDetailTerm isnt 'undefined'
        cw.readTermDetailPageHistory()
        cw.populateTermDetailPage termDetailTerm
        #jQuery('#partyTimelineSelect, #overallTimelineSelect').bind('change', (x) ->
        #    cw.makeHomepageHistoryState()
        #)
        History.Adapter.bind(window, 'statechange', ->
            cw.readTermDetailPageHistory()
            cw.populateTermDetailPage termDetailTerm
        )


    jQuery('img').error( ->
        jQuery(this).hide()
    )

    jQuery('.ngramMenu span').bind('click', (x) ->
        classToShow = jQuery(this).attr 'class'
        jQuery('.ngramMenu span').removeAttr('id')
        jQuery(this).attr('id', 'selected')
        jQuery(jQuery('.barChart:visible')[0]).hide(0, ->
            jQuery("ol##{classToShow}").show(0)
        )
    )

    jQuery('#timelineToggle input').bind('click', ->
        selectedId = jQuery('input[name=toggle]:checked', '#timelineToggle').attr 'id'
        timelines = [
            ['party', jQuery('#partyTimeline')],
            ['overall', jQuery('#overallTimeline')],
            #['custom', jQuery('#customTimeline')],
        ]
        selected = {
            'overallTimelineSelect': 'overall',
            'partyTimelineSelect': 'party',
            #'customTimelineSelect': 'custom',
        }[selectedId]

        _(timelines).each (timeline) ->
            name = timeline[0]
            obj = timeline[1]
            if name == selected
                obj.show()
            else
                obj.hide()
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
        pieces = []
        jQuery('#searchFilter select').each (select) ->
            id = jQuery(this).attr 'id'
            val = jQuery(this).val()
            pieces.push "#{id}=#{val}"
        hash = pieces.join '&'
        History.pushState {}, '', "/legislator?#{hash}"
        cw.legislatorSearch({})
    )

    if window.location.pathname.match /^\/legislator\/?$/
        cw.readLegislatorHistory()
        History.Adapter.bind(window, 'statechange', ->
            cw.readLegislatorHistory()
        )

    if window.location.pathname.match /^\/?$/
        cw.readHomepageHistory()
        History.Adapter.bind(window, 'statechange', ->
            if History.getState()['data']['slid'] isnt true
                cw.readHomepageHistory()
        )


    if not _(jQuery('#slider-range')).isEmpty()
        d = new Date()

        if cw.minMonth and cw.maxMonth
            startYear = cw.minMonth.slice(0, 4)
            endYear = cw.maxMonth.slice(0, 4)
        else
            startYear = 1996
            endYear = d.getFullYear()

        jQuery('#slider-range').slider {
            range: true,
            min: 1996,
            max: d.getFullYear(),
            values: [startYear, endYear],
            slide: (event, ui) ->
                jQuery('#years').val "#{ui.values[0]}-#{ui.values[1]}"
            stop: (event, ui) ->
                cw.minMonth = "#{ui.values[0]}01"
                cw.maxMonth = "#{ui.values[1]}12"
                if not _(_(cw.a).keys()).isEmpty() or not _(_(cw.b).keys()).isEmpty()
                    cw.limit cw.minMonth, cw.maxMonth
                else if typeof termDetailTerm isnt 'undefined' # For slider on term detail page
                    cw.limit cw.minMonth, cw.maxMonth
                    cw.buildPartyGraph cw.minMonth, cw.maxMonth
                    cw.start_date = cw.dateFromMonth(cw.minMonth)
                    cw.end_date = cw.dateFromMonth(cw.maxMonth)
                    cw.populateTermDetailPage termDetailTerm
                cw.makeHomepageHistoryState(true)
        }

    jQuery('.advanced').bind('click', ->
        t = jQuery(this)
        jQuery('ul.wordFilter').slideToggle('', ->
            if jQuery(this).is ':visible' then t.addClass 'expanded' else t.removeClass 'expanded'
        )
    )

    jQuery('#embed span').bind('click', ->
        t = jQuery('.embedContainer')
        if t.is ':visible' then t.slideUp() else t.slideDown()
        
        # Determine which graph is being shown.
        if jQuery('#partyTimeline').is(':visible')
            imgSrc = jQuery('#partyTimeline img').attr 'src'
        else
            imgSrc = jQuery('#partyTimeline img').attr 'src'
             
        window.console.log {
            'cw.start_date': cw.start_date,
            'cw.end_date': cw.end_date,
            'src': imgSrc,
        }

    )

    Emphasis.init()
