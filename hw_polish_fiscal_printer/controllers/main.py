# -*- coding: utf-8 -*-
import logging
import time
from pprint import pformat

# workaround https://bugs.launchpad.net/openobject-server/+bug/947231
# related to http://bugs.python.org/issue7980
from datetime import datetime
datetime.strptime('2012-01-01', '%Y-%m-%d')

try:
    from queue import Queue
except ImportError:
    from Queue import Queue # pylint: disable=deprecated-module
from threading import Thread, Lock

import litex.novitus_xml as lnx
import litex.novitus as ln

from serial.serialutil import SerialException
from odoo import http, _
from odoo.tools import config
from odoo.addons.hw_proxy.controllers import main as hw_proxy

from ..lib.novitus import NovitusPrinter
from ..lib.novitusxml import NovitusXMLPrinter

PROTOCOLS = {
    'novitusxml': NovitusXMLPrinter,
    'novitus': NovitusPrinter
}

_logger = logging.getLogger(__name__)

class PolishFiscalPrinter(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.queue = Queue()
        self.lock  = Lock()
        self.status = {'status': 'connecting', 'messages': []}

    def lockedstart(self):
        with self.lock:
            if not self.isAlive():
                self.daemon = True
                self.start()

    def autotdetect_printer(self):
        return 'hwgrep://.*Novitus.*'

    def get_printer(self):
        url = config.get('pfp_url', 'auto')
        protocol = config.get('pfp_protocol', 'novitus')

        try:
            if url == 'auto':
                url = self.autotdetect_printer()

            printer = PROTOCOLS[protocol](url)

            self.set_status(
                'connected',
                printer.status()
            )
            return printer

        except SerialException as e:
            # Configuration didn't point to a printer
            self.set_status('disconnected', str(e))
            return None

    def get_status(self):
        self.push_task('status')
        return self.status

    def set_status(self, status, message=None):
        _logger.info('%s: %s', status, (message or 'no message'))

        if status == self.status['status']:
            # Only append message if different from the last one
            if (
                message != None and
                len(self.status['messages']) == 0 or
                message != self.status['messages'][-1]
            ):
                self.status['messages'].append(message)
        else:
            self.status['status'] = status
            if message:
                self.status['messages'] = [message]
            else:
                self.status['messages'] = []

    def run(self):
        printer = None
        retry = True
        task = None
        data = None
        timestamp = None

        while True:
            try:
                retry = True

                timestamp, task, data = self.queue.get(True)

                printer = self.get_printer()

                if printer == None:
                    # Printer unavailable; wait and try again
                    if task != 'status':
                        self.queue.put((timestamp, task, data))

                    retry = False
                    time.sleep(5)

                    continue

                elif task == 'receipt':
                    if timestamp >= time.time() - 1 * 60 * 60:
                        _logger.info('Order to be printed: %s', pformat(data))
                        printer.print_order(data)                        

                elif task == 'cashbox':
                    if timestamp >= time.time() - 12:
                        printer.open_drawer()

                elif task == 'status':
                    pass

                retry = False

            except (ln.CommunicationError, lnx.CommunicationError) as e:
                self.set_status('disconnected', 'Printer unavailable')

            except (ln.ProtocolError, lnx.ProtocolError) as e:
                self.set_status('error', str(e))
                _logger.exception(e)

                # Fatal errors, that block receipt printing
                # In production they indicate a serious misconfiguration / bug             
                # and should be investigated ASAP
                if e.error_code in (16, 22, 27):
                    retry = False

            except Exception as e:
                self.set_status('error', str(e))
                _logger.exception(e)
                # Unknown exception; sleep for a while to avoid busy looping Odoo
                time.sleep(5)

            finally:
                if retry and task is not None:
                    self.queue.put((timestamp, task, data))

                if printer:
                    printer.close()
                    printer = None

    def push_task(self,task, data = None):
        self.lockedstart()
        self.queue.put((time.time(), task, data))


driver = PolishFiscalPrinter()

hw_proxy.drivers['polishfiscalprinter'] = driver

class PolishFiscalPrinterProxy(hw_proxy.Proxy):

    @http.route('/hw_proxy/polish_fiscal_printer_open_cashbox', type='json', auth='none', cors='*')
    def open_cashbox(self):
        driver.push_task('cashbox')

    @http.route('/hw_proxy/polish_fiscal_printer_print_receipt', type='json', auth='none', cors='*')
    def print_receipt(self, order):
        driver.push_task('receipt', order)
