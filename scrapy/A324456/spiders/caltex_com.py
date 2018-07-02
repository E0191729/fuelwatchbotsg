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


class Caltex(BasePortiaSpider):
    name = "www.caltex.com"
    allowed_domains = [u'www.caltex.com']
    start_urls = [
        u'https://www.caltex.com/sg/motorists/products-and-services/fuel-prices.html']
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
    items = [
        [
            Item(
                PortiaItem,
                None,
                u'.price-detail',
                [
                    Field(
                        u'Regular_92_with_Tehcron',
                        'div:nth-child(1) > .grid-fluid > .row-10 > div:nth-child(2) > .wrapper > p *::text',
                        []),
                    Field(
                        u'Premium_95_with_Techron',
                        'div:nth-child(2) > .grid-fluid > .row-10 > div:nth-child(2) > .wrapper > p *::text',
                        []),
                    Field(
                        u'Platinum_98_with_Tehcron',
                        'div:nth-child(3) > .grid-fluid > .row-10 > div:nth-child(2) > .wrapper > p *::text',
                        []),
                    Field(
                        u'Caltex_Diesel_with_Techron',
                        'div:nth-child(4) > .grid-fluid > .row-10 > div:nth-child(2) > .wrapper > p *::text',
                        [])])]]
