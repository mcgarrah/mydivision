import re
from io import StringIO

from lxml import etree

from .common import BaseDraw


class PowerBallDraw(BaseDraw):
    @property
    def balls(self):
        if self._balls is None:
            balls_element = self._tree.xpath('//div[@class="drawn-number Powerball"]')
            self._balls = [int(x.text) for x in balls_element]

        return self._balls

    @property
    def sups(self):
        if self._sups is None:
            sups_element = self._tree.xpath('//div[@class="drawn-number Supp Powerball"]')
            self._sups = [int(x.text) for x in sups_element]

        return self._sups

    @property
    def dividends(self):
        if self._dividends is None:
            self._dividends = []

            dividends_tablerows_elements = self._tree.xpath(
                '//div[@class="lotto-draw-result no-cufon clearfix powerball-result vic"]//table'
                '[@class="dividends-table"]//tbody/tr')

            for row_element in dividends_tablerows_elements:
                columns = row_element.xpath('.//td')

                try:
                    value = float(columns[0].text[1:].replace(',', ''))
                except ValueError:  # Probably no division amount
                    value = 0

                try:
                    winners = int(re.match(r'^(\d+).*$', columns[2].text).group(1))
                except AttributeError:
                    winners = 0

                dividend = {'name': row_element.xpath('.//th')[0].text,
                            'value': value,
                            'winners': winners,
                            'num_balls': int(columns[3].text),
                            'needs_powerball': columns[5].text is not None}

                self._dividends.append(dividend)

        return self._dividends

    def check_winner(self, picked_item):
        winning_balls = set(picked_item[0]).intersection(self.balls)
        winning_powerball = picked_item[1][0] == self.sups[0]

        for dividend in self.dividends:
            if len(winning_balls) == dividend['num_balls']:
                if not dividend['needs_powerball'] or winning_powerball:
                    amount_won = dividend['value']
                    print(dividend['name'], sorted(winning_balls), end='')

                    if winning_powerball:
                        print(' (%s)' % self.sups[0], end='')

                    print(' ${0:.2f}'.format(amount_won))
                    return amount_won
