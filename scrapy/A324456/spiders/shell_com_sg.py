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


class ShellComSg(BasePortiaSpider):
    name = "www.shell.com.sg"
    allowed_domains = [u'www.shell.com.sg']
    start_urls = [
        u'https://www.shell.com.sg/motorists/shell-fuels/shell-station-price-board.html']
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
                   u'table',
                   [Field(u'Shell_FuelSave_98',
                          'tr:nth-child(2) > td:nth-child(2) *::text, tbody > tr:nth-child(2) > td:nth-child(2) *::text',
                          [Price()]),
                       Field(u'Shell_FuelSave_95',
                             'tr:nth-child(3) > td:nth-child(2) *::text, tbody > tr:nth-child(3) > td:nth-child(2) *::text',
                             []),
                       Field(u'Shell_V_Power_Nitro+',
                             'tr:nth-child(4) > td:nth-child(2) *::text, tbody > tr:nth-child(4) > td:nth-child(2) *::text',
                             []),
                       Field(u'Shell_FuelSave_Diesel',
                             'tr:nth-child(5) > td:nth-child(2) *::text, tbody > tr:nth-child(5) > td:nth-child(2) *::text',
                             [])])]]
