import scrapy
from horses.items.base import RaceStarterInfo
from itemloaders.processors import MapCompose, TakeFirst

from .processor_functions import (
    handle_distance,
    handle_driver,
    handle_finish,
    handle_purse,
    handle_startnumber,
    is_disqualified,
)


class DutchRaceStarterInfo(RaceStarterInfo):
    disqualified = scrapy.Field(
        input_processor=MapCompose(is_disqualified), output_processor=TakeFirst()
    )
    distance = scrapy.Field(
        input_processor=MapCompose(handle_distance), output_processor=TakeFirst()
    )
    driver = scrapy.Field(
        input_processor=MapCompose(handle_driver), output_processor=TakeFirst()
    )
    finish = scrapy.Field(
        input_processor=MapCompose(handle_finish), output_processor=TakeFirst()
    )
    purse = scrapy.Field(
        input_processor=MapCompose(handle_purse), output_processor=TakeFirst()
    )
    started = scrapy.Field(output_processor=TakeFirst())
    startnumber = scrapy.Field(
        input_processor=MapCompose(handle_startnumber), output_processor=TakeFirst()
    )
