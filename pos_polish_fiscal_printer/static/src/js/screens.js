odoo.define('polish_fiscal_printer.screens', function (require) {
    "use strict";

    var screens = require('point_of_sale.screens');
    var core = require('web.core');
    
    var _t = core._t;

    screens.ReceiptScreenWidget.include({

        should_auto_print: function() {
            return !this.pos.get_order()._printed && (
                this.pos.config.iface_print_auto ||
                this.pos.config.pfp_print_through
            );
        },
        should_close_immediately: function() {
            var order = this.pos.get_order();
            var invoiced_finalized = order.is_to_invoice() ? order.finalized : true;

            return invoiced_finalized && this.pos.config.iface_print_skip_screen && (
                this.pos.proxy.printer ||
                this.pos.config.pfp_print_through
            );
        },
        
        handle_auto_print: function() {
            if (this.should_auto_print() && !this.pos.get_order().is_to_email()) {
                this.print();
                if (this.should_close_immediately()){
                    this.click_next();
                }
            } else {
                this.lock_screen(false);
            }
        },
        
        print: function() {                    
            if (this.pos.config.pfp_print_through) {
                // Printing through fiscal printer
                var order = this.pos.get_order();
                this.pos.proxy.pfp_print_fiscal(order.fiscalisation_data());
                order._printed = true;
            } else {
                if (!this.pos.proxy.printer) { // browser (html) printing
        
                    // The problem is that in chrome the print() is asynchronous and doesn't
                    // execute until all rpc are finished. So it conflicts with the rpc used
                    // to send the orders to the backend, and the user is able to go to the next 
                    // screen before the printing dialog is opened. The problem is that what's 
                    // printed is whatever is in the page when the dialog is opened and not when it's called,
                    // and so you end up printing the product list instead of the receipt... 
                    //
                    // Fixing this would need a re-architecturing
                    // of the code to postpone sending of orders after printing.
                    //
                    // But since the print dialog also blocks the other asynchronous calls, the
                    // button enabling in the setTimeout() is blocked until the printing dialog is 
                    // closed. But the timeout has to be big enough or else it doesn't work
                    // 1 seconds is the same as the default timeout for sending orders and so the dialog
                    // should have appeared before the timeout... so yeah that's not ultra reliable. 
        
                    this.lock_screen(true);
        
                    setTimeout(function(){
                        this.lock_screen(false);
                    }, 1000);
        
                    this.print_web();
                } else {    // proxy (html) printing
                    this.print_html();
                    this.lock_screen(false);
                }
            }            
        },
    });
        
});
    