(function() {
  /*
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
  
  */
  var $;
  var __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };
  $ = jQuery;
  $.deparam || ($.deparam = function(qs) {
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
  });
  window.Annotation = (function() {
    var annotationEl, coords, coordsurl, datasets, dataurls, el, endDate, heading, iterable, lines, slices, startDate, template;
    el = null;
    annotationEl = null;
    coordsurl = null;
    coords = [];
    dataurls = [];
    datasets = [];
    endDate = null;
    heading = 'Annotations.js';
    iterable = function(data) {
      return data;
    };
    lines = [];
    slices = [];
    startDate = null;
    template = 'instantiate with new Annotation(el, {iterable, template, heading, startDate, endDate})';
    function Annotation(el, params) {
      var _ref;
      this.el = el;
      this.params = params;
      _ref = this.params, this.iterable = _ref.iterable, this.template = _ref.template, this.heading = _ref.heading, this.startDate = _ref.startDate, this.endDate = _ref.endDate, this.linkTo = _ref.linkTo;
      if (!this.template) {
        this.template = this.heading;
        this.heading = null;
      }
      this.el = $(this.el);
      this.el.data('annotation', this);
      this.el.wrap('<a class="annotation-wrap" target="_top" href="#"></a>');
      if (this.linkTo) {
        this.el.parent().attr('href', this.linkTo);
      }
      this.el.parent().css('position', 'relative');
      this.annotationEl = $('<div class="annotation"><div class="inner-annotation"></div></div>').css('position', 'absolute').css('top', '50%').hide();
      this.el.after(this.annotationEl);
      this.refresh();
    }
    Annotation.prototype.applyTemplate = function(idx) {
      var dataset, html, i, varP, _ref;
      varP = /\$\{([^\}]+?)\}/gi;
      html = '';
      if (this.heading) {
        html += this.heading.replace(varP, __bind(function(match, varName) {
          var part, parts, value, _i, _len;
          try {
            value = this.datasets[0][idx];
          } catch (e) {
            return this.refresh();
          }
          parts = varName.split('.');
          for (_i = 0, _len = parts.length; _i < _len; _i++) {
            part = parts[_i];
            value = value[part];
          }
          return value.toString() || '';
        }, this));
      }
      _ref = this.datasets;
      for (i in _ref) {
        dataset = _ref[i];
        html += this.template.replace(varP, function(match, varName) {
          var part, parts, value, _i, _len;
          try {
            value = dataset[idx];
          } catch (e) {
            this.refresh();
          }
          parts = varName.split('.');
          for (_i = 0, _len = parts.length; _i < _len; _i++) {
            part = parts[_i];
            value = value[part];
          }
          if (varName === 'i') {
            return i;
          }
          if (typeof value === 'number' && (parseInt(value) !== value)) {
            value = value.toFixed(4);
          }
          return value.toString() || '';
        });
      }
      return html;
    };
    Annotation.prototype.bindMouse = function() {
      this.el.parent().bind('mouseenter.annotation', __bind(function(evt) {
        return this.annotationEl.show();
      }, this));
      this.el.parent().bind('mouseleave.annotation', __bind(function(evt) {
        return this.annotationEl.hide();
      }, this));
      return this.el.bind('mousemove.annotation', __bind(function(evt) {
        var date, month, step, x, year;
        x = evt.layerX || evt.offsetX;
        coords = this.point(evt);
        if (isNaN(coords[0])) {
          return this.annotationEl.hide();
        } else {
          step = this.step(x) + this.startOffset();
          this.annotationEl.show().stop().animate({
            'left': coords[0],
            'top': coords[1]
          }, 10).children('.inner-annotation').html(this.applyTemplate(step));
          date = this.datasets[0][step].month;
          year = date.slice(0, 4);
          month = date.slice(4, 6);
          if (!this.linkTo) {
            return this.el.parent().attr('href', "/date/" + year + "/" + month);
          }
        }
      }, this));
    };
    Annotation.prototype.destroy = function() {
      this.annotationEl.hide();
      this.el.unbind('.annotation');
      this.coordsurl = null;
      this.coords = [];
      this.dataurls = [];
      this.datasets = [];
      this.lines = [];
      this.slices = [];
      this._months = null;
      this._total = null;
      if (!(this.params['startDate'] || this.params['endDate'])) {
        this.startDate = null;
        return this.endDate = null;
      }
    };
    Annotation.prototype.getDataUrl = function(idx, url) {
      var dfd;
      dfd = $.Deferred();
      $.when(this.getJSONPVar(url)).done(__bind(function(data) {
        this.datasets[idx] = this.iterable(data);
        return dfd.resolve();
      }, this));
      return dfd.promise();
    };
    Annotation.prototype.getJSONPVar = function(url) {
      return $.ajax({
        url: url,
        dataType: 'jsonp',
        data: {
          'apikey': window.cwod_apikey
        }
      });
    };
    Annotation.prototype.loadCoords = function() {
      var dfd;
      dfd = $.Deferred();
      $.when(this.getJSONPVar(this.coordsurl)).done(__bind(function(coords) {
        var flat, i, line, matches, obj, val, x, y, _i, _len, _ref;
        _ref = coords.chartshape;
        for (_i = 0, _len = _ref.length; _i < _len; _i++) {
          obj = _ref[_i];
          matches = obj.name.match(/line(\d+?)/);
          if (matches) {
            line = matches[1];
            this.coords[line] = [];
            flat = obj.coords.slice(0, obj.coords.length / 2);
            for (i in flat) {
              val = flat[i];
              if (i % 2) {
                x = flat[i - 1];
                y = flat[i];
                this.coords[line].push([x, y]);
              }
            }
          }
        }
        return dfd.resolve();
      }, this));
      return dfd.promise();
    };
    Annotation.prototype.loadData = function() {
      var dfd, idx, reqs, url;
      dfd = $.Deferred();
      reqs = [
        (function() {
          var _ref, _results;
          _ref = this.dataurls;
          _results = [];
          for (idx in _ref) {
            url = _ref[idx];
            _results.push(this.getDataUrl(idx, url));
          }
          return _results;
        }).call(this)
      ];
      $.when.apply($, reqs).done(function() {
        return dfd.resolve();
      });
      return dfd.promise();
    };
    Annotation.prototype.point = function(evt) {
      var coordset, overlap, pair, step, x, y, ys;
      x = evt.layerX || evt.offsetX;
      step = this.step(x);
      pair = [NaN, NaN];
      if ((0 <= step && step < this.coords[0].length)) {
        ys = [
          (function() {
            var _i, _len, _ref, _results;
            _ref = this.coords;
            _results = [];
            for (_i = 0, _len = _ref.length; _i < _len; _i++) {
              coordset = _ref[_i];
              _results.push(coordset[step].slice()[1]);
            }
            return _results;
          }).call(this)
        ][0];
        y = _.min(ys);
        x = this.coords[0][step][0];
        pair = [x, y];
        if (pair[0] + this.annotationEl.outerWidth() > this.el.width()) {
          pair[0] -= this.annotationEl.outerWidth();
          this.annotationEl.addClass('flipped');
        } else {
          this.annotationEl.removeClass('flipped');
        }
        if ((overlap = pair[1] - this.annotationEl.height() / 2) < 0) {
          pair[1] += overlap * -1;
        } else if ((overlap = pair[1] + this.annotationEl.height() / 2) > this.el.height()) {
          pair[1] -= overlap - this.el.height();
        }
      }
      return pair;
    };
    Annotation.prototype.refresh = function() {
      var d, i, qparams, qs, url;
      this.destroy();
      if (!this.startDate && !this.endDate) {
        qs = window.location.href.split('?')[1];
        qparams = $.deparam(qs);
        try {
          this.startDate = qparams['start'];
        } catch (_e) {}
        try {
          this.endDate = qparams['end'];
        } catch (_e) {}
        if (!this.startDate) {
          this.startDate = '199601';
        }
        if (!this.endDate) {
          d = new Date();
          this.endDate = "" + (d.getFullYear()) + "12";
        }
      }
      if ((url = this.el.attr('data-dataurl'))) {
        this.dataurls.push(url);
      } else {
        i = 0;
        while ((url = this.el.attr("data-dataurl" + i))) {
          this.dataurls.push(url);
          i += 1;
        }
      }
      this.coordsurl = "" + (this.el.attr('src')) + "&chof=json";
      return $.when(this.loadCoords(), this.loadData()).done(__bind(function() {
        return this.bindMouse();
      }, this));
    };
    Annotation.prototype.step = function(x) {
      var max, min, range, stepsize;
      this._total || (this._total = this.coords[0].length);
      min = this.coords[0][0][0];
      max = this.coords[0][this._total - 1][0];
      range = max - min;
      stepsize = range / this._total;
      return Math.floor((x - min) / stepsize);
    };
    Annotation.prototype.startOffset = function() {
      var offset;
      this._months || (this._months = _.pluck(this.datasets[0], 'month'));
      offset = _.indexOf(this._months, this.startDate, true);
      if (offset === -1) {
        offset = 0;
      }
      return offset;
    };
    return Annotation;
  })();
}).call(this);
