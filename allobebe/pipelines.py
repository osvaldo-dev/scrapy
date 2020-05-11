# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import time
from time import time
from datetime import datetime
from datetime import timedelta
from scrapy import signals
from scrapy.utils.project import get_project_settings
from scrapy.exceptions import DropItem
import sqlalchemy as db

settings = get_project_settings()

import logging
import psycopg2
import uuid

class PSQLPipeline(object):

	logger = logging.getLogger()
	item_count = 0
	def __init__(self):
		self.create_connection()
		self.create_table()

	def create_connection(self):
		host = settings['PSQL_HOSTNAME']
		user = settings['PSQL_USERNAME']
		password = settings['PSQL_PASSWORD']
		dbname = settings['PSQL_DATABASE']
		self.engine = db.create_engine('postgresql+psycopg2://%s:%s@%s/%s' % (user, password, host, dbname))
		self.conn = self.engine.connect()
		self.metadata = db.MetaData(schema=settings['PSQL_SCHEMA'])

	def create_table(self):

		self.details = db.Table('scraped_item_parts_tst_2', self.metadata,
			db.Column('id', db.Integer(), primary_key = True),
			db.Column('href', db.String(200)),
			db.Column('href_origin', db.String(200)),
			db.Column('prop_title', db.String(200)),
			db.Column('prop_brand', db.String(50)),
			db.Column('site_name', db.String(255)),
			db.Column('frontend_uuid', db.String(255)),
			db.Column('prop_description', db.Text()),
			db.Column('hierarchy', db.Text()),
			db.Column('discount_price', db.String(50)),
			db.Column('prop_price', db.String(50)),
			db.Column('prop_size', db.String(50)),
			db.Column('prop_color', db.String(50)),
			db.Column('prop_rating', db.String(50)),
			db.Column('prop_reviews', db.String(50)),
			db.Column('prop_image_1', db.String(200)),
			db.Column('prop_image_2', db.String(200)),
			db.Column('prop_image_3', db.String(200)),
			db.Column('created_at', db.DateTime(timezone=True)),
			db.Column('updated_at', db.DateTime(timezone=True)),
			db.Column('pipeline_updated_at', db.DateTime(timezone=True)),
		)
		self.logs = db.Table('spider_logs', self.metadata,
			db.Column('spider_name', db.String(200)),
			db.Column('spider_launcher', db.String(200)),
			db.Column('spider_status', db.Integer()),
			db.Column('start_time', db.DateTime(timezone=True)),
			db.Column('end_time', db.DateTime(timezone=True)),
			db.Column('valid_nb_page', db.String(200)),
			db.Column('valid_nb_data', db.String(200)),
			db.Column('valid_nb_scraped_item', db.String(200)),
			db.Column('invalid_nb_page', db.String(200)),
			db.Column('finish_reason', db.String(200))
		)
		self.metadata.create_all(self.engine)

	def process_item(self, item, spider):
		valid = True
		for data in item:
			if not data:
				valid = False
				raise DropItem("Missing {0}!".format(data))
		if valid:
			try:
				self.store_db(item)
				
			except Exception as e:
				self.logger.debug('*'*100)
				self.logger.info('Record: "%s" is duplicated in database. IGNORE!!! (%s)' % (item['url'],e))
				self.logger.debug('*'*100)
		spider.crawler.stats.set_value('custom_stats_total_stored_in_db', self.item_count)

		return item

	def open_spider(self, spider):
		self.session = int(time())
		start_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
		ins = self.logs.insert().values(
			spider_name='Allobebe',
			spider_launcher=self.session,
			spider_status=1,
			start_time=start_time)
		self.conn.execute(ins)
		if not spider.force:
			compare_date = datetime.utcnow() - timedelta(hours=50)
			table = db.Table('spider_logs', self.metadata, autoload=True, autoload_with=self.engine)
			query = db.select([table]).where(db.and_(table.columns.spider_status == '1', table.columns.spider_name == 'Allobebe', table.columns.start_time >= compare_date, table.columns.start_time < start_time))
			ResultProxy = self.conn.execute(query)
			ResultSet = ResultProxy.fetchall()
			if ResultSet and not spider.uniq_url:
				spider.force_stop = 'already_running'

	def store_db(self, item):
		timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

		ins = self.details.insert().values(
			href=item['url'],
			href_origin=item['url_origin'],
			prop_title=item['title'],
			site_name='Allobebe',
			frontend_uuid='ffc092df-3f52-45d4-97e4-ea7c5ce6dea3Allobebe',
			prop_description=item['description'],
			hierarchy=item['classification'],
			discount_price=item['discount_price'],
			prop_price=item['former_price'],
			prop_rating=item['prop_rating'],
			prop_reviews=item['prop_reviews'],
			prop_image_1=item['prop_image_1'],
			prop_image_2=item['prop_image_2'],
			prop_image_3=item['prop_image_3'],
			prop_brand=item['prop_brand'],
			prop_color=item['prop_color'],
			prop_size=item['prop_size'],
			created_at=timestamp,
			updated_at=timestamp,
			pipeline_updated_at=timestamp)
		self.conn.execute(ins)


	def close_spider(self, spider):
		try:
			table = db.Table('spider_logs', self.metadata, autoload=True, autoload_with=self.engine)
			query = db.update(table).where(db.and_(table.columns.spider_name == 'Allobebe',table.columns.spider_launcher == str(self.session))).values(
				end_time=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
				spider_status=0,
				valid_nb_page=spider.crawler.stats.get_value('downloader/response_status_count/200'),
				valid_nb_data=spider.crawler.stats.get_value('downloader/response_count'),
				valid_nb_scraped_item=spider.crawler.stats.get_value('item_scraped_count'),
				invalid_nb_page=spider.crawler.stats.get_value('downloader/response_status_count/404'),
				finish_reason=''
			)
			self.conn.execute(query)
			self.conn.close()
			self.engine.dispose()
		except Exception:
			pass