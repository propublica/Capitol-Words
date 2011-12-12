###
CapitolWords
main application class
Requires: jQuery, jQuery ui slider, underscore
###
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
    return $.trim($("<div>#{str}</div>").text())

###
jQuery.sum
returns the sum of an array
###
$.sum = (arr) ->
    sum = 0
    for val in arr
        sum += val
    return sum

currentMonth = ->
    d = new Date()
    pad = if d.getMonth() + 1 > 9 then '' else '0'
    "#{d.getFullYear()}#{pad}#{d.getMonth() + 1}"

class window.CapitolWords
    cw: this
    a: {}
    b: {}
    debug_progress: 0
    homepageDefaults:
        'terma':'Word or phrase'
        'termb': 'Word or phrase'
        'statea': ''
        'stateb': ''
        'partya': 'All'
        'partyb': 'All'
        'start': '199601'
        'end': currentMonth()
    itemsToCompare: []
    legislatorData: []
    minMonth: undefined
    maxMonth: undefined
    random_phrase_i: undefined
    smoothing: 0
    spinner: null
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


    addLegislatorToChart: (result, maxcount, div, callback) ->
        url = 'http://capitolwords.org/api/legislators.json'
        bioguide_id = result['legislator']
        pct = (result['count'] / maxcount) * 100
        $.ajax
            dataType: 'jsonp'
            url: url
            async: false
            data:
                bioguide_id: bioguide_id
                apikey: window.cwod_apikey
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


    build_legend: ->
        [termA, termB] = cw.phrases()

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
        partyA = $.trim($('.partyA input:checked').eq(0).parent().text())
        if partyA == 'All'
            partyA = 'All Parties'
        stateA = $('#stateA')
        stateA = stateA.val() and this.states[stateA.val()] or "All states"
        termB = legend[1] and legend[1].split(' [')[0] or "(no term)"
        partyB = $.trim($('.partyB input:checked').eq(0).parent().text())
        if partyB == 'All'
            partyB = 'All Parties'
        stateB = $('#stateB')
        stateB = stateB.val() and this.states[stateB.val()] or "All states"
        template = """
        <div class="key">
            <span class="wordOne">
                <span class="color"></span><a href="/term/#{termA}" class="wordOne">#{termA}</a>
                <span class="filters">[#{stateA}, #{partyA}]</span>
            </span>
            <span class="wordTwo">
                <span class="color"></span><a href="/term/#{termB}" class="wordTwo">#{termB}</a>
                <span class="filters">[#{stateB}, #{partyB}]</span>
            </span>
        </div>
        """
        template

    buildPartyGraph: (minMonth, maxMonth, requestedUrls) ->
        if minMonth and maxMonth
            func = (v) ->
                v['month'] >= minMonth and v['month'] <= maxMonth
        else
            func = ->
                true

        if not requestedUrls
            requestedUrls = this.getDataUrlsForImage $('#partyTermChart')

        vals = [_(x[1]).select(func) for x in this.partyResults][0]
        labelPositions = this.buildXLabels vals[0]
        partyAPercentages = _(vals[0]).pluck 'percentage'
        partyBPercentages = _(vals[1]).pluck 'percentage'
        percentages = [partyAPercentages, partyBPercentages, ]
        parties = [x[0] for x in this.partyResults]

        colors = {'D': '295e72', 'R': 'bb3110',}
        params =
            x_positions:labelPositions[0]
            x_label_positions:labelPositions[1]
            width:565
            height:300
            colors:[colors[this.partyResults[0][0]], colors[this.partyResults[1][0]],]
            legend:[this.partyResults[0][0], this.partyResults[1][0],]

        # we don't bother passing requestedUrls here because 'showChart' only operates
        # directly on the homepage chart; otherwise it returns a url.
        imgUrl = this.showChart [partyAPercentages, partyBPercentages,], params

        imgTag = $ """<img id="partyTermChart"
                         src="#{imgUrl}" />"""

        if typeof requestedUrls != 'undefined'
            for i, url of requestedUrls
                imgTag.attr('data-dataurl' + i, url)
        $('#partyTimeline').html imgTag

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
                'apikey': window.cwod_apikey
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
            'apikey': window.cwod_apikey
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
                _(entries).each (entry, idx) ->
                    cycle = if idx % 2 then 'odd' else 'even'
                    html += """
                    <tr class="#{cycle}"><td colspan="2">
                        <table>
                            <tbody>
                                <tr>
                                    <td class="entTitle"><a href="#{entry.capitolwords_url}">#{cw.titleCase(entry.title)}</a></td>
                                    <td class="entDate">#{entry.date}</td>
                                </tr>
                                <tr colspan="2">
                                    <td colspan="2" class="legislators">
                                    <a href="/legislator/#{entry.bioguide_id}">#{entry.speaker_first} #{entry.speaker_last}, #{entry.speaker_party}-#{entry.speaker_state}</a>
                                    </td>
                                </tr>
                                <tr colspan="2">
                                    <td colspan="2" class="abstract">
                                        #{entry.match}
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </td></tr>
                    """
                $('#crEntries').html(html)

    getDataUrlsForImage: (el) ->
        requestedUrls = []
        if (url = $(el).attr 'data-dataurl')
            requestedUrls.push url
        else
            i = 0
            while (url = $(el).attr "data-dataurl#{i}")
                requestedUrls.push url
                i++

        requestedUrls

    getEmbedCode: (container) ->
        # Determine which graph is being shown.
        fields =
            url: window.location.href
            chart_color: if $('#embedDark:checked').length then 2 else 1
            title: window.document.title.split(' | ')[0]
            img_src: ''
            by_party_img_src: ''
            overall_img_src: ''
            start_date: $.deparam(location.href.split('?')[1])['start'] or cw.minMonth or cw.homepageDefaults['start']
            end_date: $.deparam(location.href.split('?')[1])['end'] or cw.maxMonth or cw.homepageDefaults['end']
            apikey: window.cwod_apikey

        $('#partyTimeline img').each ->
            fields['by_party_img_src'] = $('#partyTimeline img').attr 'src'
            fields['overall_img_src'] = $('#overallTimeline img').attr 'src'
            fields['chart_type'] = if $('#partyTimeline img').is(':visible') then 2 else 1
            window.termDetailTerm && fields['extra'] = {'term': termDetailTerm}
            fields['extra'] =
                by_party_dataurls: cw.getDataUrlsForImage $('#partyTimeline img').eq(0)
                overall_dataurls: cw.getDataUrlsForImage $('#overallTimeline img').eq(0)
        $('#compareGraphic img#compareTimeline').each ->
            fields['img_src'] = $(this).attr 'src'
            fields['chart_type'] = 3
            [terma, termb] = cw.phrases()
            fields['extra'] =
                terma: terma
                termb: termb
                statea: $('#stateA').val()
                stateb: $('#stateB').val()
                partya: $('input[name=partya]').val()
                partyb: $('input[name=partyb]').val()
                dataurls: cw.getDataUrlsForImage $(this)

        # resize charts to embed dimension`
        for key in ['img_src', 'by_party_img_src', 'overall_img_src']
            fields[key] = fields[key].replace /chs=[\dx]+/, 'chs=570x200'

        $.ajax
            type: 'POST'
            url: '/embed/'
            data: fields
            enctype: 'miltipart/form-data'
            success: (url) ->
                full_url = "http://capitolwords.org#{url}"
                script = """<script type="text/javascript" src="#{full_url}"></script>"""
                container.find('textarea').val script

        container.slideDown()


    getGraphData: (term) ->
        data =
            'phrase': term
            'granularity': 'month'
            'percentages': 'true'
            'mincount': 0
            'apikey': window.cwod_apikey

        url = 'http://capitolwords.org/api/dates.json'
        cw = this

        requestedUrl = "#{url}?#{$.param(data)}"

        $.ajax {
            dataType: 'jsonp',
            url: url,
            data: data,
            success: (data) ->
                results = data['results']
                cw.results = results
                counts = _(results).pluck 'count'
                percentages = _(results).pluck 'percentage'
                labelPositions = cw.buildXLabels results

                imgUrl = cw.showChart [percentages], {x_labels:labelPositions[0], x_label_positions:labelPositions[1], width:565, height:300, colors:['E0B300',]}

                overallImgTag = """<img id="termChart"
                                        src="#{imgUrl}"
                                        alt="Timeline of occurrences of #{term}"
                                        data-dataurl="#{requestedUrl}" />"""
                $('#overallTimeline').html overallImgTag

                if cw.minMonth and cw.maxMonth
                    cw.limit cw.minMonth, cw.maxMonth

                $('#termChart, #partyTermChart').trigger('load.capitolwords')

        }

    getLegislatorPopularity: (term, div) ->
        url = 'http://capitolwords.org/api/phrases/legislator.json'
        cw = this
        $.ajax
            dataType: 'jsonp'
            url: url
            data:
                'phrase': term
                'sort': 'count'
                'per_page': 10
                'start_date': cw.start_date
                'end_date': cw.end_date
                'apikey': window.cwod_apikey
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
        requestedUrls = []

        render = () ->
            chartData = []
            legendItems = []
            cw.partyResults = []
            _(partyData).each (partyResult) ->
                cw.partyResults.push partyResult

            cw.buildPartyGraph cw.minMonth, cw.maxMonth, requestedUrls

        parties = ['D', 'R', ]
        renderWhenDone = _(parties.length).after(render)

        _(parties).each (party) ->
            data = {
                'party': party,
                'phrase': term,
                'granularity': 'month',
                'percentages': true,
                'mincount': 0,
                'apikey': window.cwod_apikey
            }
            requestedUrls.push "#{url}?#{$.param(data)}"
            jQuery.ajax {
                dataType: 'jsonp',
                url: url,
                data: data,
                success: (data) ->
                    results = data['results']
                    partyData.push [party, results]
                    renderWhenDone()

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
                'apikey': window.cwod_apikey
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
                'sort': 'count'
                'per_page': 10
                'start_date': cw.start_date
                'end_date': cw.end_date
                'apikey': window.cwod_apikey
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

    highlightEntries: (entries, term) ->
        entry_matches = []
        term_parts = term.split(/[\s\-]/)
        delim = '[\\s?!.,();:\'"\\-]+?'
        regexp = new RegExp(term_parts.join(delim), "ig")
        _(entries).each (entry) ->
            match = null
            _(entry['speaking']).each (graf) ->
                graf = graf.replace /\n/, ' '
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
            apikey: window.cwod_apikey
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
            imgUrl = this.showChart [percentages], {x_labels:labelPositions[0], x_label_positions:labelPositions[1], width:565, height:300, colors:['E0B300',]}
            $('#termChart').attr('src', imgUrl)
            #$('#customChart').attr('src', imgUrl)

        else # homepage
            aVals = _(this.a['all']).select func
            bVals = _(this.b['all']).select func
            labelPositions = this.buildXLabels aVals
            labels = labelPositions[0]
            positions = labelPositions[1]
            this.showChart [_(aVals).pluck('percentage'), _(bVals).pluck('percentage')], {x_labels:labels, x_label_positions:positions}

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
        window._gaq && _gaq.push ["_trackPageView", "/?#{hash}"]

    phrases: ->
        params = $('#termSelect').serialize()
        phraseA = $('#terma').val()
        if phraseA == 'Word or phrase'
            phraseA = ''
        phraseB = $('#termb').val()
        if phraseB == 'Word or phrase'
            phraseB = ''

        if (cw.random_phrase_i isnt undefined) or (phraseA=='') and (phraseB=='') and (window.location.pathname.match /(^\/?$|homepage\.html)/) and (not (window.location.href.match /[\?#]/))
            SAMPLE_PHRASES = [
                ['global warming', 'climate change'],
                ['iraq', 'afghanistan'],
                ['war', 'peace'],
                ['ozone', 'carbon dioxide'],
                ['bailout', 'big banks']
            ]
            if cw.random_phrase_i is undefined
                cw.random_phrase_i = Math.floor(Math.random() * SAMPLE_PHRASES.length)
            return SAMPLE_PHRASES[cw.random_phrase_i]

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
                    $(this).attr('src', 'http://assets.sunlightfoundation.com/capitol-words/media/img/cwod_default.png')
                .end()
                .imagesLoaded(->).fadeIn 'fast'

        $('table#legislatorList tbody').fadeOut 'fast', buildTable

    populateTermDetailPage: (term) ->
        term = unescape term
        this.getGraphData term

        this.getStatePopularity term, jQuery('#stateBarChart')

        this.getPartyPieChart term, jQuery('#partyPieChart')
        this.getLegislatorPopularity term, jQuery('#legislatorBarChart')

        if _(this.partyResults).isUndefined()
            this.getPartyGraphData term

        if this.start_date and this.end_date
            this.getCREntries term

    readHomepageHistory: (nosubmit) ->
        cw.minMonth = cw.maxMonth = false
        param_id_map = {'terma': '#terma', 'termb': '#termb', 'statea': '#stateA', 'stateb': '#stateB', }
        state = History.getState()
        hash = state.hash.split('?')[1]

        params = $.deparam(hash)
        # showAdvanced = _.without(_.intersection(params.keys, cw.homepageDefaults.keys), 'terma', 'termb', 'start', 'end').length

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

            # if showAdvanced
            #     $('ul.wordFilter').show()
            #     $('.advanced').addClass 'expanded'

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
        data = {congress: 112}
        $("#congress").val(112)
        if hash
            pieces = hash.split '&'
            chamber = party = congress = state = undefined
            _(pieces).each (piece) ->
                [k, v] = piece.split '='
                $("##{k}").val(v)
                data[k] = v

        this.legislatorSearch(data)

    readTermDetailPageHistory: ->
        # TODO: range does not properly update
        this.minMonth = "199601"
        this.maxMonth = "201112"
        if typeof History.getState().hash is 'undefined'
            return
        hash = History.getState().hash.split('?')[1]
        if hash
            pieces = [x.split '=' for x in hash.split '&'][0]
            for piece in pieces
                [k, v] = piece
                if k == 'start'
                    this.minMonth = v
                    this.start_date = this.dateFromMonth(this.minMonth)

                else if k == 'end'
                    this.maxMonth = v
                    this.end_date = this.dateFromMonth(this.maxMonth)

               # else if k == 'pt' and v == 'true'
               #     $('#overallTimeline').hide(->
               #         $('#partyTimelineSelect').attr('checked', true)
               #         $('#partyTimeline').show()
               #     )

        if this.minMonth or this.maxMonth
            startYear = this.minMonth.slice(0, 4)
            endYear = this.maxMonth.slice(0, 4)
            $("#slider-range").slider("values", [startYear, endYear])

            this.limit this.minMonth, this.maxMonth

    sameOrigin: (url) ->
        host = document.location.host
        protocol = document.location.protocol
        sr_origin = "//#{host}"
        origin = protocol + sr_origin
        (url == origin || url.slice(0, origin.length + 1) == origin + '/') || (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') || !(/^(\/\/|http:|https:).*/.test(url))

    showChart: (data, params) ->
        {x_labels, x_label_positions, width, height, colors, legend, requestedUrls} = params
        width = width or 880
        height = height or 340

        chart = new GoogleChart width, height
        values = []
        maxValue = 0
        max = 0
        cw = this
        _(data).each (item) ->
            #values = cw.smooth(item, Number(cw.smoothing) || 1)
            values = item
            maxValue = Math.round(_(values).max()*10000)/10000
            if maxValue > max
                max = Math.round(maxValue*10000)/10000
            chart.add_data values

        chart.set_grid 0, 50, 2, 5
        chart.set_fill 'bg', 's', '00000000'
        if not colors
            colors = ['8E2844', 'A85B08', 'AF9703']
        if not legend
            legend = this.build_legend()
        chart.set_legend legend if not _(legend).isEmpty() and not location.pathname.match /^\/?$/ # no legend on homepage
        chart.set_colors(colors.slice(0, legend.length))

        chart.set_axis_labels 'y', ['', "#{max}%"]

        if x_labels
            chart.set_axis_labels 'x', x_labels

        if x_label_positions
            chart.set_axis_positions 'x', x_label_positions

        img = $('#chart img.realChart, #compareGraphic img#compareTimeline').attr('src', chart.url())

        if typeof requestedUrls == 'object' and requestedUrls.length
            if requestedUrls.length > 1
                for i, url of requestedUrls
                    img.attr("data-dataurl#{i}", url)
            else
                img.attr('data-dataurl', requestedUrls[0])
        img.fadeIn 500

        img.trigger 'load.capitolwords'

        if cw.spinner
            cw.spinner.stop()

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
        cw.spinner && cw.spinner.stop && cw.spinner.stop()
        cw.spinner = new Spinner(opts).spin target

        url = 'http://capitolwords.org/api/dates.json'
        breakdownUrl = 'http://capitolwords.org/api/chart/pie.json'
        requestedUrls = []

        [phraseA, phraseB] = cw.phrases()
        d = new Date
        startDate = if cw.minMonth then "#{cw.minMonth.slice(0,4)}-#{cw.minMonth.slice(4,6)}-01" else "1996-01-01"
        endDate = if cw.maxMonth then "#{cw.maxMonth.slice(0,4)}-12-31" else "#{d.getFullYear()}-12-31"

        queryaData =
            phrase: phraseA
            state: $('#stateA').val() or ''
            party: $('.partyA input:checked').eq(0).val()
            granularity: 'month'
            percentages: true
            mincount: 0
            apikey: window.cwod_apikey

        requestedUrls.push "#{url}?#{$.param(queryaData)}"
        querya = $.ajax
            dataType: 'jsonp'
            url: url
            data: queryaData
            success: (data) ->
                aResults = data['results']
                cw.a['all'] = aResults
                cw.a['counts'] = _(aResults).pluck 'count'
                cw.a['percentages'] = _(aResults).pluck 'percentage'

        querybData =
            phrase: phraseB
            state: $('#stateB').val() or ''
            party: $('.partyB input:checked').eq(0).val()
            granularity: 'month'
            percentages: true
            mincount: 0
            apikey: window.cwod_apikey

        requestedUrls.push "#{url}?#{$.param(querybData)}"
        queryb = $.ajax
            dataType: 'jsonp'
            url : url
            data: querybData
            success: (data) ->
                bResults = data['results']
                cw.b['all'] = bResults
                cw.b['counts'] = _(bResults).pluck 'count'
                cw.b['percentages'] = _(bResults).pluck 'percentage'

        breakdownaData =
            phrase: phraseA
            output: 'data'
            entity_type: 'party'
            start_date: startDate
            end_date: endDate
            apikey: window.cwod_apikey

        breakdowna = $.ajax
            dataType: 'jsonp'
            url: breakdownUrl
            data: breakdownaData
            success: (data) ->
                cw.a['breakdown'] = data.data

        breakdownbData =
            phrase: phraseB
            output: 'data'
            entity_type: 'party'
            start_date: startDate
            end_date: endDate
            apikey: window.cwod_apikey

        breakdownb = $.ajax
            dataType: 'jsonp'
            url: breakdownUrl
            data: breakdownbData
            success: (data) ->
                cw.b['breakdown'] = data.data


        $.when(querya, queryb, breakdowna, breakdownb)
            .done ->
                # if cw.minMonth or cw.maxMonth
                #     cw.limit cw.minMonth, cw.maxMonth
                # else
                labelPositions = cw.buildXLabels cw.a['all']
                labels = labelPositions[0]
                positions = labelPositions[1]
                cw.showChart [cw.a['percentages'], cw.b['percentages']], {x_labels:labels, x_label_positions:positions, requestedUrls:requestedUrls}
                if cw.minMonth or cw.maxMonth
                    cw.limit cw.minMonth, cw.maxMonth
            .then ->
                if cw.spinner
                    cw.spinner.stop()

                legend_html = cw.build_legend_html()
                $('#compareGraphic div.key span.wordOne span.legend-text').eq(0).html($(legend_html).find('span.wordOne').html())
                $('#compareGraphic div.key span.wordTwo span.legend-text').eq(0).html($(legend_html).find('span.wordTwo').html())

                # update percentage bar chart
                aTotal = $.sum(cw.a.breakdown[1])
                if 'D' not in cw.a.breakdown[0]
                    $("#compareGraphic .key .wordOne .party-breakdown .D").animate({'width': 0})
                    $("#compareGraphic .key .wordOne .party-breakdown-labels .D .percentage").html("0%")
                if 'R' not in cw.a.breakdown[0]
                    $("#compareGraphic .key .wordOne .party-breakdown .R").animate({'width': 0})
                    $("#compareGraphic .key .wordOne .party-breakdown-labels .R .percentage").html("0%")
                for i, party of cw.a.breakdown[0]
                    $("#compareGraphic .key .wordOne .party-breakdown .#{party}").animate({'width': "#{((cw.a.breakdown[1][i] / aTotal) * 100).toFixed(0)}%"})
                    $("#compareGraphic .key .wordOne .party-breakdown-labels .#{party} .percentage").html("#{((cw.a.breakdown[1][i] / aTotal) * 100).toFixed(0)}%")

                bTotal = $.sum(cw.b.breakdown[1])
                if 'D' not in cw.b.breakdown[0]
                    $("#compareGraphic .key .wordTwo .party-breakdown .D").animate({'width': 0})
                    $("#compareGraphic .key .wordTwo .party-breakdown-labels .D .percentage").html("0%")
                if 'R' not in cw.b.breakdown[0]
                    $("#compareGraphic .key .wordTwo .party-breakdown .R").animate({'width': 0})
                    $("#compareGraphic .key .wordTwo .party-breakdown-labels .R .percentage").html("0%")
                for i, party of cw.b.breakdown[0]
                    $("#compareGraphic .key .wordTwo .party-breakdown .#{party}").animate({'width': "#{(cw.b.breakdown[1][i] / bTotal) * 100}%"})
                    $("#compareGraphic .key .wordTwo .party-breakdown-labels .#{party} .percentage").html("#{((cw.b.breakdown[1][i] / bTotal) * 100).toFixed(0)}%")

                cw.random_phrase_i = undefined

        if not skipState
            this.makeHomepageHistoryState(true)

    titleCase: (s) ->
        s.replace(/\w\S*/g, (txt) ->
            txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase()
        )

    trimGraph: ->
        if this.year_values.length == 2 then true else false
