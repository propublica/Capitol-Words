spinner = null
$ = jQuery

###
jQuery.deparam
reverses jQuery's param() method, converting a querystring back to an object
###
$.deparam = (qs) ->
    params = {}
    return params unless qs
    pieces = qs.split /[&=]/
    $.each pieces, (idx, val) ->
        if idx % 2
            params[pieces[idx-1]] = val
    return params

###
jQuery.cleanedValue
decodes uri components and strips html tags
###
$.cleanedValue = (str) ->
    return '' unless str
    str = decodeURIComponent(str).replace /\+/g, ' '
    return $("<div>#{str}</div>").text().trim()

###
CapitolWords
main application class
###
class window.CapitolWords
    a: {}
    b: {}
    homepageDefaults:
        'terma':'Word or phrase'
        'termb': 'Word or phrase'
        'statea':''
        'stateb':''
        'partya':'All'
        'partyb': 'All'
        'start':'199601'
        'end':'201112'
    itemsToCompare: []
    legislatorData: []
    minMonth: undefined
    maxMonth: undefined
    random_phrase_i: undefined
    smoothing: 0
    year_values: []
    states :
        "AL": "Alabama",            "AK": "Alaska",         "AZ": "Arizona",        "AR": "Arkansas",
        "CA": "California",         "CO": "Colorado",       "CT": "Connecticut",    "DE": "Delaware",
        "FL": "Florida",            "GA": "Georgia",        "HI": "Hawaii",         "ID": "Idaho",
        "IL": "Illinois",           "IN": "Indiana",        "IA": "Iowa",           "KS": "Kansas",
        "KY": "Kentucky",           "LA": "Louisiana",      "ME": "Maine",          "MD": "Maryland",
        "MA": "Massachusetts",      "MI": "Michigan",       "MN": "Minnesota",      "MS": "Mississippi",
        "MO": "Missouri",           "MT": "Montana",        "NE": "Nebraska",       "NV": "Nevada",
        "NH": "New Hampshire",      "NJ": "New Jersey",     "NM": "New Mexico",     "NY": "New York",
        "NC": "North Carolina",     "ND": "North Dakota",   "OH": "Ohio",           "OK": "Oklahoma",
        "OR": "Oregon",             "PA": "Pennsylvania",   "RI": "Rhode Island",   "SC": "South Carolina",
        "SD": "South Dakota",       "TN": "Tennessee",      "TX": "Texas",          "UT": "Utah",
        "VT": "Vermont",            "VA": "Virginia",       "WA": "Washington",     "WV": "West Virginia",
        "WI": "Wisconsin",          "WY": "Wyoming",        "DC": "District of Columbia",
        "AA": "Armed Forces Americas",                      "AE": "Armed Forces Europe",
        "AP": "Armed Forces Pacific",                       "AS": "American Samoa",
        "GU": "Guam",                                       "MP": "Northern Mariana Islands",
        "PR": "Puerto Rico",                                "VI": "Virgin Islands",

    # annotation properties
    annotation_interval: null
    annotation_interval_frequency: 50
    annotation_line_coords: []
    annotation_results: []
    inchart: false


    addLegislatorToChart: (result, maxcount, div, callback) ->
        url = 'http://capitolwords.org/api/legislators.json'
        bioguide_id = result['legislator']
        pct = (result['count'] / maxcount) * 100
        cw = this
        $.ajax
            dataType: 'jsonp'
            url: url
            async: false
            data:
                'bioguide_id': bioguide_id
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
                
    annotation_callback: () ->
        if (not window.cw.inchart) or (not window.cw.annotation_line_coords)
            jQuery('.annotation').hide()
            return

        window.cw.annotation_show dp for dp in window.cw.findActiveDataPoints()                

    annotation_show: (dp) ->
        [selected, selected_chart] = window.cw.findSelectedChart()
        
        FUZZ_X = 5
        FUZZ_Y = 6
        if selected is 'homepage'
            FUZZ_Y = 13

        dp_series_i = dp[0]
        dp_result = dp[1]
        dp_x = dp[2]
        dp_y = dp[3]

        MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
        annotation_month = MONTHS[(parseInt (dp_result.month.substr 4, 2), 10) - 1]
        annotation_year = dp_result.month.substr 0, 4
        annotation_text = ('<span class="annotation-count">' + dp_result.count + ' mention' + (if dp_result.count!=1 then 's' else '') + '</span><br /><span class="annotation-date">in ' + annotation_month + ' ' + annotation_year + '</span>')
        (jQuery '#annotation-'+selected+'-'+dp_series_i+' .inner-annotation').html annotation_text

        if not ((jQuery '#annotation-'+selected+'-'+dp_series_i).hasClass 'flipped')
            (jQuery '#annotation-'+selected+'-'+dp_series_i).css {
                left: jQuery(selected_chart).offset().left + dp_x + FUZZ_X,
                top: jQuery(selected_chart).offset().top + dp_y + FUZZ_Y
            }
        else
            (jQuery '#annotation-'+selected+'-'+dp_series_i).css {
                right: jQuery(window).width() - (jQuery(selected_chart).offset().left + dp_x + FUZZ_X),
                top: jQuery(selected_chart).offset().top + dp_y + FUZZ_Y
            }

        jQuery('#annotation-'+selected+'-'+dp_series_i).show()

    build_legend: ->
        [termA, termB] = window.cw.phrases()

        partyA = $('.partyA input:checked').eq(0).val()
        stateA = $('#stateA').val()

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

        partyB = $('.partyB input:checked').eq(0).val()
        stateB = $('#stateB').val()

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


    build_legend_html: ->
        legend = this.build_legend()
        termA = legend[0] and legend[0].split(' [')[0] or "(no term)"
        partyA = $('.partyA input:checked').eq(0).parent().text().trim()
        if partyA == 'All'
            partyA = 'All Parties'
        stateA = $('#stateA')
        stateA = stateA.val() and this.states[stateA.val()] or "All states"
        termB = legend[1] and legend[1].split(' [')[0] or "(no term)"
        partyB = $('.partyB input:checked').eq(0).parent().text().trim()
        if partyB == 'All'
            partyB = 'All Parties'
        stateB = $('#stateB')
        stateB = stateB.val() and this.states[stateB.val()] or "All states"
        template = """
        <div class="key">
            Comparing
            <span class="wordOne">
                <span class="color"></span><a href="/term/#{termA}" class="wordOne">#{termA}</a>
                <span class="filters">[#{stateA}, #{partyA}]</span>
            </span>
            and
            <span class="wordTwo">
                <span class="color"></span><a href="/term/#{termB}" class="wordTwo">#{termB}</a>
                <span class="filters">[#{stateB}, #{partyB}]</span>
            </span>
        </div>
        """
        template

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

        window.cw.annotation_line_coords['party'] = []
        jQuery.getJSON (imgUrl + '&chof=json'), (data) ->
            copy_coords = (c) ->
                if c.name.match /^line/
                    window.cw.annotation_line_coords['party'].push (jQuery.extend true, [], c.coords)

            copy_coords(csj) for csj in data.chartshape

        imgTag = "<img id=\"partyTermChart\" src=\"#{imgUrl}\"/>"
        jQuery('#partyTimeline').html imgTag

        ((((jQuery '#partyTermChart').mouseenter (event) ->
           window.cw.inchart = true).mouseleave (event) ->
              window.cw.inchart = false).mousemove (event) ->
                 window.cw.pagex = event.pageX).click (event) ->
                     window.cw.handleChartClick event


    buildXLabels: (values) ->
        years = _(_(values).pluck('month')).select((x) ->
            x.match /01$/)

        positions = [Math.round((($.inArray year, years) / years.length) * 100) for year in years]
        labels = _(years).map( (x) ->
            "1/#{x.slice(2,4)}"
        )
        [labels, positions]

    customizeChart: ->
        party = $('#partySelect').val()
        state = $('#stateSelect').val()
        url = 'http://capitolwords.org/api/chart/timeline.json'
        $.ajax
            dataType: 'jsonp'
            url: url
            data:
                'party': party
                'state': state
                'phrase': $('#term').val()
                'granularity': 'month'
                'percentages': 'true'
                'legend': 'false'
                'mincount': 0
            success: (data) ->
                results = data['results']
                imgUrl = results['url']
                imgTag = """<img src="#{imgUrl}"/>"""
                $('#customChart').attr 'src', imgUrl

    dateFromMonth: (month) ->
        datePieces = month.match(/(\d{4})(\d{2})/).slice(1,3)
        datePieces.push '01'
        datePieces.join '-'

    endDate: ->
        d = new Date()
        if this.year_values[1] then "#{this.year_values[1]}-12-31" else "#{d.getFullYear()}-12-31"

    findActiveDataPoints: ->
        return_vals = []

        [selected, selected_chart] = window.cw.findSelectedChart()

        DETECTION_FUZZ_X = 6
        if selected is 'homepage'
            DETECTION_FUZZ_X = 21
        
        series_i = 0

        while series_i<window.cw.annotation_line_coords[selected].length                
            datapoint_i = 0
            while ((window.cw.annotation_line_coords[selected][series_i][datapoint_i]+DETECTION_FUZZ_X)<(window.cw.pagex - (jQuery selected_chart).offset().left) and (datapoint_i<window.cw.annotation_results[selected][series_i].length*2))
                datapoint_i += 2

            if (datapoint_i/2) < window.cw.annotation_results[selected][series_i].length    
                return_vals.push [ series_i, window.cw.annotation_results[selected][series_i][datapoint_i/2], window.cw.annotation_line_coords[selected][series_i][datapoint_i], window.cw.annotation_line_coords[selected][series_i][datapoint_i+1] ]

            series_i += 1

        return return_vals

    findSelectedChart: ->
        if (jQuery '#annotation-homepage-0').length>0
            return ['homepage', 'img.default']
        else if (jQuery('#overallTimelineSelect').attr 'checked')!='checked'
            return ['party', '#partyTermChart']
        else
            return ['term', '#termChart']

    getCookie: (name) ->
        if document.cookie and (document.cookie isnt '')
            cookies = _(document.cookie.split ';').map ((x) -> $.trim x)
            for cookie in cookies
                [cookieName, cookieContent] = cookie.split('=', 2)
                if cookieName is name
                    return decodeURIComponent cookieContent

    getCREntries: (term) ->
        url = 'http://capitolwords.org/api/text.json'
        cw = this
        data =
            'phrase': term
            'bioguide_id': "['' TO *]"
            'start_date': cw.start_date
            'end_date': cw.end_date
            'sort': 'date desc,score desc'
        $.ajax
            dataType: 'jsonp'
            url: url
            data: data
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
                $('#crEntries').html(html)

    getEmbedCode: (container) ->
        # Determine which graph is being shown.
        if $('#partyTimeline').is(':visible')
            imgSrc = $('#partyTimeline img').attr 'src'
        else
            imgSrc = $('#overallTimeline img').attr 'src'


        data =
            img_src: imgSrc
            url: window.location.href
            title: window.document.title.split(' | ')[0]
            chart_type: if $('#embedDark:checked').length == 1 then 'dark' else 'light'

        $.ajax
            type: 'POST'
            url: '/embed/'
            data: data
            success: (url) ->
                full_url = "http://capitolwords.org#{url}"
                script = """<script type="text/javascript" src="#{full_url}"></script>"""
                container.find('textarea').val script

        container.slideDown()

    getGraph: (term) ->
        data =
            'phrase': term
            'granularity': 'month'
            'percentages': 'true'
            'mincount': 0
            'legend': false

        url = 'http://capitolwords.org/api/chart/timeline.json'
        $.ajax
            dataType: 'jsonp'
            url: url
            data: data
            success: (data) ->
                results = data['results']
                imgUrl = results['url']
                overallImgTag = """<img src="#{imgUrl}" alt="Timeline of occurrences of #{term}"/>"""
                #customImgTag = """<img id="customChart" src="#{imgUrl}" alt="Custom timeline of occurrences of "#{term}"/>"""
                $('#overallTimeline').html overallImgTag
                #$('#customTimeline').append customImgTag

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

                window.cw.annotation_results['term'] = [ (jQuery.extend true, [], results), ]
                window.cw.annotation_line_coords['term'] = []

                jQuery.getJSON (imgUrl + '&chof=json'), (data) ->

                    copy_coords = (c) ->
                        if c.name is 'line0'
                            window.cw.annotation_line_coords['term'].push (jQuery.extend true, [], c.coords)

                    copy_coords(csj) for csj in data.chartshape

                    overallImgTag = "<img id=\"termChart\" src=\"#{imgUrl}\" alt=\"Timeline of occurrences of #{term}\"/>"
                    jQuery('#overallTimeline').html overallImgTag

                    ((((jQuery '#termChart').mouseenter (event) ->
                       window.cw.inchart = true).mouseleave (event) ->
                          window.cw.inchart = false).mousemove (event) ->
                             window.cw.pagex = event.pageX).click (event) ->
                                 window.cw.handleChartClick event

                if cw.minMonth and cw.maxMonth
                    cw.limit cw.minMonth, cw.maxMonth
        }

    getLegislatorPopularity: (term, div) ->
        url = 'http://capitolwords.org/api/phrases/legislator.json'
        cw = this
        $.ajax
            dataType: 'jsonp'
            url: url
            data:
                'phrase': term
                'sort': 'relative'
                'per_page': 10
                'start_date': cw.start_date
                'end_date': cw.end_date
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

    getPartyGraph: (term) ->
        url = 'http://capitolwords.org/api/chart/timeline.json'
        cw = this
        $.ajax
            dataType: 'jsonp'
            url: url
            data:
                'phrase': term
                'granularity': 'month'
                'percentages': 'true'
                'mincount': 0
                'legend': true
                'split_by_party': true
                'start_date': cw.start_date
                'end_date': cw.end_date
            success: (data) ->
                results = data['results']
                imgUrl = results['url']
                imgTag = """<img src="#{imgUrl}" alt="Timeline of occurrences of #{term}"/>"""
                $('#partyTimeline').html imgTag


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

        window.cw.annotation_results['party'] = []
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

                    window.cw.annotation_results['party'].push results
            }

    getPartyPieChart: (term, div, width, height, callback) ->
        width = '' if _(width).isUndefined()
        height = '' if _(width).isUndefined()
        url = 'http://capitolwords.org/api/chart/pie.json'
        cw = this
        $.ajax
            dataType: 'jsonp'
            url: url
            data:
                'phrase': term
                'entity_type': 'party'
                'width': width
                'height': height
                'start_date': cw.start_date
                'end_date': cw.end_date
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

    getStatePopularity: (term, div) ->
        url = 'http://capitolwords.org/api/phrases/state.json'
        cw = this
        $.ajax
            dataType: 'jsonp'
            url: url
            data:
                'phrase': term
                'sort': 'relative'
                'per_page': 10
                'start_date': cw.start_date
                'end_date': cw.end_date
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

    handleChartClick: (event) ->
        active_data_point_result = window.cw.findActiveDataPoints()[0][1]
        url = '/date/'+active_data_point_result.month.substr(0,4)+'/'+active_data_point_result.month.substr(4,2)
        window.location.href = url

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

    legislatorSearch: (data) ->
        cw = this
        data =
            chamber: data['chamber'] or $('#chamber').val()
            party: data['party'] or $('#party').val()
            congress: data['congress'] or $('#congress').val()
            state: data['state'] or $('#state').val()
        $.ajax
            dataType: 'jsonp'
            url: 'http://capitolwords.org/api/legislators.json'
            data: data
            success: (data) ->
                cw.populateLegislatorList data['results']

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
            $('#termChart').attr('src', imgUrl)
            #$('#customChart').attr('src', imgUrl)

        else
            aVals = _(this.a['all']).select func
            bVals = _(this.b['all']).select func
            labelPositions = this.buildXLabels aVals
            labels = labelPositions[0]
            positions = labelPositions[1]
            this.showChart [_(aVals).pluck('percentage'), _(bVals).pluck('percentage')], labels, positions

    makeHomepageHistoryState: (slid) ->
        cw = this
        stateA = $('#stateA').val() or cw.homepageDefaults['statea']
        stateB = $('#stateB').val() or cw.homepageDefaults['stateb']
        partyA = $('.partyA input:checked').eq(0).val() or cw.homepageDefaults['partya']
        partyB = $('.partyB input:checked').eq(0).val() or cw.homepageDefaults['partyb']

        [phraseA, phraseB] = this.phrases()

        params =
            "terma": phraseA
            "termb": phraseB
            "statea": stateA
            "stateb": stateB
            "partya": partyA
            "partyb": partyB
            "start": this.minMonth or cw.homepageDefaults['start']
            "end": this.maxMonth or cw.homepageDefaults['end']

        hashParams = {}
        _.each params, (v, k) ->
            if v isnt cw.homepageDefaults[k] and v isnt undefined
                hashParams[k] = v

        hash = $.param(hashParams)
        History.pushState {'slid': slid}, '', "?#{hash}"

    phrases: ->
        phraseA = $('#terma').val()
        if phraseA == 'Word or phrase'
            phraseA = ''
        phraseB = $('#termb').val()
        if phraseB == 'Word or phrase'
            phraseB = ''
         
        if (window.cw.random_phrase_i isnt undefined) or (phraseA=='') and (phraseB=='') and (window.location.pathname.match /(^\/?$|homepage\.html)/) and (not (window.location.href.match /[\?#]/))
            SAMPLE_PHRASES = [
                ['global warming', 'climate change'],
                ['iraq', 'afghanistan'],
                ['war', 'peace'],
                ['ozone', 'carbon dioxide'],
                ['bailout', 'big banks']
            ]
            if window.cw.random_phrase_i is undefined
                window.cw.random_phrase_i = Math.floor(Math.random() * SAMPLE_PHRASES.length)
            return SAMPLE_PHRASES[window.cw.random_phrase_i]
            
        return [phraseA, phraseB]

    populateLegislatorList: (legislators) ->
        buildTable = ->
            $('table#legislatorList tbody').empty()
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
                    $('table#legislatorList tbody').append tr

            $('table#legislatorList tbody')
                .find('img').error ->
                    $(this).hide()
                .end()
                .imagesLoaded(->).fadeIn 'fast'

        $('table#legislatorList tbody').fadeOut 'fast', buildTable

    populateTermDetailPage: (term) ->

        # hacky, but necessary: the history stuff fires this twice otherwise, which pollutes the
        # count objects used for the annotations
        if window.term_has_been_populated
            return
        window.term_has_been_populated = true

        if _(this.results).isUndefined()
            this.getGraphData term

        this.getStatePopularity term, jQuery('#stateBarChart')

        this.getPartyPieChart term, jQuery('#partyPieChart')
        this.getLegislatorPopularity term, jQuery('#legislatorBarChart')

        if _(this.partyResults).isUndefined()
            this.getPartyGraphData term

        if this.start_date and this.end_date
            this.getCREntries term
     
        window.clearInterval window.cw.annotation_interval
        window.cw.annotation_interval = window.setInterval window.cw.annotation_callback, window.cw.annotation_interval_frequency

    readHomepageHistory: (nosubmit) ->
        cw = this
        param_id_map = {'terma': '#terma', 'termb': '#termb', 'statea': '#stateA', 'stateb': '#stateB', }
        state = History.getState()
        hash = state.hash.split('?')[1]
        params = $.deparam(hash)
        showAdvanced = _.without(_.intersection(params.keys, cw.homepageDefaults.keys), 'terma', 'termb', 'start', 'end').length

        if hash
            _(_.defaults(params, cw.homepageDefaults)).each (v, k) ->
                id = param_id_map[k]
                $("#{id}").val $.cleanedValue v

                if k == 'partya' and v
                    $("#partyA#{v}").attr('checked', true)
                else if k == 'partyb' and v
                    $("#partyB#{v}").attr('checked', true)
                else if k == 'start' and v isnt cw.homepageDefaults[k]
                    cw.minMonth = v
                else if k == 'end' and v isnt cw.homepageDefaults[k]
                    cw.maxMonth = v

            if showAdvanced
                $('ul.wordFilter').show()
                $('.advanced').addClass 'expanded'

            cw.minMonth = cw.minMonth or cw.homepageDefaults['start']
            cw.maxMonth = cw.maxMonth or cw.homepageDefaults['end']

            startYear = cw.minMonth.slice(0, 4)
            endYear = cw.maxMonth.slice(0, 4)
            $("#slider-range").slider("option", "values", [startYear, endYear])
            cw.limit cw.minMonth, cw.maxMonth

            if not nosubmit
                cw.submitHomepageCompareForm(true)

    readLegislatorHistory: ->
        hash = History.getState().hash.split('?')[1]
        data = {}
        if hash
            pieces = hash.split '&'
            chamber = party = congress = state = undefined
            _(pieces).each (piece) ->
                [k, v] = piece.split '='
                $("##{k}").val(v)
                data[k] = v

        this.legislatorSearch(data)

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
#                $('#overallTimeline').hide(->
#                    $('#partyTimelineSelect').attr('checked', true)
#                    $('#partyTimeline').show()
#                )


        if this.minMonth or this.maxMonth
            startYear = this.minMonth.slice(0, 4)
            endYear = this.maxMonth.slice(0, 4)
            $("#slider-range").slider("option", "values", [startYear, endYear])

            this.limit this.minMonth, this.maxMonth

    sameOrigin: (url) ->
        host = document.location.host
        protocol = document.location.protocol
        sr_origin = "//#{host}"
        origin = protocol + sr_origin
        (url == origin || url.slice(0, origin.length + 1) == origin + '/') || (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') || !(/^(\/\/|http:|https:).*/.test(url))

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

        if $('#annotation-homepage-0').length>0
            window.cw.annotation_line_coords['homepage'] = []
            jQuery.getJSON (chart.url() + '&chof=json'), (data) ->
                copy_coords = (c) ->
                    if c.name.match /^line/
                        window.cw.annotation_line_coords['homepage'].push (jQuery.extend true, [], c.coords)

                copy_coords(csj) for csj in data.chartshape            
            
            $('#chart img.realChart, #compareGraphic img.default').attr('src', chart.url()).fadeIn 100

            ((((jQuery '#chart img.realChart, #compareGraphic img.default').mouseenter (event) ->
               window.cw.inchart = true).mouseleave (event) ->
                  window.cw.inchart = false).mousemove (event) ->
                     window.cw.pagex = event.pageX).click (event) ->
                         window.cw.handleChartClick event

            window.clearInterval window.cw.annotation_interval
            window.cw.annotation_interval = window.setInterval window.cw.annotation_callback, window.cw.annotation_interval_frequency

        if spinner
            spinner.stop()

        chart.url()

    smooth: (list, degree) ->
        win = degree * 2 - 1
        weight = _.range(0, win).map( (x) -> 1.0 )
        weightGauss = []

        for i in _.range(0, win)
            i = i-degree+1
            frac = i/win
            gauss = 1 / Math.exp((4*(frac))*(4*(frac)))
            weightGauss.push gauss

        weight = _(weightGauss).zip(weight).map (x) ->
            x[0]*x[1]

        smoothed = _.range(0, (list.length+1)-win).map (x) ->
            0.0

        func = (memo, num) ->
            memo + num

        _(_.range(smoothed.length)).each (i) ->
            smoothed[i] = _(list.slice(i, i+win)).zip(weight).map (x) ->
                x[0]*x[1]
            .reduce(func, 0) / _(weight).reduce(func, 0)

    startDate: ->
        if this.year_values[0] then "#{this.year_values[0]}-01-01" else '1996-01-01'

    submitHomepageCompareForm: (skipState) ->
        cw = this
        opts =
            lines: 12
            length: 7
            width: 4
            radius: 10
            color: '#000'
            speed: 1
            trail: 100
            shadow: true

        target = document.getElementById 'compareGraphic'
        # stop the spinner first if it's already running
        spinner && spinner.stop && spinner.stop()
        spinner = new Spinner(opts).spin target

        url = 'http://capitolwords.org/api/dates.json'

        [phraseA, phraseB] = cw.phrases()

        window.cw.annotation_results['homepage'] = [[], []]
        window.cw.annotation_line_coords['homepage'] = []

        querya = $.ajax
            dataType: 'jsonp'
            url: url
            data:
                phrase: phraseA
                state: $('#stateA').val() or ''
                party: $('.partyA input:checked').eq(0).val()
                granularity: 'month'
                percentages: true
                mincount: 0
            success: (data) ->
                aResults = data['results']
                cw.a['all'] = aResults
                cw.a['counts'] = _(aResults).pluck 'count'
                cw.a['percentages'] = _(aResults).pluck 'percentage'
                window.cw.annotation_results['homepage'][0] = (jQuery.extend true, [], aResults)

        queryb = $.ajax
            dataType: 'jsonp'
            url : url
            data:
                phrase: phraseB
                state: $('#stateB').val() or ''
                party: $('.partyB input:checked').eq(0).val()
                granularity: 'month'
                percentages: true
                mincount: 0
            success: (data) ->
                bResults = data['results']
                cw.b['all'] = bResults
                cw.b['counts'] = _(bResults).pluck 'count'
                cw.b['percentages'] = _(bResults).pluck 'percentage'
                window.cw.annotation_results['homepage'][1] = (jQuery.extend true, [], bResults)

        $.when(querya, queryb)
            .done ->
                if cw.minMonth or cw.maxMonth
                    cw.limit cw.minMonth, cw.maxMonth
                else
                    labelPositions = cw.buildXLabels cw.a['all']
                    labels = labelPositions[0]
                    positions = labelPositions[1]
                    cw.showChart [cw.a['percentages'], cw.b['percentages']], labels, positions
            .then ->
                if spinner
                    spinner.stop()

                $('#compareGraphic div.key').eq(0).replaceWith(cw.build_legend_html())

                window.cw.random_phrase_i = undefined

        if not skipState
            this.makeHomepageHistoryState(true)

    titleCase: (s) ->
        s.replace(/\w\S*/g, (txt) ->
            txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase()
        )

    trimGraph: ->
        if this.year_values.length == 2 then true else false

###
Create a global CW instance within this closure
###
cw = new window.CapitolWords
window.cw = cw
History = window.History

###
Add csrf token to ajax POSTs
###
$(document).ajaxSend (event, xhr, settings) ->
    # Adapted from https://docs.djangoproject.com/en/dev/ref/contrib/csrf/
    if (settings.type is 'POST') and cw.sameOrigin(settings.url)
        xhr.setRequestHeader "X-CSRFToken", cw.getCookie('csrftoken')

###
Handle special routes
###
History.Adapter.bind window, 'statechange', ->
    if window.location.pathname.match /^\/legislator\/?$/
        cw.readLegislatorHistory()

    else if window.location.pathname.match /^term\/[.+]\/?/
        cw.readTermDetailPageHistory()
        cw.populateTermDetailPage termDetailTerm

    else if window.location.pathname.match /^\/?$/
        cw.readHomepageHistory()

# force statechange on initial load
$(window).trigger 'statechange'

###
DomReady Handler
###
$(document).ready ->
    if typeof termDetailTerm isnt 'undefined'
        cw.readTermDetailPageHistory()
        cw.populateTermDetailPage termDetailTerm
        #$('#partyTimelineSelect, #overallTimelineSelect').bind('change', (x) ->
        #    cw.makeHomepageHistoryState()
        #)


    $('img').error ->
        $(this).hide()

    $('#toggleSearchCompare').click ->
        $('.toggleSearchCompare').slideToggle()
        false

    $('.ngramMenu span').bind 'click', (x) ->
        classToShow = $(this).attr 'class'
        $('.ngramMenu span').removeAttr('id')
        $(this).attr('id', 'selected')
        $('.barChart:visible').eq(0).hide 0, ->
            $("ol##{classToShow}").show(0)

    $('#timelineToggle input').bind 'click', ->
        selectedId = $('input[name=toggle]:checked', '#timelineToggle').attr 'id'
        timelines = [
            ['party', $('#partyTimeline')],
            ['overall', $('#overallTimeline')],
            #['custom', $('#customTimeline')],
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

    $('#partySelect, #stateSelect').change ->
        cw.customizeChart()

    $('.compareSubmit').bind 'click', ->
        cw.submitHomepageCompareForm()

    $('#termSelect input').bind 'keyup', (e) ->
        if e.keyCode == 13 then cw.submitHomepageCompareForm()

    $('#termSelect input').bind 'focus', ->
        if $(this).val() == 'Word or phrase' then $(this).val ''

    $('#termSelect input').bind 'blur', ->
        if $(this).val() == '' then $(this).val 'Word or phrase'

    $('#searchFilterButton').bind 'click', ->
        pieces = []
        $('#searchFilter select').each (select) ->
            id = $(this).attr 'id'
            val = $(this).val()
            pieces.push "#{id}=#{val}"
        hash = pieces.join '&'
        History.pushState {}, '', "/legislator?#{hash}"
        cw.legislatorSearch({})

    $('#signUp').find('input[type=text]').bind 'focus', ->
        el = $(this)
        try
          el.parent().find('label[for=' + el.attr('id') + ']').eq(0).addClass('hidden')
    .bind 'blur', ->
        el = $(this)
        if !el.val()
          try
            el.parent().find('label[for=' + el.attr('id') + ']').eq(0).removeClass('hidden')

    if not _($('#slider-range')).isEmpty()
        d = new Date()

        if cw.minMonth and cw.maxMonth
            startYear = cw.minMonth.slice(0, 4)
            endYear = cw.maxMonth.slice(0, 4)
        else
            startYear = 1996
            endYear = d.getFullYear()

        $('#slider-range').slider
            range: true
            min: 1996
            max: d.getFullYear()
            values: [startYear, endYear]
            slide: (event, ui) ->
                $('#years').val "#{ui.values[0]}-#{ui.values[1]}"
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

    $('.advanced').bind 'click', ->
        t = $(this)
        $('ul.wordFilter').slideToggle '', ->
            if $(this).is ':visible' then t.addClass 'expanded' else t.removeClass 'expanded'

    $('#embed span').bind 'click', ->
        t = $('.embedContainer')
        if t.is ':visible'
            t.slideUp()
        else
            cw.getEmbedCode t

    $('#customizeEmbed input').change ->
        cw.getEmbedCode $('.embedContainer')

    # reset images, bind ajax calls to do the same
    (area = $('#rtColumn')) && area.length && area.imagesLoaded ->

    # fire sample search if arriving fresh on the homepage
    if (window.location.pathname.match /(^\/?$|homepage\.html)/) and (not (window.location.href.match /[\?#]/))
        cw.submitHomepageCompareForm()
