odoo.define('polish_fiscal_printer.models', function (require) {
    "use strict";
    
    var core = require('web.core');        
    var pos_model = require('point_of_sale.models');
    var _t = core._t;

    pos_model.load_fields(
        'pos.config', 
        ['pfp_print_through', 'pfp_cashdrawer']
    );
    pos_model.load_fields('pos.payment.method', ['pfp_fiscal_id']);

    // Override loaded to modify use_proxy logic
    var models = pos_model.PosModel.prototype.models;
    for (var i = 0; i < models.length; i++) {
        var model = models[i];
        if (model.model === 'pos.config') {
            var old_loaded = model.loaded;
            model.loaded = function(self, configs) {
                old_loaded(self, configs);

                self.config.use_proxy = self.config.is_posbox && (
                    self.config.iface_electronic_scale ||
                    self.config.iface_print_via_proxy ||
                    self.config.iface_scan_via_proxy ||
                    self.config.iface_customer_facing_display ||
                    self.config.pfp_print_through
                );                
            }
        }
    }        

    pos_model.Order = pos_model.Order.extend({
        fiscalisation_data: function() {            
            var orderlines = [];

            this.orderlines.each(function(ol) {
                orderlines.push({
                    quantity: ol.get_quantity(),
                    unit_name: ol.get_unit().name,
                    price: ol.get_price_with_tax_before_discount() / ol.get_quantity(),                    
                    discount: '' + ol.get_discount() + '%',
                    product_name: ol.get_product().display_name,
                    product_description_sale: ol.get_product().description_sale,
                    taxes: ol.get_taxes()                                    
                });
            });
            
            var paymentlines = [];
            this.paymentlines.each(function(pl){
                paymentlines.push({
                    amount: pl.get_amount(),
                    payment_method: pl.payment_method.name,
                    pfp_fiscal_id: pl.payment_method.pfp_fiscal_id
                });          
            });
            
            var cashier = this.pos.get_cashier();
                        
            return {
                client: this.get_client(),
                orderlines: orderlines,
                paymentlines: paymentlines,            
                total_with_tax: this.get_total_with_tax(),                                
                name : this.uid,                
                server_id: this.server_id,
                cashier: cashier ? cashier.name : null,                                
                currency: this.pos.currency,       
                checkout_id: this.pos.config_id 
            }        
        }
    });
    
})