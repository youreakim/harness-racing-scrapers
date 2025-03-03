import scrapy
from itemloaders.processors import TakeFirst, MapCompose

from horses.items.base import RaceInfo
from .processor_functions import handle_distance, handle_racenumber, handle_racetype, handle_purse, handle_startmethod


class DutchRaceInfo(RaceInfo):
    distance = scrapy.Field(
        input_processor=MapCompose(handle_distance),
        output_processor=TakeFirst()
    )
    purse = scrapy.Field(
        input_processor=MapCompose(handle_purse),
        output_processor=TakeFirst()
    )
    racenumber = scrapy.Field(
        input_processor=MapCompose(handle_racenumber),
        output_processor=TakeFirst()
    )
    racetype = scrapy.Field(
        input_processor=MapCompose(handle_racetype),
        output_processor=TakeFirst()
    )
    startmethod = scrapy.Field(
        input_processor=MapCompose(handle_startmethod),
        output_processor=TakeFirst()
    )
