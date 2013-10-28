#!/usr/bin/env python
"""
Python library to check Euroticket à la card balance and recent history.
"""

import argparse
import collections
import http.cookiejar
import urllib
import ssl
from html.parser import HTMLParser
from xml.etree import ElementTree


Card = collections.namedtuple('Card', ['card_holder_name', 'card_number', 'expiration_date',
                                       'outstanding_balance','current_balance', 'movements'])
Movement = collections.namedtuple('Movement', ['id', 'date', 'type', 'description', 'debit', 'credit', 'balance'])


class Alacard:
    """Python library to check Euroticket à la card balance and history."""

    MAIN_URL = 'https://www.euroticket-alacard.pt/alc/pages/private/customer/customer.jsf'
    AUTH_URL = 'https://www.euroticket-alacard.pt/alc/pages/login.jsf'
    ENCODING = 'UTF-8'

    XPATH_INPUTS = './/form[@id="loginform"]//input[@name]'
    XPATH_NAME = './/table[@id="panelAcountData"]/tbody/tr/td[1]/table/tbody/tr[2]/td'
    XPATH_CARD = './/table[@id="panelAcountData"]/tbody/tr/td[2]/table/tbody/tr[2]/td'
    XPATH_DATE = './/table[@id="panelAcountData"]/tbody/tr/td[3]/table/tbody/tr[2]/td'
    XPATH_OUTB = './/table[@class="balance"]/tbody/tr/td[1]/table/tbody/tr/td[2]'
    XPATH_CURB = './/table[@class="balance"]/tbody/tr/td[2]/table/tbody/tr/td[2]'
    XPATH_MOVS = './/table[@class="rf-dt"]/tbody/tr[@class]'
    XPATH_MOV_ID = 'td[2]'
    XPATH_MOV_DATE = 'td[1]'
    XPATH_MOV_TYPE = 'td[3]'
    XPATH_MOV_DESC = 'td[4]'
    XPATH_MOV_CRED = 'td[5]/span'
    XPATH_MOV_DEBI = 'td[6]/span'
    XPATH_MOV_BALA = 'td[7]/span'

    def __init__(self):
        """Creates the HTTP processor with a cookie jar and an enforced SSLv3 protocol."""

        # the SSLv3 handler is needed because the à la card web server only allows the
        # SSLv3 protocol and do not supports automatic secure protocol renegotiation.
        https_handler = urllib.request.HTTPSHandler(context=ssl.SSLContext(ssl.PROTOCOL_SSLv3))
        cookie_processor = urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar())
        self.opener = urllib.request.build_opener(https_handler, cookie_processor)
        urllib.request.install_opener(self.opener)

    def get(self, username, password, history=False):
        """Connects to à la card website, authenticates and retrieve your card details."""

        # get main page
        # this is needed because there is an auto-generated field that must be submitted
        dom = self.__request(self.MAIN_URL)

        # extract form fields and build auth form
        data = {field.get('name'): field.get('value') for field in dom.findall(self.XPATH_INPUTS)}
        data['loginform:username'] = username
        data['loginform:password'] = password

        # authenticate and extract card data
        dom = self.__request(self.AUTH_URL, data)

        if history:
            # retrieve and extract card history
            # TODO retrieve all the movements
            movements = dom.findall(self.XPATH_MOVS)
        else:
            movements = []

        return Card(dom.findtext(self.XPATH_NAME).strip(),                  # card holder name
                    dom.findtext(self.XPATH_CARD).strip(),                  # card number
                    dom.findtext(self.XPATH_DATE).strip(),                  # card expiration date
                    dom.findtext(self.XPATH_CURB).strip(),                  # card outstanding balance
                    dom.findtext(self.XPATH_OUTB).strip(),                  # card current balance
                    [Movement(mov.findtext(self.XPATH_MOV_ID).strip(),      # movement id
                              mov.findtext(self.XPATH_MOV_DATE).strip(),    # movement date
                              mov.findtext(self.XPATH_MOV_TYPE).strip(),    # movement type
                              mov.findtext(self.XPATH_MOV_DESC).strip(),    # movement description
                              mov.findtext(self.XPATH_MOV_CRED).strip(),    # movement credit
                              mov.findtext(self.XPATH_MOV_DEBI).strip(),    # movement debit
                              mov.findtext(self.XPATH_MOV_BALA).strip())    # movement balance
                     for mov in movements])

    def print(self, card):
        """Prints the card to the standard output stream."""

        header = ("Holder Name:         %s\n"
                  "Card Number:         %s\n"
                  "Expiration Date:     %s\n"
                  "Outstanding Balance: %s\n"
                  "Current Balance:     %s")
        print(header % card[:5])

        if card.movements:
            print()
            movement_header = [('Id', 'Date', 'Type', 'Description', 'Debit', 'Credit', 'Balance')]
            self.__print_table(movement_header + card.movements, ' | ')

    def __request(self, url, data=None, one_way=False):
        """Creates and executes an HTTP request."""

        if data:
            req = urllib.request.Request(url, urllib.parse.urlencode(data).encode(self.ENCODING))
        else:
            req = urllib.request.Request(url)
        res = self.opener.open(req)
        if not one_way:
            html = res.read().decode(self.ENCODING)     # read and decode html
            parser = NaiveHTMLParser()
            dom = parser.feed(html)
            parser.close()
            return dom

    def __print_table(self, rows, separator=' '):
        """Print the card history in a tabular fashion."""

        if len(rows) == 0:
            return

        # find out the number of columns
        width = len(rows[0])

        # find out each column width
        lengths = [0] * width
        for row in rows:
            for i in range(width):
                lengths[i] = max(lengths[i], len(str(row[i]).strip()))

        patterns = ['%-' + str(length) + 's' for length in lengths]
        pattern = separator + separator.join(patterns) + separator

        # print it
        for row in rows:
            print(pattern % row)


class NaiveHTMLParser(HTMLParser):
    """
    Python 3.x HTMLParser extension with ElementTree support.
    @see https://github.com/marmelo/python-htmlparser
    """

    def __init__(self):
        self.root = None
        self.tree = []
        HTMLParser.__init__(self)

    def feed(self, data):
        HTMLParser.feed(self, data)
        return self.root

    def handle_starttag(self, tag, attrs):
        if len(self.tree) == 0:
            element = ElementTree.Element(tag, dict(self.__filter_attrs(attrs)))
            self.tree.append(element)
            self.root = element
        else:
            element = ElementTree.SubElement(self.tree[-1], tag, dict(self.__filter_attrs(attrs)))
            self.tree.append(element)

    def handle_endtag(self, tag):
        self.tree.pop()

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)
        pass

    def handle_data(self, data):
        if self.tree:
            self.tree[-1].text = data

    def get_root_element(self):
        return self.root

    def __filter_attrs(self, attrs):
        return filter(lambda x: x[0] and x[1], attrs) if attrs else []


if __name__ == "__main__":
    # parse arguments
    parser = argparse.ArgumentParser(description='Check Euroticket à la card balance and history.')
    parser.add_argument('-u', metavar='username', required=True, help='the card number')
    parser.add_argument('-p', metavar='password', required=True, help='the card password')
    parser.add_argument('-m', action='store_true', required=False, help='display card movements')
    args = parser.parse_args()

    # show me the money
    alc = Alacard()
    card = alc.get(args.u, args.p, args.m)
    alc.print(card)
