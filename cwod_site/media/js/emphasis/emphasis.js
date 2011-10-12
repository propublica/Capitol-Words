
var Emphasis = {
    init: function() {
        this.config();

        this.pl = false; // Paragraph List
        this.p  = false; // Paragraph Anchor
        this.h  = false; // Highlighted paragraphs
        this.s  = false; // Highlighted sentences
        this.vu = false; // Are paragraph links visible or not
        this.kh = "|";

        this.addCSS();
        this.readHash();

		jQuery(document).keydown(function(ev) {
		  Emphasis.keydown(ev);
		});
    },

    config: function() {
    /*
        Eligible Paragraphs
        This uses some common markup for plain and simpel paragraphs - those that are not empty, no classes.
        We use PrototypeJS for its css selector awesomeness, but your needs might be simpler (getElementsByTagName('p') etc.)
    */	
		this.running           = true;
        this.paraSelctors      = jQuery("p");

    //  Class names
        this.classReady        = "emReady";
        this.classActive       = "emActive";
        this.classHighlight    = "emHighlight";
        this.classInfo         = "emInfo";
        this.classAnchor       = "emAnchor";
        this.classActiveAnchor = "emActiveAnchor";
    },

	goOverlay: function(keys, h) {
		jQuery("p.emReady").addClass("emPop");
		jQuery(document.body).append("<div id='emOverlay'></div>");
		
		jQuery('#emOverlay').click(function() {
		  jQuery('#emOverlay').fadeOut("fast",function() {
			    jQuery(this).remove();
          });
		});
	},

    addCSS: function() {
    /*  Inject the minimum styles rules required */
        var st = document.createElement('style');
        jQuery(st).html('p.' + this.classActive + ' span { background-color:#f2f4f5; } p span.' + this.classHighlight + ' { background-color:#fff0b3; } span.' + this.classInfo + ' { position:absolute; margin:-1px 0px 0px -8px; padding:0; font-size:10px; background-color: transparent !important} span.' + this.classInfo + ' a { text-decoration: none; } a.' + this.classAnchor + ' { color: darkBlue; font-family: Helvetica, Arial; font-size: 10px; } a.' + this.classActiveAnchor + ' { color: #000; font-size: 11px; }');
        document.getElementsByTagName("head")[0].appendChild(st);
    },

    readHash: function() {
    /*  Read and interpret the URL hash */
        var lh = decodeURI(location.hash);
        var p  = false, h = [], s = {}, k = [];

        if (lh.indexOf('[')<0 && lh.indexOf(']')<0) {
        /*  Version 1 Legacy support
            #p20h4s2,6,10,h6s5,1 -> p = 20, h = [ 4, 6 ], s = { "4": [ 2, 6, 10 ] , "6": [ 5, 1 ] }
        */
            var a, re = /[ph][0-9]+|s[0-9,]+|[0-9]/g;
            if (lh) {
                while ((a = re.exec(lh)) !== null) {
                    var f = a[0].substring(0, 1);
                    var r = a[0].substring(1);
                    if (f == 'p') {
                        p = parseInt(r);
                    } else if (f == 'h') {
                        h.push(parseInt(r));
                    } else {
                        a = r.split(',');
                        for (var i = 0; i < a.length; i++) {
                            a[i] = parseInt(a[i]);
                        }
                        s[h[h.length - 1]] = a;
                    }
                }
            }
        } else {
        /*  Version 2
            #h[tbsaoa,Sstaoo,2,4],p[FWaadw] -> p = "FWaadw", h = [ "tbsaoa", "Sstaoo" ], s = { "Sstaoo" : [ 2, 4 ] }
        */
            var findp = lh.match(/p\[([^[\]]*)\]/);
            var findh = lh.match(/h\[([^[\]]*)\]/);
            var undef, hi;

            p  = (findp && findp.length>0) ? findp[1] : false;
            hi = (findh && findh.length>0) ? findh[1] : false;

            if (hi) {

                hi = hi.match(/[a-zA-Z]+(,[0-9]+)*/g);
    
            	for (var i = 0; i < hi.length; i++) {
	
                    var a   = hi[i].split(',');
                    var key = a[0];

                    var pos = this.findKey(key)['index'];

                    if (pos!=undef) {
                        h.push(parseInt(pos)+1);
	                    k.push(key);

                        var b = a;
                        b.shift();

                        if (b.length>0) {
                            for (var j=1; j<b.length; j++) {
                                b[j] = parseInt(b[j]);
                            }
                        }
                        s[h[h.length - 1]] = b;
                    }
                }
            }
        }

        this.p = p; this.h = h; this.s = s;

        this.goAnchor(p);
        this.goHighlight(h, s);

		if (lh.indexOf('context')>0) {
        	this.goOverlay(k, h);
		}
    },

    keydown: function(e){
    /*  Look for double-shift keypress */
        var self = Emphasis;
        var kc   = e.keyCode;
        self.kh  = self.kh + kc + '|';
        if (self.kh.indexOf('|16|16|')>-1) {
            self.vu = (self.vu) ? false : true;
            self.paragraphInfo(self.vu);
        }
        setTimeout(function(){ self.kh = '|'; }, 500);
    },

    paragraphList: function() {
    /*  Build a list of Paragrphs, keys, and add meta-data to each Paragraph in DOM, saves list for later re-use */
        if (this.pl) return this.pl;
        var instance = this;
        var list = [];
        var keys = [];
        var c    = 0;
        var len  = this.paraSelctors.length;

        for (var p=0; p<len; p++) {
            var pr = this.paraSelctors[p];
            if ((pr.innerText || pr.textContent || "").length>0) {
                var k = instance.createKey(pr);
                list.push(pr);
                keys.push(k);
                pr.setAttribute("data-key", k); // Unique Key
                pr.setAttribute("data-num", c); // Order

				jQuery(pr).click(function(e) {
					instance.paragraphClick(e);
				});

                c++;
            }
        }

        this.pl = { list: list, keys: keys };
        return this.pl;
    },

    paragraphClick: function(e) {
    /*  Clicking a Paragrsph has consequences for Highlighting, selecting and changing active Anchor */

        if (!this.vu) { return; }

        var hasChanged = false;
        var pr = (e.currentTarget.nodeName=="P") ? e.currentTarget : false; // Paragraph
        var sp = (e.target.nodeName=="SPAN")     ? e.target        : false; // Span
        var an = (e.target.nodeName=="A")        ? e.target        : false; // Anchor

        if (an) {
        /*  Click an Anchor link */
            if (!jQuery(an).hasClass(this.classActiveAnchor)) {
                this.updateAnchor(an);
                hasChanged = true;
                e.preventDefault();
            }
        }

        if (!pr && !sp) {
            this.removeAllClasses("p", this.classActive);
            return;
        }

        if (jQuery(pr).hasClass(this.classReady)) {
            if (!jQuery(pr).hasClass(this.classActive) && (sp && !jQuery(sp).hasClass(this.classHighlight))) {
            //  If not current Active p tag, clear any others out there and make this the Active p tag
                this.removeAllClasses("p", this.classActive);
                jQuery(pr).addClass(this.classActive); // Mark as Active
            } else {
                if (!jQuery(pr).hasClass(this.classActive)) {
                    this.removeAllClasses("p", this.classActive);
                    jQuery(pr).addClass(this.classActive); // Mark as Active
                }

                if (sp) {
                    jQuery(sp).toggleClass(this.classHighlight);
                    hasChanged = true;
                }
            }
        } else {
        //  Add span tags to all Sentences within Paragraph and mark Paragraph as Ready
            var lines = this.getSentences(pr);
            var jLen  = lines.length;

            for (var j=0; j<jLen; j++) {
                lines[j] = "<span data-num='" + (j+1) + "'>" + this.rtrim(lines[j]) + "</span>";
            }

            var txt = lines.join('. ').replace(/__DOT__/g, ".").replace(/<\/span>\./g, ".<\/span>");
            var chr = txt.substring(txt.length-8).charCodeAt(0);
            if ("|8221|63|46|41|39|37|34|33|".indexOf(chr)==-1) { txt += "."; }

            jQuery(pr).html(txt);
            pr.setAttribute('data-sentences', jLen);

            this.removeAllClasses("p", this.classActive);
            jQuery(pr).addClass(this.classActive); // Mark as Active
            jQuery(pr).addClass(this.classReady);  // Mark as Ready
            hasChanged = true;
        }

        if (hasChanged) {
            this.updateURLHash();
        }
    },

    paragraphInfo: function(mode) {
    /*  Toggle anchor links next to Paragraphs */

        if (mode) {
            var hasSpan = (jQuery('span.' + this.classInfo)[0]) ? true : false;

            if (!hasSpan) {
                var pl  = this.paragraphList();
                var len = pl.list.length;
                for (var i=0; i<len; i++) {
                    var para = pl.list[i] || false;
                    if (para) {
                        var key        = pl.keys[i];
                        var isActive   = (key==this.p) ? (" " + this.classActiveAnchor) : "";
                        jQuery(para).html("<span class='" + this.classInfo + "'><a class='"+ this.classAnchor + isActive + "' href='#p[" + key + "]' data-key='" + key + "' title='Link to " + this.ordinal(i+1) + " paragraph'>&para;</a></span>" + jQuery(para).html());
                    }
                }
            }
        } else {
            var spans = jQuery('span.' + this.classInfo);
            var len = spans.length;
            for (var i=0; i<len; i++) {
                jQuery(spans[i]).remove();
            }
            this.removeAllClasses(this.classActive);
        }
    },

    updateAnchor: function(an) {
    /*  Make this A tag the one and only Anchor */
        this.p = jQuery(an).attr("data-key");
        this.removeAllClasses("a", this.classActiveAnchor);
        jQuery(an).addClass(this.classActiveAnchor);
    },

    updateURLHash: function() {
    /*  Scan the Paragraphs, note selections, highlights and update the URL with the new Hash */
        var h     = "h[";
        var paras = jQuery('p.emReady');
        var pLen  = paras.length;

        for (var p=0; p<pLen; p++) {
            var key = jQuery(paras[p]).attr("data-key");
            if (jQuery(paras[p]).hasClass(this.classHighlight)) {
                h += "," + key; // Highlight full paragraph
            } else {
                var spans = jQuery(paras[p]).find('span.' + this.classHighlight);
                var sLen  = spans.length;
                var nSent = jQuery(paras[p]).attr("data-sentences");

                if (sLen>0) { h += "," + key; }

                if (nSent!=sLen) {
                    for (var s=0; s<sLen; s++) {
                        h += "," + jQuery(spans[s]).attr("data-num");
                    }
                }
            }
        }

        var anchor    = ((this.p) ? "p[" + this.p + "]," : "");
        var hash      = (anchor + (h.replace("h[,", "h[") + "]")).replace(",h[]", "");
        location.hash = hash;
    },

    createKey: function(p) {
    /*  From a Paragraph, generate a Key */
        var key = "";
        var len = 6;
        var txt = (p.innerText || p.textContent || '').replace(/[^a-z\. ]+/gi, '');
        if (txt && txt.length>1) {

            var lines = this.getSentences(txt);
            if (lines.length>0) {
                var first = this.cleanArray(lines[0].replace(/[\s\s]+/gi, ' ').split(' ')).slice(0, (len/2));
                var last  = this.cleanArray(lines[lines.length-1].replace(/[\s\s]+/gi, ' ').split(' ')).slice(0, (len/2));
                var k     = first.concat(last);

                var max = (k.length>len) ? len : k.length;
                for (var i=0; i<max; i++) {
                    key += k[i].substring(0, 1);
                }
            }
        }
        return key;
    },

    findKey: function(key) {
    /*  From a list of Keys, locate the Key and corresponding Paragraph */
        var pl = this.paragraphList();
        var ln = pl.keys.length;
        var ix = false;
        var el = false;

        for (var i=0;i<ln;i++) {
            if (key==pl.keys[i]) { // Direct Match
                return { index: i, elm: pl.list[i] };
            } else { // Look for 1st closest Match
                if (!ix) {
                    var ls = this.lev(key.slice(0, 3), pl.keys[i].slice(0, 3));
                    var le = this.lev(key.slice(-3)  , pl.keys[i].slice(-3));
                    if ((ls+le)<3) {
                        ix = i;
                        el = pl.list[i];
                    }
                }
            }
        }
        return { index: ix, elm: el };
    },

    goAnchor: function(p) {
    /*  Move view to top of a given Paragraph */
        if (!p) return;
        var pg = (isNaN(p)) ? this.findKey(p)['elm'] : (this.paragraphList().list[p-1] || false);
        var instance = this;
        if (pg) {
            setTimeout(function(){

                //pg.scrollTo();
				jQuery(pg).animate({scrollTop:0}, 'slow');

            }, 500);
        }
    },

    goHighlight: function(h, s) {
    /*  Highlight a Paragraph, or specific Sentences within it */
        if (!h) return;
        var hLen = h.length;

        for (var i=0; i<hLen; i++) {
            var para = this.paragraphList().list[h[i]-1] || false;
            if (para) {
                var sntns = s[h[i].toString()] || false;
                var multi = !sntns || sntns.length==0; // Individual sentences, or whole paragraphy?
                var lines = this.getSentences(para);
                var jLen  = lines.length;

            /*  First pass. Add SPAN tags to all lines. */
                for (var j=0; j<jLen; j++) {
                    var k = (multi) ? j : sntns[j]-1;
                    lines[j] = "<span data-num='" + (j+1) + "'>" + lines[j] + "</span>";
                }

            /*  Second pass, update span to Highlight selected lines */
                for (var j=0; j<jLen; j++) {
                    var k    = (multi) ? j : sntns[j]-1;
                    var line = lines[k] || false;
                    if (line) {
                        lines[k] = lines[k].replace("<span", "<span class='" + this.classHighlight + "'");
                    }
                }

                para.setAttribute("data-sentences", jLen);
                jQuery(para).html(lines.join('. ').replace(/__DOT__/g, ".").replace(/<\/span>\./g, ".<\/span>"));
                jQuery(para).addClass('emReady'); /* Mark the paragraph as having SPANs */
            }
        }
    },

    getSentences: function(el) {
    /*  Break a Paragraph into Sentences, bearing in mind that the "." is not the definitive way to do so */
        var html    = (typeof el=="string") ? el : el.innerHTML;
        var mrsList = "Mr,Ms,Mrs,Miss,Msr,Dr,Gov,Pres,Sen,Prof,Gen,Rep,St,Messrs,Col,Sr,Jf,Ph,Sgt,Mgr,Fr,Rev,No,Jr,Snr";
        var topList = "A,B,C,D,E,F,G,H,I,J,K,L,M,m,N,O,P,Q,R,S,T,U,V,W,X,Y,Z,etc,oz,cf,viz,sc,ca,Ave,St";
        var geoList = "Calif,Mass,Penn,AK,AL,AR,AS,AZ,CA,CO,CT,DC,DE,FL,FM,GA,GU,HI,IA,ID,IL,IN,KS,KY,LA,MA,MD,ME,MH,MI,MN,MO,MP,MS,MT,NC,ND,NE,NH,NJ,NM,NV,NY,OH,OK,OR,PA,PR,PW,RI,SC,SD,TN,TX,UT,VA,VI,VT,WA,WI,WV,WY,AE,AA,AP,NYC,GB,IRL,IE,UK,GB,FR";
        var numList = "0,1,2,3,4,5,6,7,8,9";
        var webList = "aero,asia,biz,cat,com,coop,edu,gov,info,int,jobs,mil,mobi,museum,name,net,org,pro,tel,travel,xxx";
        var extList = "www";
        var d       = "__DOT__";

        var list = (topList+","+geoList+","+numList+","+extList).split(",");
        var len  = list.length;
        for (var i=0;i<len;i++) {
            html = html.replace(new RegExp((" "+list[i]+"\\."), "g"), (" "+list[i]+d));
        }

        list = (mrsList+","+numList).split(",");
        len  = list.length;
        for (var i=0;i<len;i++) {
            html = html.replace(new RegExp((list[i]+"\\."), "g"), (list[i]+d));
        }

        list = (webList).split(",");
        len  = list.length;
        for (var i=0;i<len;i++) {
            html = html.replace(new RegExp(("\\."+list[i]), "g"), (d+list[i]));
        }

        var lines = this.cleanArray(html.split('. '));
        return lines;
    },

    ordinal: function(n) {
        var sfx = ["th","st","nd","rd"], val = n%100;
        return n + (sfx[(val-20)%10] || sfx[val] || sfx[0]);
    },

    lev: function(a, b) {
    /*  Get the Levenshtein distance - a measure of difference between two sequences */
        var m = a.length;
        var n = b.length;
        var r = []; r[0] = [];
        if (m < n) { var c = a; a = b; b = c; var o = m; m = n; n = o; }
        for (var c = 0; c < n+1; c++) { r[0][c] = c; }
        for (var i = 1; i < m+1; i++) {
            r[i] = [];
            r[i][0] = i;
            for (var j=1; j<n+1; j++) {
                r[i][j] = this.smallest(r[i-1][j]+1, r[i][j-1]+1, r[i-1][j-1]+((a.charAt(i-1)==b.charAt(j-1))? 0 : 1));
            }
        }
        return r[m][n];
    },

    smallest: function(x,y,z) {
    /*  Return smallest of two values */
        if (x < y && x < z) return x;
        if (y < x && y < z) return y;
        return z;
    },

    rtrim: function(txt) {
    /*  Trim whitespace from right of string */
        return txt.replace(/\s+$/, "");
    },

    cleanArray: function(a){
    /*  Remove empty items from an array */
        var n = [];
        for (var i = 0; i<a.length; i++){
            if (a[i] && a[i].replace(/ /g,'').length>0){ n.push(a[i]); }
        }
        return n;
    },

    removeAllClasses: function(tag, klass) {
    /*  Remove classes */
        if (!klass || !tag) return;
        var els = jQuery((tag + "." + klass));
        for (var i=0; i<els.length; i++){
            jQuery(els[i]).removeClass(klass);
        }
    }
};
