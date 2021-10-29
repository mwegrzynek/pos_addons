import litex.novitus_xml as lnx


from . import fiscal_ready_name


class NovitusXMLPrinter(lnx.Printer):
    '''
    High level printing API - Novitus XML protocol
    '''

    def print_order(self, order):
        # Reset transaction state
        self.receipt_cancel()

        # Set error handling
        self.set_error('silent')

        # Get PTUs from printer
        ptus = {
            'free' if rate == 'free' else float(rate[:-1]): name
            for name, rate in self.taxrates_get()
        }

        vat_id = None

        client = order.get('client')
        if client:
            vat_id = client.get('vat')

        checkout_id = str(order.get('checkout_id', 1))

        if vat_id:
            # We have a VAT ID -- prepare invoice
            self.invoice_begin(
                invoice_type='invoice',
                number=order['name'],
                nip=vat_id,
                description='original',
                copies=-1,
                customer=client['name']
            )
        else:
            self.receipt_begin()

        for ol in order['orderlines']:

            ptu = None
            # Find right PTU
            for tax in ol['taxes']:
                if tax['name'] == 'VAT-ZW':
                    ptu = ptus['free']
                    break
                elif 'VAT' in tax['name']:
                    ptu = ptus.get(float(tax['amount']))
                    break

            if ptu is None:
                raise RuntimeError(
                    'Can not determine PTU for product "{}". Are taxes configured correctly?'.format(
                        ol['product_name']
                    )
                )

            self.item(
                name=fiscal_ready_name(ol['product_name']),
                quantity=ol['quantity'],
                quantityunit=ol['unit_name'],
                description=fiscal_ready_name(ol['product_description_sale']) if ol['product_description_sale'] else '',
                ptu=ptu,
                price=round(ol['price'], 2),
                discount_value=ol['discount']
            )

        for pl in order['paymentlines']:
            self.payment_add(
                type_=pl['pfp_fiscal_id'],
                value=pl['amount']
            )

        if vat_id:
            self.invoice_close(
                total=round(order['total_with_tax'], 2),
                systemno=order['name'],
                checkout=checkout_id,
                cashier=order['cashier'],
                buyer=''
            )
        else:
            self.receipt_close(
                total=round(order['total_with_tax'], 2),
                systemno=order['name'],
                checkout=checkout_id,
                cashier=order['cashier']
            )

    def status(self):
        return 'Connected to: {}; DLE: {}, ENQ: {}'.format(
            self.url,
            self.enq(),
            self.dle()
        )