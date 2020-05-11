# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from scrapy.http import HtmlResponse
import sqlalchemy as db
import psycopg2
from datetime import datetime
from datetime import timedelta
from scrapy.exceptions import IgnoreRequest

from scrapy.utils.project import get_project_settings
settings = get_project_settings()
class AllobebeSpiderMiddleware(object):
	# Not all methods need to be defined. If a method is not defined,
	# scrapy acts as if the spider middleware does not modify the
	# passed objects.

	@classmethod
	def from_crawler(cls, crawler):
		# This method is used by Scrapy to create your spiders.
		s = cls()
		crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
		return s

	def process_spider_input(self, response, spider):
		# Called for each response that goes through the spider
		# middleware and into the spider.

		# Should return None or raise an exception.
		return None

	def process_spider_output(self, response, result, spider):
		# Called with the results returned from the Spider, after
		# it has processed the response.

		# Must return an iterable of Request, dict or Item objects.
		for i in result:
			yield i

	def process_spider_exception(self, response, exception, spider):
		# Called when a spider or process_spider_input() method
		# (from other spider middleware) raises an exception.

		# Should return either None or an iterable of Response, dict
		# or Item objects.
		pass

	def process_start_requests(self, start_requests, spider):
		# Called with the start requests of the spider, and works
		# similarly to the process_spider_output() method, except
		# that it doesn’t have a response associated.

		# Must return only requests (not items).
		for r in start_requests:
			yield r

	def spider_opened(self, spider):
		spider.logger.info('Spider opened: %s' % spider.name)


class CustomDownloaderMiddleware(object):
	# Not all methods need to be defined. If a method is not defined,
	# scrapy acts as if the downloader middleware does not modify the
	# passed objects.

	def __init__(self, crawler):
		self.crawler = crawler
		self.create_connection()
		# Permit shell execution
		if crawler.spider:
			now = datetime.utcnow() - timedelta(days=2)
			
			query = db.select([self.table.columns.href, self.table.columns.discount_price]).where(db.and_(self.table.columns.site_name == 'Allobebe', self.table.columns.updated_at >= now.strftime("%Y-%m-%d")))
			ResultProxy = self.conn.execute(query)
			ResultSet = ResultProxy.fetchall()
			self.items = ResultSet

		else:
			self.items = []

	@classmethod
	def from_crawler(cls, crawler):
		return cls(crawler)

	def process_request(self, request, spider):
		# Get meta prices for comparaison
		discount_price = request.meta.get('discount_price', False)

		if discount_price:  # It's discount item
			# Check if exist
			if (request.url, str(discount_price)) in self.items:
				timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
				query = db.update(self.table).where(self.table.columns.href == request.url).values(
					updated_at=timestamp,
				)
				self.conn.execute(query)
				raise IgnoreRequest('already exist')
			else:
				del_st = db.delete(self.table).where(self.table.columns.href == request.url)
				self.conn.execute(del_st)

	def process_response(self, request, response, spider):
		return response

	def process_exception(self, request, exception, spider):
		pass

	def spider_opened(self, spider):
		spider.logger.info('Spider opened: %s' % spider.name)
	
	def create_connection(self):
		host = settings['PSQL_HOSTNAME']
		user = settings['PSQL_USERNAME']
		password = settings['PSQL_PASSWORD']
		dbname = settings['PSQL_DATABASE']
		self.engine = db.create_engine('postgresql+psycopg2://%s:%s@%s/%s' % (user, password, host, dbname))
		self.conn = self.engine.connect()
		self.metadata = db.MetaData(schema=settings['PSQL_SCHEMA'])
		self.table = db.Table('scraped_item_parts_tst_2', self.metadata, autoload=True, autoload_with=self.engine)