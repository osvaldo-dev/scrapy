from scrapy.downloadermiddlewares import retry


class RetryMiddleware(retry.RetryMiddleware):
    pass
