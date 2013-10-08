#!/usr/bin/env python
"""
Python library to check Euroticket à la card balance and history.
"""

import argparse
import collections
import html.parser
import http.cookiejar
import re
import urllib
import ssl


Card = collections.namedtuple('Card', ['card_holder_name', 'card_number', 'expiration_date',
                                       'outstanding_balance','current_balance', 'movements'])
Movement = collections.namedtuple('Movement', ['id', 'date', 'type', 'description', 'credit', 'debit', 'balance'])


class Alacard:
    """Python library to check Euroticket à la card balance and history."""

    BASE_URL = 'https://www.euroticket-alacard.pt/'
    MAIN_URL = 'jsp/portlet/c_index.jsp?_reset=true&_portal=www.alacard.pt'
    AUTH_URL = 'jsp/portlet/consumer/jve/c_login.jsp'
    HIST_URL = 'jsp/portlet/c_consumerprogram_home.jsp?section.jsp:section=account&' \
               'page.jsp:page=consumer/account/c_alltransactions.jsp'
    LOUT_URL = 'jsp/portlet/logout.jsp'
    ENCODING = 'ISO-8859-1'

    def __init__(self):
        """Creates the HTTP processor with a cookie jar and an enforced SSLv3 protocol."""

        # the SSLv3 handler is needed because the à la card web server only allows the
        # SSLv3 protocol and do not supports automatic secure protocol renegotiation.
        https_handler = urllib.request.HTTPSHandler(context=ssl.SSLContext(ssl.PROTOCOL_SSLv3))
        cookie_processor = urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar())
        self.opener = urllib.request.build_opener(https_handler, cookie_processor)
        urllib.request.install_opener(self.opener)
        # borrow the html parser's unescape
        self.html_parser = html.parser.HTMLParser()

    def get(self, username, password, history=False):
        """Connects to à la card website, authenticates and retrieve your card details."""

        # get main page and extract form fields and their values
        # this is needed because there is an auto-generated field that must be submitted
        regexp = '<input.*?name="(.*?)".*?(value="(.*?)".*?)?>'
        fields = self.__request(self.BASE_URL + self.MAIN_URL, regexp=regexp)

        # build auth form
        data = {}
        for field in fields:
            data[field[0]] = field[2]
        data['consumer/jve/c_login.jsp:login_id_form'] = username
        data['consumer/jve/c_login.jsp:password_form'] = password

        # authenticate and extract card data
        regexp = '<tr>\s*?' \
                 '<td class="formLabel">\s*(.*?)\s*</td>\s*' \
                 '<td class="txt">\s*(.*?)\s*</td>\s*' \
                 '</tr>'
        info = self.__request(self.BASE_URL + self.AUTH_URL, data, regexp=regexp)

        if history:
            # retrieve and extract card history
            regexp = '<tr class="tablerowalt[12]">\s*?' + \
                     '<td.*?>\s*(.*?)\s*</td>\s*' * 7 + \
                     '</tr>'
            movements = self.__request(self.BASE_URL + self.HIST_URL, regexp=regexp)
        else:
            movements = []

        # logout
        self.__request(self.BASE_URL + self.LOUT_URL, one_way=True)

        return Card(info[2][1],                                                     # card holder name
                    info[3][1],                                                     # card number
                    info[4][1],                                                     # card expiration date
                    float(info[0][1].replace('€', '').replace(',', '.')),           # card outstanding balance
                    float(info[1][1].replace('€', '').replace(',', '.')),           # card current balance
                    [Movement(mov[1],                                               # movement id
                              mov[0],                                               # movement date
                              mov[2],                                               # movement type
                              re.sub('.*: ', '', mov[3]),                           # movement description
                              float(mov[4].replace('€', '').replace(',', '.')),     # movement credit
                              float(mov[5].replace('€', '').replace(',', '.')),     # movement debit
                              float(mov[6].replace('€', '').replace(',', '.')))     # movement balance
                     for mov in movements])

    def print(self, card):
        """Prints the card to the standard output stream."""

        header = ("Holder Name:         %s\n"
                  "Card Number:         %s\n"
                  "Expiration Date:     %s\n"
                  "Outstanding Balance: %s\n"
                  "Current Balance:     %s\n")
        print(header % card[:5])

        if card.movements:
            movement_header = [('Id', 'Date', 'Type', 'Description', 'Credit', 'Debit', 'Balance')]
            self.__print_table(movement_header + card.movements, ' | ')

    def __request(self, url, data=None, one_way=False, regexp=None):
        """Creates and executes an HTTP request."""

        if data:
            req = urllib.request.Request(url, urllib.parse.urlencode(data).encode(self.ENCODING))
        else:
            req = urllib.request.Request(url)
        res = self.opener.open(req)
        if not one_way:
            html = res.read().decode(self.ENCODING)
            html = self.html_parser.unescape(html)
            if regexp:
                return re.compile(regexp, re.DOTALL).findall(html)
            else:
                return html

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


if __name__ == "__main__":
    # parse arguments
    parser = argparse.ArgumentParser(description='Check Euroticket à la card balance and history.')
    parser.add_argument('-u', metavar='username', required=True, help='the card number')
    parser.add_argument('-p', metavar='password', required=True, help='the card CVV number twice (unless you changed it!)')
    parser.add_argument('-m', action='store_true', required=False, help='display card movements')
    args = parser.parse_args()

    # show me the money
    alc = Alacard()
    card = alc.get(args.u, args.p, args.m)
    alc.print(card)
