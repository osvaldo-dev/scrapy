# -*- coding: utf-8 -*-
import scrapy
from scrapy.utils.project import get_project_settings
from allobebe.items import AllobebeItem
from datetime import datetime
import re
import json
from urllib.parse import unquote
import html
from bs4 import BeautifulSoup

settings = get_project_settings()

class AllobebeSpider(scrapy.Spider):
	name = "allobebe"
	allowed_domains = ["allobebe.fr"]
	start_urls = ['']
	page_url = ''
	total_duplicate = 0
	def __init__(self, category=None, debug=False, uniq_url=None, force=None, *args, **kwargs):
		self.debug = debug
		self.uniq_url = uniq_url
		self.force = force
		self.force_stop = False
		super(AllobebeSpider, self).__init__(*args, **kwargs)
		self.start_urls = [
			'https://www.allobebe.fr/outlet-S3-1.html',
			'https://www.allobebe.fr/code-extra5-O2447-1.html',
			'https://www.allobebe.fr/code-dodo-O2290-1.html',
			'https://www.allobebe.fr/jusqua-25-de-remise-chez-mam-O2456-1.html',
			'https://www.allobebe.fr/vives-les-promos-badabulle-O2474-1.html',
			'https://www.allobebe.fr/promos-sur-lunivers-du-sommeil-babymoov-O2473-1.html',
			'https://www.allobebe.fr/la-technologie-softness-par-renolux-O2455-1.html',
			'https://www.allobebe.fr/nouveaux-themes-disney-O2467-1.html',
			'https://www.allobebe.fr/un-mobile-upside-down-offert-O2468-1.html',
			'https://www.allobebe.fr/30-de-remise-sur-les-themes-amy-et-zoe-aston-et-jack-noukies-O2472-1.html',
			'https://www.allobebe.fr/vive-le-printemps-O2470-1.html',
			'https://www.allobebe.fr/atmosphera-for-kids-M438-1.html',
			'https://www.allobebe.fr/nouveautes-N1-1.html',
			'https://www.allobebe.fr/frais-de-port-offert-sur-sauthon-meubles-O2031-1.html',
			'https://www.allobebe.fr/outlet-S3-1.html',
		]

	def parse(self, response):
		if len(response.body) < 1000:
			return
		prod_list = response.css('.productsListItem')
		if prod_list is None or len(prod_list)==0:
			return
		for prod in prod_list:
			# soup = BeautifulSoup(str(prod.get()), "html.parser")
			discount = prod.css('.itemPriceOut span').xpath('text()').get()
			if discount and len(discount) > 0:
				detail_href = prod.css('.itemProductLink').xpath('@href').get()
				detail_url = response.urljoin(detail_href)

				final_price = prod.css('.itemPrice span').xpath('text()').get()
				final_price = re.findall(r'[\d\,]+', final_price)
				former_price = re.findall(r'[\d\,]+', discount)

				final_price = final_price[0].replace(',','.')
				former_price = former_price[0].replace(',','.')

				request = scrapy.Request(url=detail_url, callback=self.parse_details)
				request.meta['url_origin'] = response.url
				request.meta['discount_price'] = final_price
				request.meta['former_price'] = former_price
				print(final_price)
				print(former_price)
				print('-'*80)
				yield request

		pg_urls = response.xpath('//select[@id="pagesGoTo"]/option/@value').extract()
		if len(pg_urls):
			flag = False
			for pg_url in pg_urls:
				if flag == False and pg_url.strip()=='':
					flag = True
				if flag == True and pg_url.strip()!='':
					flag = False
					pg_url = response.urljoin(pg_url)
					yield scrapy.Request(url=pg_url, callback=self.parse)

	def parse_details(self, response):

		item = AllobebeItem()
		item['status'] = response.status
		item['url'] = response.url
		item['url_origin'] = response.meta['url_origin']
		item['title'] = response.xpath('//div[@class="productTitle"]/h1/span/text()').extract_first()
		
		item['discount_price'] = response.meta['discount_price']
		item['former_price'] = response.meta['former_price']
		item['prop_brand'] = response.xpath('//*[@itemprop="brand"]/text()').get()

		item['prop_color'] = ''
		item['prop_size'] = ''

		item['prop_rating'] = response.xpath('//*[@itemprop="ratingValue"]/text()').extract_first()
		item['prop_reviews'] = response.xpath('//*[@itemprop="ratingCount"]/text()').extract_first()

		if item['prop_reviews']:
			temp = re.findall(r'[\d]+', item['prop_reviews'])
			item['prop_reviews'] = temp[0]

		item['description'] = str(response.css('.productDescTxt').get())
		item['description'] = re.sub(r'class=\"[^\"]+\"', '', item['description'])
		bread = response.css('.breadcrumbs').xpath('.//a/span/text()').extract()
		item['classification'] = '<|=|>'.join([x.strip() for x in bread[:-1]])

		item['prop_image_1'] = ''
		item['prop_image_2'] = ''
		item['prop_image_3'] = ''
		
		imgUrls = response.xpath('//a[@class="itemLink"]/@href').extract()
		index = 0
		for img in imgUrls:
			if index > 2:
				break
			item['prop_image_'+str(index+1)] = img
			index += 1

		yield item
