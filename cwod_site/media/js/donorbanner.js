/* Modernizr 2.6.3 (Custom Build) | MIT & BSD
 * Build: http://modernizr.com/download/#-csstransforms-csstransforms3d-csstransitions-canvas-canvastext-cssclasses-teststyles-testprop-testallprops-hasevent-prefixes-domprefixes-load
 */
(function($){
    // A Modernizr shim to detect css transform support, global is named DonorBannerModernizr
    window.DonorBannerModernizr=function(a,b,c){function A(a){j.cssText=a}function B(a,b){return A(m.join(a+";")+(b||""))}function C(a,b){return typeof a===b}function D(a,b){return!!~(""+a).indexOf(b)}function E(a,b){for(var d in a){var e=a[d];if(!D(e,"-")&&j[e]!==c)return b=="pfx"?e:!0}return!1}function F(a,b,d){for(var e in a){var f=b[a[e]];if(f!==c)return d===!1?a[e]:C(f,"function")?f.bind(d||b):f}return!1}function G(a,b,c){var d=a.charAt(0).toUpperCase()+a.slice(1),e=(a+" "+o.join(d+" ")+d).split(" ");return C(b,"string")||C(b,"undefined")?E(e,b):(e=(a+" "+p.join(d+" ")+d).split(" "),F(e,b,c))}var d="2.6.3",e={},f=!0,g=b.documentElement,h="modernizr",i=b.createElement(h),j=i.style,k,l={}.toString,m=" -webkit- -moz- -o- -ms- ".split(" "),n="Webkit Moz O ms",o=n.split(" "),p=n.toLowerCase().split(" "),q={},r={},s={},t=[],u=t.slice,v,w=function(a,c,d,e){var f,i,j,k,l=b.createElement("div"),m=b.body,n=m||b.createElement("body");if(parseInt(d,10))while(d--)j=b.createElement("div"),j.id=e?e[d]:h+(d+1),l.appendChild(j);return f=["&#173;",'<style id="s',h,'">',a,"</style>"].join(""),l.id=h,(m?l:n).innerHTML+=f,n.appendChild(l),m||(n.style.background="",n.style.overflow="hidden",k=g.style.overflow,g.style.overflow="hidden",g.appendChild(n)),i=c(l,a),m?l.parentNode.removeChild(l):(n.parentNode.removeChild(n),g.style.overflow=k),!!i},x=function(){function d(d,e){e=e||b.createElement(a[d]||"div"),d="on"+d;var f=d in e;return f||(e.setAttribute||(e=b.createElement("div")),e.setAttribute&&e.removeAttribute&&(e.setAttribute(d,""),f=C(e[d],"function"),C(e[d],"undefined")||(e[d]=c),e.removeAttribute(d))),e=null,f}var a={select:"input",change:"input",submit:"form",reset:"form",error:"img",load:"img",abort:"img"};return d}(),y={}.hasOwnProperty,z;!C(y,"undefined")&&!C(y.call,"undefined")?z=function(a,b){return y.call(a,b)}:z=function(a,b){return b in a&&C(a.constructor.prototype[b],"undefined")},Function.prototype.bind||(Function.prototype.bind=function(b){var c=this;if(typeof c!="function")throw new TypeError;var d=u.call(arguments,1),e=function(){if(this instanceof e){var a=function(){};a.prototype=c.prototype;var f=new a,g=c.apply(f,d.concat(u.call(arguments)));return Object(g)===g?g:f}return c.apply(b,d.concat(u.call(arguments)))};return e}),q.canvas=function(){var a=b.createElement("canvas");return!!a.getContext&&!!a.getContext("2d")},q.canvastext=function(){return!!e.canvas&&!!C(b.createElement("canvas").getContext("2d").fillText,"function")},q.csstransforms=function(){return!!G("transform")},q.csstransforms3d=function(){var a=!!G("perspective");return a&&"webkitPerspective"in g.style&&w("@media (transform-3d),(-webkit-transform-3d){#modernizr{left:9px;position:absolute;height:3px;}}",function(b,c){a=b.offsetLeft===9&&b.offsetHeight===3}),a},q.csstransitions=function(){return G("transition")};for(var H in q)z(q,H)&&(v=H.toLowerCase(),e[v]=q[H](),t.push((e[v]?"":"no-")+v));return e.addTest=function(a,b){if(typeof a=="object")for(var d in a)z(a,d)&&e.addTest(d,a[d]);else{a=a.toLowerCase();if(e[a]!==c)return e;b=typeof b=="function"?b():b,typeof f!="undefined"&&f&&(g.className+=" "+(b?"":"no-")+a),e[a]=b}return e},A(""),i=k=null,e._version=d,e._prefixes=m,e._domPrefixes=p,e._cssomPrefixes=o,e.hasEvent=x,e.testProp=function(a){return E([a])},e.testAllProps=G,e.testStyles=w,g.className=g.className.replace(/(^|\s)no-js(\s|$)/,"$1$2")+(f?" js "+t.join(" "):""),e}(this,this.document),function(a,b,c){function d(a){return"[object Function]"==o.call(a)}function e(a){return"string"==typeof a}function f(){}function g(a){return!a||"loaded"==a||"complete"==a||"uninitialized"==a}function h(){var a=p.shift();q=1,a?a.t?m(function(){("c"==a.t?B.injectCss:B.injectJs)(a.s,0,a.a,a.x,a.e,1)},0):(a(),h()):q=0}function i(a,c,d,e,f,i,j){function k(b){if(!o&&g(l.readyState)&&(u.r=o=1,!q&&h(),l.onload=l.onreadystatechange=null,b)){"img"!=a&&m(function(){t.removeChild(l)},50);for(var d in y[c])y[c].hasOwnProperty(d)&&y[c][d].onload()}}var j=j||B.errorTimeout,l=b.createElement(a),o=0,r=0,u={t:d,s:c,e:f,a:i,x:j};1===y[c]&&(r=1,y[c]=[]),"object"==a?l.data=c:(l.src=c,l.type=a),l.width=l.height="0",l.onerror=l.onload=l.onreadystatechange=function(){k.call(this,r)},p.splice(e,0,u),"img"!=a&&(r||2===y[c]?(t.insertBefore(l,s?null:n),m(k,j)):y[c].push(l))}function j(a,b,c,d,f){return q=0,b=b||"j",e(a)?i("c"==b?v:u,a,b,this.i++,c,d,f):(p.splice(this.i++,0,a),1==p.length&&h()),this}function k(){var a=B;return a.loader={load:j,i:0},a}var l=b.documentElement,m=a.setTimeout,n=b.getElementsByTagName("script")[0],o={}.toString,p=[],q=0,r="MozAppearance"in l.style,s=r&&!!b.createRange().compareNode,t=s?l:n.parentNode,l=a.opera&&"[object Opera]"==o.call(a.opera),l=!!b.attachEvent&&!l,u=r?"object":l?"script":"img",v=l?"script":u,w=Array.isArray||function(a){return"[object Array]"==o.call(a)},x=[],y={},z={timeout:function(a,b){return b.length&&(a.timeout=b[0]),a}},A,B;B=function(a){function b(a){var a=a.split("!"),b=x.length,c=a.pop(),d=a.length,c={url:c,origUrl:c,prefixes:a},e,f,g;for(f=0;f<d;f++)g=a[f].split("="),(e=z[g.shift()])&&(c=e(c,g));for(f=0;f<b;f++)c=x[f](c);return c}function g(a,e,f,g,h){var i=b(a),j=i.autoCallback;i.url.split(".").pop().split("?").shift(),i.bypass||(e&&(e=d(e)?e:e[a]||e[g]||e[a.split("/").pop().split("?")[0]]),i.instead?i.instead(a,e,f,g,h):(y[i.url]?i.noexec=!0:y[i.url]=1,f.load(i.url,i.forceCSS||!i.forceJS&&"css"==i.url.split(".").pop().split("?").shift()?"c":c,i.noexec,i.attrs,i.timeout),(d(e)||d(j))&&f.load(function(){k(),e&&e(i.origUrl,h,g),j&&j(i.origUrl,h,g),y[i.url]=2})))}function h(a,b){function c(a,c){if(a){if(e(a))c||(j=function(){var a=[].slice.call(arguments);k.apply(this,a),l()}),g(a,j,b,0,h);else if(Object(a)===a)for(n in m=function(){var b=0,c;for(c in a)a.hasOwnProperty(c)&&b++;return b}(),a)a.hasOwnProperty(n)&&(!c&&!--m&&(d(j)?j=function(){var a=[].slice.call(arguments);k.apply(this,a),l()}:j[n]=function(a){return function(){var b=[].slice.call(arguments);a&&a.apply(this,b),l()}}(k[n])),g(a[n],j,b,n,h))}else!c&&l()}var h=!!a.test,i=a.load||a.both,j=a.callback||f,k=j,l=a.complete||f,m,n;c(h?a.yep:a.nope,!!i),i&&c(i)}var i,j,l=this.yepnope.loader;if(e(a))g(a,0,l,0);else if(w(a))for(i=0;i<a.length;i++)j=a[i],e(j)?g(j,0,l,0):w(j)?B(j):Object(j)===j&&h(j,l);else Object(a)===a&&h(a,l)},B.addPrefix=function(a,b){z[a]=b},B.addFilter=function(a){x.push(a)},B.errorTimeout=1e4,null==b.readyState&&b.addEventListener&&(b.readyState="loading",b.addEventListener("DOMContentLoaded",A=function(){b.removeEventListener("DOMContentLoaded",A,0),b.readyState="complete"},0)),a.yepnope=k(),a.yepnope.executeStack=h,a.yepnope.injectJs=function(a,c,d,e,i,j){var k=b.createElement("script"),l,o,e=e||B.errorTimeout;k.src=a;for(o in d)k.setAttribute(o,d[o]);c=j?h:c||f,k.onreadystatechange=k.onload=function(){!l&&g(k.readyState)&&(l=1,c(),k.onload=k.onreadystatechange=null)},m(function(){l||(l=1,c(1))},e),i?k.onload():n.parentNode.insertBefore(k,n)},a.yepnope.injectCss=function(a,c,d,e,g,i){var e=b.createElement("link"),j,c=i?h:c||f;e.href=a,e.rel="stylesheet",e.type="text/css";for(j in d)e.setAttribute(j,d[j]);g||(n.parentNode.insertBefore(e,n),m(c,0))}}(this,document),DonorBannerModernizr.load=function(){yepnope.apply(window,[].slice.call(arguments,0))};

    var STATE_OPEN = 0,
        STATE_COLLAPSED = 1,
        STATE_DISMISSED = 2;

    var Banner = function(container) {
        var that = this;
        this.$container = $(container);
        this.$toggleButton = $('#donor_banner .toggleButton');
        this.state = null;

        this.$toggleButton.click(function() {
            switch (that.state) {
                case STATE_OPEN:
                    that.collapse();
                    break;
                case STATE_COLLAPSED:
                    that.dismiss();
                    break;
            }
            that.saveState();
        });

        this.loadState();
    };

    Banner.prototype.open = function() {
        this.$container.addClass("revealbanner");
        this.$toggleButton.text("Not now");
        this.state = STATE_OPEN;
    };

    Banner.prototype.collapse = function() {
        this.$container.addClass("revealbanner").addClass("collapsed");
        this.$toggleButton.text("Close");
        this.state = STATE_COLLAPSED;
    };

    Banner.prototype.dismiss = function() {
        this.$container.removeClass("revealbanner").removeClass('collapsed');
        this.state = STATE_DISMISSED;
    };

    Banner.prototype.saveState = function() {
        if (window.localStorage) {
            localStorage.setItem("donorbanner-state", this.state);
        }
    };

    Banner.prototype.loadState = function() {

        var newState = STATE_OPEN;

        if (window.localStorage) {
            var storedState = localStorage.getItem("donorbanner-state");
            if (storedState !== null) {
                newState = parseInt(storedState, 10);
            }
        } else {
            newState = STATE_COLLAPSED;
        }

        if (newState != this.state) {
            if (newState == STATE_OPEN) {
                this.open();
            } else if (newState == STATE_COLLAPSED) {
                this.collapse();
            } else if (newState == STATE_DISMISSED) {
                this.dismiss();
            }
            this.state = newState;
        }
    };

    Banner.ab = [
        // A
        {
            quote: false,
            bottom: -288,
            html: "Sunlight Foundation is a nonpartisan nonprofit organization. We depend on the generosity of our supporters to continue our work. Help us double down on our efforts to ensure government is open and accountable.",
            urls: {
                sf: "ES4WiEhrlKe%2f9j9OGXCNodMmdQoOrgASmlaFEr0uTpcxt4jU6Ma%2fOg%3d%3d",
                ie: "ES4WiEhrlKe%2f9j9OGXCNof38UsvW3kOnbcu2kq1k1UeLBWZdw6EaWA%3d%3d",
                staffers: "ES4WiEhrlKe%2f9j9OGXCNocVXIAgloWOqMcGt2LJ9uXxkhzVDuIABvw%3d%3d",
                capitol_words: "ES4WiEhrlKe%2f9j9OGXCNoYdS88QuItcf17fGeXpa37S7Di3iCqLaYg%3d%3d",
                politwoops: "ES4WiEhrlKe%2f9j9OGXCNoS2csdmdnrp6ArrSuDBxiiGrXWloo%2f6mYg%3d%3d",
                party_time: "ES4WiEhrlKe%2f9j9OGXCNof3kv6PXngP719vXVDasLnJY0lK5P8asNw%3d%3d",
                open_states: "ES4WiEhrlKe%2f9j9OGXCNoQTfY0m6GK4WTCd2rvv9qknPXVVWd0UFjg%3d%3d",
                docket_wrench: "ES4WiEhrlKe%2f9j9OGXCNocEdR3dwL1upGgHfXQRbt9LmOK1ZAy5TLQ%3d%3d"
            }
        },

        // B
        {
            quote: false,
            bottom: -288,
            html: "Sunlight Foundation is a nonpartisan nonprofit organization. It is thanks to your support that we can continue fighting for government transparency. Help us double down on our efforts to ensure government is open and accountable.",
            urls: {
                sf: "ES4WiEhrlKfWo%2fvH%2fdIKWxB1hxm18rj5KzPHUHQTCHIEnapdW%2f%2bfVQ%3d%3d",
                ie: "ES4WiEhrlKfWo%2fvH%2fdIKW03%2ficCkzziGX17Nb%2bDL2Et%2bVwWe0BEE9Q%3d%3d",
                staffers: "ES4WiEhrlKfWo%2fvH%2fdIKW4jbEN7%2b5xv6tCxzC%2bmE3doYWyLeNC40%2bQ%3d%3d",
                capitol_words: "ES4WiEhrlKfWo%2fvH%2fdIKWw9RcnDLfIQbjAO9PDgwWADTV9J5xtIj1Q%3d%3d",
                politwoops: "ES4WiEhrlKfWo%2fvH%2fdIKW8IFqxBfKqm9GkNCN1D13AsTDn9PAUa2Kw%3d%3d",
                party_time: "ES4WiEhrlKfWo%2fvH%2fdIKW0O84xzsQPdmcP8hjdpP7IDAsQ2q3V7Ltg%3d%3d",
                open_states: "ES4WiEhrlKfWo%2fvH%2fdIKWyy6Yu%2byDsWdjsZJPa9Fk3QaXrlBwDm7ZA%3d%3d",
                docket_wrench: "ES4WiEhrlKfWo%2fvH%2fdIKW%2b8xRMAClZzl3aiELyIMCPPzyV%2bzP2kBog%3d%3d"
            }
        },

        // C
        {
            quote: false,
            bottom: -288,
            html: "Sunlight produces dozens of tools to help you connect with government, track political influence and even power websites of your own. Now, we need your help to continue maintaining and improving our open gov tools.",
            urls: {
                sf: "ES4WiEhrlKcv4AqxZW817QuA4EJ8PHJ8%2bcFMCJwI9loDVHGkAfz0mA%3d%3d",
                ie: "ES4WiEhrlKcv4AqxZW817YbJy89J%2f7f8FRD9fGb8QkhqVujAm5sTNw%3d%3d",
                staffers: "ES4WiEhrlKcv4AqxZW817XjU371Zwwsxbf6ns9U2qHYkNhBu7zx07w%3d%3d",
                capitol_words: "ES4WiEhrlKcv4AqxZW817ZaUlO5GHlq%2fEPYSiXjKmaJNJ%2bNi9zqf%2bg%3d%3d",
                politwoops: "ES4WiEhrlKcv4AqxZW817UHg3k7XGFtmIedcydnzas%2bIs6nhzq%2fi5Q%3d%3d",
                party_time: "ES4WiEhrlKcv4AqxZW817fELBRpeAFwoUsmccTfUEt5XHamHdduECw%3d%3d",
                open_states: "ES4WiEhrlKcv4AqxZW817cmeY1X0EcwdV8Dbik%2fxJqklw9%2fINM1GMQ%3d%3d",
                docket_wrench: "ES4WiEhrlKcv4AqxZW817XC5zC57iJd9SS2OJE8uW7y8CtNYBKHOVQ%3d%3d"
            }
        },

        // D
        {
            quote: false,
            bottom: -288,
            html: "For more than seven years, Sunlight has supported the tools you use to keep government open and accountable. Now, we need your help to continue maintaining and improving our open gov tools.",
            urls: {
                sf: "ES4WiEhrlKfHGG%2bMqKRtBQFMy%2fHN6HeroDXRWhJYh3YzDNvmu45Mbw%3d%3d",
                ie: "ES4WiEhrlKfHGG%2bMqKRtBeHzWJhoNpw1SHgV%2fbnLqng%2bQuvKvh3JRQ%3d%3d",
                staffers: "ES4WiEhrlKfHGG%2bMqKRtBYU9AZGvuLwEbDhbmJFtTFnkjfuuoBvlfw%3d%3d",
                capitol_words: "ES4WiEhrlKfHGG%2bMqKRtBUHKNlQiTm1L1t%2fAZtdIDifarpB1r5ZOiQ%3d%3d",
                politwoops: "ES4WiEhrlKfHGG%2bMqKRtBQ5K1%2fhDAG6vyp0P6ErJ9n8b%2bFjS%2bnZukQ%3d%3d",
                party_time: "ES4WiEhrlKfHGG%2bMqKRtBen922i%2fYHhJj1JEtdW1hF8P2gtHH3Fm%2fg%3d%3d",
                open_states: "ES4WiEhrlKfHGG%2bMqKRtBcdM60Z3vPVNUfDqDo1BZEv20bP6C0C3Iw%3d%3d",
                docket_wrench: "ES4WiEhrlKfHGG%2bMqKRtBVKtb14vSnMU5dPs%2fCEKztH9TZDfWZiuzA%3d%3d"
            }
        },

        // E
        {
            quote: true,
            bottom: -288,
            html: "&ldquo;TurboVote got its start through Sunlight. Not only did they provide our first grant, they served as our fiscal sponsor and guided us in the initial structuring and building of our organization. We couldn't have gotten off the ground without them.&rdquo; <span class=\"attribution\">&mdash; <em>Seth Flaxman, TurboVote</em></span>",
            urls: {
                sf: "ES4WiEhrlKfiBxc3Kpg8cYRz2%2bRR%2f1fzLYu6pb7u65ZqNZbZieRkFg%3d%3d",
                ie: "ES4WiEhrlKfiBxc3Kpg8cfHj7Aebd6qH9LNcUSj633k83FgeurrtcQ%3d%3d",
                staffers: "ES4WiEhrlKfiBxc3Kpg8cWDlfqDH1uxY5GzS5yL%2bUQ1NCDg8WJMkzw%3d%3d",
                capitol_words: "ES4WiEhrlKfiBxc3Kpg8ce6YeCbWSMeQaQE3hAEXcsYfk%2fIGzT5K1g%3d%3d",
                politwoops: "ES4WiEhrlKfiBxc3Kpg8cWec3Th0pAGlo%2fQVClQngfMsYk%2bKWxuq0w%3d%3d",
                party_time: "ES4WiEhrlKfiBxc3Kpg8caGUCsN%2bZHf6YEjh93orBwwHoGnkTtSnkg%3d%3d",
                open_states: "ES4WiEhrlKfiBxc3Kpg8cSoqdq3HMdqJCp1bFf10GIejjsNc9W6rcQ%3d%3d",
                docket_wrench: "ES4WiEhrlKfiBxc3Kpg8cSeVmriKsVfjkNbyzSZnHB%2bi%2fEDOfmO2FQ%3d%3d"
            }
        },

        // F
        {
            quote: true,
            bottom: -288,
            html: "&ldquo;I came to Sunlight because I believe technology is incredibly powerful and government is incredibly important. I don't think there's any better place for working to bring the two together.&rdquo; <span class=\"attribution\">&mdash; <em>Tom Lee, Director of Sunlight Labs</em></span>",
            urls: {
                sf: "ES4WiEhrlKdDXjRIAQuDVNDReMFLMcETTNSqPh2aPnJJfwJooSR4oQ%3d%3d",
                ie: "ES4WiEhrlKdDXjRIAQuDVMJKNCEZQctzkjD5GBZJ7VfCiWJS8KbKFQ%3d%3d",
                staffers: "ES4WiEhrlKdDXjRIAQuDVMuhVE%2f0VX25PmDKP4qWmwPhPUnnPC6r5w%3d%3d",
                capitol_words: "ES4WiEhrlKdDXjRIAQuDVLmIAHZlEp16be5Qmh5Hggspi8RZIjuzLg%3d%3d",
                politwoops: "ES4WiEhrlKdDXjRIAQuDVCfxOZR0J0x3nF%2fBimKx4D2gKuWLu%2bT%2bTQ%3d%3d",
                party_time: "ES4WiEhrlKdDXjRIAQuDVPoBVZzDImnRdKYZWksI0pDcke46DDHpNg%3d%3d",
                open_states: "ES4WiEhrlKdDXjRIAQuDVFRJyBUQ36TPvO6zVffwBy8XoaAY7ICiUA%3d%3d",
                docket_wrench: "ES4WiEhrlKdDXjRIAQuDVDDbD3qYmbsmplBi%2fBJTF5X3a68ujD8F0w%3d%3d"
            }
        },

        // G
        {
            quote: true,
            bottom: -296,
            html: "&ldquo;Sunlight was one of the first organizations to really engage the technology community around improving government, and the organization has continued to inspire and leverage people with these critical skills in this important task. They are the leaders in a movement that matters.&rdquo; <span class=\"attribution\">&mdash; <em>Jen Pahlka, Founder of Code for America</em></span>",
            urls: {
                sf: "ES4WiEhrlKfGvWU2dfGp3eWO79ir6PwlHnibLmScIoFaYIOveDlleA%3d%3d",
                ie: "ES4WiEhrlKfGvWU2dfGp3Zbzsqph%2bGUtjX3zjy2%2bILW2PHhJUKUC0g%3d%3d",
                staffers: "ES4WiEhrlKfGvWU2dfGp3fLoCreho%2f7dwq1OECAps8HQqsz%2f9m5DRA%3d%3d",
                capitol_words: "ES4WiEhrlKfGvWU2dfGp3Y%2frdMS0Qx6UqbbQn1Svr3LllHNEGrCTuw%3d%3d",
                politwoops: "ES4WiEhrlKfGvWU2dfGp3R7JJHsqOyOeP5JQj%2fxiRMMsjikamB4p2Q%3d%3d",
                party_time: "ES4WiEhrlKfGvWU2dfGp3V3b6yfnZ4UlFeMxRQmtbWDedwubWbR%2fHA%3d%3d",
                open_states: "ES4WiEhrlKfGvWU2dfGp3YvzZnTOP6hbAlgKiBcRQWZ50WkjVeIpuw%3d%3d",
                docket_wrench: "ES4WiEhrlKfGvWU2dfGp3ZEkRrkhFGTTmNTBVOedFQAYOJKJNuBxRg%3d%3d"
            }
        },

        // H
        {
            quote: true,
            bottom: -296,
            html: "&ldquo;Since I began working at Sunlight six years ago, I've seen us evolve from a small non-profit working to expose money in politics to a global leader in the transparency movement. I'm thrilled to be working everyday to help define accountability and create a more open, inclusive democracy.&rdquo; <span class=\"attribution\">&mdash; <em>John Wonderlich, Sunlight Foundation Policy Director</em></span>",
            urls: {
                sf: "ES4WiEhrlKfJPbNqTm4u93n2EKLmptx%2bXuXhGUhShTkMQxiJ934IDg%3d%3d",
                ie: "ES4WiEhrlKfJPbNqTm4u99TMzAAb%2fw22gmRZo%2btPIP1F5bfvt8SeEg%3d%3d",
                staffers: "ES4WiEhrlKfJPbNqTm4u9%2fRdaO2x4KdNAAioCGZChq%2bCU5oj%2f7Balw%3d%3d",
                capitol_words: "ES4WiEhrlKfJPbNqTm4u9%2fNo%2feShXRMNT658paou%2bCg1cud1cy%2frXg%3d%3d",
                politwoops: "ES4WiEhrlKfJPbNqTm4u92wcYDlYpBhwEkV7hT4QKDxgiCMsH2hW4w%3d%3d",
                party_time: "ES4WiEhrlKfJPbNqTm4u93LXjTO8fi7nYCtxHhbSdf5nQlWCkA5kLw%3d%3d",
                open_states: "ES4WiEhrlKfJPbNqTm4u9%2bOpUJXwEn9FaNSf3AeopvapdHZsh0K%2brg%3d%3d",
                docket_wrench: "ES4WiEhrlKfJPbNqTm4u9%2f%2b6uk2bgIknIr7m77ZLNvdxSWKbsy6Syg%3d%3d"
            }
        },

        // I
        {
            quote: true,
            bottom: -288,
            html: "&ldquo;The Sunlight Foundation exists to seize the potential that technology offers to hold government accountable. Open and accessible data in the hands of citizens are key to that.&rdquo; <span class=\"attribution\">&mdash; <em>Ellen Miller, Co-Founder and Executive Director of the Sunlight Foundation</em></span>",
            urls: {
                sf: "ES4WiEhrlKcrHsC%2bG4xM%2fIpHYocnOuJGPqa%2fNUMT2%2fmkDvGXBgk28g%3d%3d",
                ie: "ES4WiEhrlKcrHsC%2bG4xM%2fP7qWUrWPfFnMgShofpe4jDVGot57NPwNA%3d%3d",
                staffers: "ES4WiEhrlKcrHsC%2bG4xM%2fJLtbIXcrupQgQhaW1WxAtG6uXfv2e1JPA%3d%3d",
                capitol_words: "ES4WiEhrlKcrHsC%2bG4xM%2fObwYT85cAhLI4hxs1wVSUDF8Ha1w26B4Q%3d%3d",
                politwoops: "ES4WiEhrlKcrHsC%2bG4xM%2fFS5KOb8TrRQNgySODlnPMc4YXyYBjCeFQ%3d%3d",
                party_time: "ES4WiEhrlKcrHsC%2bG4xM%2fHr6sONflyVB5uYb5v4HZ3m9NoZ0RZPqCw%3d%3d",
                open_states: "ES4WiEhrlKcrHsC%2bG4xM%2fKytDEZ3It4B%2fY7l9Qy6SPAxrAHsNsJScg%3d%3d",
                docket_wrench: "ES4WiEhrlKcrHsC%2bG4xM%2fFqbmuVWq8PXgPkp0ms1cLF5muRhipIMtA%3d%3d"
            }
        }
    ];

    window.abSwap = function(site) {
        var test = Banner.ab[Math.floor(Math.random() * Banner.ab.length)];
        var $p = $("#donor_banner p.because");

        if (test.quote)
            $p.addClass("quote")
        else
            $p.removeClass("quote");

        $p.html(test.html);

        var $bubble = $("#donor_banner .bubble");
        $bubble.css("bottom", "" + test.bottom + "px");

        var url = test.urls[site];
        var base = "https://services.myngp.com/ngponlineservices/contribution.aspx?X=";
        $("#donor_banner a.btn").attr("href", base + url);
    }

    $(document).ready(function() {
        var banner = new Banner($('html'));

        // HEY: change this to your site code, as seen in the above object
        abSwap('capitol_words');
    });

})(jQuery);