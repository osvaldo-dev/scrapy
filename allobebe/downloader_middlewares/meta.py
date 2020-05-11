# -*- coding: utf-8 -*-

import json
import random

import re


class userAgent(object):
    def __init__(self, ua_file):
        with open(ua_file, 'r') as f:
            self.user_agents = json.load(f)

    @classmethod
    def from_crawler(cls, crawler):
        o = cls(crawler.settings['USER_AGENT_FILE'])
        return o

    def generate_user_agent(self, spider):
        user_agent_template = spider.settings.get('USER_AGENT_TEMPLATE', '')
        ua = None
        if user_agent_template:
            all_occurances = len([m.start() for m in re.finditer('{rand', user_agent_template)])

            rands = {f'rand{i + 1}': random.randrange(1, 1000) for i in range(all_occurances + 1)}

            ua = user_agent_template.format(**rands)
        return ua

    def process_request(self, request, spider):
        user_agent = self.generate_user_agent(spider)

        if not user_agent:
            user_agent_label = spider.settings.getdict('USER_AGENT_LABEL', {})

            if user_agent_label:
                uas = list(filter(lambda ua: user_agent_label.items() <= ua.items(), self.user_agents))
            else:
                uas = self.user_agents

            user_agent = random.choice(uas)['ua']

        request.headers.setdefault('User-Agent', user_agent)
        # spider.logger.debug(user_agent)
