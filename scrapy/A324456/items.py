from __future__ import absolute_import

import scrapy
from collections import defaultdict
from scrapy.loader.processors import Join, MapCompose, Identity
from w3lib.html import remove_tags
from .utils.processors import Text, Number, Price, Date, Url, Image


class PortiaItem(scrapy.Item):
    fields = defaultdict(
        lambda: scrapy.Field(
            input_processor=Identity(),
            output_processor=Identity()
        )
    )

    def __setitem__(self, key, value):
        self._values[key] = value

    def __repr__(self):
        data = str(self)
        if not data:
            return '%s' % self.__class__.__name__
        return '%s(%s)' % (self.__class__.__name__, data)

    def __str__(self):
        if not self._values:
            return ''
        string = super(PortiaItem, self).__repr__()
        return string


class PetrolPriceInSingaporeCaltexSingaporeItem(PortiaItem):
    Caltex_Diesel_with_Techron = scrapy.Field(
        input_processor=Number(),
        output_processor=Join(),
    )
    Platinum_98_with_Tehcron = scrapy.Field(
        input_processor=Number(),
        output_processor=Join(),
    )
    Premium_95_with_Techron = scrapy.Field(
        input_processor=Number(),
        output_processor=Join(),
    )
    Regular_92_with_Tehcron = scrapy.Field(
        input_processor=Number(),
        output_processor=Join(),
    )


class ShellStationPriceBoardShellSingaporeItem(PortiaItem):
    Shell_FuelSave_Diesel = scrapy.Field(
        input_processor=Price(),
        output_processor=Join(),
    )
    Shell_FuelSave_95 = scrapy.Field(
        input_processor=Price(),
        output_processor=Join(),
    )
    Shell_FuelSave_98 = scrapy.Field(
        input_processor=Price(),
        output_processor=Join(),
    )


class LatestPumpPricesSpcSingaporePetroleumComItem(PortiaItem):
    LEVO_92 = scrapy.Field(
        input_processor=Text(),
        output_processor=Join(),
    )
    LEVO_DIESEL = scrapy.Field(
        input_processor=Text(),
        output_processor=Join(),
    )
    LEVO_95 = scrapy.Field(
        input_processor=Text(),
        output_processor=Join(),
    )
    LEVO_98 = scrapy.Field(
        input_processor=Text(),
        output_processor=Join(),
    )
