import scrapy
from horses.items.base import RaceInfo
from horses.items.base.processor_functions import handle_basic
from itemloaders.processors import MapCompose, TakeFirst

from .processor_functions import (
    get_distance,
    get_race_purse,
    get_racename,
    get_racenumber,
    get_startmethod,
)


class ItalianRaceInfo(RaceInfo):
    # längsta
    conditions = scrapy.Field(
        input_processor=MapCompose(handle_basic), output_processor=TakeFirst()
    )
    distance = scrapy.Field(
        input_processor=MapCompose(get_distance), output_processor=TakeFirst()
    )
    purse = scrapy.Field(
        input_processor=MapCompose(get_race_purse), output_processor=TakeFirst()
    )
    racename = scrapy.Field(
        input_processor=MapCompose(get_racename), output_processor=TakeFirst()
    )
    racenumber = scrapy.Field(
        input_processor=MapCompose(get_racenumber), output_processor=TakeFirst()
    )
    startmethod = scrapy.Field(
        input_processor=MapCompose(get_startmethod), output_processor=TakeFirst()
    )
