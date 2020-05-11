# -*- coding: utf-8 -*-
import base64
import codecs
import os
import random
from urllib.parse import urlparse

import time
from scrapy.exceptions import NotConfigured


class RotatingProxyMiddleware(object):
    def __init__(self, proxy_lists):
        self.proxy_lists = proxy_lists
        self.proxy_lists_keys = list(proxy_lists.keys())
        self.default_proxy_label = 'all'

    @classmethod
    def from_crawler(cls, crawler):
        s = crawler.settings
        proxy_path = s.get('ROTATING_PROXY_LIST_PATH', None)

        proxy_lists = {}

        if proxy_path is not None:
            if os.path.isdir(proxy_path):
                proxy_files = list(map(lambda p: os.path.join(proxy_path, p), os.listdir(proxy_path)))
            else:
                proxy_files = [proxy_path]

            for proxy_file in proxy_files:
                proxy_name, _ = os.path.splitext(os.path.basename(proxy_file))

                with codecs.open(proxy_file, 'r', encoding='utf8') as f:
                    proxy_list = [line.strip() for line in f if line.strip()]
                    proxy_lists[proxy_name] = proxy_list
        else:
            proxy_lists['all'] = s.getlist('ROTATING_PROXY_LIST')

        if not proxy_list:
            raise NotConfigured()
        # This method is used by Scrapy to create your spiders.
        s = cls(proxy_lists=proxy_lists)
        return s

    def get_random(self, proxy_label=None):
        proxy_keys = self.proxy_lists_keys
        proxy_label = proxy_label or self.default_proxy_label

        if proxy_label:
            proxy_keys = list(filter(lambda k: proxy_label in k, proxy_keys)) or proxy_keys

        proxy = random.choice(self.proxy_lists[random.choice(proxy_keys)])
        auth = None

        if '{rand}' in proxy:
            proxy = proxy.format(rand=str(time.time()).replace('.', ''))

        if '@' in proxy:
            up = urlparse(proxy)
            auth, domain = up.netloc.split('@')
            proxy = '{scheme}://{domain}'.format(scheme=up.scheme, domain=domain)
            auth = 'Basic ' + base64.b64encode(auth.encode()).decode()

        results = {
            'proxy': proxy,
            'basic_auth': auth,
        }

        return results

    def process_request(self, request, spider):
        if request.meta.get('skip_proxy', False):
            return
        proxy_label = spider.settings.get('PROXY_LABEL', None)

        proxy = self.get_random(proxy_label=proxy_label)
        if proxy['basic_auth']:
            request.headers['Proxy-Authorization'] = proxy['basic_auth']
        request.meta['proxy'] = proxy['proxy']

    def process_response(self, request, response, spider):
        return response

    def process_exception(self, request, exception, spider):
        pass
