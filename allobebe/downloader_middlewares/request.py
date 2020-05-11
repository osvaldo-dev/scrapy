# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from scrapy.exceptions import IgnoreRequest

from promosphere.extra.psqlwrapper import psqlWrapper
from promosphere.extra.utils import Utils


class isRequestItem(object):
    def __init__(self, crawler):
        self.crawler = crawler
        self.Utils = Utils()

        # Permit shell execution
        if crawler.spider:
            self.DB = psqlWrapper()

            c = self.DB.get_cursor()
            now = datetime.utcnow() - timedelta(days=2)

            c.execute(
                """SELECT href, discount_price, prop_price FROM scraped_item_parts_2 WHERE site_name = %(site_name)s AND updated_at >= %(min_date)s """,
                {'site_name': crawler.spider.name, 'min_date': now.strftime("%Y-%m-%d")})

            self.DB.conn.commit()
            self.items = c.fetchall()

        else:
            self.items = []

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def process_request(self, request, spider):
        # Get meta prices for comparaison
        price = request.meta.get('prop_price', False)
        discount_price = request.meta.get('discount_price', False)

        if price and discount_price:  # It's discount item
            # Format prices
            price = self.Utils.format_price(price)
            discount_price = self.Utils.format_price(discount_price)

            # Check price
            if price == 0 or discount_price == 0:
                raise IgnoreRequest('isRequestItem_price_null')

            if price == discount_price:
                raise IgnoreRequest('isRequestItem_prices_egal')

            # Check if exist
            if (request.url, str(discount_price), str(price)) in self.items:
                self.DB.update(request.url)
                raise IgnoreRequest('already exist')

            else:
                # Remove it in case
                self.DB.delete_one(request.url)

        elif price or discount_price:  # It's not discount item
            raise IgnoreRequest('not_discount_item')
    # else: # It's not item page


class isRequestItemNoDB(object):
    def __init__(self, crawler):
        self.crawler = crawler
        self.Utils = Utils()

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def process_request(self, request, spider):
        # Get meta prices for comparaison
        price = request.meta.get('prop_price', False)
        discount_price = request.meta.get('discount_price', False)

        if price and discount_price:  # It's discount item
            # Format prices
            price = self.Utils.format_price(price)
            discount_price = self.Utils.format_price(discount_price)

            # Check price
            if price == 0 or discount_price == 0:
                raise IgnoreRequest('isRequestItem_price_null')

            if price == discount_price:
                raise IgnoreRequest('isRequestItem_prices_egal')

        elif price or discount_price:  # It's not discount item
            raise IgnoreRequest('not_discount_item')
