
from odoo.tests.common import TransactionCase

from . import simple_receipt, discounted_receipt_with_client, NOVITUS_URL

class TestNovitusReceipt(TransactionCase):

    def setUp(self):
        from ..lib.novitus import NovitusPrinter

        self.prt = NovitusPrinter(NOVITUS_URL)

    def tests_simple_receipt(self):
        self.prt.print_order(simple_receipt)
        
    def tests_discounted_receipt_with_client(self):
        self.prt.print_order(discounted_receipt_with_client)
        
    