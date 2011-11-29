$ = jQuery

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

    else if window.location.pathname.match /^\/term\/.+\/?$/
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
    # if we're looking at a specific term, get the history hash and populate
    if typeof termDetailTerm isnt 'undefined'
        cw.readTermDetailPageHistory()
        cw.populateTermDetailPage termDetailTerm
        #$('#partyTimelineSelect, #overallTimelineSelect').bind('change', (x) ->
        #    cw.makeHomepageHistoryState()
        #)

    # replace broken images with a blank gif
    $('img').error ->
        $(this).attr('src', '/media/img/no_leg_image.gif')

    # toggle the 2-term search form
    $('#toggleSearchCompare').click (e) ->
        e.preventDefault()
        $('.toggleSearchCompare').slideToggle 'fast', 'swing'

    # behavior for the 'compare thing' button on the single term page
    $('#compareTermBtn').live 'click', (e) ->
        e.preventDefault()
        word = $(this).find('em').text()
        $('#terma').val word
        $('#toggleSearchCompare').trigger 'click'

    # ngram phrases tabs
    $('.ngramMenu span').bind 'click', (x) ->
        classToShow = $(this).attr 'class'
        $('.ngramMenu span').removeAttr('id')
        $(this).attr('id', 'selected')
        $('.barChart:visible').eq(0).hide 0, ->
            $("ol##{classToShow}").show(0)

    # show/hide overall/by-party sparklines
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
                obj.show().imagesLoaded ->
            else
                obj.hide()

    $('#partySelect, #stateSelect').change ->
        cw.customizeChart()

    $('.compareSubmit').bind 'click', (e) ->
        if window.location.pathname.match /^\/?$/
            e.preventDefault()
            cw.submitHomepageCompareForm()
        else
            return true

    $('#termSelect input').bind 'keyup', (e) ->
        if e.keyCode == 13 then $('.compareSubmit').trigger 'click'

    $('#termSelect input[type=text]').bind 'focus', ->
        if $(this).val() == 'Word or phrase' then $(this).val ''

    $('#termSelect input[type=text]').bind 'blur', ->
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

    # slider behavior
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
        $('ul.wordFilter').slideToggle 'fast', 'swing', ->
            if $(this).is ':visible' then t.addClass 'expanded' else t.removeClass 'expanded'

    $('#embed a').bind 'click', (e) ->
        e.preventDefault()
        t = $('.embedContainer')
        if t.is ':visible'
            t.slideUp()
        else
            cw.getEmbedCode t

    $('#customizeEmbed input').change ->
        cw.getEmbedCode $('.embedContainer')

    $('#compareGraphic img#compareTimeline, #overallTimeline img, #partyTimeline img').live 'load.capitolwords', ->
        existingAnnotation = $(this).data('annotation')
        if existingAnnotation
            existingAnnotation.refresh()
        else
            heading = '<p class="meta">${verboseMonth}</p>'
            template = '<p class="data"><span class="color-${i}"></span> ${count} ${noun} (${percentage}%)</p>'
            iterable = (data) ->
                data = data.results
                $.each data, (i, obj) ->
                    o = obj.month
                    y = o.substr 0,4
                    m = parseInt o.substr(4,2), 10
                    mos = ['', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
                    data[i].verboseMonth = "#{mos[m]} #{y}"
                    obj.noun = if obj.count is 1 then 'mention' else 'mentions'
                data
            new Annotation this, {iterable:iterable, heading:heading, template:template}

    $('#compareGraphic img#compareTimeline, #overallTimeline img, #partyTimeline img').each ->
        if not $(this).parent().hasClass('annotation-wrap')
            $(this).trigger 'load.capitolwords'

    # reset images, bind ajax calls to do the same
    (area = $('#rtColumn, .crContent')) && area.length && area.imagesLoaded ->

    # fire sample search if arriving fresh on the homepage
    if (window.location.pathname.match /(^\/?$|homepage\.html)/) and (not (window.location.href.match /\?/))
        cw.submitHomepageCompareForm()