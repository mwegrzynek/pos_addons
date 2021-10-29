
from odoo.tests.common import TransactionCase

from . import NOVITUS_URL, simple_receipt, discounted_receipt_with_client, NOVITUS_XML_URL

class TestNovitusXMLReceipt(TransactionCase):

    def setUp(self):
        from ..lib.novitusxml import NovitusXMLPrinter
        self.prt = NovitusXMLPrinter(NOVITUS_XML_URL)        

    def tests_simple_receipt(self):
        self.prt.print_order(simple_receipt)
        
    def tests_discounted_receipt_with_client(self):
        self.prt.print_order(discounted_receipt_with_client)
        
    