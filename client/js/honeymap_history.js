
/*
 This file is part of HoneyMap (https://github.com/fw42/honeymap/),
 developed within the Honeynet Project (https://www.honeynet.org/),
 written by Florian Weingarten, Mark Schloesser, Johannes Gilger.

 See website for license and contact information.
 */

var validateDate = function(dateString) {
 return /^\d{4}\-(0?[1-9]|1[012])\-(0?[1-9]|[12][0-9]|3[01])$/.test(dateString);
};

(function () {
    var Honeymap, Log, config,
            g_bind = function (fn, me) {
                return function () {
                    return fn.apply(me, arguments);
                };
            };

    getConfig = function (config, data) {
        return {
            backgroundColor: '',
            series: {
                markers: [],
                regions: [
                    {
                        scale: config.colors.scale,
                        attribute: 'fill',
                        normalizeFunction: 'polynomial',
                        values: data//gdpData,
                    }
                ]
            },
            onRegionLabelShow: function (ev, label, code) {
                label.html("<big>" + label.html() + "</big>");
                return label.append(Honeymap.eventCountSummary(_this.hits.region[code]));
            },
            onRegionTipShow: function (e, el, code) {
                val = jQuery('#world-map').vectorMap('get', 'mapObject').series.regions[0].values[code];
                if (typeof val === "undefined") {
                    val = 0;
                }
                el.html(el.html() + ' (' + val + ')'); //gdpData[code]
            }
        };
    };


    Honeymap = (function () {

        function Honeymap(config, data) {
            var _this = this;
            this.config = config;
            this.hits = {
                region: {
                    total: {}
                },
                marker: {
                    total: 0
                }
            };
            this.captions = {};
            this.mapElem = jQuery('#world-map');
            this.fitSize();
            this.mapElem.vectorMap(getConfig(config, data));// gdpData
            this.mapObj = this.mapElem.vectorMap('get', 'mapObject');
            this.mapObj.regions['US'].config.name = "USA";
        }

        Honeymap.prototype.fitSize = function () {
            this.mapElem.width(jQuery(document).width() - 100);
            return this.mapElem.height(0.8 * jQuery(document).height());
        };

        Honeymap.prototype.updateRegionColors = function () {
            this.mapObj.series.regions[0].params.min = null;
            this.mapObj.series.regions[0].params.max = null;
            return this.mapObj.series.regions[0].setValues(this.hits.region["total"]);
        };

        Honeymap.prototype.regionCode = function (x, y) {
            var efp, rc;
            efp = jQuery(document.elementFromPoint(x + this.mapElem.offset().left, y + this.mapElem.offset().top));
            if (efp.is('path')) {
                return efp.attr('data-code');
            } else if (efp.is('circle') || (efp.is('div') && efp.hasClass('marker_animation'))) {
                efp.hide();
                rc = this.regionCode(x, y);
                efp.show();
                return rc;
            } else {
                return null;
            }
        };

        Honeymap.prototype.regionName = function (regionCode) {
            return this.mapObj.getRegionName(regionCode);
        };

        Honeymap.eventCountSummary = function (hits, origin) {
            var count, summary, total, type;
            if (hits == null)
                return;
            total = 0;
            summary = "<hr/>";
            if (origin === "dst") {
                summary += "<b>Destination:</b><br/>";
            } else if (origin === "src") {
                summary += "<b>Source:</b><br/>";
            }
            for (type in hits) {
                count = hits[type];
                count || (count = 0);
                summary += "<b>" + type + "</b>: " + count + "<br/>";
                total += count;
            }
            return summary + "<hr/><b>total</b>: " + total + " events";
        };

        return Honeymap;

    })();

    Log = (function () {

        function Log(config) {
            this.elem = jQuery("#log");
            this.max = config.markersMaxVisible;
            this.fitSize();
        }

        Log.prototype.fitSize = function () {
            this.elem.width(0.6 * jQuery(document).width());
            this.elem.css("margin-top", 0.03 * jQuery(document).height());
            return this.elem.height(0.15 * jQuery(document).height());
        };

        Log.prototype.clearOld = function () {
            var entries;
            entries = this.elem.find("div.log_entry");
            if (entries.length >= this.max) {
                entries.slice(0, entries.length / 2).remove();
                return this.elem.find("br").nextUntil('div.log_entry', 'br').remove();
            }
        };

        Log.prototype.add = function (msg) {
            var scroll;
            this.clearOld();
            scroll = this.elem.scrollTop() + this.elem.innerHeight() === this.elem[0].scrollHeight;
            this.elem.append('<div class="log_entry">' + msg + '</div><br/>');
            if (scroll)
                return this.elem.scrollTop(this.elem[0].scrollHeight);
        };

        return Log;

    })();

    config = {
        markersMaxVisible: 150,
        colors: {
            scale: ['#C8EEFF', '#006699']
        }
    };


    /**
     * Nacita ze souboru dny mapy.
     */
    Loader = (function () {

        function Loader() {
            Loader.self = this;
            this.log = new Log(config);
            //init mapa
            this.data = {"CZ": 0, "RU": 1000};//init data
            this.honeymap = new Honeymap(config, this.data);//data[Object.keys(data)[0]]
            jQuery(window).resize(function () {
                this.honeymap.fitSize();
                return log.fitSize();
            });
            this.mapObject = jQuery('#world-map').vectorMap('get', 'mapObject');

            $controls = $("<div/>", {"id": "controls-wrapper"}).prependTo("#world-map");


            //XX vsechny tyhle HTML-elementy controls by mohly byt v HTML sablone...
            //Autoplay button
            this.honeymap.interval = false;
            $("<span/>", {"id": "autoplay-toggler"}).text("▶").appendTo($controls).on("click", function () {
                //l = $("<label/>", {"id": "autoplay-toggler"}).prependTo("#world-map");
                //$("<input/>", {"type": "checkbox"}).appendTo(l).on("change", function () {
                if (!Loader.self.honeymap.interval) {//autoplay = true
                    $(this).text("⏸");
                    Loader.self.honeymap.interval = setInterval(function () {// DEMO AUTOPLAYE
                        //v = Math.floor(Math.random() * 6);
                        v = ($(Loader.self.honeymap.slider).slider('getValue') + 1) % 24;
                        $(Loader.self.honeymap.slider).slider('setValue', v).change();
                        Loader.self.changeValues(Loader.self.data[v]);
                    }, 500);
                } else {
                    $(this).text("▶");
                    clearInterval(Loader.self.honeymap.interval);
                    Loader.self.honeymap.interval = false;
                }



            });

            //Slider
            this.honeymap.slider = $("<div/>").appendTo(//slider zabije vsechny parametry, pro css pouzijeme wrapper
                    $("<div/>", {"id": "honeymap-slider-wrapper"}).appendTo($controls)
                    ).slider({
                value: Object.keys(this.data).sort().shift() * 1,
                min: 0,
                max: 23,
                step: 1,
                handle: 'square'
            }).on("change", {"this": this}, function (o) {//zmena slideru -> zmena mapy
                //jQuery('#world-map').vectorMap(getConfig(config, gdpDataPerHours[o.value.newValue]));
                if (typeof o.value !== "undefined") {
                    Loader.self.changeValues(Loader.self.data[o.value.newValue]);
                }
            });
            $("<div/>",{id:"hourIndicator"}).appendTo($controls);


            //Datepicker
            $('<div class="input-group date"><input type="text" placeholder="date" class="form-control"><span class="input-group-addon"><i class="glyphicon glyphicon-th"></i></span></div>').appendTo(
                    $('<div/>', {"id": "sandbox-container"}).appendTo($controls)).datepicker({
                format: "yyyy-mm-dd",
                endDate: "today",
                autoclose: true
            }).change(function (o) {//zmena data
                if(validateDate($(".input-group.date input").val())) {
                    Loader.self.loadDay($(".input-group.date input").val());
                }
            });


            this.log.add("<b>Welcome to HoneyMap</b>");
            this.log.add("This is weekly attack countries display of <a href=\"https://www.nic.cz/\" target=\"_blank\">CZ.NIC</a> honeypots.");
            this.log.add("");
            this.log.add("<b>Vítejte na HoneyMap</b>");
            this.log.add("Toto je týdenní zobrazení útokú ze zemí na honeypoty provozovaných sdružením <a href=\"https://www.nic.cz/\" target=\"_blank\">CZ.NIC</a>.");
            this.log.add("");
        }

        function data_max(arr) {
            return Math.max.apply(null, Object.keys(arr).map(function (e) {
                return arr[e];
            }));
        }
        function data_min(arr) {
            return Math.min.apply(null, Object.keys(arr).map(function (e) {
                return arr[e];
            }));
        }

        //Slider
        Loader.prototype.changeValues = function (values) {//values nejsou serazene a maji dvouciferne klice (hodina 01 misto 1)
            if(typeof values === "undefined") {
                return;
            }

            this.mapObject.series.regions[0].clear();

            this.mapObject.series.regions[0].scale.setMin(data_min(values));//XX maxmin hodnoty se pocitaji z aktualni hodiny... takhle by se mohly pocitat z celeho dne
            this.mapObject.series.regions[0].scale.setMax(data_max(values));

            this.mapObject.series.regions[0].setValues(values);
            $("#hourIndicator").html($(".slider .tooltip-inner").html() + ":00");
            //$(".slider .tooltip-inner").html($(".slider .tooltip-inner").html() + ":00");
            //console.log($(".slider .tooltip-inner").html());
        };

        Loader.prototype.loadDay = function (day) {
            if (day === this.day) {
                return;
            } else {
                this.day = day;
                window.location.hash = "#" + day;
            }
            $.ajax({
                url: '/input/' + day + '.json',
                dataType: 'json',
                context: this,
                complete: function (gdpDataPerHours) {
                    if ((typeof gdpDataPerHours.responseJSON !== "undefined")) {
                        this.log.add("Loaded: " + day + " <a href='/input/" + day + ".json'>csv</a>");
                    } else {
                        this.log.add("Failed: " + day);
                    }

                    this.data = {};
                    for (var key in gdpDataPerHours.responseJSON) {
                        this.data[key * 1] = gdpDataPerHours.responseJSON[key];
                    }
                    this.changeValues(this.data[$(this.honeymap.slider).slider('getValue')]);
                }
            });

        };
        return Loader;
    })();



    jQuery(document).ready(function () {
        //Nacist data pro den
        loader = new Loader();
        if (validateDate(window.location.hash.substring(1))) { //zjistit den z hashe
            var day = window.location.hash.substring(1);
            loader.loadDay(day);
            $("#sandbox-container input").val(day);
        } else {
            var d = new Date();
            d.setDate(d.getDate() - 1);
            var dateString = d.toISOString().slice(0,10);
            $("#sandbox-container input").val(dateString);
            loader.loadDay(dateString);
            window.location.hash = "#" + dateString;
        };

        $(window).on('hashchange', function () {
            if (validateDate(window.location.hash.substring(1))) {
                var day = window.location.hash.substring(1);
                loader.loadDay(day);
                $("#sandbox-container input").val(day);
            }
        });

    });

}).call(this);
