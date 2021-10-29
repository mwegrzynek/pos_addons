odoo.define('polish_fiscal_printer.devices', function (require) {
    "use strict";

    var pos_devices = require('point_of_sale.devices');    

    pos_devices.ProxyDevice.include({
        
        pfp_print_fiscal: function(order) {
            
            return this.message(
                'polish_fiscal_printer_print_receipt', {
                    order: order
                },                 
            );
        },
    });
});

