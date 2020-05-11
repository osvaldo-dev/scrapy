# -*- coding: utf-8 -*-

# Scrapy settings for allobebe project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html
import os
import sys
BOT_NAME = 'allobebe'

SPIDER_MODULES = ['allobebe.spiders']
NEWSPIDER_MODULE = 'allobebe.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'allobebe (+http://www.yourdomain.com)'
USER_AGENT = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:63.0) Gecko/20100101 Firefox/63.0'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16
DOWNLOAD_DELAY = 0.5
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 0.5
AUTOTHROTTLE_MAX_DELAY = 1.5
AUTOTHROTTLE_TARGET_CONCURRENCY = 50

RETRY_TIMES = 20
RETRY_HTTP_CODES = [500, 502, 503, 504, 400, 408, 403]
# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'allobebe.middlewares.Gadgets360ComSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
# DOWNLOADER_MIDDLEWARES = {
#    'allobebe.middlewares.DartyComDownloaderMiddleware': 543,
# }

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   'allobebe.pipelines.PSQLPipeline': 300,
}
# PSQL_HOSTNAME = "localhost"
# PSQL_USERNAME = "postgres"
# PSQL_PASSWORD = "nsdpwd7NSDPWD&"
# PSQL_DATABASE = "but"
# PSQL_SCHEMA = "public"
# USER_AGENT_FILE = 'allobebe/uas.json'

# ROTATING_PROXY_LIST_PATH = 'allobebe/proxies/proxies-test.txt'

PSQL_HOSTNAME = "localhost"
PSQL_USERNAME = "pgscrapy"
PSQL_PASSWORD = "Td*4h6VtS)%Cp9ES"
PSQL_DATABASE = "promosphere"
PSQL_SCHEMA = "scbackend"
ROTATING_PROXY_LIST_PATH = '/home/scrapy/promosphere/proxies/main_proxies.txt'

USER_AGENT_FILE = '/home/scrapy/uas.json'

DOWNLOADER_MIDDLEWARES = {
    'allobebe.downloader_middlewares.meta.userAgent': 500,
    'allobebe.middlewares.CustomDownloaderMiddleware': 543,
    # 'allobebe.downloader_middlewares.proxy.RotatingProxyMiddleware': 510,
    'rotating_proxies.middlewares.RotatingProxyMiddleware': 610,
    'rotating_proxies.middlewares.BanDetectionMiddleware': 620,
    # ...
}
