odoo.define('polish_fiscal_printer.chrome', function (require) {
    "use strict";

    var core = require('web.core');
    var pos_chrome = require('point_of_sale.chrome'); 

    var _t = core._t;

    pos_chrome.ProxyStatusWidget.include({

        set_smart_status: function(status){
            if(status.status === 'connected'){
                var warning = false;
                var msg = '';
                if(this.pos.config.iface_scan_via_proxy){
                    var scanner = status.drivers.scanner ? status.drivers.scanner.status : false;
                    if( scanner != 'connected' && scanner != 'connecting'){
                        warning = true;
                        msg += _t('Scanner');
                    }
                }
                if( this.pos.config.iface_print_via_proxy || 
                    this.pos.config.iface_cashdrawer ){
                    var printer = status.drivers.printer ? status.drivers.printer.status : false;
                    if (printer != 'connected' && printer != 'connecting') {
                        warning = true;
                        msg = msg ? msg + ' & ' : msg;
                        msg += _t('Printer');
                    }
                }
                if( this.pos.config.iface_electronic_scale ){
                    var scale = status.drivers.scale ? status.drivers.scale.status : false;
                    if( scale != 'connected' && scale != 'connecting' ){
                        warning = true;
                        msg = msg ? msg + ' & ' : msg;
                        msg += _t('Scale');
                    }
                }

                if( this.pos.config.pfp_print_through ){
                    var pfp = status.drivers.polishfiscalprinter ? status.drivers.polishfiscalprinter.status : false;
                    if( pfp != 'connected' && pfp != 'connecting' ){
                        warning = true;
                        msg = msg ? msg + ' & ' : msg;
                        msg += _t('Fiscal Printer');
                    }
                }
    
                msg = msg ? msg + ' ' + _t('Offline') : msg;
                this.set_status(warning ? 'warning' : 'connected', msg);
            }else{
                this.set_status(status.status, status.msg || '');
            }
        }
    });


});