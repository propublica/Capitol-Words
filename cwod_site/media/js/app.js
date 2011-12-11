(function() {
  var $, History, cw;
  $ = jQuery;
  /*
  Create a global CW instance within this closure
  */
  cw = new window.CapitolWords;
  window.cw = cw;
  History = window.History;
  /*
  Add csrf token to ajax POSTs
  */
  $(document).ajaxSend(function(event, xhr, settings) {
    if ((settings.type === 'POST') && cw.sameOrigin(settings.url)) {
      return xhr.setRequestHeader("X-CSRFToken", cw.getCookie('csrftoken'));
    }
  });
  /*
  Handle special routes
  */
  History.Adapter.bind(window, 'statechange', function() {
    if (window.location.pathname.match(/^\/legislator\/?$/)) {
      return cw.readLegislatorHistory();
    } else if (window.location.pathname.match(/^\/term\/.+\/?$/)) {
      cw.readTermDetailPageHistory();
      return cw.populateTermDetailPage(termDetailTerm);
    } else if (window.location.pathname.match(/^\/?$/)) {
      return cw.readHomepageHistory();
    }
  });
  $(window).trigger('statechange');
  /*
  DomReady Handler
  */
  $(document).ready(function() {
    var area, d, endYear, startYear;
    if (typeof termDetailTerm !== 'undefined') {
      cw.readTermDetailPageHistory();
      cw.populateTermDetailPage(termDetailTerm);
    }
    $('img').error(function() {
      return $(this).attr('src', 'http://assets.sunlightfoundation.com/capitol-words/media/img/cwod_default.png');
    });
    $('#toggleSearchCompare').click(function(e) {
      e.preventDefault();
      return $('.toggleSearchCompare').slideToggle('fast', 'swing');
    });
    $('#compareTermBtn').live('click', function(e) {
      var word;
      e.preventDefault();
      word = $(this).find('em').text();
      $('#terma').val(word);
      return $('#toggleSearchCompare').trigger('click');
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
          return obj.show().imagesLoaded(function() {
            return $(this).find('img').load();
          });
        } else {
          return obj.hide();
        }
      });
    });
    $('#partySelect, #stateSelect').change(function() {
      return cw.customizeChart();
    });
    $('.compareSubmit').bind('click', function(e) {
      if (window.location.pathname.match(/^\/?$/)) {
        e.preventDefault();
        return cw.submitHomepageCompareForm();
      } else {
        return true;
      }
    });
    $('#termSelect input').bind('keyup', function(e) {
      if (e.keyCode === 13) {
        return $('.compareSubmit').trigger('click');
      }
    });
    $('#termSelect input[type=text]').bind('focus', function() {
      if ($(this).val() === 'Word or phrase') {
        return $(this).val('');
      }
    });
    $('#termSelect input[type=text]').bind('blur', function() {
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
      return $('ul.wordFilter').slideToggle('fast', 'swing', function() {
        if ($(this).is(':visible')) {
          return t.addClass('expanded');
        } else {
          return t.removeClass('expanded');
        }
      });
    });
    $('#embed a').bind('click', function(e) {
      var t;
      e.preventDefault();
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
    $('#compareGraphic img#compareTimeline, #overallTimeline img, #partyTimeline img').live('load.capitolwords', function() {
      var existingAnnotation, heading, iterable, template;
      existingAnnotation = $(this).data('annotation');
      if (existingAnnotation) {
        return existingAnnotation.refresh();
      } else {
        heading = '<p class="meta">${verboseMonth}</p>';
        template = '<p class="data"><span class="color-${i}"></span> ${count} ${noun} (${percentage}%)</p>';
        iterable = function(data) {
          data = data.results;
          $.each(data, function(i, obj) {
            var m, mos, o, y;
            o = obj.month;
            y = o.substr(0, 4);
            m = parseInt(o.substr(4, 2), 10);
            mos = ['', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
            data[i].verboseMonth = "" + mos[m] + " " + y;
            return obj.noun = obj.count === 1 ? 'mention' : 'mentions';
          });
          return data;
        };
        return new Annotation(this, {
          iterable: iterable,
          heading: heading,
          template: template
        });
      }
    });
    $('#compareGraphic img#compareTimeline, #overallTimeline img, #partyTimeline img').each(function() {
      if (!$(this).parent().hasClass('annotation-wrap')) {
        return $(this).trigger('load.capitolwords');
      }
    });
    (area = $('#rtColumn, .crContent')) && area.length && area.imagesLoaded(function() {
      return $(this).find('img').load();
    });
    if ((window.location.pathname.match(/(^\/?$|homepage\.html)/)) && (!(window.location.href.match(/\?/)))) {
      return cw.submitHomepageCompareForm();
    }
  });
}).call(this);
