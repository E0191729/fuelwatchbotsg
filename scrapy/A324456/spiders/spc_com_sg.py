from __future__ import absolute_import

from scrapy import Request
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy.loader.processors import Identity
from scrapy.spiders import Rule

from ..utils.spiders import BasePortiaSpider
from ..utils.starturls import FeedGenerator, FragmentGenerator
from ..utils.processors import Item, Field, Text, Number, Price, Date, Url, Image, Regex
from ..items import PortiaItem


class SpcComSg(BasePortiaSpider):
    name = "www.spc.com.sg"
    allowed_domains = [u'www.spc.com.sg']
    start_urls = [
        u'https://www.spc.com.sg/our-business/spc-service-station/latest-pump-price']
    rules = [
        Rule(
            LinkExtractor(
                allow=(),
                deny=('.*')
            ),
            callback='parse_item',
            follow=True
        )
    ]
    items = [[Item(PortiaItem,
                   None,
                   u'.col-lg-12',
                   [Field(u'LEVO_98',
                          'div:nth-child(1) > .pump-price *::text',
                          []),
                       Field(u'LEVO_95',
                             'div:nth-child(2) > .pump-price *::text',
                             []),
                       Field(u'LEVO_92',
                             'div:nth-child(3) > .pump-price *::text',
                             []),
                       Field(u'LEVO_DIESEL',
                             'div:nth-child(4) > .pump-price *::text',
                             [])])]]
