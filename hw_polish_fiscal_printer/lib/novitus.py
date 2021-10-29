import litex.novitus as ln


from . import fiscal_ready_name


class NovitusPrinter(ln.Printer):
    '''
    High level printing API - Novitus protocol
    '''

    def print_order(self, order):
        # Reset transaction state
        self.receipt_cancel()

        # Set error handling
        self.set_error('silent')

        # Get PTUs from printer
        ptus = {
            'free' if rate == 'free' else float(rate[:-1]): name
            for name, rate in self.taxrates_get() if rate != 'unused'
        }

        vat_id = None

        client = order.get('client')
        if client:
            vat_id = client.get('vat')

        checkout_id = str(order.get('checkout_id', 1))

        if vat_id:
            # We have a VAT ID -- prepare invoice
            self.invoice_begin(
                no_of_lines=len(order['orderlines']),            
                number=order['name'],
                nip=vat_id,
                customer='{name}\n{street}\n{zip} {city}\n{country_id[1]}'.format(**client)
            )
        else:
            self.receipt_begin(
                system_identifier=order['name']
            )

        for line_no, ol in enumerate(order['orderlines'], start=1):

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
                line_no=line_no,
                name=fiscal_ready_name(ol['product_name'])[:40],
                quantity=ol['quantity'],                
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
                number=order['name'],                
                seller=order['cashier']
            )
        else:
            self.receipt_close(
                total=round(order['total_with_tax'], 2),                
                cashier=order['cashier']
            )

    def status(self):
        return 'Connected to: {}; DLE: {}, ENQ: {}'.format(
            self.url,
            self.enq(),
            self.dle()
        )