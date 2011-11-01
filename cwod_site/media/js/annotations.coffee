###
Annotation class for Capitol Words sparklines

Requires:
- jQuery
- underscore.js

Usage: new Annotation($('img#myChart'), params)
- el, {params}
- el: a target image node, including a set of
     attrs data-datasrc(n) containing the data urls to be
     fetched for numbers of mentions, etc,
- {params}: A JSON structure including:
    - template (required):
        A string of data to be interpolated with each sparkline's dataset
        and appended into the annotation box, 1 per dataset
    - heading (optional):
        A template-like string to optionally be applied before the first
        dataset's template is rendered; for example to create a date heading.
        will only have access to the first dataset when rendering
    - iterable (optional):
        A function to pre-process the ajax response for each incoming dataset.
        The default is to pass the data straight through
    - startDate (optional):
        A YYYYMM string representing the first month to display annotations for.
        The default is '199601'
    - endDate (optional):
        A YYYYMM string representing the last month to display annotations for.
        The default is the current month.
    - linkTo (optional):
        Bypasses the normal date-linking behavior, for embeds.

Data-params:
It is expected that `el` will include a Google Charts src attribute, as well as a
data-dataurl attribute for each dataset to be displayed. The `src` attr is used to fetch
a json representation of the chart, and `data-dataurl`s point to the Capitol Words API query
the chart was built from. If more than one dataurl is present (i.e., 2 lines in a chart), they
should be serialized as `data-dataurl0`, `data-dataurl1`, etc.

A Note on templates:
While the goal was to provide a syntax that would allow reuse of possibly pre-existing
jQuery templates, only ${} is supported. Other $.template syntax features will NOT be interpolated.

###
$ = jQuery
$.deparam ||= (qs) ->
    params = {}
    return params unless qs
    pieces = qs.split /[&=]/
    $.each pieces, (idx, val) ->
        if idx % 2
            params[pieces[idx-1]] = val
    return params

class window.Annotation
    el = null
    annotationEl = null
    coordsurl = null
    coords = []
    dataurls = []
    datasets = []
    endDate = null
    heading = 'Annotations.js'
    iterable = (data) ->
        return data
    lines = []
    slices = []
    startDate = null
    template = 'instantiate with new Annotation(el, {iterable, template, heading, startDate, endDate})'

    constructor: (@el, @params) ->
        {@iterable, @template, @heading, @startDate, @endDate, @linkTo} = @params
        if !@template
            @template = @heading
            @heading = null
        @el = $(@el)
        @el.data 'annotation', this
        @el.wrap '<a class="annotation-wrap" target="_top" href="#"></a>'
        if @linkTo
            @el.parent().attr 'href', @linkTo
        @el.parent().css('position', 'relative')
        @annotationEl = $('<div class="annotation"><div class="inner-annotation"></div></div>')
                            .css('position', 'absolute')
                            .css('top', '50%')
                            .hide()
        @el.after(@annotationEl)
        @refresh()

    applyTemplate: (idx) ->
        varP = /\$\{([^\}]+?)\}/gi
        html = ''
        # if a heading template was passed, render it
        if @heading
            html += @heading.replace(varP, (match, varName) =>
                    try
                        value = @datasets[0][idx]
                    catch e
                        return @refresh()
                    parts = varName.split('.')
                    for part in parts
                        value = value[part]
                    return value.toString() or ''
                )
        # apply all datasets to the main template
        for i, dataset of @datasets
            html += @template.replace(varP, (match, varName) ->
                        try
                            value = dataset[idx]
                        catch e
                            @refresh()
                        # expand dot-notated vars to their final value
                        parts = varName.split('.')
                        for part in parts
                            value = value[part]
                        # i is a special var name for the index
                        # of the current data set
                        if varName == 'i'
                            return i
                        # round floats appropriately
                        if typeof value is 'number' and (parseInt(value) != value)
                            value = value.toFixed(4)

                        return value.toString() or ''
                    )
        return html

    bindMouse: ->
        @el.parent().bind 'mouseenter.annotation', (evt) =>
            @annotationEl.show()
        @el.parent().bind 'mouseleave.annotation', (evt) =>
            @annotationEl.hide()
        @el.bind 'mousemove.annotation', (evt) =>
            x = evt.layerX or evt.offsetX
            coords = @point evt
            if isNaN coords[0]
                @annotationEl.hide()
            else
                step = @step(x) + @startOffset()
                @annotationEl
                    .show().stop().animate({'left': coords[0], 'top': coords[1]}, 10)
                    .children('.inner-annotation').html(@applyTemplate step)
                date = @datasets[0][step].month
                year = date.slice 0, 4
                month = date.slice 4, 6
                if not @linkTo
                    @el.parent().attr 'href', "/date/#{year}/#{month}"

    destroy: ->
        @annotationEl.hide()
        @el.unbind '.annotation'
        @el.parent().unbind '.annotation'
        @coordsurl = null
        @coords = []
        @dataurls = []
        @datasets = []
        @lines = []
        @slices = []
        @_months = null
        @_total = null
        # if startDAte and/or endDate were passed to the constructor, this
        # is an embed, so leave them as they are
        if not (@params['startDate'] or @params['endDate'])
            @startDate = null
            @endDate = null

    getDataUrl: (idx, url) ->
        dfd = $.Deferred()
        $.when(@getJSONPVar url)
            .done (data) =>
                @datasets[idx] = @iterable data
                dfd.resolve()

        return dfd.promise()

    getJSONPVar: (url) ->
        $.ajax
            url: url
            dataType: 'jsonp'
            data: {'apikey': window.cwod_apikey}

    loadCoords: ->
        dfd = $.Deferred()
        $.when(@getJSONPVar @coordsurl)
            .done (coords) =>
                for obj in coords.chartshape
                    matches = obj.name.match(/line(\d+?)/)
                    if matches
                        line = matches[1]
                        @coords[line] = []
                        # only take the first half, google returns an image map
                        flat = obj.coords.slice(0, (obj.coords.length/2))
                        for i, val of flat
                            if i % 2
                                x = flat[i-1]
                                y = flat[i]
                                @coords[line].push([x, y])
                dfd.resolve()

        return dfd.promise()

    loadData: ->
        dfd = $.Deferred()
        reqs = [@getDataUrl(idx, url) for idx, url of @dataurls]
        $.when.apply($, reqs)
            .done ->
                dfd.resolve()

        return dfd.promise()

    point: (evt) ->
        x = evt.layerX or evt.offsetX
        step = @step(x)
        pair = [NaN, NaN]
        if 0 <= step < @coords[0].length
            ys = [coordset[step].slice()[1] for coordset in @coords][0]
            y = _.min(ys)
            x = @coords[0][step][0]
            # y = 0
            # $.each(ys, (idx, val) ->
            #     y += val
            #     )
            # y = y / ys.length
            pair = [x, y]
            # buffer for image boundaries
            if pair[0] + @annotationEl.outerWidth() > @el.width()
                pair[0] -= @annotationEl.outerWidth()
                @annotationEl.addClass('flipped')
            else
                @annotationEl.removeClass('flipped')

            if (overlap = pair[1] - @annotationEl.height()/2) < 0
                pair[1] += (overlap * -1)
            else if (overlap = pair[1] + @annotationEl.height()/2) > @el.height()
                pair[1] -= (overlap - @el.height())
        return pair

    refresh: ->
        @destroy()
        if not @startDate and not @endDate
            qs = window.location.href.split('?')[1]
            qparams = $.deparam(qs)
            try
                @startDate = qparams['start']

            try @endDate = qparams['end']

            if not @startDate then @startDate = '199601'
            if not @endDate
                d = new Date()
                @endDate = "#{d.getFullYear()}12"

        if (url = @el.attr 'data-dataurl')
            @dataurls.push url
        else
            i = 0
            while (url = @el.attr "data-dataurl#{i}")
                @dataurls.push url
                i +=1

        @coordsurl = "#{@el.attr('src')}&chof=json"

        $.when(@loadCoords(), @loadData())
            .done =>
                @bindMouse()

    step: (x) ->
        @_total ||= @coords[0].length
        min = @coords[0][0][0]
        max = @coords[0][@_total-1][0]
        range = max - min
        stepsize = range/@_total
        return Math.floor((x - min) / stepsize)

    startOffset: ->
        @_months ||= _.pluck(@datasets[0], 'month')
        offset = _.indexOf(@_months, @startDate, true)
        if offset is -1 then offset = 0
        offset
